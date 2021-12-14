'''
MNcwi Configuration global variables

These variables define a local installation of the CWI database
They describe:
    File locations 
    The local database schema
    The names of the source cwi data files (on the MGS ftp site)
    
To import this file, write:

    from MNcwi_config import *

@author: William Olsen
'''
import os, platform

MNcwi_SCHEMA_IDENTIFIER_MODEL = 'CWI'
MNcwi_MNU_INSERT = None
MNcwi_DATA_TABLE_PREFIX = 'c4'

# choose the schema version.
MNcwi_SCHEMA_VERSION = 4

if MNcwi_SCHEMA_VERSION == 0:
    ### Clone of cwi data files with no modifications
    MNcwi_DB_VERSION = "c4.0.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.0.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi00.sqlite"

elif MNcwi_SCHEMA_VERSION == 1:
    ### Add c4locs file
    MNcwi_DB_VERSION = "c4.1.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.1.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi10.sqlite"

elif MNcwi_SCHEMA_VERSION == 2:
    ### Add columns rowid and wellid to all tables
    MNcwi_DB_VERSION = "c4.2.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.2.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi20.sqlite"

elif MNcwi_SCHEMA_VERSION == 3:
    ### Add Foreign Key constraints on wellid to data tables
    MNcwi_DB_VERSION = "c4.3.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.3.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi30.sqlite"

elif MNcwi_SCHEMA_VERSION == 4:
    ### Iteration 0 of MNU identifier model: omit Unique constraints
    MNcwi_DB_VERSION = "c4.4.0"
    MNcwi_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.4.0.sql"
    MNcwi_MNU_INSERT = "../sql/mnu_insert_c4.4.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi40.sqlite"

elif MNcwi_SCHEMA_VERSION == 4.1:
    ### Iteration 1 of MNU identifier model: Has Unique constraints
    MNcwi_DB_VERSION = "c4.4.1"
    MNcwi_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.4.1.sql"
    MNcwi_MNU_INSERT = "../sql/mnu_insert_c4.4.1.sql"
    MNcwi_MNU_VIEWS = "../sql/mnu_views_c4.4.1.sql"
    MNcwi_DB_NAME    = "../db/MNcwi41.sqlite"


MNcwi_SCHEMA_VERSION = int(MNcwi_DB_VERSION.split('.')[1])
MNcwi_SCHEMA_MINOR_VERSION = int(MNcwi_DB_VERSION.split('.')[2])

MNcwi_SCHEMA_HAS_LOCS = MNcwi_SCHEMA_VERSION >= 1
MNcwi_SCHEMA_HAS_WELLID = MNcwi_SCHEMA_VERSION >= 2
MNcwi_REFORMAT_UNIQUE_NO = MNcwi_SCHEMA_VERSION >= 3
MNcwi_SCHEMA_HAS_FKwellid_CONSTRAINTS = MNcwi_SCHEMA_VERSION >= 3
MNcwi_SCHEMA_HAS_DATA_CONSTRAINTS = MNcwi_SCHEMA_VERSION >= 4
   
MNcwi_DOWNLOAD_FILES = [ 
    "cwidata_csv.zip",
    "cwilocs.zip",
    "xcwiunlocs.zip",
    #"cwi_info_csv.zip"
]
if platform.system() == 'Windows':
    MNcwi_DOWNLOAD_DIR = "R:/cwi"
    MNcwi_DOWNLOAD_CWIDATACSV_DIR = f"{MNcwi_DOWNLOAD_DIR}/cwidata_csv"
    MNcwi_DOWNLOAD_DB_NAME = f"{MNcwi_DOWNLOAD_DIR}/cwi{MNcwi_SCHEMA_VERSION}{MNcwi_SCHEMA_MINOR_VERSION}.sqlite"

    MNcwi_DIR = "../db"
    MNcwi_DOWNLOAD_LOGFILE = "../db/MN_cwi_download.log"
    
elif platform.system() == 'Linux':
    MNcwi_DOWNLOAD_DIR = f"{os.path.expanduser('~')}/R/cwi"
    MNcwi_DOWNLOAD_CWIDATACSV_DIR = f"{MNcwi_DOWNLOAD_DIR}/cwidata_csv"
    MNcwi_DOWNLOAD_DB_NAME = f"{MNcwi_DOWNLOAD_DIR}/cwi{MNcwi_SCHEMA_VERSION}{MNcwi_SCHEMA_MINOR_VERSION}.sqlite"

    MNcwi_DIR = f"{os.path.expanduser('~')}/data/MN/Ocwi"
    MNcwi_DOWNLOAD_LOGFILE = f"{MNcwi_DIR}/Ocwi_download.log"


MNcwi_DOWNLOAD_APPROPRIATIONS_CSV = f"{MNcwi_DOWNLOAD_DIR}/mpars_index_permits_installations.csv"

if   1:
    # Clone of SWUDS download file, with only addition of id cols & Unique_no.
    MNcwi_SWUDS_VERSION = "r1.1.0"
    MNcwi_SWUDS_SCHEMA  = "../sql/swudsschema_r1.1.0.sql"
    MNcwi_SWUDS_TABLEAP = 'r1ap_full'
elif 0:
    # Convert SWUDS download file to relational database form, with code tables.
    MNcwi_SWUDS_VERSION = "r1.2.0"
    MNcwi_SWUDS_SCHEMA  = "../sql/swudsschema_r1.2.0.sql"

if __name__ == '__main__':
    import os
    print (f"MNcwi_DB_VERSION = {MNcwi_DB_VERSION}")
    print (f"MNcwi_DB_SCHEMA = {MNcwi_DB_SCHEMA}")
    print (f"MNcwi_DOWNLOAD_DIR = {os.path.abspath(MNcwi_DOWNLOAD_DIR)}")
    print (f"MNcwi_DOWNLOAD_DB_NAME = {os.path.abspath(MNcwi_DOWNLOAD_DB_NAME)}",
           f". (Exists = {os.path.exists(MNcwi_DOWNLOAD_DB_NAME)})")
    print (f"MNcwi_DOWNLOAD_LOGFILE = {os.path.abspath(MNcwi_DOWNLOAD_LOGFILE)}",
           f". (Exists = {os.path.exists(MNcwi_DOWNLOAD_LOGFILE)})")

    print (f"MNcwi_DIR = {os.path.abspath(MNcwi_DIR)}")
    print (f"MNcwi_DB_NAME = {os.path.abspath(MNcwi_DB_NAME)}",
           f". (Exists = {os.path.exists(MNcwi_DB_NAME)})")
    print ("MNcwi_DOWNLOAD_FILES:")
    for f in MNcwi_DOWNLOAD_FILES:
        print (f"   {f:<15} : Exists={os.path.exists(os.path.join(MNcwi_DOWNLOAD_CWIDATACSV_DIR, f))}" )
    assert os.path.exists(MNcwi_DB_SCHEMA), f"Missing MNcwi_DB_SCHEMA {MNcwi_DB_SCHEMA}"
    assert os.path.exists(MNcwi_DOWNLOAD_DIR), f"Missing MNcwi_DOWNLOAD_DIR {MNcwi_DOWNLOAD_DIR}"
    assert os.path.exists(MNcwi_DOWNLOAD_CWIDATACSV_DIR), f"Missing MNcwi_DOWNLOAD_CWIDATACSV_DIR {MNcwi_DOWNLOAD_CWIDATACSV_DIR}"
    assert os.path.exists(MNcwi_DIR), f"Missing MNcwi_DIR {MNcwi_DIR}"