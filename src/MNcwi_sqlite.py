'''
Created on Sep 12, 2020

@author: Bill Olsen

A cwi clone database in sqlite.

Two service functions are included:

-   showprogress() : a semi-graphical progress indicator.
-   qmarks() : generate a string of "?" characters for use in queries.

Class c4db implements only variables and methods that are agnostic as to
the database schema and database engine.  

Class c4db inherits from class DB_SQLite.
DB_SQLite holds SQLite dependent methods, and inherits the context manager 
mixin class DB_context_manager.

Class DB_context_manager is a mixin class: 
    it adds functionality to a class that inherits it, 
    it has no __init__, and 
    it depends on some methods to be implemented by a class that inherits it. 

    Syntax options for the context manager:
        with c4db(db_name) as db:  
        with c4db(db_name, commit=True):
        with c4db(db_name, open_db=False):
    
    Defaults argument values: 
        open_db=True.  Explicitly call db.open_db() to open the connection
        commit=False.  Prohibit commits
        

Methods
-------
    with c4db() as db:     [context manager syntax]

    showprogress()
    qmarks() or c4db.qmarks()
    c4db.query()
    c4db.queryone()
    c4db.get_tablenames()
    c4db.get_viewnames()
    c4db.get_column_names()
    c4db.get_column_type_dict()

'''
import csv
import os
import sqlite3 as sqlite
from collections import OrderedDict

# from MNcwi_config import MNcwi_DATA_TABLE_PREFIX

def showprogress(n, b=10):
    """
    Provide a semi-graphical progress indicator in the console
    
    Arguments 
    ---------
    n : integer. 
        Iteration counter
    b : integer. 
        if b>0: Iteration printing interval. (optional)
        if b=0: Terminates the progress indicator 
    
    Returns
    -------
    n+1    if b>0
    0      if b=0
        
    Usage
    ----- 
    icount = 0
    <begin loop>:
        <do stuff>
        icount = showprogress(icount, 500)
    showprogress(icount, 0)
    """
    if b==0:
        print ('!',n)
        return 0
    n += 1
    bbb, bb = 100*b, 10*b 
    if  n%bbb==0: print (',',n)
    elif n%bb==0: print (',',end='',flush=True)
    elif  n%b==0: print ('.',end='',flush=True)
    return n 

def qmarks(vals):
    '''
    Return a string of comma separated questionmarks for vals

    Questionmark parameter markers are used in pysqlite execute methods to 
    prevent sql injection. See the pysqlite documentation.
    
    Arguments
    vals : iterable (list or tuple), integer, or string.
           vals is interpreted to determine 'n' the number of '?' symbols 
           required.  As follows:
             iterable : n = len(vals)
             string   : n=1.
             int      : n = vals
    Examples
        vals = 'Bill'         n=1, return '?'
        vals = 4              n=4, return '?,?,?,?'
        vals = [4]            n=1, return '?'
        vals = (1,2,'Bill')   n=3, return '?,?,?'
        
    Notes: 
        The interpretation of 'n' from vals is pretty intuitive when vals is an
    iterable or an integer.  But the interpretation of n from other argument 
    types would be arbitrary, and not intuitive for users.  Therefore Other 
    non-iterable types are left to throw an error when len() is called.  But 
    strings have a len() method, so are treated as a special case that is 
    intepreted as signifying a single val.
        The qmarks method can be imported by itself, but is also made available
    as a method in class DB_SQLite.
    '''
    if isinstance(vals, str):
        return '?'
    elif isinstance(vals, int):
        return ','.join(vals * ['?'])
    else:
        return ','.join(len(vals) * ['?'])
        
    
class DB_context_manager():
    """ 
    A mixin class defining a context manager for a database. 
    
    The DB_context_manager mixin class defines 2 variables
        _context_connected   True if the db connection was open already
        _context_autocommit  If True, commit edits at exit.

    The database class inheriting DB_context_manager must define the following 
    methods:
        open_db()
        commit_db()
        close_db()
    
    The database class's commit_db() method should call context_permits_commit()
    prior to committing edits, and should not commit if not permitted.
        
    Usage:
        with mydb(commit=True) as db:    # _context_autocommit = True
        with mydb(commit=False) as db:   # _context_autocommit = False
        with mydb() as db:               # _context_autocommit = False

        When _context autocommit is True, edits will be committed when the 
    context is exited, AND the user can manually call commit_db() in code any 
    time while the context is still open.
        When _context autocommit is False, all calls to commit_db() are ignored.
    In this context, it is safe to play with the database because nothing will
    be committed.  BUT WARNING: a programmer can ignore _context_autocommit by  
    directly calling mydb.cur.commit().
    """   
    def __init__(self, commit=False):    
        self._context_connected = False
        self._context_autocommit = commit
    
    def __enter__(self):
        self._context_connected = self.open_db()  
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        if self._context_autocommit==True:
            self.commit_db()
        if self._context_connected == False:
            self.close_db()
        self._context_connected = False
        self._context_autocommit = False
    
    def context_permits_commit(self):
        if self._context_autocommit == False:
            print ('Commit is forbidden by the context manager.')
        return self._context_autocommit

