/* CWI SCHEMA

Version:    c4.4.0
Date:       2021-02-19
Author:     William Olsen

These are queries for populating the c7id table with identifiers contained in
the c4ix or c4locs tables in the MGS version of c4.  The data is first imorted 
to c4id, then analyzed, and finally copied into c7id. The order that queries
are run in is critical.

The c7id table implements version 4 of the MNU identifier model.  The MNU 
identifier model has data integrity constraints on identifiers that the data in
the c4ix and c4id tables may violate.  The queries in this file fail when they 
attempt to append records to c7id that are not MNU-compliant.

The queries attempt to correctly identify which data is non-compliant, to
label it with the reason why it is non-compliant, and then to import it to c7id
in a way that makes it compliant.  In most cases there is some level of 
ambiguity that can only be resolved with certainty by reference to original 
sources.  But in many cases the ambiguity is low enough that guesses can be 
made.  

An auxilliary table, c7id_match, is used to keep track of probable redundant
wellids that should be merged.

Most queries are broken into 3 parts: First an exploratory query that simply
displays the found records and the the planned labels, second a query that 
updates labels in c4id, and third a query to populate c7id_match.

Comparisson of c4id to c7id can identify every case where data has been 
modified, and traces are left in both tables to indicate the reason for the 
change.  In some cases the reason is limitations in the CWI identifier model,
but in other cases the reason is an actual error in the CWI data. In the latter
case, CWI maintainers should be notified of the error, and documentation 
should be provided sufficient to guide corrections.

There are a number of individual queries that are run in succession. Each 
identifies a particular group of non-compliant identifiers, and updates 
labeling columns in c4id.  In each case the MNU value is set to a value 
between 10 and 20.    These values then determine how the row is appended 
to the c7id table.  The MNU values are reassigned to Recal that in the MNU 
identifier model, regular Minnesota Unique Well Numbers are assigned MNU=1, 
and non-MNU identifiers are assigned MNU=0. These queries do not change the 
MNU values of MNU-compliant records.

In version 4 of the MNU identifier model, MNU compliant identifiers  have MNU 
values from 1 to 5, and values from 6 to 9 are used to flag identifiers that 
need some kind of manual evaluation.  When the data is copied from c4id to 
c7id, MNU values from 10 to 20 are translated to to 1 to 9 range.

There are sometimes recent well records found in the shape files used to fill 
the c4locs table that are not yet in c4ix or c4id.  These Recent records have 
to be appended to c4ix when Foreign Keys are implemented, because c4locs.wellid 
references c4ix.wellid. Why does this matter here?  When identifiers are added 
to c4id from c4ix, their origin is recorded by setting c4id.ID_PROG='c4ix';
when their origin is c4locs, then we set c4id.ID_PROG='c4locs'. 

c4.4.0 version:
    - Contains the c4 data tables
    - Adds table c4locs for well coordinates.
    - Adds rowid and wellid to each c4 data table
    - Adds Foreign Key constraints to all tables, wellid -> c4ix(wellid)
    + Makes c7id into the main table for all well identifiers.
        + Add all Unique Well Numbers in c4ix & c4locs into c4id.
            ID_TYPE = 'c4ix' or 'c4locs'; identifies the source.
            ID_PROG = 'MNUNIQ';
            pMNU = 1; These will be the primary identifiers by default
        + Add conditional unique indices on c7id to enforce uniqueness.
        + Add Views on c7id to simplify using Unique Well Numbers for search
          and for export.
        + Data, as cloned from cwi is found in c4id. But it may not pass all 
		  integrity checks required by c7id.
  
References:

sql/cwischema_c4_versions.txt

County Well Index, 2021, Database created and maintained by the Minnesota
Geological Survey, a department of the University of Minnesota,  with the
assistance of the Minnesota Department of Health.
http://mgsweb2.mngs.umn.edu/cwi_doc/cwidoc.htm

https://www.sqlite.org
*/

update c4id
    set MNU = 0
;

update c4id
    set MNU = 1
    where ID_PROG in ('MNUNIQ','WMWSR','WSERIES')
;

-- Remove records from c4id where the IDENTIFIER is null.
Delete from c4id 
where IDENTIFIER is Null;
;

-- Remove identifiers from c4id where the identifier is equivalent to the wellid. 
-- The wellid's should be found in c4ix, and will later be imported to c7id as
-- identifiers along with all of the other wellids in c4ix.
Delete from c4id 
where MNU = 1
  and cast(wellid as text) = IDENTIFIER 
;

-- Queries on c4id & c4ix to run before modifying c4id or filling c7id.
-- Assumes that c4id.MNU has been set to (0,1).
-- ========================================================================= --

