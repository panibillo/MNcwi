'''
Created on Oct 10, 2020

@author: Bill
'''
import csv
import datetime
import os
import  shapefile
from distro import linux_distribution
from pip._internal.vcs import git

from OWI_sqlfile import execute_statements_from_file
from OWI_sqlite import c4db

from OWI_config import  OWI_version_40 as C
from OWI_config import  SWUDS_version_0 as S

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
class safedate():
    def __init__(self, default='%m/%d/%Y'):
        self.fmt = default
        self.fmts = ( default,
                     '%m-%d-%Y',
                     '%Y/%m/%d',
                     '%Y-%m-%d',
                     '%Y%m%d')
    def date(self, x):
        """
        Try to convert string x to a date using format self.fmt
        If that fails, try the other formats in self.fmts. If one succeeds,
        store the successful format in self.fmt for use on the next call.
        """
        try:
            return datetime.datetime.strptime(x,self.fmt).date()
        except:
            for fmt in self.fmts:
                try:
                    d=datetime.datetime.strptime(x,fmt).date()
                    self.fmt = fmt
                    return d
                except:
                    pass
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
        elif T == 'DATE':
            dcol_func[n] = safedate().date
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
    # with open(csvname, 'r', encoding='ascii') as datafile:
    with open(csvname, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for line in reader:
            yield tuple(colfunc[col](line[col]) for col in col_names)

def csv_wellid_generator(csvname, col_names, colfunc, MNUcol='RELATEID'):
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
    -   Sets wellid to Null if the MNUcol cannot be converted to an integer. 
    """
    with open(csvname, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for line in reader:
            wellid = safeint(line[MNUcol])
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

        for srec in shpf:
            yield tuple([cwi_loc] + [srec.record[k] for k in keys])


class cwi_csvupdate():
    """ Methods for importing csv files into OWI database tables. """
    
    def __init__(self,
                 cwidatacsvdir,
                 locsdir):
        self.cwidatacsvdir = cwidatacsvdir
        self.locsdir = locsdir
        self.data_table_suffixes = 'ix id ad an c1 c2 pl rm st wl'.split()
        self.data_table_names = [f'c4{x}' for x in self.data_table_suffixes]
        self.locs_table_name = 'c4locs'

        assert os.path.exists(self.cwidatacsvdir), f"Missing {self.cwidatacsvdir}"
        assert os.path.exists(self.locsdir), f"Missing {self.locsdir}"
    
    def delete_table_data(self, db, 
                          tables=None):    
        """
        Delete all from the c4* data and locs tables. Preparing to import.
        
        Arguments
        ---------
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

        for table_name in table_names:
            assert table_name in existing_tables, f'{table_name} missing from db'
            print (f'OK {table_name}')
            
            n = db.cur.execute(f"select count(*) from {table_name};").fetchone()[0]
            if n>0:
                print (f"skipping {table_name}, {n} records already in db.")
                continue
                        
            csvname = os.path.join(self.cwidatacsvdir, f'{table_name}.csv')
            assert os.path.exists(csvname), csvname

            ok = self.force_to_ascii(csvname)
            
            with open(csvname, 'r') as f:
                headers = f.readline()
            csv_cols = headers.replace('"',' ').replace(',',' ').split()
         
            col_names, col_convert = get_col_names_and_converters(db, table_name, csv_cols)
            
            if schema_has_constraints and not 'WELLID' in headers.upper():
                insert = (f"INSERT INTO {table_name}\n"
                          f" (wellid, {', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks( len(col_names) + 1 )});")
                csvgen = csv_wellid_generator
            else:
                insert = (f"INSERT INTO {table_name}\n"
                          f" ({', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks(col_names)});")
                csvgen = csv_generator
            print ('begin: ',insert)
            db.cur.executemany(insert, csvgen(csvname, col_names, col_convert))
            print (f"Completed table {table_name}") 
    

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

    def force_to_ascii(self, fname):
        """ 
        Remove any non-ASCII characters from the csv files.
        
        This is a crude fix that deletes information.  But experience shows that the
        only data affected in Dec 2021 was a single address with encoded '1/2' 
        symbol.
        """
        try:
            with open(fname, 'rb') as source_file:
                contents = source_file.read()
            with open(fname, 'w+b') as dest_file:
                dest_file.write(contents.decode('ascii','ignore').encode('ascii','ignore'))
            return True
        except Exception as e:
            print (f"Error forcing {fname} to ASCII")
            print (e)
            return False

def RUN_import_csv(data=True, 
                   locs=True,
                   wellids=True,
                   resume_MNU_at = 0):
    """ 
    Demonstrate full import from csv files. 
    Creates a new OWI.sqlite.  Does not update an existing OWI.sqlite

    Arguments
    ---------
        data : boolean
               Data tables are touched only if True
        locs : boolean
               locs table is touched only if True
                
    Prerequisites
    -------------
        - OWI_config.py defined files and directories:
        - OWI_DOWNLOAD_DB_NAME        
            - must not exist or is completely empty of data tables.
        - OWI_DB_SCHEMA               must exist: named schema file.
        - OWI_DOWNLOAD_DIR            must exist: wells.shp and unloc_wells.shp 
        - OWI_DOWNLOAD_CWIDATACSV_DIR must exist: cwidata .csv files
        
    IMPORTANT!!!!!
    --------------
    -   If it runs incompletely or with errors, the final state may be faulty.
    -   If it runs incompletely or with errors, you can try to comment out
        sections below that have been complete in order to only run the 
        incomplete portions. The logic allows limited user control from this
        method, but does not recognize when steps have been completed.  For 
        example, reading in csv files twice will just create duplicate records.
    """
    from OWI_sqlite import c4db 
       
    if C.OWI_SCHEMA_HAS_DATA_CONSTRAINTS:
        print('Warning. The CWI data files do not pass UNIQUE constaints')
        #raise NotImplementedError('Data constraints models are not implemented')

    C4 = cwi_csvupdate( C.OWI_DOWNLOAD_CWIDATACSV_DIR,
                        C.OWI_DOWNLOAD_WELLSSHP_DIR)
    
    create = not os.path.exists(C.OWI_DOWNLOAD_DB_NAME)
    
    print (f"Importing data to {C.OWI_DOWNLOAD_DB_NAME}")
    with c4db(db_name=C.OWI_DOWNLOAD_DB_NAME, commit=True) as db:
        
        if create: 
            print (f"creating tables, constraints, and views from {C.OWI_DB_SCHEMA}")
            execute_statements_from_file(db, C.OWI_DB_SCHEMA)

        if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = False')
 
        if data: 
            C4.delete_table_data(db, 'data')
            C4.import_data_from_csv( db, C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS)
            db.commit_db()
        
        if locs and C.OWI_SCHEMA_HAS_LOCS: 
            C4.delete_table_data(db,'locs')
            if not C4.import_locs_from_csv(db, C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS):
                C4.import_cwi_locs(db)
            db.commit_db()
        
        if wellids:
            if C.OWI_SCHEMA_HAS_WELLID:
                C4.populate_wellid_and_index(db, C.OWI_SCHEMA_HAS_LOCS)
                db.commit_db()
            
            
            if C.OWI_REFORMAT_UNIQUE_NO:
                """ Removes leading 0's from identifiers in c4ix.UNIQUE_NO and
                    c4locs.UNIQUE_NO.  This is really optional.
                """
                print (f"OWI_REFORMAT_UNIQUE_NO: {C.OWI_REFORMAT_UNIQUE_NO}, data:{data}, locs:{locs}")
                if data:
                    db.update_unique_no_from_wellid('c4ix')
                    db.commit_db()
                if locs and C.OWI_SCHEMA_HAS_LOCS:
                    db.update_unique_no_from_wellid('c4locs')
                    db.commit_db()
 
        if C.OWI_SCHEMA_IDENTIFIER_MODEL == 'MNU':
            for sqlfile in C.OWI_MNU_INSERT[resume_MNU_at:]:
                execute_statements_from_file(db, sqlfile)
                # Resumat:
                #       0: OWI_MNU_INSERT_LOCS = ["../sql/insert_c4locs_to_c4ix.sql",]
                #       1: OWI_MNU_CLEAN_C4ID = ["../sql/mnu1_update_o1.1.0.sql",]
                #       2: OWI_MNU_INIT_O1ID = ["../sql/mnu1_init_o1id_o1.1.0.sql",]
                #       3: OWI_MNU_UPDATE_O1ID = ["../sql/mnu1_update_o1.1.0.sql",]
                #       4: OWI_MNU_ANALYZE_O1ID = ["../sql/mnu2_analyze_faults_o1.1.0.sql",]
                #       5: OWI_MNU_RESOLVE_O1ID = ["../sql/mnu3_resolve_faults_o1.1.0.sql",]
        
        # if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS and C.OWI_SCHEMA_HAS_LOCS:
        #     C4.append_c4locs_to_c4ix(db)
        #     db.commit_db()
            
        if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = True')


def import_swuds_full(self, db, csvname, table_name='r1ap_full'):
    """
    Import the swuds csv file into r1ap without modification.
    """
    existing_tables = db.get_tablenames()
    assert table_name in existing_tables,  f'{table_name} missing from db'

    assert os.path.exists(csvname), csvname
    with open(csvname, 'r') as f:
        headers = f.readline()
    csv_cols = headers.replace('"',' ').replace(',',' ').split()

    col_names, col_convert = get_col_names_and_converters(db, table_name, csv_cols)
    insert = (f"INSERT INTO {table_name}\n"
              f" (wellid, {', '.join(col_names)})\n"
              f" VALUES ({db.qmarks( len(col_names)+1 )});")
    
    db.cur.executemany(insert, csv_wellid_generator(csvname, col_names, col_convert, MNUcol = 'well_number'))
    print (f"Completed importing table {table_name}") 
    
    for u in ('update r1ap_full set unique_no = well_number;',
              'update r1ap_full set apid = rowid;' 
              ):
        db.query(u)
    print (f"Completed updating table {table_name}") 
        
def RUN_import_swuds(create=False):

    if 1:
        csvname = S.OWI_DOWNLOAD_APPROPRIATIONS_CSV
        db_name = C.OWI_DOWNLOAD_DB_NAME
    elif 0:
        # Testing
        csvname = r'F:\Bill\Workspaces\Py1\OWIsqlite\demo_data\mpars_demo.csv'
        db_name = r'F:\Bill\Documents\GW\CWI\c4db.sqlite'

    with c4db(db_name=db_name, commit=True) as db:
        if create:
            execute_statements_from_file(db, S.OWI_SWUDS_SCHEMA)
        import_swuds_full(db, csvname)
        
if __name__ == '__main__':
    RUN_import_csv(data=False, 
                   locs=False,
                   wellids = False,
                   resume_MNU_at=4)
    #RUN_import_swuds(create=True)
            
    print ('\n',r'\\\\\\\\\\\\\\\ DONE (OWI_import_csv.py) ///////////////')    
        