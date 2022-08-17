from abc import abstractmethod
from design_patterns.observer_pattern import Observer
import pandas as pd
import sqlite3
from sqlite3 import Cursor


class Database(Observer):
    def __init__(self, db_path: str) -> None:
        Observer.__init__(self)
        self.path = db_path

    def update(self, state) -> None:
        print("DATABASE: Updating")
        return None

    def get_table(self, table_name: str) -> pd.DataFrame:
        with sqlite3.connect(self.path) as db:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", db)
        return df

    def print_table(self, table_name: str) -> None:
        df = self.get_table(table_name)
        if df.empty:
            print(f"Empty Table: {table_name}", end="\n\n")
        else:
            print(f"Table: {table_name}\n{df}", end='\n\n')
        return None

    def create_table(self, name: str, columns: str) -> None:
        query = f"CREATE TABLE IF NOT EXISTS {name} ({columns});"
        self._execute(query)
        return None

    def insert_into_table(self, name: str, columns: str, values: str) -> None:
        query = f"INSERT INTO {name} ({columns}) VALUES ({values});"
        self._execute(query)
        return None

    def drop_table(self, table_name: str) -> None:
        self._execute(f"DROP TABLE {table_name};")
        return None

    def _execute(self, query: str) -> None:
        with sqlite3.connect(self.path) as db:
            c: Cursor = db.cursor()
            c.execute(query)
            c.close()
            db.commit()
        return None