-- 1) C4ID_KNOWN_XREFS  
--    Wells with 2 wellids, 2 entries in c4ix, and 2 entries in c4id that cross-
--    reference each other.  These are redundant records known to CWI maintainers,
--    that they choose to retain as redundant records.
--
-- 1.1 explore the data
-- select A.wellid as wellidA, B.identifier as identifierB, C.wellid as wellidC, 
--        B.wellid as wellidB, A.identifier as identifierA, C.identifier as identifierC,
--       'C4ID_KNOWN_XREFS' as mexplain,
--       'DELETE ixB idA' as mplan,
--       0 as mresolved 
-- from c4id A
-- left join c4id B
--   on cast(A.wellid as text) = B.identifier
--   and A.MNU=1 and B.MNU=1 
-- left join c4id C
--   on cast(B.wellid as text) = C.identifier
--   and B.MNU=1 and C.MNU=1 
-- where A.wellid != B.wellid
--   and B.wellid != C.wellid
--   and A.identifier = C.identifier
-- order by A.wellid
-- ;
--
-- 1.2 set mexplain in c4id
update c4id set mexplain='C4ID_KNOWN_XREFS', MNU=11
where rowid in ( 
    select A.rowid  
    from c4id A
    left join c4id B
      on cast(A.wellid as text) = B.identifier
      and A.MNU in(1,11) and B.MNU in(1,11) 
    left join c4id C
      on cast(B.wellid as text) = C.identifier
      and B.MNU in(1,11) and C.MNU in(1,11)
    where A.wellid != B.wellid
      and B.wellid != C.wellid
      and A.identifier = C.identifier)
;

-- 1.3 fill c7id_match  -- 87 rows
insert into c7id_match (wellid1, identifier1, wellid2, identifier2, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1,  
       B.wellid as wellid1, B.identifier as identifier2,  
      'C4ID_KNOWN_XREFS' as mexplain,
      'MNU=11, MERGE id2 INTO id1' as mplan,
      0 as mresolved 
from c4id A
left join c4id B
  on cast(A.wellid as text) = B.identifier
  and A.MNU in(1,11) and B.MNU in(1,11)  
left join c4id C
  on cast(B.wellid as text) = C.identifier
  and B.MNU in(1,11) and C.MNU in(1,11)  
where A.wellid <= B.wellid
  and B.wellid != C.wellid
  and A.identifier = C.identifier
;

-- ========================================================================= --
-- 12) C4ID_UNRESOLVED_MERGES
-- 12.1 exploration 
select  A.identifier,  A.wellid,  A.id_type, A.id_prog, A.MNU, a.mexplain
from c4id A
left join c4ix B
on A.identifier = B.unique_no
where A.MNU in (1,12)
  and (A.mexplain is null or A.mexplain = 'C4ID_UNRESOLVED_MERGES')
  and A.id_prog = 'MNUNIQ'
  and B.wellid is not null
  order by b.unique_no
;

-- 12.2 set mexplain in c4id
select * from c4id
--update c4id set mexplain='C4ID_UNRESOLVED_MERGES', MNU=12
where rowid in ( 
    select A.rowid  
    from c4id A
    left join c4ix B
    on A.identifier = B.unique_no
    where A.MNU in (1,12)
      and A.mexplain is null 
      and A.id_prog = 'MNUNIQ'
      and B.wellid is not null
      order by b.unique_no
);    
-- 12.3  insert into c7id_match  --  
-- insert into c7id_match (wellid1, identifier1, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
      'C4ID_UNRESOLVED_MERGES' as mexplain,
      'MNU=12, MANUAL CHECK' as mplan,
      0 as mresolved 
from c4id A
where A.MNU=12
;

-- ========================================================================= --
-- 13) C4ID_UNRESOLVED_MERGES_WMWSR
-- 13.1 exploration 
select  A.identifier,  A.wellid,  A.id_type, A.id_prog, A.MNU, a.mexplain
from c4id A
left join c4ix B
on A.identifier = B.unique_no
where A.MNU in (1,13)
  and (A.mexplain is null or A.mexplain = 'C4ID_UNRESOLVED_MERGES_WMWSR')
  and A.id_prog = 'WMWSR'
  and B.wellid is not null
  order by b.unique_no
;

