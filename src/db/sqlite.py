import sqlite3
import threading


DBNAME = 'crypt_currency.db'


class _SQLiteDBSingleton:

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(_SQLiteDBSingleton, cls).__new__(cls)
        return cls._instance


class _SQLiteDB(_SQLiteDBSingleton):

    def get_conn(self):
        return self._conn

    def set_conn(self, conn):
        self._conn = conn

    def __del__(self):
        print('closing connection to db')
        self._conn.close()


_db_instance = _SQLiteDB()
print('opening connection to db')
_conn = sqlite3.connect(DBNAME, check_same_thread=False)
_db_instance.set_conn(_conn)
lock = threading.Lock()


def get_db_conn():
    return _db_instance.get_conn()


def execute_commit(sql, args=[]):
    lock.acquire()
    cur = _db_instance.get_conn().cursor()
    cur.execute(sql, args)
    res = cur.fetchall()
    _db_instance.get_conn().commit()
    lock.release()
    return res
