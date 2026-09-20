import streamlit as st
from datetime import datetime

from config.settings import BASE_DIR, COLOR_MAPPING, DEFAULT_ROW_LIMIT, CACHE_TTL_DATA, CACHE_TTL_NAMES
from repositories.log_repository import DuckDBLogRepository
from services.log_service import LogService

from components.sidebar import render_view_mode_selector, render_project_selector, render_filters
from components.charts import render_analytics_dashboard
from components.data_table import render_metrics_and_export, render_log_table, render_json_detail

# --- INITIALIZATION ---
st.set_page_config(page_title="Multi-Project Log Viewer", layout="wide", page_icon="📜")

# Create logs directory if missing
if not BASE_DIR.exists():
    BASE_DIR.mkdir(parents=True)

# Dependency Injection
@st.cache_resource
def get_log_service():
    repo = DuckDBLogRepository()
    return LogService(repository=repo)

log_service = get_log_service()

# --- SIDEBAR UI ---
refresh_counter = render_view_mode_selector()
target_path, selected_project = render_project_selector(BASE_DIR)

# Fetch distinct names for filters (Cached)
@st.cache_data(ttl=CACHE_TTL_NAMES)
def fetch_distinct_log_names(file_pattern: str, cache_buster: int = 0):
    return log_service.get_available_names(file_pattern)

available_names = fetch_distinct_log_names(target_path, refresh_counter)
filters = render_filters(available_names)

row_limit = st.sidebar.slider("Max Rows", min_value=100, max_value=10000, value=DEFAULT_ROW_LIMIT)

# --- MAIN UI ---
st.title("📜 Multi-Project JSON Log Viewer")

if st.session_state.get('active_interval_text'):
    st.info(f"🟢 **Live Mode Active:** ข้อมูลกำลังรีเฟรชทุกๆ {st.session_state['active_interval_text']} (อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')})")

# Query wrapper (Cached)
@st.cache_data(ttl=CACHE_TTL_DATA)
def fetch_multi_log_data(file_pattern: str, filter_args: dict, limit: int, cache_buster: int = 0):
    return log_service.get_logs(
        file_pattern=file_pattern,
        search=filter_args.get('search_term', ''),
        levels=filter_args.get('selected_levels', []),
        include_names=filter_args.get('selected_include_names', []),
        exclude_names=filter_args.get('selected_exclude_names', []),
        start_dt=filter_args.get('start_datetime'),
        end_dt=filter_args.get('end_datetime'),
        limit=limit
    )

try:
    df = fetch_multi_log_data(target_path, filters, row_limit, refresh_counter)

    if df.empty:
        st.warning("ไม่พบข้อมูล Log ในไฟล์หรือโปรเจกต์ที่เลือก")
        if filters.get('is_time_filter_active'):
            st.info(f"💡 คำแนะนำ: ตอนนี้คุณกำลังค้นหาข้อมูลระหว่าง `{filters['start_datetime']}` ถึง `{filters['end_datetime']}`\n\nลองตรวจสอบว่าไฟล์ Log มีข้อมูลในช่วงเวลานี้หรือไม่ หรือลองขยายวันที่ให้กว้างขึ้นครับ")
    else:
        # 1. Analytics Dashboard
        render_analytics_dashboard(df, COLOR_MAPPING)

        # 2. Metrics & Export
        render_metrics_and_export(df, selected_project)

        # 3. Log Table
        selected_rows = render_log_table(df)

        # 4. JSON Detail
        render_json_detail(df, selected_rows)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลด Log: {e}")
