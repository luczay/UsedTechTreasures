import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector.errors import Error


class Database:
    """
        Database class
        Attributes:
            _conn: MySQL connection object
            _cursor: Cursor object
    """
    def __init__(self):
        """ Constructor """
        self._conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='admin123',
            database='products'
        )
        self._cursor = self._conn.cursor()

    # Enter and exit methods are necessary for the with statement
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self) -> list[tuple]:
        return self.cursor.fetchall()

    def fetchone(self) -> tuple:
        return self.cursor.fetchone()

    def query(self, sql, params=None) -> list[tuple]:
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    @staticmethod
    def add_scraped_data(df: pd.DataFrame, temp: bool):
        """
            Uploads data to the database from a dataframe
        """
        db_name = 'product'
        if temp:
            db_name = 'temp_product'

        try:
            engine = create_engine('mysql+mysqlconnector://root:admin123@localhost:3306/products?auth_plugin'
                                   '=mysql_native_password', echo=False)
            df.to_sql(db_name, engine, if_exists='append', index=False)
        except Error as e:
            print(e)