class DB_SQLite(DB_context_manager):
        
    def __init__(self, db_name=None, open_db=False, commit=False, converttypes=True):
        self.db_name = db_name
        self.qmarks = qmarks
        self.converttypes = converttypes  
        if open_db: 
            self.connection_open = self.open_db(converttypes=converttypes)
        else: 
            self.connection_open = False
        super().__init__(commit)
 
    def __str__(self):
        rv=(f"     database name:      {self.db_name}",
            f"     connection_open:    {self.connection_open}",
            f"    _context_connected:  {self._context_connected}",
            f"    _context_autocommit: {self._context_autocommit}")
        return '\n'.join(rv)

    def __repr__(self):
        rv = (f"DB_SQLite(db_name='{self.db_name}'," 
              f" open_db={self.connection_open}," 
              f" commit={self._context_autocommit})")
        return rv

    def open_db(self):
        """
        Open a connection to the db.
        
        https://pynative.com/python-sqlite-date-and-datetime/
        """
        try:
            if self.converttypes:
                self.con = sqlite.connect(self.db_name,
                                          detect_types=sqlite.PARSE_DECLTYPES |
                                                       sqlite.PARSE_COLNAMES)
            else:
                self.con = sqlite.connect(self.db_name)
 
            self.con = sqlite.connect(self.db_name)
            self.cur = self.con.cursor()
            self.connection_open = True
        except:
            print (f"db_sqlite/db_open: ERROR - could not open database: {self.db_name}.")
            self.connection_open = False
        return self.connection_open
        
    def close_db(self, commit=None):    
        if commit==True:
            self.commit_db()
        if hasattr(self, 'cur'):
            self.cur.close()
            self.con.close()
        self.connection_open = False

    def commit_db(self, msg=''):
        if self.db_name == ':memory:':
            return True
        if self.context_permits_commit() == False:
            return False
        try:
            self.con.commit()
            return True
        except Exception as e:
            print ('Exception attempting to commit. ' + msg)
            print(e)
            return False

    def vacuum(self):
        try:
            self.cur.execute('VACUUM')
            return True
        except Exception as e:
            print (e)
            return False
        
    def query(self, sql, vals=None, n=None):
        """ 
        Execute a query and return the result set
        """
        rv = []
        if vals is None:
            try:
                self.cur.execute(sql)
                #rv = self.cur.fetchall()
            except Exception as e:
                print(f"ERROR A: query failed\n{sql}\n{str(e)}\n===============") 
                return rv
        else:             
            try:
                self.cur.execute(sql, vals)
                #rv = self.cur.fetchall()
            except Exception as e1:
                try:
                    self.cur.execute(sql, tuple(vals))
                    #rv = self.cur.fetchall()
                except Exception as e2:
                    print(f"ERROR B: query failed\n{sql}")
                    print(f"{str(vals)[:60]}...,{str(vals)[-60:]}")
                    print(f">>err1: {str(e1)}\n--------------------")
                    print(f">>err2: {str(e2)}\n====================") 
                    return rv
        if n==None:
            rv = self.cur.fetchall()
        else:
            rv = self.cur.fetchmany(n)
        return rv            

    def queryone(self, sql, vals=None, default=None):
        """
        Execute a query and return first result tuple, or value.
        
        Returns
        -------
        If query returns multiple values per row: return first row as tuple.
        If query returns a one value per row: return the value (not as tuple)
        """
        rv = self.query(sql, vals=vals, n=1)
        if len(rv)==1:
            rv = rv[0]
            if len(rv)==1:
                return rv[0]
            else:
                return rv
        else:
            return default
    
    def get_tablenames(self):
        ''' Return a tuple of all Table names in the database'''
        data = self.cur.execute("select name from sqlite_master where type='table'").fetchall()
        rv = tuple(row[0] for row in data)
        return rv

    def get_viewnames(self):
        ''' Return a tuple of all View names in the database'''
        data = self.cur.execute("select name from sqlite_master where type='view'").fetchall()
        return tuple(row[0] for row in data)

    def get_column_names(self, table_name):
        """ Return a list of field_names table_name."""
        data = self.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
        return [str(f[1]) for f in data]

    def get_column_type_dict (self, table_name):
        """ 
        Return a dictionary of {field_name: field_type} for table_name.
        """
        data = self.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
        return OrderedDict({str(f[1]) : str(f[2]) for f in data})

    def export_table_to_csv(self, table_name, csv_name, where=''):   
        """      
        Export [selected] records from table tablename to a csv file.
        
        Arguments
        ---------
        tablename : string. Name of a table in the database
        csv_name  : string. Filename of the csv file (with path)
        where     : string, Optional. Where clause. If where is empty then all
                    records are exported.   E.g.  where="where wellid = 123"
        
        Notes
        -----
        -   The csv file must not exist. If it already exists, simply abort.
        -   All columns are written in native order except rowid.
        -   The csv dialect is 'excel' with all non-numeric values quoted.
        """
        
        cols = self.get_column_names(table_name)
        if 'rowid' in cols:
            cols.remove('rowid')
        s = f"""select {', '.join(cols)} 
                from {table_name} {where} 
                order by wellid;""".replace('                ',' ')
        
        if os.path.exists(csv_name):
            raise NotImplementedError(
                'Overwriting existing csv files is not allowed: '+csv_name)
            return False
        with open(csv_name, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, 
                            dialect='excel')
