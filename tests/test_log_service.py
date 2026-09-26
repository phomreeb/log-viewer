import pytest
from pathlib import Path
from services.log_service import LogService
from repositories.log_repository import DuckDBLogRepository

@pytest.fixture
def log_service():
    repo = DuckDBLogRepository()
    return LogService(repo)

@pytest.fixture
def project_a_logs():
    # Use the actual path to the logs in the workspace
    base_path = Path(__file__).parent.parent / "logs" / "project_a"
    return str(base_path / "*")

def test_get_logs_basic(log_service, project_a_logs):
    df = log_service.get_logs(
        file_pattern=project_a_logs,
        search='',
        levels=[],
        include_names=[],
        exclude_names=[],
        start_dt=None,
        end_dt=None,
        limit=10
    )
    assert not df.empty, "Dataframe should not be empty"
    assert len(df) <= 10, "Should respect the limit parameter"

def test_get_logs_time_filter(log_service, project_a_logs):
    df = log_service.get_logs(
        file_pattern=project_a_logs,
        search='',
        levels=[],
        include_names=[],
        exclude_names=[],
        start_dt='2026-09-16 00:00:00',
        end_dt='2026-09-16 23:59:59',
        limit=100
    )
    # The result could be empty or populated depending on the actual log file contents,
    # but the query shouldn't fail (validating the comma replacement logic for timestamps)
    assert df is not None

def test_get_logs_warn_warning_mapping(log_service, project_a_logs):
    df_warn = log_service.get_logs(
        file_pattern=project_a_logs,
        search='',
        levels=['WARN'],
        include_names=[],
        exclude_names=[],
        start_dt=None,
        end_dt=None,
        limit=100
    )
    
    df_warning = log_service.get_logs(
        file_pattern=project_a_logs,
        search='',
        levels=['WARNING'],
        include_names=[],
        exclude_names=[],
        start_dt=None,
        end_dt=None,
        limit=100
    )
    
    # Since we mapped WARN and WARNING to the same query logic,
    # requesting 'WARN' should return the exact same data as requesting 'WARNING'.
    assert len(df_warn) == len(df_warning), "WARN and WARNING should return the same number of results"

