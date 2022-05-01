'''
OWI database

Dependencies:
    Python >= 3.7
    OWI_logins.py  

Some code is copied from convert_cwi_to_pandas.py by Randal Barnes     

The purpose of module OWI_download_ftp is to download specified zip files from  
the Minnesota Geologic Survey ftp site, and unzip the files.  

Method RUN_download_cwi demonstrates usage.
'''

import os, shutil
import time
import datetime
from ftplib import FTP
import zipfile

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
                           downloadshppath,
                           downloadfiles):
    ''' 
    Download newer cwi files from ftp. Unzip. Return list of new files. 
    
    This function downloads and extracts cwi files from the MGS ftp site.
    File dates are compared, and the ftp download only progresses if the
    ftp version is newer.  
    
    The ftp login should be defined in OWI_logins.py
    The download targets are defined in OWI_config.py
    
    Notes on variable names:
        src is used for ftp source files
        dst is used for local copies of the files
    '''

    log.info(msg=('Downloading CWI sources from ftp site'))
    rv = []
    ftpstart = time.time()
    with FTP(ftpaddr) as ftp:
        ftp.login(user=ftpuser, passwd=ftppass)
        log.debug(msg='ftp Log-in successful')
        
        # Get the modify dates of the files on the ftp site. Formatted as integer, e.g. 20170521081548
        dict_ftp_file_modify_times = {f[0].lower():int(float(f[1].get('modify'))) for f in ftp.mlsd(path=ftppath)}
    
        for fname in downloadfiles:
            if 'locs' in fname: 
                destfile = os.path.join(downloadshppath, fname)
            else:
                destfile = os.path.join(downloadpath, fname)
            if os.path.exists(destfile):
                # Compare file times to see if a fresh download is needed
                mtime = datetime.datetime.fromtimestamp( os.path.getmtime(destfile) )
                desttime = int(mtime.strftime('%Y%m%d%H%M%S'))
                if dict_ftp_file_modify_times[fname.lower()] < desttime:
                    log.info(f'{fname} is up to date. Download skipped.')
                    continue
                
            start = time.time()
            print( f"downloading {fname} ...", end='' )
            
            with open(destfile, 'wb') as localfile:
                try:
                    ftp.retrbinary('RETR '+ftppath+'/'+fname, localfile.write, 1024 )
                except Exception as e:
                    lines = ftp.retrlines('LIST')
                    print (lines)
                    print (f"ERROR downloading {ftppath+'/'+fname} to {destfile}")
                    raise e
                    
            duration = (time.time()-start)/60.0
            print( f"  ... DONE. completed in {duration:1.3f} minutes")
            rv.append (destfile)
            
            if '.zip' in fname:
                print(f"unzipping {destfile} ..." )
                
                with zipfile.ZipFile(destfile, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(destfile))  
                
                log.info(f'{fname} downloaded and unzipped.')
            else:
                log.info(f'{fname} downloaded.')
                
    # for basename in ('wells.', 'unloc_wells.', 'cwilocs.zip'):
    #     for f in os.listdir(downloadpath):
    #         if f.startswith(basename):
    #             src = os.path.join(downloadpath, f)
    #             dst = os.path.join(downloadshppath, f)
    #             try:
    #                 shutil.move (src, dst)
    #             except Exception as e:
    #                 print (f'Moving "{src}" to "{dst}"')
    #                 print (e)
    
    duration = (time.time()-ftpstart)/60.0    
    print(f"*** ftp download & unzip finished in {duration:1.3f} minutes ***" )        
    return rv


def RUN_download_cwi():
    import OWI_logins as L
    from OWI_config import OWI_version_40 as C
    
    newfiles = download_cwi_from_ftp(
        ftpaddr = L.OWI_FTP_ADDRESS,
        ftppath = L.OWI_FTP_PATH,
        ftpuser = L.OWI_FTP_USERNAME, 
        ftppass = L.OWI_FTP_PASSWORD,
        downloadpath = C.OWI_DOWNLOAD_DIR,
        downloadshppath = C.OWI_DOWNLOAD_WELLSSHP_DIR,
        downloadfiles = C.OWI_DOWNLOAD_FILES) 
    print ('New files created:\n   ' + '\n   '.join(newfiles))
    return newfiles


if __name__ == '__main__':
    RUN_download_cwi()  
    
    print ('\n///////////// DONE ///////////////')