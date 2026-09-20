from repositories.log_repository import DuckDBLogRepository
from services.log_service import LogService
import pandas as pd

repo = DuckDBLogRepository()
service = LogService(repo)

df = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_a/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt='2026-09-16 00:00:00',
    end_dt='2026-09-16 23:59:59',
    limit=100
)
print("DF length project_a:", len(df))

df_b = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_b/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt='2026-09-16 00:00:00',
    end_dt='2026-09-16 23:59:59',
    limit=100
)
print("DF length project_b:", len(df_b))
