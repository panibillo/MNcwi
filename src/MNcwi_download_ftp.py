'''
MNcwi database

Dependencies:
    Python >= 3.7
    MNcwi_logins.py  

Some code is copied from convert_cwi_to_pandas.py by Randal Barnes     

The purpose of module MNcwi_download_ftp is to download specified zip files from  
the Minnesota Geologic Survey ftp site, and unzip the files.  

Method RUN_download_cwi demonstrates usage.
'''

import os
import time
import datetime
from ftplib import FTP
# import pyodbc
import zipfile



# import sys
# print (sys.version_info)
# import ftplib
# print (ftplib.__dir__())


import logging

log = logging.getLogger('CWI_refresh')
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

__author__ = "William C Olsen"
__version__ = "2021-10-10"

def download_cwi_from_ftp( ftpaddr,
                           ftppath,
                           ftpuser, 
                           ftppass,
                           downloadpath,
                           downloadfiles):
    ''' 
    Download newer cwi files from ftp. Unzip. Return list of new files. 
    
    This function downloads and extracts cwi files from the MGS ftp site.
    File dates are compared, and the ftp download only progresses if the
    ftp version is newer.  
    
    The ftp login should be defined in MNcwi_logins.py
    The download targets are defined in MNcwi_config.py
    
    Notes on variable names:
        src is used for ftp source files
        dst is used for local copies
    '''

    log.info(msg=('Downloading CWI sources from ftp site'))
    rv = []
    ftpstart = time.time()
    with FTP(ftpaddr) as ftp:
        ftp.login(user=ftpuser, passwd=ftppass)
        log.debug(msg='ftp Log-in successful')
        
        # Get the modify dates of the files on the ftp site. Formatted as integer, e.g. 20170521081548
        dict_ftp_file_modify_times = {f[0]:int(float(f[1].get('modify'))) for f in ftp.mlsd(path=ftppath)}
    
        for fname in downloadfiles:
            destfile = os.path.join(downloadpath, fname)
            if os.path.exists(destfile):
                # Compare file times to see if a fresh download is needed
                mtime = datetime.datetime.fromtimestamp( os.path.getmtime(destfile) )
                desttime = int(mtime.strftime('%Y%m%d%H%M%S'))
                if dict_ftp_file_modify_times[fname] < desttime:
                    log.info(f'{fname} is up to date. Download skipped.')
                    continue
                
            start = time.time()
            print( f"downloading {fname} ...", end='' )
            with open(destfile, 'wb') as localfile:
                ftp.retrbinary('RETR '+ftppath+'/'+fname, localfile.write, 1024 )
            duration = (time.time()-start)/60.0
            print( f"  ... DONE. completed in {duration:1.3f} minutes")
            rv.append (destfile)
            
            if '.zip' in fname:
                print(f"unzipping {destfile} ..." )
                with zipfile.ZipFile(destfile, 'r') as zip_ref:
                    zip_ref.extractall(downloadpath)  
                log.info(f'{fname} downloaded and unzipped.')
            else:
                log.info(f'{fname} downloaded.')
    
    duration = (time.time()-ftpstart)/60.0    
    print(f"*** ftp download & unzip finished in {duration:1.3f} minutes ***" )        
    return rv


def RUN_download_cwi():
    import MNcwi_logins as L
    import MNcwi_config as C
    
    newfiles = download_cwi_from_ftp(
        ftpaddr = L.MNcwi_FTP_ADDRESS,
        ftppath = L.MNcwi_FTP_PATH,
        ftpuser = L.MNcwi_FTP_USERNAME, 
        ftppass = L.MNcwi_FTP_PASSWORD,
        downloadpath = C.MNcwi_DOWNLOAD_DIR,
        downloadfiles = C.MNcwi_DOWNLOAD_FILES) 
    print ('New files created:\n   ' + '\n   '.join(newfiles))
    return newfiles


if __name__ == '__main__':
    RUN_download_cwi()  
    
    print ('\n///////////// DONE ///////////////')