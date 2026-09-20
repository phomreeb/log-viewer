from services.log_service import LogService
from repositories.log_repository import DuckDBLogRepository
import pandas as pd

repo = DuckDBLogRepository()
service = LogService(repo)

df = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_a/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt=None,
    end_dt=None,
    limit=100
)
print("With No Date:", len(df))

df2 = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_a/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt='2026-09-16 00:00:00',
    end_dt='2026-09-16 23:59:59',
    limit=100
)
print("With Date:", len(df2))
