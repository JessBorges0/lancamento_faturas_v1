import pandas as pd
from sqlalchemy import create_engine
from controller.config import ConfigLoader
from sql.query_cervello import QueryCervello

class DatabaseIntegration:

    def __init__(self):
        self.querys = QueryCervello()
        self.configs = ConfigLoader()
        self.server = self.configs.server_sql
        self.database = self.configs.database_sql

    def create_connection(self):
        conn_str = f'mssql+pyodbc://{self.server}/{self.database}?driver=SQL Server&trusted_connection=yes'
        self.connection = create_engine(conn_str)
        return self.connection
    
    def close_connection(self):
        self.connection.dispose()
    
    def calls_queue(self, calls):
        query = self.querys.queue_calls_query(calls)
        df = pd.read_sql_query(query,
                               self.create_connection(),
                               dtype={'Chamado': int})
        self.close_connection()

        if isinstance(df, pd.DataFrame):
            if not df.empty:
                return True, df
            else:
                return True, None
        else:
            return False, None

    def attachments_queue(self, calls):
        query = self.querys.queue_attachments_query(calls)
        df = pd.read_sql_query(query,
                               self.create_connection(),
                               dtype={'Chamado': int})
        self.close_connection()

        if isinstance(df, pd.DataFrame) and not df.empty:
            return True, df
        else:
            return False, None
    
