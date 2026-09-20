import duckdb

db = duckdb.connect(':memory:')
query = """
SELECT CAST('2026-09-16 00:09:46.476000' AS TIMESTAMP)
"""
try:
    df = db.execute(query).df()
    print(df)
except Exception as e:
    print(f"Error: {e}")
