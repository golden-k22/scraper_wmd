import mysql.connector
from mysql.connector import Error
from threading import Thread
import threading
from concurrent.futures import Future

def call_with_future(fn, future, args, kwargs):
    try:
        result = fn(*args, **kwargs)
        future.set_result(result)
    except Exception as exc:
        future.set_exception(exc)


def threaded(fn):
    def wrapper(*args, **kwargs):
        future = Future()
        Thread(target=call_with_future, args=(fn, future, args, kwargs)).start()
        return future
    return wrapper

class SqlManager:

    def __init__(self, window, host, user, pwd, port, database, *args, **kwargs):
        self.interface = window
        self.connection = None
        self.connect(host, user, pwd, port, database)
        self.connectionLock = threading.Lock()
        # connectThread.join()

    @threaded
    def connect(self, host, user, password, port, db):
        print("Trying to connect sql...")
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password,
                port=port,
                database=db
            )
            self.interface.connectedDB(db)
            print(f"Connected {db} Database")
        except Error as e:
            print(f"Error: {e}")

    def __del__(self):

        if self.connection:
            self.connection.close()
            print("Database connection closed")

    @threaded
    def query(self, sql, params=None):
        if not self.connection:
            print("No connection to the database. Query aborted.")
            return
        with self.connectionLock:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(sql, params or ())
                    result = cursor.fetchall()
                    self.connection.commit()
                    cursor.close()
                    return result
                except Error as e:
                    print(f"Error during query execution: {e}")
                    cursor.close()

    @threaded
    def insert_query(self, sql, params=None):
        if not self.connection:
            print("No connection to the database. Query aborted.")
            return
        with self.connectionLock:
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(sql, params or ())
                    result = cursor.lastrowid
                    self.connection.commit()
                    cursor.close()
                    return result
                except Error as e:
                    print(f"Error during query execution: {e}")
                    cursor.close()