import os
import pandas as pd
from sqlalchemy import create_engine
from clickhouse_sqlalchemy import types

class DB_Connection:
    def __init__(self):
        print("Connecting to ClickHouse")
        self.engine = create_engine('clickhouse://localhost/default')

    def drop(self, table_name: str) -> None:
        print(f"Dropping table {table_name}")
        with self.engine.connect() as con:
            con.execute(f"DROP TABLE IF EXISTS {table_name}")

    def append_df(self, df: pd.DataFrame, table_name: str) -> None:
        print(f"Appending data to {table_name}")
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False, dtype=types.to_dict(df))

    def get_df(self, table_name: str) -> pd.DataFrame:
        print(f"Get data from {table_name}")
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, self.engine)


if __name__ == '__main__':
    connection = DB_Connection()
    df = pd.read_csv('data/Test_Abalone_X.csv')
    connection.drop('test')
    connection.append_df(df, 'test')
    connection.append_df(df, 'test')
    df_get = connection.get_df('test')
    connection.drop('test')
    connection = DB_Connection()
    connection = DB_Connection()
    print(len(df), len(df_get))
