'''
OWI Configuration global variables

These variables define a local installation of the CWI/OWI database
They describe:
    File locations  
    The local database schema
    The names of the source cwi data files that are downloaded.

Variables are stored in classes.
There is a distinct class for each version of OWI that can be created.
There are also generic classes inherited by or used by the version classes
    
Suggested usage:
    from OWI_config import OWI_version_[number] as C
    from OWI_config import SWUDS_version_[number] as S
then
    myvar = C.[varname]
    myvar = S.[varname]   

@author: William Olsen
'''
import os, platform

class OWIfiles:
    """ 
    Declare files and directories - Customize to your own installation(s)
    
    Notes
    -----
    The following are defined, but are not yet in use
    -   OWI_DIR   (for the production version of the database)
    -   OWI_DOWNLOAD_LOGFILE  (log of download activity)
    -   cwi_info_csv.zip is conceived, but not yet produced by MGS.
    """
    OWI_DOWNLOAD_FILES = [ 
        "cwidata_csv.zip",
        "cwilocs.zip",
        "xcwiunlocs.zip",
        #"cwi_info_csv.zip"
    ]
    if platform.system() == 'Windows':
        OWI_DOWNLOAD_DIR = "R:/cwi"
        OWI_DIR = "../db"
        
    elif platform.system() == 'Linux':
        OWI_DOWNLOAD_DIR = f"{os.path.expanduser('~')}/R/cwi"
        OWI_DIR = f"{os.path.expanduser('~')}/data/MN/OWI"
        
    OWI_DOWNLOAD_CWIDATACSV_DIR = f"{OWI_DOWNLOAD_DIR}/cwidata_csv"
    OWI_DOWNLOAD_WELLSSHP_DIR = f"{OWI_DOWNLOAD_DIR}/wellsshp"
    OWI_DOWNLOAD_LOGFILE = f"{OWI_DIR}/OWI_download.log"
    

#####################################################################
class CWI_base(OWIfiles):
    """ Common configurations for versions using only c4-- tables."""
    OWI_SCHEMA_IDENTIFIER_MODEL = 'CWI'
    OWI_DATA_TABLE_PREFIX = 'c4'
    OWI_MNU_INSERT = None
    OWI_SCHEMA_HAS_LOCS = False
    OWI_SCHEMA_HAS_WELLID = False
    OWI_REFORMAT_UNIQUE_NO = False
    OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS = False
    OWI_SCHEMA_HAS_DATA_CONSTRAINTS = False
#####################################################################
    
class OWI_version_0(CWI_base):
    """ Clone of cwi data files with no modifications """
    OWI_SCHEMA_VERSION = 0
    OWI_SCHEMA_MINOR_VERSION = 0
    OWI_DB_VERSION = "c4.0.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.0.0.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"


class OWI_version_1(CWI_base):
    """ Add c4locs file """
    OWI_SCHEMA_VERSION = 1
    OWI_SCHEMA_MINOR_VERSION = 0
    OWI_DB_VERSION = "c4.1.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.1.0.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"
    OWI_SCHEMA_HAS_LOCS = True
    
class OWI_version_2(CWI_base):
    """ Add columns rowid and wellid to all tables """
    OWI_SCHEMA_VERSION = 2
    OWI_SCHEMA_MINOR_VERSION = 0
    OWI_DB_VERSION = "c4.2.0"
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.2.0.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"
    OWI_SCHEMA_HAS_LOCS = True
    OWI_SCHEMA_HAS_WELLID = True

class OWI_version_3(CWI_base):
    """ Add Foreign Key constraints on wellid to data tables """
    OWI_SCHEMA_VERSION = 3
    OWI_DB_VERSION = "c4.3.0"
    OWI_SCHEMA_MINOR_VERSION = 0
    OWI_DB_SCHEMA  = "../sql/cwischema_c4.3.0.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/cwi{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"
    OWI_SCHEMA_HAS_LOCS = True
    OWI_SCHEMA_HAS_WELLID = True
    OWI_REFORMAT_UNIQUE_NO = True
    OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS = True
#####################################################################

#####################################################################
class OWI_base(OWIfiles):
    """ Common configurations for versions using o1-- tables."""
    OWI_SCHEMA_IDENTIFIER_MODEL = 'MNU'
    OWI_DATA_TABLE_PREFIX = 'o1'
    OWI_SCHEMA_HAS_LOCS = True
    OWI_SCHEMA_HAS_WELLID = True
    OWI_REFORMAT_UNIQUE_NO = True
    OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS = True
    OWI_SCHEMA_HAS_DATA_CONSTRAINTS = True
#####################################################################

class OWI_version_40(OWI_base):
    """ Iteration 0 of MNU identifier model: omit Unique constraints """
    OWI_SCHEMA_VERSION = 4
    OWI_SCHEMA_MINOR_VERSION = 0
    OWI_DB_VERSION = "o1.1.0"
    OWI_DB_SCHEMA  = "../sql/owischema_o1.1.0.sql"
    OWI_MNU_INSERT = "../sql/mnu_insert_o1.1.0.sql"
    OWI_MNU_VIEWS = "../sql/mnu_views_o1.1.0.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/OWI{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"
    # OWI_DB_SCHEMA  = "../sql/cwischema_c4.4.0.sql"
    # OWI_MNU_INSERT = "../sql/mnu_insert_c4.4.0.sql"

