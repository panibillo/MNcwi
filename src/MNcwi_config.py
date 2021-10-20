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

MNcwi_SCHEMA_IDENTIFIER_MODEL = 'CWI'
MNcwi_MNU_INSERT = None

if   0:
    MNcwi_DB_VERSION = "c4.0.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.0.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi00.sqlite"
elif 0:
    MNcwi_DB_VERSION = "c4.1.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.1.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi10.sqlite"
elif 0:
    MNcwi_DB_VERSION = "c4.2.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.2.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi20.sqlite"
elif 0:
    MNcwi_DB_VERSION = "c4.3.0"
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.3.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi30.sqlite"
elif 1:
    MNcwi_DB_VERSION = "c4.4.0"
    MNcwi_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    MNcwi_DB_SCHEMA  = "../sql/cwischema_c4.4.0.sql"
    MNcwi_MNU_INSERT = "../sql/mnu_insert_c4.4.0.sql"
    MNcwi_DB_NAME    = "../db/MNcwi40.sqlite"

MNcwi_SCHEMA_VERSION = int(MNcwi_DB_VERSION.split('.')[1])
MNcwi_SCHEMA_MINOR_VERSION = int(MNcwi_DB_VERSION.split('.')[2])

MNcwi_SCHEMA_HAS_LOCS = MNcwi_SCHEMA_VERSION >= 1
MNcwi_SCHEMA_HAS_WELLID = MNcwi_SCHEMA_VERSION >= 2
MNcwi_SCHEMA_HAS_CONSTRAINTS = MNcwi_SCHEMA_VERSION >= 3
MNcwi_REFORMAT_UNIQUE_NO = MNcwi_SCHEMA_VERSION >= 3
   
MNcwi_DOWNLOAD_FILES = [ 
    "cwidata_csv.zip",
    "cwilocs.zip",
    "xcwiunlocs.zip",
    #"cwi_info_csv.zip"
]
MNcwi_DOWNLOAD_DIR = "R:/cwi"
MNcwi_DOWNLOAD_CWIDATACSV_DIR = "R:/cwi/cwidata_csv"
MNcwi_DOWNLOAD_DB_NAME = f"R:/cwi/cwi{MNcwi_SCHEMA_VERSION}{MNcwi_SCHEMA_MINOR_VERSION}.sqlite"

MNcwi_DIR = "../db"
MNcwi_DOWNLOAD_LOGFILE = "../db/MN_cwi_download.log"



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
        print (f"   {f}")
    assert os.path.exists(MNcwi_DB_SCHEMA), f"Missing MNcwi_DB_SCHEMA {MNcwi_DB_SCHEMA}"
    assert os.path.exists(MNcwi_DOWNLOAD_DIR), f"Missing MNcwi_DOWNLOAD_DIR {MNcwi_DOWNLOAD_DIR}"
    assert os.path.exists(MNcwi_DOWNLOAD_CWIDATACSV_DIR), f"Missing MNcwi_DOWNLOAD_CWIDATACSV_DIR {MNcwi_DOWNLOAD_CWIDATACSV_DIR}"
    assert os.path.exists(MNcwi_DIR), f"Missing MNcwi_DIR {MNcwi_DIR}"