#                            quoting=csv.QUOTE_NONNUMERIC)
            w.writerow(cols)
            for row in self.query(s):
                w.writerow(row)
        print (f"{table_name} written to {csv_name}")

class c4db(DB_SQLite): 
    def __init__(self, db_name=None, 
                       open_db=False, 
                       commit=False):
        
        DB_SQLite.__init__(self, db_name, open_db=open_db, commit=commit)
        
#         datatables = 'ix ad an c1 c2 id pl rm st wl locs'.split()
#         self.datatables = [f"{MNcwi_DATA_TABLE_PREFIX}{t}" for t in datatables]

    def __str__(self):
        rv=(f"c4db() a SQLite implementation of County Well Index",
            super().__str__() )
        return '\n'.join(rv)

    def __repr__(self):
        rv = (f"c4db(db_name='{self.db_name}'," 
              f" open_db={self.connection_open}," 
              f" commit={self._context_autocommit})")
        return rv

    def update_unique_no_from_wellid(self, tablename):
        """
        Update column UNIQUE_NO in table c5ix to remove leading zeros.
        
        Arguments
        ---------
        tablename: string.  value is either 'c4ix' or 'c4locs'
            
        Notes
        -----
        This routine does not issue a COMMIT
        
        Assumes that the wellid is equivalent to the Unique_no. That assumption
        should be true for versions of cwi through c4 and c5 at least.
        """
        assert tablename in ('c4ix c4locs')
        u = f"update {tablename} set UNIQUE_NO = cast(wellid as text);"     
        try:
            self.query(u)
            return True
        except Exception as e:
            print ('update_unique_no_from_wellid():\n  ', e)
            return False 

     
#     def set_triggers_enabled(self, enable):
#         assert isinstance(enable, bool)
#         if self.connection_open:
#             self.con.create_function("trigs_enabled", 0, self.
#         
# def triggers_on():      
#     return 1  
# def triggers_off():      
#     return 0  

if __name__=='__main__':
    if 0: 
        print ('Test of __str__() and __repr__()')
        COMMIT = False
        DB_NAME = ":memory:"
        print("\nDemonstrate opening c4db using a context manager")
        with c4db(db_name=DB_NAME, commit=COMMIT) as db:
            print (repr(db))
            print (db)
    
        print("\nDemonstrate opening and closing c4db without a context manager")
        db = c4db(db_name=DB_NAME, open_db=False,  commit=True)
        print (repr(db))
        print (db)
        db.close_db()
           
        print("\nDemonstrate opening DB_SQLite using a context manager")
        with DB_SQLite(db_name=DB_NAME) as db:
            print (repr(db))
            print (db)
    
        print("\nDemonstrate opening and closing DB_SQLite without a context manager")
        db = DB_SQLite(db_name=DB_NAME, open_db=True,  commit=False)
        print (repr(db))
        print (db)
        db.close_db()
    if 1:
        assert isinstance(True, bool)
        assert isinstance(False, bool)
        DB_NAME = ":memory:"
        
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        print (type(con), con)
        print (type(cur))
        con.create_function("trig_enabled", 0, triggers_on)
        cur.execute("select trig_enabled()" )
        print ('ON?', cur.fetchone()[0])
        con.create_function("trig_enabled", 0, triggers_off)
        cur.execute("select trig_enabled()" )
        print ('OFF?', cur.fetchone()[0])

        with c4db(db_name=DB_NAME, commit=True, open_db=True) as db:
            print (type(db.con), db.con)
            print (type(db.cur))
            print (db.connection_open)
            print (db.get_tablenames())
            db.con.create_function("trig_enabled", 0, triggers_on)
            db.con.create_function("trig_enabled", 0, triggers_on)
            v = db.queryone("trig_enabled()")
            print ('ON?',v)
            db.con.create_function('triggers_enabled', 0, triggers_off)
            v = db.queryone("triggers_enabled()")
            print ('OFF?',v)
        
    print ('\n',r'\\\\\\\\\\\\\\\\\\ DONE //////////////////')        
        