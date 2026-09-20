import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
from streamlit_autorefresh import st_autorefresh

def render_view_mode_selector() -> int:
    """Render the view mode selector and return the refresh counter."""
    st.sidebar.header("🔄 View Mode")

    view_mode = st.sidebar.segmented_control(
        "โหมดการดูข้อมูล",
        options=["Static (ย้อนหลัง)", "Live (อัตโนมัติ)"],
        default="Static (ย้อนหลัง)"
    )

    if view_mode == "Live (อัตโนมัติ)":
        refresh_interval = st.sidebar.selectbox(
            "ความถี่ในการอัปเดต (Refresh Interval)",
            options=["5 วินาที", "10 วินาที", "30 วินาที", "60 วินาที"],
            index=0
        )
        interval_mapping = {
            "5 วินาที": 5000,
            "10 วินาที": 10000,
            "30 วินาที": 30000,
            "60 วินาที": 60000
        }
        
        # Determine actual interval text to display in info banner
        st.session_state['active_interval_text'] = refresh_interval
        refresh_counter = st_autorefresh(interval=interval_mapping[refresh_interval], key="live_log_refresh")
    else:
        st.session_state['active_interval_text'] = None
        refresh_counter = 0

    st.sidebar.divider()
    return refresh_counter

def render_project_selector(base_dir: Path) -> Tuple[str, str]:
    """Render project and file selector, returns target path string and selected project name."""
    st.sidebar.header("📁 Project & File Selector")

    projects = [p.name for p in base_dir.iterdir() if p.is_dir()]

    if not projects:
        st.sidebar.warning("ไม่พบโฟลเดอร์โปรเจกต์ใน ./logs")
        st.info("กรุณาสร้างโฟลเดอร์โปรเจกต์ใน `./logs/<project-name>/` แล้วใส่ไฟล์ .log ลงไป")
        st.stop()

    selected_project = st.sidebar.selectbox("Select Project", options=projects)

    project_path = base_dir / selected_project
    log_files = list(project_path.glob("*.log*")) + list(project_path.glob("*.json*"))
    file_names = [f.name for f in log_files]

    file_options = ["ALL FILES (รวมทุกไฟล์ในโปรเจกต์)"] + file_names
    selected_file_option = st.sidebar.selectbox("Select Log File", options=file_options)

    if selected_file_option == "ALL FILES (รวมทุกไฟล์ในโปรเจกต์)":
        target_path = str(project_path / "*")
    else:
        target_path = str(project_path / selected_file_option)

    st.sidebar.divider()
    return target_path, selected_project

def render_filters(available_names: list) -> Dict[str, Any]:
    """Render filters and return a dictionary of selected values."""
    st.sidebar.header("🔍 Filters")
    filters = {}
    
    filters['search_term'] = st.sidebar.text_input("Search (Message/Payload)", value="")
    filters['selected_levels'] = st.sidebar.multiselect(
        "Log Levels",
        options=["INFO", "WARN", "ERROR", "DEBUG"],
        default=["INFO", "WARN", "ERROR"]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("⏱️ Time Range Filter")
    enable_time_filter = st.sidebar.checkbox("Enable Time Filter", value=False)

    filters['start_datetime'] = None
    filters['end_datetime'] = None

    if enable_time_filter:
        import datetime
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=yesterday)
            start_time = st.time_input("Start Time", value=pd.to_datetime("00:00:00").time())
        with col2:
            end_date = st.date_input("End Date", value=today)
            end_time = st.time_input("End Time", value=pd.to_datetime("23:59:59").time())
        
        filters['start_datetime'] = f"{start_date} {start_time}"
        filters['end_datetime'] = f"{end_date} {end_time}"
        filters['is_time_filter_active'] = True
    else:
        filters['is_time_filter_active'] = False

    filters['selected_include_names'] = []
    filters['selected_exclude_names'] = []

    if available_names:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📌 Log Name Filters")
        filters['selected_include_names'] = st.sidebar.multiselect("Include Names (เลือกเฉพาะ)", options=available_names)
        filters['selected_exclude_names'] = st.sidebar.multiselect("Exclude Names (ยกเว้น)", options=available_names)

    return filters
