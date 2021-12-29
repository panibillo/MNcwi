/*
Insert newer records from c4locs table into c4ix table.
*/


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
  WHERE X.wellid IS NULL
;
