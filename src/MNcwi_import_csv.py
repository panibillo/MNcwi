'''
Created on Oct 10, 2020

@author: Bill
'''
import csv
import os
import  shapefile

""" 
Simple type checking, type converting, and text cleaning functions.
These are used for importing .csv files, and assume that the data in the .csv
files will conform to the anticipated data types.  No warnings or error messages
will be generated.
"""
def safeint(x):
    try:    return int(x)
    except: return None
def safefloat(x):
    try:    return float(x)
    except: return None
def safetext(x):
    try:   
        rv = x.strip()
        if not rv:
            return None
        return rv
    except: 
        return None

def get_col_names_and_converters(db, table_name, csv_cols):
    """ 
    Return a list of column names, and a dict of type converter functions.
    
    Only include columns appearing in BOTH the table def and in csv_cols. 
    The csv DictReader method is case sensitive to the column names as entered
    in the csv file, while the sql queries are not case sensitive to the column 
    names.  Returned column names must match the case in csv_cols.
    """
    data = db.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall() 
    utbl_cols = [c[1].upper() for c in data]
    ucol_types = [c[2].upper() for c in data]
    ucsv_cols = [c.upper() for c in csv_cols]
    col_names, dcol_func = [], {}
    for N,T in zip(utbl_cols, ucol_types):
        if not N in ucsv_cols:
            continue
        n = csv_cols[ucsv_cols.index(N)] 
        col_names.append(n)   
        if   T == 'INTEGER':
            dcol_func[n] = safeint
        elif T == 'REAL':
            dcol_func[n] = safefloat
        elif T == 'TEXT':
            dcol_func[n] = safetext
        elif T == 'CHAR':
            dcol_func[n] = safetext
        else:
            raise NotImplementedError(f'type {T} is not implemented for table {table_name} in column {n}')
    return col_names, dcol_func