-- 13.2 set mexplain in c4id
select * from c4id
--update c4id set mexplain='C4ID_UNRESOLVED_MERGES_WMWSR', MNU=13
where rowid in ( 
    select A.rowid  
    from c4id A
    left join c4ix B
    on A.identifier = B.unique_no
    where A.MNU in (1,13)
      and (A.mexplain is null or A.mexplain='C4ID_UNRESOLVED_MERGES_WMWSR')
      and A.id_prog = 'WMWSR'
      and B.wellid is not null
      order by b.unique_no
);    
-- 13.3  insert into c7id_match  --  
-- insert into c7id_match (wellid1, identifier1, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
      'C4ID_UNRESOLVED_MERGES_WMWSR' as mexplain,
      'MNU=13, MANUAL CHECK' as mplan,
      0 as mresolved 
from c4id A
where A.MNU=13
;

-- ========================================================================= --
-- 14) C4ID_UNRESOLVED_MERGES_WSERIES
-- 14.1 exploration 
select  A.identifier,  A.wellid,  A.id_type, A.id_prog, A.MNU, a.mexplain
from c4id A
left join c4ix B
on A.identifier = B.unique_no
where A.MNU in (1,14)
  and (A.mexplain is null or A.mexplain = 'C4ID_UNRESOLVED_MERGES_WSERIES')
  and A.id_prog = 'WSERIES'
  and B.wellid is not null
  order by b.unique_no
;

-- 14.2 set mexplain in c4id
select * from c4id
-- update c4id set mexplain='C4ID_UNRESOLVED_MERGES_WSERIES', MNU=14
where rowid in ( 
    select A.rowid  
    from c4id A
    left join c4ix B
    on A.identifier = B.unique_no
    where A.MNU in (1,14)
      and A.mexplain is null 
      and A.id_prog = 'WSERIES'
      and B.wellid is not null
      order by b.unique_no
);    
-- 14.3  insert into c7id_match  --  
-- insert into c7id_match (wellid1, identifier1, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
      'C4ID_UNRESOLVED_MERGES_WSERIES' as mexplain,
      'MNU=14, MANUAL CHECK' as mplan,
      0 as mresolved 
from c4id A
where A.MNU=14
;


-- ========================================================================= --
-- 2) C4ID_BAD_LINKS_OR_REDUNDANT_WELLS : 37 records.
-- These cannot be deleted because the corrupt identifiers are W-numbers and this is thier only occurance.
-- 2.1 exploration
-- select A.wellid as wellid1, A.identifier as identifier1, 
--        B.wellid as wellid2, B.identifier as identifier2,
--       'C4ID_BAD_LINKS_OR_REDUNDANT_WELLS' as mexplain,
--       'MNU=9, MANUAL FIX' as mplan,
--       0 as mresolved 
-- from c4id A
-- left join c4id B
--   on A.identifier = B.identifier
--   and A.MNU=1 and B.MNU=1 
-- where 
--   A.wellid < B.wellid
--   and A.identifier like('%W%')
-- ;

-- 2.2 set mexplain in c4id  -- 74 rows
update c4id set mexplain='C4ID_BAD_LINKS_OR_REDUNDANT_WELLS', MNU=9
where rowid in (
select A.rowid 
from c4id A
left join c4id B
  on A.identifier = B.identifier
  and A.MNU=1 and B.MNU=1 
where 
  A.wellid != B.wellid
  and A.identifier like('%W%'))
order by identifier;

-- 2.3 insert rows in c7id_match -- 37 rows
insert into c7id_match (wellid1, identifier1, wellid2, identifier2, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
       B.wellid as wellid2, B.identifier as identifier2,
      'C4ID_BAD_LINKS_OR_REDUNDANT_WELLS' as mexplain,
      'MNU=9, MANUAL FIX' as mplan,
      0 as mresolved 
from c4id A
left join c4id B
  on A.identifier = B.identifier
  and A.MNU=9 and B.MNU=9 
where 
  A.wellid < B.wellid
  and A.identifier like('%W%')
;

-- ========================================================================= --
-- 3) 'C4ID_1WELL_ASSIGNED_2HNUMBERS' -- 25 records
-- Multiple H-numbers assigned to One construction number   
--
-- 3.1 C4ID_1WELL_ASSIGNED_2HNUMBERS - Exploration
-- select A.wellid as wellid1, A.identifier as identifier1, 
--        B.wellid as wellid2, B.identifier as identifier2,
--       'C4ID_1WELL_ASSIGNED_2HNUMBERS' as mexplain,
--       'MNU=8, MANUAL FIX' as mplan,
--       0 as mresolved 
--       ,X.WELLID,Y.WELLID,X.USE_C, Y.USE_C
-- from c4id A
-- left join c4id B
--   on A.wellid = B.wellid
--   and A.MNU=1 and B.MNU=1 
-- left join c4ix X
--   on X.wellid = A.wellid
-- left join c4ix Y
--   on Y.wellid = B.wellid
-- where A.identifier < B.identifier 
--   and A.identifier like ('H%')
--   and B.identifier like ('H%')
-- order by A.wellid;
--
-- 3.2 C4ID_1WELL_ASSIGNED_2HNUMBERS update c4id  -- 42 rows
update c4id set mexplain='C4ID_1WELL_ASSIGNED_2HNUMBERS', MNU=8
where rowid in (
   select A.rowid
   from c4id A
    left join c4id B
      on A.wellid = B.wellid
      and A.MNU=1 and B.MNU=1 
    left join c4ix X
      on X.wellid = A.wellid
    left join c4ix Y
      on Y.wellid = B.wellid
    where A.identifier != B.identifier 
      and A.identifier like ('H%')
      and B.identifier like ('H%'))  
