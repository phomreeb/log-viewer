import duckdb
import pandas as pd
import json

db = duckdb.connect(':memory:')
query = """
SELECT 
    timestamp,
    CAST(REPLACE(CAST(timestamp AS VARCHAR), ',', '.') AS TIMESTAMP) as parsed_ts,
    CAST('2026-09-16 00:00:00' AS TIMESTAMP) as start_ts,
    CAST('2026-09-16 23:59:59' AS TIMESTAMP) as end_ts,
    CAST(REPLACE(CAST(timestamp AS VARCHAR), ',', '.') AS TIMESTAMP) BETWEEN CAST('2026-09-16 00:00:00' AS TIMESTAMP) AND CAST('2026-09-16 23:59:59' AS TIMESTAMP) as is_between
FROM read_json_auto('/home/arisu/Workspaces/log-viewer/logs/project_a/app.log.2026-09-16', union_by_name=true)
LIMIT 5
"""
try:
    df = db.execute(query).df()
    print(df)
except Exception as e:
    print(f"Error: {e}")
