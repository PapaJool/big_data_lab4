import os
import clickhouse_connect
import pandas as pd
from typing import Dict

class Database():
    def __init__(self):
        host = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
        port = int(os.getenv('CLICKHOUSE_PORT', '8123'))
        username = os.getenv('CLICKHOUSE_USER')
        password = os.getenv('CLICKHOUSE_PASSWORD')
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
                `timestamp` DateTime('UTC') DEFAULT now(),
                `insert_time` DateTime DEFAULT now()
            ) ENGINE = MergeTree
            ORDER BY tuple();  -- No specific order needed
        """)

    def insert_data(self, tablename: str, X, y, predictions):
        X_values = []
        y_values = []

        # Извлекаем значения из всех образцов
        for i in range(len(X)):
            X_values.append(X[i])  # Добавляем сам список X[i]
            y_values.append(y[i])  # Добавляем сам список y[i]

        # Создаем DataFrame из значений
        df = pd.DataFrame({'X': X_values, 'y': y_values, 'predictions': predictions})

        # Вставляем данные в базу данных
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
