#!/usr/bin/env python3 -u

import os

import clickhouse_connect
import pandas as pd
from typing import Dict


class Database():
    def __init__(self):
        host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        port = int(os.getenv('CLICKHOUSE_PORT', '8123'))
        username = os.getenv('CLICKHOUSE_LOGIN', 'default')
        password = os.getenv('CLICKHOUSE_PWD', '0000')
        self.client = clickhouse_connect.get_client(host=host, username=username, port=port, password=password)

    def create_database(self, database_name="lab2_bd"):
        self.client.command(f"""CREATE DATABASE IF NOT EXISTS {database_name};""")

    def create_table(self, table_name: str, columns: Dict):
        cols = ""
        for k, v in columns.items():
            cols += f"`{k}` {v}, "
        id_column = list(filter(lambda i: 'Id' in i[0], columns.items()))[0][0]
        self.client.command(f"""
            CREATE TABLE IF NOT EXISTS {table_name} 
            (
                {cols}
            ) ENGINE = MergeTree
            ORDER BY {id_column};
        """)

    def insert_df(self, tablename: str, df: pd.DataFrame):
        self.client.insert_df(tablename, df)

    def read_table(self, tablename: str) -> pd.DataFrame:
        return self.client.query_df(f'SELECT * FROM {tablename}')

    def drop_database(self, database_name: str):
        self.client.command(f'DROP DATABASE IF EXISTS {database_name}')

    def drop_table(self, table_name: str):
        self.client.command(f'DROP TABLE IF EXISTS {table_name}')

    def table_exists(self, table_name: str):
        return self.client.query_df(f'EXISTS {table_name}')

if __name__ == '__main__':
    db = Database()
    db.create_database("lab2_bd")
    db.create_table("test1", {'nameId': 'UInt32'})
    db.create_table("test2", {'nameId': 'UInt32', 'name3': 'UInt32'})
    db.insert_df("test1", pd.DataFrame({"nameId": [1]}))
    db.insert_df("test2", pd.DataFrame({"nameId": [1], "name3": [1]}))
    print(db.read_table("test1"))
    print(db.read_table("test2"))
    db.drop_table("test1")
    db.drop_table("test2")
    db.drop_database("lab2_bd")