from repositories.log_repository import DuckDBLogRepository
from services.log_service import LogService

repo = DuckDBLogRepository()
service = LogService(repo)

df = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_a/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt='2026-09-15 00:00:00',
    end_dt='2026-09-15 23:59:59',
    limit=100
)
print("DF length 2026-09-15:", len(df))

df_14 = service.get_logs(
    file_pattern='/home/arisu/Workspaces/log-viewer/logs/project_a/*',
    search='',
    levels=['INFO', 'WARN', 'ERROR'],
    include_names=[],
    exclude_names=[],
    start_dt='2026-09-14 00:00:00',
    end_dt='2026-09-14 23:59:59',
    limit=100
)
print("DF length 2026-09-14:", len(df_14))
