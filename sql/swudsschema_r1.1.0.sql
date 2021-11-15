/* 
DNR swuds data  mpars_index_permits_installations.xlsx

Author: Bill Olsen
Revision: 2021-11-11

This schema follows the spreadsheet/csv file served on the MNDNR website
https://www.dnr.state.mn.us/waters/watermgmt_section/appropriations/wateruse.html

Columns 1-4 are new and not define in the source: rowid, apid, wellid, unique_no.

Although the table is very un-normalized, yet it is not so big.
*/



CREATE TABLE IF NOT EXISTS r1ap_full (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    apid        INTEGER,
    wellid      INTEGER,
    unique_no TEXT,
    permit_number TEXT,
    general_permit_number TEXT,
    pending_action TEXT,
    permit_status TEXT,
    permit_class TEXT,
    permit_total_volume_mgy REAL,
    permit_total_acres INTEGER,
    permit_effective_date DATE,
    permit_expiration_date DATE,
    project_name TEXT,
    landowner TEXT,
    agent TEXT,
    installation_name TEXT,
    installation_status TEXT,
    installation_pumping_rate_gpm INTEGER,
    legal_description TEXT,
    utm_x REAL,
    utm_y REAL,
    county_name TEXT,
    watershed_major TEXT,
    watershed_name TEXT,
    resource_type TEXT,
    resource_category TEXT,
    resource_name TEXT,
    resource_number TEXT,
    well_number TEXT,
    well_depth_ft INTEGER,
    aquifer TEXT,
    aquifer_category TEXT,
    use_type TEXT,
    use_category TEXT,
    use_1988_mg REAL,
    use_1989_mg REAL,
    use_1990_mg REAL,
    use_1991_mg REAL,
    use_1992_mg REAL,
    use_1993_mg REAL,
    use_1994_mg REAL,
    use_1995_mg REAL,
    use_1996_mg REAL,
    use_1997_mg REAL,
    use_1998_mg REAL,
    use_1999_mg REAL,
    use_2000_mg REAL,
    use_2001_mg REAL,
    use_2002_mg REAL,
    use_2003_mg REAL,
    use_2004_mg REAL,
    use_2005_mg REAL,
    use_2006_mg REAL,
    use_2007_mg REAL,
    use_2008_mg REAL,
    use_2009_mg REAL,
    use_2010_mg REAL,
    use_2011_mg REAL,
    use_2012_mg REAL,
    use_2013_mg REAL,
    use_2014_mg REAL,
    use_2015_mg REAL,
    use_2016_mg REAL,
    use_2017_mg REAL,
    use_2018_mg REAL,
    use_2019_mg REAL,
    use_2020_mg REAL);