def csv_generator(csvname, col_names, colfunc):
    """ 
    Yield next line from csv file as a tuple of type converted values
    
    Arguments:
    csvname   : Filename of an existing csv file to be read.
    col_names : Column names as entered in csv header (may be subset or reordered)
    col_func  : Dictionary of type conversion functions 
    
    Notes:
    -   The yielded values are ordered as in col_names.
    -   The yielded values are type converted using functions in colfunc.
    -   Both col_names and the keys used in col_func must match csv header  
        entries exactly, including case.
    """
    with open(csvname, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for line in reader:
            yield tuple(colfunc[col](line[col]) for col in col_names)

def csv_wellid_generator(csvname, col_names, colfunc):
    """ 
    Yield next line from csv file as a tuple of type converted values
    
    Arguments:
    csvname   : Filename of an existing csv file to be read.
    col_names : Column names as entered in csv header (may be subset or reordered)
    col_func  : Dictionary of type conversion functions 
    
    Notes:
    -   The yielded values are ordered as in col_names.
    -   The yielded values are type converted using functions in colfunc.
    -   Both col_names and the keys used in col_func must match csv header  
        entries exactly, including case.
    """
    with open(csvname, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for line in reader:
            wellid = int(line['RELATEID'])
            yield tuple([wellid]+[colfunc[col](line[col]) for col in col_names])
         
def shp_locs_generator(shpname):
    """
    Yield next row from a shapefile's attribute table as a tuple.
    
    The first column in a shapefile is an internal flag that is not of interest.
    It is replaced with a text value of either 'loc' or 'unloc' depending on
    whether 'unloc' appears in shpname. 
      
    The order and values of all other columns are preserved
    """
    if 'unloc' in shpname:
        cwi_loc = 'unloc'
    else:
        cwi_loc = 'loc'
    assert os.path.exists(shpname), f"Shape file not found {shpname}."
    with shapefile.Reader(shpname) as shpf: 
        keys = tuple((f[0] for f in shpf.fields[1:]))
        
#         print ('DEBUG : ICOUNT STATMENT IS FOR DEBUG')
#         ICOUNT = 0
        for srec in shpf:
#             ICOUNT += 1
#             if ICOUNT > 10: 
#                 break
            yield tuple([cwi_loc] + [srec.record[k] for k in keys])


        
class cwi_csvupdate():
    
    def __init__(self,
                 cwidatacsvdir,
                 locsdir):
        self.cwidatacsvdir = cwidatacsvdir
        self.locsdir = locsdir
        self.data_table_suffixes = 'ix ad an c1 c2 id pl rm st wl'.split()
        self.data_table_names = [f'c4{x}' for x in self.data_table_suffixes]
        self.locs_table_name = 'c4locs'

        assert os.path.exists(self.cwidatacsvdir), f"Missing {self.cwidatacsvdir}"
        assert os.path.exists(self.locsdir), f"Missing {self.locsdir}"
    
    def read_sql_file(self, schemafile): 
        """
        Read sql statments from an sql file.
        Returns a list of the statements in the order read.
        """
        assert os.path.exists(schemafile), schemafile
        with open(schemafile) as f:
            ftxt = f.read()    
        
        # The file is allowed to have 1 comment block before the sql statements.
        # So try splitting on the close comment symbol.
        try:  
            ftxt = ftxt.split('*/')[1] 
        except:
            pass
        #Split the text on the ';' symbol into distinct sql statements.
        statements = [t.strip() + ';' for t in ftxt.split(';')[:-1]]
        
        assert len(statements) >= 1
        return statements
         
           
    def execute_statements_from_file(self, db, c4schemafile):
        """
        Confirm that the database does not exist, and create it.
        Read the table definitions from an sql file
        """
        print (db.db_name)
        statements = self.read_sql_file(c4schemafile)
        for s in statements:
            db.query(s)

    def delete_table_data(self, db, 
                          tables=None):    
        """
        Delete all from the c4* data and locs tables
        
        Arguments:
            db     : an open database instance
            tables : either None, or a string including 'data' and/or 'locs' 
        """
        dodata = tables is None or 'data' in tables
        dolocs = tables is None or 'locs' in tables
        if dodata:
            for t in self.data_table_names:
                csvname = os.path.join(self.cwidatacsvdir, f'{t}.csv')
                if not os.path.exists(csvname):
                    print(f'Missing {csvname}, Table {t} not refreshed')
                    continue
                db.query(f"DELETE FROM {t};")
            print ('data files emptied')
        if dolocs:
            for fname, val in(('wells.shp',       'loc'  ), 
                              ('unloc_wells.shp', 'unloc')):
                shpname = os.path.join(self.locsdir, fname)
                if os.path.exists(shpname):
                    db.query (f"DELETE FROM c4locs where cwi_loc = '{val}';",)
                    print (f"DELETE FROM c4locs where cwi_loc = '{val}';")
                else:
                    print(f'Missing {shpname}, {val} records not refreshed')
        db.commit_db()
        db.vacuum()
                 
    def import_data_from_csv(self, db, schema_has_constraints, table_names=None):    
        """ 
        Create c4 tables in an sqlite db, and read in data from csv files
 
        Notes
        ----- 
        Assumes that the csv files have already been downloaded and extracted.
            fullset/cwidata_csv.zip
        This version deletes existing tables if present! It does not update.
        Some details and steps will depend on the c4version selected, described
           below.
         
        schema_versions and constraints
        -------------------------------
        c4.0.# & c4.1.# define the tables exactly as MGS (except c4locs).
        c4.2.# & up add column wellid to every table.
        c4.3.# & up may put foreign key and unique constraints on the wellid
                 column, so the row generator must supply the wellid at the 
                 time that a record is created.
        """
        
        if table_names is None: 
            table_names = self.data_table_names 
        
        existing_tables = db.get_tablenames()
        for tablename in table_names:
            assert tablename in existing_tables, f'{tablename} missing from db'
            print (f'OK {tablename}')
            
            csvname = os.path.join(self.cwidatacsvdir, f'{tablename}.csv')
            assert os.path.exists(csvname), csvname
            with open(csvname, 'r') as f:
                headers = f.readline()
            csv_cols = headers.replace('"',' ').replace(',',' ').split()
         
            col_names, col_convert = get_col_names_and_converters(db, tablename, csv_cols)
            
            if schema_has_constraints and not 'WELLID' in headers.upper():
                insert = (f"INSERT INTO {tablename}\n"
                          f" (wellid, {', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks( len(col_names) + 1 )});")
                csvgen = csv_wellid_generator
            else:
                insert = (f"INSERT INTO {tablename}\n"
                          f" ({', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks(col_names)});")
                csvgen = csv_generator
            print ('begin: ',insert)
            db.cur.executemany(insert, csvgen(csvname, col_names, col_convert))
            print (f"Completed table {tablename}") 
    
    def import_locs_from_csv(self, db, schema_has_constraints):
        """
        If locs is supplied as a csv file rather than shapefile(s), then read it
        in like the other data tables.
        """
        csvname = os.path.join(self.cwidatacsvdir, 'c4locs.csv') 
        if os.path.exists(csvname):
            self.import_data_from_csv( db, schema_has_constraints, 
                                       table_names=('c4locs',) )
            print (f"c4locs table was imported from csv file: {csvname}")
            return True
        return False
        
    def import_cwi_locs(self, db):
        """
        Import the shapefiles into table c4locs. 
        
        There is one shapefile for located wells (wells.shp) and another for
        unlocated wells (unloc_wells.shp). Both are read into a single table,
        c4locs. Their origin  is distinguished by the value in a newly added
        column 'cwi_loc' with values of either 'loc' or 'unloc'.
        
        All columns defined in the shapefiles should have matching named columns
        in c4locs.

        The shapefiles have many columns that either reproduce data in c4ix
        or other tables, or summarize multiple values as a single value.
        """
        fnames = ['wells.dbf', 'unloc_wells.dbf']
        for fname in fnames:
            shpname = os.path.join(self.locsdir, fname)
            if not os.path.exists(shpname):
                print (f"shapefile '{shpname}' not present for import to db")
                continue
            
            # Peek into the shapefile to get the column names.
            # Change the name of column 1 to 'cwi_loc'
            with shapefile.Reader(shpname) as shpf: 
                cols = tuple(['cwi_loc'] + [f[0] for f in shpf.fields[1:]])
            qmarks = db.qmarks(cols)
            insert = f"""insert into {self.locs_table_name} (
                         {', '.join(cols)}
                         ) values ({qmarks});""".replace('                         ','  ')

            print ('begin: ',insert)
            db.cur.executemany(insert, shp_locs_generator(shpname))
            print (f'completed import of shapefile {shpname}')

    def append_c4locs_to_c4ix(self, db):        
        """
        Append new records in c4locs to c4ix.
        
        The shapefiles may contain well records not yet entered in the cwi data 
        tables. These records are identified because they have wellid values 
        missing from c4ix. 
        
        These records must be appended to c4ix in order to meet the Foreign Key 
        constraint (c4locs.wellid references c4ix.wellid).  Information from 
        these records is not added o other c4 data tables, even if the 
        information is present.
        """
        print ('Appending Recent records in c4locs to c4ix')
        i = """Insert into c4ix (
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
                  WHERE X.wellid IS NULL;""".replace('                ','')
        db.query(i)
            
    def populate_wellid_and_index(self, db, haslocs):
        """
        Set the wellid values in all data tables.
        The wellid values should also be equivalent to RELATEID.
        Table locs, if present, already has wellids.
        """
        table_names = list(self.data_table_names)
        if haslocs: table_names.append('c4locs')
        u = """UPDATE {tablename}
               set wellid = cast(RELATEID as integer)
               where wellid is null;""".replace('               ',' ')
        s = """create index if not exists idx_{tablename}_wellid 
               on  {tablename}(wellid);""".replace('               ',' ')
        for tablename in table_names:
            print (f'populating and indexing wellid in table {tablename} ...')
            db.query(u.format(tablename=tablename))
            db.query(s.format(tablename=tablename))
        print (f"Completed updating wellid in table {tablename}")


def RUN_import_csv(data=True, 
                   locs=True):
    """ 
    Demonstrate full import from csv files.

    Arguments
    ---------
        data : boolean
               Data tables are touched only if True
        locs : boolean
               locs table is touched only if True
                
    Prerequisites
    -------------
        - MNcwi_DOWNLOAD_DB_NAME        
            - must not exist or is completely empty of data tables.
        - MNcwi_DB_SCHEMA               must exist: named schema file.
        - MNcwi_DOWNLOAD_DIR            must exist: wells.shp and unloc_wells.shp 
        - MNcwi_DOWNLOAD_CWIDATACSV_DIR must exist: cwidata .csv files
    """
    from MNcwi_sqlite import c4db 
    import MNcwi_config as C
       
    if C.MNcwi_SCHEMA_HAS_DATA_CONSTRAINTS:
        print('Warning. The CWI data files do not pass UNIQUE constaints')
        raise NotImplementedError('Data constraints models are not implemented')

    C4 = cwi_csvupdate( C.MNcwi_DOWNLOAD_CWIDATACSV_DIR,
                        C.MNcwi_DOWNLOAD_DIR)
    
    create = not os.path.exists(C.MNcwi_DOWNLOAD_DB_NAME)
    
    print (f"Importing data to {C.MNcwi_DOWNLOAD_DB_NAME}")
    with c4db(db_name=C.MNcwi_DOWNLOAD_DB_NAME, commit=True) as db:
        
        if create: 
            print (f"creating tables, constraints, and views from {C.MNcwi_DB_SCHEMA}")
            C4.execute_statements_from_file(db, C.MNcwi_DB_SCHEMA)
 
        if C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = False')
 
        if data: 
            C4.delete_table_data(db, 'data')
            C4.import_data_from_csv( db, C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS)
            db.commit_db()
 
        if locs and C.MNcwi_SCHEMA_HAS_LOCS: 
            C4.delete_table_data(db,'locs')
            if not C4.import_locs_from_csv(db, C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS):
                C4.import_cwi_locs(db)
            db.commit_db()
 
        if C.MNcwi_SCHEMA_HAS_WELLID: # and not C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            C4.populate_wellid_and_index(db, C.MNcwi_SCHEMA_HAS_LOCS)
            db.commit_db()
             
 
        if C.MNcwi_REFORMAT_UNIQUE_NO:
            if data:
                db.update_unique_no_from_wellid('c4ix')
                db.commit_db()
            if locs and C.MNcwi_SCHEMA_HAS_LOCS:
                db.update_unique_no_from_wellid('c4locs')
                db.commit_db()
 
        if C.MNcwi_SCHEMA_IDENTIFIER_MODEL == 'MNU':
            C4.execute_statements_from_file(db, C.MNcwi_MNU_INSERT)
        
        if C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS and C.MNcwi_SCHEMA_HAS_LOCS:
            C4.append_c4locs_to_c4ix(db)
            db.commit_db()
            
        if C.MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = True')

if __name__ == '__main__':
    RUN_import_csv()
    
    print ('\n',r'\\\\\\\\\\\\\\\\\\ DONE //////////////////')    
        