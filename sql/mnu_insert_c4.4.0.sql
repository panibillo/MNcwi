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

Insert into c4ix (
    wellid, RELATEID, COUNTY_C, UNIQUE_NO, WELLNAME,
    TOWNSHIP, RANGE, RANGE_DIR, SECTION, SUBSECTION, MGSQUAD_C,
    ELEVATION, ELEV_MC,
    STATUS_C, USE_C,
    LOC_MC, LOC_SRC, DATA_SRC,
    DEPTH_DRLL, DEPTH_COMP, DATE_DRLL,
    CASE_DIAM, CASE_DEPTH, GROUT,
    POLLUT_DST, POLLUT_DIR, POLLUT_TYP,
    STRAT_DATE, STRAT_UPD, STRAT_SRC, STRAT_GEOL, STRAT_MC,
    DEPTH2BDRK, FIRST_BDRK, LAST_STRAT, OHTOPUNIT, OHBOTUNIT,
    AQUIFER, CUTTINGS, CORE, BHGEOPHYS,
    GEOCHEM, WATERCHEM, OBWELL, SWL, DH_VIDEO,
    INPUT_SRC, UNUSED, ENTRY_DATE, UPDT_DATE)
SELECT
    L.wellid, L.RELATEID, L.COUNTY_C, L.UNIQUE_NO, L.WELLNAME,
    L.TOWNSHIP, L.RANGE, L.RANGE_DIR, L.SECTION, L.SUBSECTION, L.MGSQUAD_C,
    L.ELEVATION, L.ELEV_MC,
    L.STATUS_C, L.USE_C,
    L.LOC_MC, L.LOC_SRC, L.DATA_SRC,
    L.DEPTH_DRLL, L.DEPTH_COMP, L.DATE_DRLL,
    L.CASE_DIAM, L.CASE_DEPTH, L.GROUT,
    L.POLLUT_DST, L.POLLUT_DIR, L.POLLUT_TYP,
    L.STRAT_DATE, L.STRAT_UPD, L.STRAT_SRC, L.STRAT_GEOL, L.STRAT_MC,
    L.DEPTH2BDRK, L.FIRST_BDRK, L.LAST_STRAT, L.OHTOPUNIT, L.OHBOTUNIT,
    L.AQUIFER, L.CUTTINGS, L.CORE, L.BHGEOPHYS,
    L.GEOCHEM, L.WATERCHEM, L.OBWELL, L.SWL, L.DH_VIDEO,
    L.INPUT_SRC, L.UNUSED, L.ENTRY_DATE, L.UPDT_DATE
FROM c4locs L
LEFT JOIN c4ix X
  ON L.wellid = X.wellid
  WHERE X.wellid IS NULL;
*/

Insert into c4id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, is_MNU, is_pMNU)
    select wellid, RELATEID, UNIQUE_NO, 'c4ix', 'MNUNIQ', 1, 1
    from c4ix;

Insert into c4id (wellid, RELATEID, IDENTIFIER, ID_TYPE, 
            ID_PROG, is_MNU, is_pMNU)
    select L.wellid, L.RELATEID, L.UNIQUE_NO, L.CWI_loc, 
            'MNUNIQ', 1, 1
    from c4locs L
    left join c4ix X
      on L.wellid = X.wellid
    where X.wellid is NULL;
