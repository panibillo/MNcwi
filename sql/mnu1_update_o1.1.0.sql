/* CWI SCHEMA

Version:    c4.4.0
Date:       2021-02-19
Author:     William Olsen

These are queries for populating the o1id table with identifiers contained in
the c4ix or c4locs tables in the MGS version of c4.  The data is first imorted 
to c4id, then analyzed, and finally copied into o1id. The order that queries
are run in is critical.

The o1id table implements version 4 of the MNU identifier model.  The MNU 
identifier model has data integrity constraints on identifiers that the data in
the c4ix and c4id tables may violate.  The queries in this file fail when they 
attempt to append records to o1id that are not MNU-compliant.

The queries attempt to correctly identify which data is non-compliant, to
label it with the reason why it is non-compliant, and then to import it to o1id
in a way that makes it compliant.  In most cases there is some level of 
ambiguity that can only be resolved with certainty by reference to original 
sources.  But in many cases the ambiguity is low enough that guesses can be 
made.  

An auxilliary table, o1id_match, is used to keep track of probable redundant
wellids that should be merged.

Most queries are broken into 3 parts: First an exploratory query that simply
displays the found records and the the planned labels, second a query that 
updates labels in c4id, and third a query to populate o1id_match.

Comparisson of c4id to o1id can identify every case where data has been 
modified, and traces are left in both tables to indicate the reason for the 
change.  In some cases the reason is limitations in the CWI identifier model,
but in other cases the reason is an actual error in the CWI data. In the latter
case, CWI maintainers should be notified of the error, and documentation 
should be provided sufficient to guide corrections.

There are a number of individual queries that are run in succession. Each 
identifies a particular group of non-compliant identifiers, and updates 
labeling columns in c4id.  In each case the MNU value is set to a value 
between 10 and 20.    These values then determine how the row is appended 
to the o1id table.  The MNU values are reassigned to Recal that in the MNU 
identifier model, regular Minnesota Unique Well Numbers are assigned MNU=1, 
and non-MNU identifiers are assigned MNU=0. These queries do not change the 
MNU values of MNU-compliant records.

In version 4 of the MNU identifier model, MNU compliant identifiers  have MNU 
values from 1 to 5, and values from 6 to 9 are used to flag identifiers that 
need some kind of manual evaluation.  When the data is copied from c4id to 
o1id, MNU values from 10 to 20 are translated to to 1 to 9 range.

There are sometimes recent well records found in the shape files used to fill 
the c4locs table that are not yet in c4ix or c4id.  These Recent records have 
to be appended to c4ix when Foreign Keys are implemented, because c4locs.wellid 
references c4ix.wellid. Why does this matter here?  When identifiers are added 
to c4id from c4ix, their origin is recorded by setting c4id.ID_TYPE='c4ix'.

c4.4.0 version:
    - Contains the c4 data tables
    - Adds table c4locs for well coordinates.
    - Adds rowid and wellid to each c4 data table
    - Adds Foreign Key constraints to all tables, wellid -> c4ix(wellid)
    + Makes o1id into the main table for all well identifiers.
        + Add all Unique Well Numbers in c4ix & c4locs into c4id.
            ID_TYPE = 'c4ix' or 'c4locs'; identifies the source.
            ID_PROG = 'MNUNIQ';
            sMNU = 1; These will be the primary identifiers by default
        + Add conditional unique indices on o1id to enforce uniqueness.
        + Add Views on o1id to simplify using Unique Well Numbers for search
          and for export.
        + Data, as cloned from cwi is found in c4id. But it may not pass all 
		  integrity checks required by o1id.
  
References:

sql/cwischema_c4_versions.txt

County Well Index, 2021, Database created and maintained by the Minnesota
Geological Survey, a department of the University of Minnesota,  with the
assistance of the Minnesota Department of Health.
http://mgsweb2.mngs.umn.edu/cwi_doc/cwidoc.htm

https://www.sqlite.org
*/

update c4id
    set MNU = 0, sMNU = 0
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
-- The wellid's should be found in c4ix, and will later be imported to o1id as
-- identifiers along with all of the other wellids in c4ix.
Delete from c4id 
where MNU = 1
  and cast(wellid as text) = IDENTIFIER 
;

-- Create the code table for MNU identifier relationship types
CREATE TABLE MNU_relationship(
    rowid       INTEGER PRIMARY KEY NOT NULL,
    Code        INTEGER NOT NULL,
    Descrptn    TEXT    NOT NULL);
    
INSERT INTO MNU_relationship(Code, Descrptn)
VALUES
(0,'not a MNU identifier'),
(1,'MNU identifier for a standard well'),
(2,'MNU identifier for a set of wells; individual wells do not have wellids'),
(3,'MNU identifier for a set of wells; individual wells also have wellids'),
(4,'provisional MNU identifier, wellid represents a site'),
(8,'presumed identifier or assignment error'),
(9,'cross reference between IDENTIFIER for a well set and a wellid for an individual well');
