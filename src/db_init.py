import os
import clickhouse_connect
import pandas as pd
from typing import Dict


class Database():
    def __init__(self):
        host = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
        port = int(os.getenv('CLICKHOUSE_PORT', '8123'))
        username = os.getenv('CLICKHOUSE_LOGIN')
        password = os.getenv('CLICKHOUSE_PWD')
        self.client = clickhouse_connect.get_client(host=host, username=username, port=port, password=password)

    def create_database(self, database_name="lab2_bd"):
        self.client.command(f"""CREATE DATABASE IF NOT EXISTS {database_name};""")

    def create_table(self, table_name: str, columns: Dict):
        cols = ""
        for k, v in columns.items():
            cols += f"`{k}` {v}, "
        self.client.command(f"""
            CREATE TABLE IF NOT EXISTS {table_name} 
            (
                {cols}
                `timestamp` DateTime('UTC') DEFAULT now()
            ) ENGINE = MergeTree
            ORDER BY tuple();  -- No specific order needed
        """)

    def insert_data(self, tablename: str, X, y, predictions):
        # Combine X, y, and predictions into a DataFrame
        df = pd.DataFrame({'X': [X], 'y': [y], 'predictions': [predictions]})
        # Insert into the database
        self.insert_df(tablename, df)

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
    db.create_table("predictions", {'X': 'String', 'y': 'String', 'predictions': 'String', 'timestamp': 'DateTime'})
