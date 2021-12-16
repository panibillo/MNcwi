'''
OWI Configuration global variables

These variables define a local installation of the CWI database
They describe:
    File locations 
    The local database schema
    The names of the source cwi data files (on the MGS ftp site)
    
To import this file, write:

    from OWI_config import *

@author: William Olsen
'''
import os, platform

OWI_SCHEMA_IDENTIFIER_MODEL = 'CWI'
OWI_MNU_INSERT = None
OWI_DATA_TABLE_PREFIX = 'c4'

# choose the schema version.
OWI_SCHEMA_VERSION = 4

if OWI_SCHEMA_VERSION == 0:
    ### Clone of cwi data files with no modifications
    OWI_DB_VERSION = "c4.0.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.0.0.sql"
    OWI_DB_NAME    = "../db/OWI00.sqlite"

elif OWI_SCHEMA_VERSION == 1:
    ### Add c4locs file
    OWI_DB_VERSION = "c4.1.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.1.0.sql"
    OWI_DB_NAME    = "../db/OWI10.sqlite"

elif OWI_SCHEMA_VERSION == 2:
    ### Add columns rowid and wellid to all tables
    OWI_DB_VERSION = "c4.2.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.2.0.sql"
    OWI_DB_NAME    = "../db/OWI20.sqlite"

elif OWI_SCHEMA_VERSION == 3:
    ### Add Foreign Key constraints on wellid to data tables
    OWI_DB_VERSION = "c4.3.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.3.0.sql"
    OWI_DB_NAME    = "../db/OWI30.sqlite"

elif OWI_SCHEMA_VERSION == 4:
    ### Iteration 0 of MNU identifier model: omit Unique constraints
    OWI_DB_VERSION = "c4.4.0"
    OWI_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.4.0.sql"
    OWI_MNU_INSERT = "../sql/mnu_insert_c4.4.0.sql"
    OWI_DB_NAME    = "../db/OWI40.sqlite"

elif OWI_SCHEMA_VERSION == 4.1:
    ### Iteration 1 of MNU identifier model: Has Unique constraints
    OWI_DB_VERSION = "c4.4.1"
    OWI_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.4.1.sql"
    OWI_MNU_INSERT = "../sql/mnu_insert_c4.4.1.sql"
    OWI_MNU_VIEWS = "../sql/mnu_views_c4.4.1.sql"
    OWI_DB_NAME    = "../db/OWI41.sqlite"


OWI_SCHEMA_VERSION = int(OWI_DB_VERSION.split('.')[1])
OWI_SCHEMA_MINOR_VERSION = int(OWI_DB_VERSION.split('.')[2])

OWI_SCHEMA_HAS_LOCS = OWI_SCHEMA_VERSION >= 1
OWI_SCHEMA_HAS_WELLID = OWI_SCHEMA_VERSION >= 2
OWI_REFORMAT_UNIQUE_NO = OWI_SCHEMA_VERSION >= 3
OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS = OWI_SCHEMA_VERSION >= 3
OWI_SCHEMA_HAS_DATA_CONSTRAINTS = OWI_SCHEMA_VERSION >= 4
   
OWI_DOWNLOAD_FILES = [ 
    "cwidata_csv.zip",
    "cwilocs.zip",
    "xcwiunlocs.zip",
    #"cwi_info_csv.zip"
]
if platform.system() == 'Windows':
    OWI_DOWNLOAD_DIR = "R:/cwi"
    OWI_DOWNLOAD_CWIDATACSV_DIR = f"{OWI_DOWNLOAD_DIR}/cwidata_csv"
    OWI_DOWNLOAD_DB_NAME = f"{OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"

    OWI_DIR = "../db"
    OWI_DOWNLOAD_LOGFILE = "../db/MN_cwi_download.log"
    
elif platform.system() == 'Linux':
    OWI_DOWNLOAD_DIR = f"{os.path.expanduser('~')}/R/cwi"
    OWI_DOWNLOAD_CWIDATACSV_DIR = f"{OWI_DOWNLOAD_DIR}/cwidata_csv"
    OWI_DOWNLOAD_DB_NAME = f"{OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"

    OWI_DIR = f"{os.path.expanduser('~')}/data/MN/OWI"
    OWI_DOWNLOAD_LOGFILE = f"{OWI_DIR}/OWI_download.log"


OWI_DOWNLOAD_APPROPRIATIONS_CSV = f"{OWI_DOWNLOAD_DIR}/mpars_index_permits_installations.csv"

if   1:
    # Clone of SWUDS download file, with only addition of id cols & Unique_no.
    OWI_SWUDS_VERSION = "r1.1.0"
    OWI_SWUDS_SCHEMA  = "../sql/swudsschema_r1.1.0.sql"
    OWI_SWUDS_TABLEAP = 'r1ap_full'
elif 0:
    # Convert SWUDS download file to relational database form, with code tables.
    OWI_SWUDS_VERSION = "r1.2.0"
    OWI_SWUDS_SCHEMA  = "../sql/swudsschema_r1.2.0.sql"

if __name__ == '__main__':
    import os
    print (f"OWI_DB_VERSION = {OWI_DB_VERSION}")
    print (f"OWI_DB_SCHEMA = {OWI_DB_SCHEMA}")
    print (f"OWI_DOWNLOAD_DIR = {os.path.abspath(OWI_DOWNLOAD_DIR)}")
    print (f"OWI_DOWNLOAD_DB_NAME = {os.path.abspath(OWI_DOWNLOAD_DB_NAME)}",
           f". (Exists = {os.path.exists(OWI_DOWNLOAD_DB_NAME)})")
    print (f"OWI_DOWNLOAD_LOGFILE = {os.path.abspath(OWI_DOWNLOAD_LOGFILE)}",
           f". (Exists = {os.path.exists(OWI_DOWNLOAD_LOGFILE)})")

    print (f"OWI_DIR = {os.path.abspath(OWI_DIR)}")
    print (f"OWI_DB_NAME = {os.path.abspath(OWI_DB_NAME)}",
           f". (Exists = {os.path.exists(OWI_DB_NAME)})")
    print ("OWI_DOWNLOAD_FILES:")
    for f in OWI_DOWNLOAD_FILES:
        print (f"   {f:<15} : Exists={os.path.exists(os.path.join(OWI_DOWNLOAD_CWIDATACSV_DIR, f))}" )
    assert os.path.exists(OWI_DB_SCHEMA), f"Missing OWI_DB_SCHEMA {OWI_DB_SCHEMA}"
    assert os.path.exists(OWI_DOWNLOAD_DIR), f"Missing OWI_DOWNLOAD_DIR {OWI_DOWNLOAD_DIR}"
    assert os.path.exists(OWI_DOWNLOAD_CWIDATACSV_DIR), f"Missing OWI_DOWNLOAD_CWIDATACSV_DIR {OWI_DOWNLOAD_CWIDATACSV_DIR}"
    assert os.path.exists(OWI_DIR), f"Missing OWI_DIR {OWI_DIR}"