import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
from streamlit_autorefresh import st_autorefresh
import json

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

    # Init project from URL
    default_project_idx = 0
    if "project" in st.query_params:
        url_project = st.query_params["project"]
        if url_project in projects:
            default_project_idx = projects.index(url_project)

    def on_project_change():
        st.query_params["project"] = st.session_state.selector_project

    selected_project = st.sidebar.selectbox(
        "Select Project", 
        options=projects,
        index=default_project_idx,
        key="selector_project",
        on_change=on_project_change
    )
    # Ensure URL is set on first load
    st.query_params["project"] = selected_project

    project_path = base_dir / selected_project
    log_files = list(project_path.glob("*.log*")) + list(project_path.glob("*.json*"))
    file_names = [f.name for f in log_files]
    file_options = ["ALL FILES (รวมทุกไฟล์ในโปรเจกต์)"] + file_names

    # Init file from URL
    default_file_idx = 0
    if "file" in st.query_params:
        url_file = st.query_params["file"]
        if url_file in file_options:
            default_file_idx = file_options.index(url_file)

    def on_file_change():
        st.query_params["file"] = st.session_state.selector_file

    selected_file_option = st.sidebar.selectbox(
        "Select Log File", 
        options=file_options,
        index=default_file_idx,
        key="selector_file",
        on_change=on_file_change
    )
    st.query_params["file"] = selected_file_option

    if selected_file_option == "ALL FILES (รวมทุกไฟล์ในโปรเจกต์)":
        target_path = str(project_path / "*")
    else:
        target_path = str(project_path / selected_file_option)

    st.sidebar.divider()
    return target_path, selected_project

def sync_filter_to_url():
    """Callback to sync session state back to URL params"""
    if "filter_search_term" in st.session_state:
        st.query_params["search"] = st.session_state.filter_search_term
    
    if "filter_selected_levels" in st.session_state:
        st.query_params["levels"] = json.dumps(st.session_state.filter_selected_levels)
        
    if "filter_include_names" in st.session_state:
        st.query_params["include"] = json.dumps(st.session_state.filter_include_names)
        
    if "filter_exclude_names" in st.session_state:
        st.query_params["exclude"] = json.dumps(st.session_state.filter_exclude_names)

def render_filters(available_names: list) -> Dict[str, Any]:
    """Render filters and return a dictionary of selected values."""
    st.sidebar.header("🔍 Filters")
    filters = {}
    
    # Initialize from URL first, otherwise use defaults
    if 'filter_search_term' not in st.session_state:
        st.session_state['filter_search_term'] = st.query_params.get("search", "")
        
    if 'filter_selected_levels' not in st.session_state:
        if "levels" in st.query_params:
            try:
                st.session_state['filter_selected_levels'] = json.loads(st.query_params.get("levels"))
            except:
                st.session_state['filter_selected_levels'] = ["INFO", "WARNING", "ERROR"]
        else:
            st.session_state['filter_selected_levels'] = ["INFO", "WARNING", "ERROR"]
            
    if 'filter_include_names' not in st.session_state:
        if "include" in st.query_params:
            try:
                st.session_state['filter_include_names'] = json.loads(st.query_params.get("include"))
            except:
                st.session_state['filter_include_names'] = []
                
    if 'filter_exclude_names' not in st.session_state:
        if "exclude" in st.query_params:
            try:
                st.session_state['filter_exclude_names'] = json.loads(st.query_params.get("exclude"))
            except:
                st.session_state['filter_exclude_names'] = []
    
    filters['search_term'] = st.sidebar.text_input(
        "Search (Message/Payload)", 
        key="filter_search_term",
        on_change=sync_filter_to_url
    )
    
    filters['selected_levels'] = st.sidebar.multiselect(
        "Log Levels",
        options=["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"],
        key="filter_selected_levels",
        on_change=sync_filter_to_url
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("⏱️ Time Range Filter")
    enable_time_filter = st.sidebar.checkbox("Enable Time Filter", value=False, key="filter_enable_time")

    filters['start_datetime'] = None
    filters['end_datetime'] = None

    if enable_time_filter:
        import datetime
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        # Initialize default dates in session state if not present
        if 'filter_start_date' not in st.session_state:
            st.session_state['filter_start_date'] = yesterday
        if 'filter_start_time' not in st.session_state:
            st.session_state['filter_start_time'] = pd.to_datetime("00:00:00").time()
        if 'filter_end_date' not in st.session_state:
            st.session_state['filter_end_date'] = today
        if 'filter_end_time' not in st.session_state:
            st.session_state['filter_end_time'] = pd.to_datetime("23:59:59").time()

        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", key="filter_start_date")
            start_time = st.time_input("Start Time", key="filter_start_time")
        with col2:
            end_date = st.date_input("End Date", key="filter_end_date")
            end_time = st.time_input("End Time", key="filter_end_time")
        
        filters['start_datetime'] = f"{start_date} {start_time}"
        filters['end_datetime'] = f"{end_date} {end_time}"
        filters['is_time_filter_active'] = True
    else:
        filters['is_time_filter_active'] = False

    filters['selected_include_names'] = []
    filters['selected_exclude_names'] = []

    if available_names:
        # Sort available names so the options list is strictly stable
        stable_names = sorted(available_names)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📌 Log Name Filters")
        
        # Validate that session state options still exist in available_names
        # (in case url params have outdated names)
        valid_includes = [name for name in st.session_state.get('filter_include_names', []) if name in stable_names]
        st.session_state['filter_include_names'] = valid_includes
        
        valid_excludes = [name for name in st.session_state.get('filter_exclude_names', []) if name in stable_names]
        st.session_state['filter_exclude_names'] = valid_excludes

        filters['selected_include_names'] = st.sidebar.multiselect(
            "Include Names (เลือกเฉพาะ)", 
            options=stable_names, 
            key="filter_include_names",
            on_change=sync_filter_to_url
        )
        filters['selected_exclude_names'] = st.sidebar.multiselect(
            "Exclude Names (ยกเว้น)", 
            options=stable_names, 
            key="filter_exclude_names",
            on_change=sync_filter_to_url
        )

    return filters
