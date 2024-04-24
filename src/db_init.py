import os
import clickhouse_connect
import pandas as pd
from typing import Dict
import numpy as np

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
                `insert_time` DateTime('UTC') DEFAULT now(),
            ) ENGINE = MergeTree
            ORDER BY tuple();  -- No specific order needed
        """)

    from datetime import datetime

    def insert_data(self, tablename: str, X, y, predictions):
        try:
            # Преобразуем X и predictions в списки
            X_values = X
            predictions_values = predictions
            y_value = y

            # Создаем запрос INSERT INTO ... VALUES
            query = f"INSERT INTO {tablename} (X, y, predictions, insert_time) VALUES (%s, %s, %s, NOW())"

            # Выполняем запрос с использованием защиты от SQL-инъекций
            self.client.command(query, (X_values, y_value, predictions_values))

        except Exception as e:
            print(f"Ошибка при вставке данных в таблицу {tablename}: {e}")

    def read_table(self, tablename: str) -> pd.DataFrame:
        return self.client.query_df(f'SELECT * FROM {tablename}')

    def drop_database(self, database_name: str):
        self.client.command(f'DROP DATABASE IF EXISTS {database_name}')

    def drop_table(self, table_name: str):
        self.client.command(f'DROP TABLE IF EXISTS {table_name}')

    def delete_data(self, table_name: str):
        self.client.command(f'DELETE FROM {table_name} WHERE 1=1')

    def table_exists(self, table_name: str):
        return self.client.query_df(f'EXISTS {table_name}')
