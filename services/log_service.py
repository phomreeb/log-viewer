import pandas as pd
from pathlib import Path
from typing import List, Optional

from repositories.log_repository import DuckDBLogRepository

class LogService:
    def __init__(self, repository: DuckDBLogRepository):
        self.repository = repository
        self.read_opts = "filename='_log_file', union_by_name=true"

    def get_available_names(self, file_pattern: str) -> List[str]:
        columns = self.repository.get_columns_schema(file_pattern, self.read_opts)
        if "name" in columns:
            return self.repository.get_distinct_names(file_pattern, self.read_opts)
        return []

    def get_logs(self, file_pattern: str, search: str, levels: List[str], include_names: List[str], exclude_names: List[str], start_dt: Optional[str], end_dt: Optional[str], limit: int) -> pd.DataFrame:
        columns = self.repository.get_columns_schema(file_pattern, self.read_opts)
        if not columns:
            return pd.DataFrame()

        query = f"SELECT * FROM read_json_auto('{file_pattern}', {self.read_opts}) WHERE 1=1"
        params = []

        if levels and "level" in columns:
            placeholders = ", ".join(["?"] * len(levels))
            query += f" AND UPPER(level) IN ({placeholders})"
            params.extend([l.upper() for l in levels])

        if include_names and "name" in columns:
            placeholders = ", ".join(["?"] * len(include_names))
            query += f" AND CAST(name AS VARCHAR) IN ({placeholders})"
            params.extend(include_names)
            
        if exclude_names and "name" in columns:
            placeholders = ", ".join(["?"] * len(exclude_names))
            query += f" AND CAST(name AS VARCHAR) NOT IN ({placeholders})"
            params.extend(exclude_names)

        if start_dt and end_dt and "timestamp" in columns:
            # ใช้ REPLACE() แปลงจุลภาค (,) เป็นจุดทศนิยม (.) ก่อน และใช้ TRY_CAST() แทน CAST()
            # เพื่อป้องกันกรณีที่ Log บางบรรทัดมีฟอร์แมตผิดเพี้ยน จะได้ไม่ทำให้ Query ทั้งหมดพัง
            query += " AND TRY_CAST(REPLACE(CAST(timestamp AS VARCHAR), ',', '.') AS TIMESTAMP) BETWEEN TRY_CAST(? AS TIMESTAMP) AND TRY_CAST(? AS TIMESTAMP)"
            params.extend([start_dt, end_dt])

        if search:
            search_conditions = []
            for col in columns:
                search_conditions.append(f"CAST({col} AS VARCHAR) ILIKE ?")
                params.append(f"%{search}%")
                
            if search_conditions:
                query += " AND (" + " OR ".join(search_conditions) + ")"

        if "timestamp" in columns:
            query += " ORDER BY timestamp DESC"
            
        query += f" LIMIT {limit}"

        df = self.repository.execute_query(query, params)

        # ปรับแต่งคอลัมน์ให้เหลือแค่ชื่อไฟล์
        if not df.empty and '_log_file' in df.columns:
            df['source_log_file'] = df['_log_file'].apply(lambda x: Path(x).name)
            df.drop(columns=['_log_file'], inplace=True)
            
        return df
