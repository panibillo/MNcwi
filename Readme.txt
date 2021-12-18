OWI - An SQLite implementation of the Minnesota County Well Index database. 

Date:   	2021-10-02
Author: 	William Olsen   
License:    MIT   https://opensource.org/licenses/MIT

Summary:
The purpose of this project is to replicate a functional CWI database using SQLite.
The target audience is persons or programs who have permission to download data from the CWI ftp website maintained by the Minnesota Geologic Survey.
Major project components include:
	A database class that interfaces to pysqlite3, implementing a context manager.
	A script to automate downloading and unzipping of files from an ftp site.
	A script to automate importing of the downloaded files into the sqlite database.
	A public config file defining paths, schema versions, and files.
	A non-public config file defining the download site and logins.

Dependencies:
Python >= 3.7 
An attempt is made to restrict project dependencies only to freely available libraries. Non-standard Python libraries include
	pysqlite
	shapefile (pyshape is used for reading shape files)
	ftplib
	zipfile

This project defines both software versions and schema versions for the database.

The sqlite database is implemented in several schema versions. Each version is defined by a schema file (DDL file) in subdirectory sql.

The schema version numbering system for the different schemas remains tentative.  
Originally, all versions are identified as c4.[S].[V]  where S distinguishes major differences in the schema, and V distinguishes minor differences in the schema.

An outline of current versions is provided in cwischema_c4_versions.txt.

Download directives are contained in the non-public file 
	config/OWI_logins.py  
Only a template version of this file is maintained in the git repo. Implementers of this project are responsible for requesting login information from the Minnesota Geologic Survey. 
	
Import directives, including schema version information, are contained in file
	config/OWI_config.py  
It declares the local path names, the version number, and the version schema:
	OWI_DB_VERSION   
	OWI_DB_SCHEMA

Initial software versions are suitable only for building a local database from scratch. There is no functionality for maintaining a local database by adding only new records or updating only changed records.


References:

County Well Index, 2021, Database created and maintained by the Minnesota Geological Survey, a department of the University of Minnesota,  with the assistance of the Minnesota Department of Health.
CWI documentation:  http://mgsweb2.mngs.umn.edu/cwi_doc/cwidoc.htm
MWI map interface:  https://mnwellindex.web.health.state.mn.us/
MWI text search:    https://mnwellindex.web.health.state.mn.us/mwi/

http://mgsweb2.mngs.umn.edu/cwi_doc/cwiDataTables.htm

https://www.sqlite.org




