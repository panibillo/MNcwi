"""
A driver to create a fresh local copy of cwi from scratch

Purpose
-------
    o   Create an all new sqlite database to mirror the CWI database as served   
        on the Minnesota Geologic Survey ftp site as the c4 data tables
    o   Download selected .zip files if the ftp site versions are newer
    o   Unzip any newer .zip files that have been downloaded
    o   Create or re-create the target sqlite database using a specified schema 
    o   Import the unzipped data to the sqlite database
Authors
-------
    William C. Olsen
    panibillo at gmail.com
    
Version
-------
    2021-10-14
"""

from MNcwi_download_ftp import RUN_download_cwi
from MNcwi_import_csv import RUN_import_csv

RUN_download_cwi()
RUN_import_csv()