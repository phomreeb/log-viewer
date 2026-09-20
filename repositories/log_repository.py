import duckdb
import pandas as pd
from typing import List

class DuckDBLogRepository:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path

    def get_columns_schema(self, file_pattern: str, read_opts: str) -> List[str]:
        conn = duckdb.connect(self.db_path)
        try:
            schema_query = f"DESCRIBE SELECT * FROM read_json_auto('{file_pattern}', {read_opts}) LIMIT 1"
            columns_info = conn.execute(schema_query).fetchall()
            return [col[0] for col in columns_info]
        except Exception:
            return []
        finally:
            conn.close()

    def get_distinct_names(self, file_pattern: str, read_opts: str) -> List[str]:
        conn = duckdb.connect(self.db_path)
        try:
            query = f"SELECT DISTINCT CAST(name AS VARCHAR) as log_name FROM read_json_auto('{file_pattern}', {read_opts}) WHERE name IS NOT NULL"
            names = [row[0] for row in conn.execute(query).fetchall()]
            return sorted(names)
        except Exception:
            return []
        finally:
            conn.close()

    def execute_query(self, query: str, params: list) -> pd.DataFrame:
        conn = duckdb.connect(self.db_path)
        try:
            return conn.execute(query, params).df()
        except Exception as e:
            print(f"[DuckDB Error] {e} | Query: {query} | Params: {params}")
            return pd.DataFrame()
        finally:
            conn.close()
