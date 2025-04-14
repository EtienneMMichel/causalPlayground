import pandas as pd
from datetime import datetime
import sqlalchemy as sa

from dotenv import load_dotenv
import os
load_dotenv()


CLOUD_CONFIG = {
        "user":os.getenv("USER_DB"),
        "password":os.getenv("PASSWORD"),
        "host":os.getenv("HOST"),
        "port":os.getenv("PORT"),
        "database_name":os.getenv("DATABASE_NAME"),
    }


class Database():
    def __init__(self):
        cloud_config = CLOUD_CONFIG
        user = cloud_config["user"] if "user" in list(cloud_config.keys()) else None
        password = cloud_config["password"] if "password" in list(cloud_config.keys()) else None
        host = cloud_config["host"] if "host" in list(cloud_config.keys()) else None
        port = cloud_config["port"] if "port" in list(cloud_config.keys()) else None
        database_name = cloud_config["database_name"] if"database_name" in list(cloud_config.keys()) else None
        self.engine = sa.create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')

    def query(self, q:str):
        '''
        q  [str]: SQL query 
        '''
        with self.engine.connect() as connection:
            response = connection.execute(sa.text(q))
        return response
    
    def get_table(self, table:str, additional_query:str=""):
        '''
        table [str]: table name
        additional_query [str]: filters
        '''
        q = f"SELECT * FROM {table} " + additional_query
        response = self.query(q)
        return pd.DataFrame(response)
    
    def drop_table(self, table:str):
        '''
        table [str]: table to drop
        '''
        q = f"DROP TABLE IF EXISTS {table}"
        return self.query(q)

    def save_dataframe(self, df, table_name, if_exists='append'):
        df.to_sql(table_name, self.engine, if_exists=if_exists)

    def already_in_table(self, path, date):
        return False

def load_and_preprocess_data_from_cloud(config):
    
    timeframe = config["data"]["timeframe"]
    start_date = config["data"]["start_date"]
    end_date = config["data"]["end_date"]
    symbols = config["data"]["symbols"]
    # saving_path = TEMP_STORING_PATH.format(symbols="-".join(symbols), timeframe=timeframe, start_date=start_date, end_date=end_date)
    # if os.path.exists(saving_path):
    #     return pd.read_csv(saving_path)
    

    # start_date = datetime(day=1, month=int(start_date_list[0]), year=int(start_date_list[1])) if len(start_date_list) == 2 else datetime(day=int(start_date_list[0]), month=int(start_date_list[1]), year=int(start_date_list[2]))
    # end_date = datetime(day=1, month=int(end_date_list[0]), year=int(end_date_list[1])) if len(end_date_list) == 2 else datetime(day=int(end_date_list[0]), month=int(end_date_list[1]), year=int(end_date_list[2]))
    start_date_list = start_date.split("-")
    end_date_list = end_date.split("-")
    start_date = datetime(day=1, month=int(start_date_list[0]), year=int(start_date_list[1])) if len(start_date_list) == 2 else datetime(day=int(start_date_list[0]), month=int(start_date_list[1]), year=int(start_date_list[2]))
    end_date = datetime(day=1, month=int(end_date_list[0]), year=int(end_date_list[1])) if len(end_date_list) == 2 else datetime(day=int(end_date_list[0]), month=int(end_date_list[1]), year=int(end_date_list[2]))
    start_date = start_date.strftime('%Y/%m/%d')
    end_date = end_date.strftime('%Y/%m/%d')
    db = Database()
    df = None
    for symbol in symbols:
        where_query = f"WHERE datetime between '{start_date}' and '{end_date}'"
        group_symbol = "".join(symbol.split("_"))
        table_name = f'public."{group_symbol}_{timeframe}"'
        df_symbol = db.get_table(table_name, additional_query=where_query)
        df_symbol.rename(columns=dict(zip(df_symbol.columns, [f"{symbol}-{c}" if c != "datetime" else c for c in df_symbol.columns])), inplace=True)
        if df is None:
            df = df_symbol 
            df = df.set_index('datetime')
        else:
            df = df.join(df_symbol.set_index('datetime'))
    df.sort_index(inplace=True)
    df["date"] = df.index
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = (df["date"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    # df.to_csv(saving_path, index=False)
    
    
    return df



def preprocess(config):
    '''
    load data from config file
    '''
    data = load_and_preprocess_data_from_cloud(config)
    data['date'] = pd.to_datetime(data['date'], unit='s')
    return data