/* CWI SCHEMA 

Version:    c4.4.0    
Date:       2021-02-19
Author:     William Olsen   

These are statements for populating the c4id table with identifiers contained
only in the c4ix or c4locs tables in the MGS version of c4.

Note that there may be Recent well records found in the shape files used to fill the c4locs table that are not yet in the data files used to fill c4ix.  These Recent records have to be appended to c4ix when Foreign Keys are implemented, because c4locs.wellid references c4ix.wellid. Why does this matter here?  When identifiers are added to c4id from c4ix, then their origin is recorded by setting c4id.ID_PROG='c4ix'. The shapefile origins of the Recent records can be retained if the queries below are run BEFORE the Recent records are added to c4ix.

c4.4.0 version:
    - Contains the c4 data tables
    - Adds table c4locs for well coordinates.
    - Adds rowid and wellid to each c4 data table
    - Adds Foreign Key constraints to all tables, wellid -> c4ix(wellid)
    + Makes c4id into the main location for all well identifiers.
        + Add all Unique Well Numbers in c4ix & c4locs into c4id.
            ID_TYPE = 'c4ix' or 'c4locs'; identifies the source.
            ID_PROG = 'MNUNIQ';
            is_pMNU = 1; These will be the primary identifiers by default
        + Add conditional unique indices on c4id to enforce uniqueness.
        + Add Views on c4id to simplify using Unique Well Numbers for search
          and for export.
        + Data, as cloned from cwi, may not pass all integrity checks.
        
References:

sql/cwischema_c4_versions.txt

County Well Index, 2021, Database created and maintained by the Minnesota 
Geological Survey, a department of the University of Minnesota,  with the 
assistance of the Minnesota Department of Health.

https://www.sqlite.org
*/

update c4id
    set is_MNU = 1
    where ID_PROG in ('MNUNIQ','WMWSR','WSERIES')
;

Insert into c4id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, is_MNU, is_pMNU)
    select wellid, RELATEID, UNIQUE_NO, 'c4ix', 'MNUNIQ', 1, 1
    from c4ix
;

Insert into c4id (wellid, RELATEID, IDENTIFIER, ID_TYPE, 
            ID_PROG, is_MNU, is_pMNU)
    select L.wellid, L.RELATEID, L.UNIQUE_NO, L.CWI_loc, 
            'MNUNIQ', 1, 1
    from c4locs L
    left join c4ix X
      on L.wellid = X.wellid
    where X.wellid is NULL
;