class OWI_version_41(OWI_version_40):
    """ Iteration 1 of MNU identifier model: Has Unique constraints """
    OWI_SCHEMA_VERSION = 4
    OWI_SCHEMA_MINOR_VERSION = 1
    OWI_DB_VERSION = "o1.1.1"
    OWI_MNU_INSERT = "../sql/mnu_insert_o1.1.1.sql"
    OWI_MNU_VIEWS = "../sql/mnu_views_o1.1.1.sql"
    OWI_DOWNLOAD_DB_NAME = f"{OWIfiles().OWI_DOWNLOAD_DIR}/OWI{OWI_SCHEMA_VERSION}{OWI_SCHEMA_MINOR_VERSION}.sqlite"

class SWUDS_version_0:
    """ Clone of SWUDS download file, with only addition of id cols & Unique_no. """
    OWI_DOWNLOAD_APPROPRIATIONS_CSV = f"{OWIfiles().OWI_DOWNLOAD_DIR}/mpars_index_permits_installations.csv"
    OWI_SWUDS_VERSION = "r1.1.0"
    OWI_SWUDS_SCHEMA  = "../sql/swudsschema_r1.1.0.sql"
    OWI_SWUDS_TABLEAP = 'r1ap_full'

# class SWUDS_version_1:
#     """ Convert SWUDS download file to relational database form, with code tables. """
#     OWI_DOWNLOAD_APPROPRIATIONS_CSV = f"{OWIfiles().OWI_DOWNLOAD_DIR}/mpars_index_permits_installations.csv"
#     OWI_SWUDS_VERSION = "r1.2.0"
#     OWI_SWUDS_SCHEMA  = "../sql/swudsschema_r1.2.0.sql"
#     OWI_SWUDS_TABLEAP = 'r1ap_full'

if __name__ == '__main__':
    import os
    R = SWUDS_version_0
    for C in ( OWI_version_0(),
               OWI_version_1(),
               OWI_version_2(),
               OWI_version_3(),
               OWI_version_40() ):
        print (f"OWI_DB_VERSION = {C.OWI_DB_VERSION}")
        print (f"OWI_DB_SCHEMA = {C.OWI_DB_SCHEMA}")
        print (f"OWI_DOWNLOAD_DIR = {os.path.abspath(C.OWI_DOWNLOAD_DIR)}")
        print (f"OWI_DOWNLOAD_DB_NAME = {os.path.abspath(C.OWI_DOWNLOAD_DB_NAME)}",
               f". (Exists = {os.path.exists(C.OWI_DOWNLOAD_DB_NAME)})")
        print (f"OWI_DOWNLOAD_LOGFILE = {os.path.abspath(C.OWI_DOWNLOAD_LOGFILE)}",
               f". (Exists = {os.path.exists(C.OWI_DOWNLOAD_LOGFILE)})")
    
        print (f"OWI_DIR = {os.path.abspath(C.OWI_DIR)}")
        print ("OWI_DOWNLOAD_FILES:")
        assert os.path.exists(C.OWI_DOWNLOAD_CWIDATACSV_DIR), f"Missing OWI_DOWNLOAD_CWIDATACSV_DIR {C.OWI_DOWNLOAD_CWIDATACSV_DIR}"
        for f in C.OWI_DOWNLOAD_FILES:
            print (f"   {f:<15} = Exists={os.path.exists(os.path.join(C.OWI_DOWNLOAD_CWIDATACSV_DIR, f))}" )
        assert os.path.exists(C.OWI_DB_SCHEMA), f"Missing OWI_DB_SCHEMA {C.OWI_DB_SCHEMA}"
        assert os.path.exists(C.OWI_DOWNLOAD_DIR), f"Missing OWI_DOWNLOAD_DIR {C.OWI_DOWNLOAD_DIR}"
        assert os.path.exists(C.OWI_DIR), f"Missing OWI_DIR {C.OWI_DIR}"
        
        assert os.path.exists(C.OWI_DOWNLOAD_WELLSSHP_DIR), f"Missing OWI_DOWNLOAD_WELLSSHP_DIR {C.OWI_DOWNLOAD_WELLSSHP_DIR}"
                                                                                             
    for S in ( SWUDS_version_0(),
               #SWUDS_version_1() 
             ):
        
        print (f"OWI_SWUDS_VERSION = {S.OWI_SWUDS_VERSION}")
        print (f"OWI_DOWNLOAD_APPROPRIATIONS_CSV = {S.OWI_DOWNLOAD_APPROPRIATIONS_CSV}")
        print (f"OWI_SWUDS_SCHEMA = {S.OWI_SWUDS_SCHEMA}")
        assert os.path.exists(S.OWI_SWUDS_SCHEMA), f"Missing OWI_SWUDS_SCHEMA {S.OWI_SWUDS_SCHEMA}"

    print (r'\\\\\\\\\\\ DONE ////////////')
                                                                                             
                                                                                             