;

-- 3.3  insert into c7id_match  -- 25 rows
insert into c7id_match (wellid1, identifier1 ,wellid2, identifier2, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
       B.wellid as wellid2, B.identifier as identifier2,
      'C4ID_1WELL_ASSIGNED_2HNUMBERS' as mexplain,
      'MNU=8, MANUAL FIX' as mplan,
      0 as mresolved 
      --,X.WELLID,Y.WELLID,X.USE_C, Y.USE_C
from c4id A
left join c4id B
  on A.wellid = B.wellid
  and A.MNU=8 and B.MNU=8 
left join c4ix X
  on X.wellid = A.wellid
left join c4ix Y
  on Y.wellid = B.wellid
where A.identifier < B.identifier 
  and A.identifier like ('H%')
  and B.identifier like ('H%')
order by A.wellid;


-- 4) C4ID_H_IS_MULTY_OR_BAD_REF  -- 3473 records
--    One H number is assigned to multiple wellids
-- 4.1 Exploration
--select A.wellid as wellid1, A.identifier as identifier1, 
--       B.wellid as wellid2, B.identifier as identifier2,
--      'C4ID_H_IS_MULTY_OR_BAD_REF' as mexplain,
--      'MNU=7, ASSUME_MULTIWELL_H' as mplan,
--      0 as mresolved 
--from c4id A
--left join c4id B
--  on A.identifier = B.identifier
--  and A.MNU=1 and B.MNU=1 
--where 
--  A.wellid < B.wellid
--  and A.identifier like('%H%')
--;
--
-- 4.2  update c4id  -- 1803 rows
update c4id set mexplain='C4ID_H_IS_MULTY_OR_BAD_REF', MNU=7
where rowid in (
    select A.rowid 
    from c4id A
    left join c4id B
      on A.identifier = B.identifier
      and A.MNU=1 and B.MNU=1 
    where 
      A.wellid != B.wellid
      and A.identifier like('%H%')
);

-- 4.3  insert into c7id_match  --  1803 rows
insert into c7id_match (wellid1, identifier1, mexplain, mplan, mresolved)
select A.wellid as wellid1, A.identifier as identifier1, 
      'C4ID_H_IS_MULTY_OR_BAD_REF' as mexplain,
      'MNU=7, ASSUME_MULTIWELL_H' as mplan,
      0 as mresolved 
from c4id A
where A.MNU=7
;
 
-- -- Verify that there are no more multiwell references in c4id
-- -- should return count=0. Depends on prior queries changing the MNU number from 1.
-- select count(A.rowid)  
-- from c4id A
-- left join c4id B
--   on A.identifier = B.identifier
--   and A.MNU=1 and B.MNU=1 
-- where 
--   A.wellid < B.wellid;
--   
-- -- summarize results:
-- select mexplain, MNU, count(*) from c4id group by mexplain, MNU;
-- select mexplain, mplan, count(*) from c7id_match group by mexplain, mplan;
-- select MNU, count(*) from c7id group by MNU;
-- 
-- 5) Begin insertion of records into c7id
-- 5.1 insert identifiers from c4ix.  --562489 records
Insert into c7id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, MNU, pMNU)
    select wellid, RELATEID, UNIQUE_NO, 'c4ix', 'MNUNIQ', 1, 1
    from c4ix
;

-- 5.2 append records from c4locs (may or may not have records, depends on state of source)
-- select CWI_loc, count(*) from c4locs group by CWI_loc;
Insert into c7id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, MNU, pMNU)
    select L.wellid, L.RELATEID, L.UNIQUE_NO, L.CWI_loc, 'MNUNIQ', 1, 1
    from c4locs L
    left join c4ix X
      on L.wellid = X.wellid
    where X.wellid is NULL
;

-- 5.3 append strictly normal MNU records from c4id: where MNU=1 and mexplain is NULL. -- 49699 rows
Insert into c7id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, MNU, pMNU)
    select wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, MNU, pMNU
    from c4id
    where MNU=1 and mexplain is null
;

select id_type, id_prog, MNU, pMNU, count(*) from c7id group by id_type, id_prog, MNU, pMNU;




