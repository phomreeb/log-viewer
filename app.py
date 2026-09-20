import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

from repositories.log_repository import DuckDBLogRepository
from services.log_service import LogService

# --- DEPENDENCY INJECTION ---
repo = DuckDBLogRepository()
log_service = LogService(repository=repo)

st.set_page_config(page_title="Multi-Project Log Viewer", layout="wide", page_icon="📜")
st.title("📜 Multi-Project JSON Log Viewer")

# กำหนดโฟลเดอร์หลักที่เก็บ Log
BASE_DIR = Path("./logs")

# สร้างโฟลเดอร์หลักให้อัตโนมัติถ้ายังไม่มี
if not BASE_DIR.exists():
    BASE_DIR.mkdir(parents=True)

# --- SIDEBAR: View Mode ---
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
    refresh_counter = st_autorefresh(interval=interval_mapping[refresh_interval], key="live_log_refresh")
else:
    refresh_counter = 0

st.sidebar.divider()

# --- SIDEBAR: Dynamic Project & File Selector ---
st.sidebar.header("📁 Project & File Selector")

# 1. สแกนหาโฟลเดอร์โปรเจกต์ทั้งหมดใน ./logs
projects = [p.name for p in BASE_DIR.iterdir() if p.is_dir()]

if not projects:
    st.sidebar.warning("ไม่พบโฟลเดอร์โปรเจกต์ใน ./logs")
    st.info("กรุณาสร้างโฟลเดอร์โปรเจกต์ใน `./logs/<project-name>/` แล้วใส่ไฟล์ .log ลงไป")
    st.stop()

selected_project = st.sidebar.selectbox("Select Project", options=projects)

# 2. สแกนหาไฟล์ .log / .json ทั้งหมดในโปรเจกต์ที่เลือก
project_path = BASE_DIR / selected_project
log_files = list(project_path.glob("*.log*")) + list(project_path.glob("*.json*"))
file_names = [f.name for f in log_files]

# ตัวเลือกสำหรับดูทุกไฟล์พร้อมกัน หรือเลือกเฉพาะไฟล์
file_options = ["ALL FILES (รวมทุกไฟล์ในโปรเจกต์)"] + file_names
selected_file_option = st.sidebar.selectbox("Select Log File", options=file_options)

# 3. กำหนด Path Pattern
if selected_file_option == "ALL FILES (รวมทุกไฟล์ในโปรเจกต์)":
    target_path = str(project_path / "*")
else:
    target_path = str(project_path / selected_file_option)

st.sidebar.divider()

# --- SIDEBAR: Log Filters ---
st.sidebar.header("🔍 Filters")
search_term = st.sidebar.text_input("Search (Message/Payload)", value="")
selected_levels = st.sidebar.multiselect(
    "Log Levels",
    options=["INFO", "WARN", "ERROR", "DEBUG"],
    default=["INFO", "WARN", "ERROR"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Time Range Filter")
enable_time_filter = st.sidebar.checkbox("Enable Time Filter", value=False)

start_datetime = None
end_datetime = None

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
    
    # Format as standard SQL Timestamp string for DuckDB (YYYY-MM-DD HH:MM:SS)
    start_datetime = f"{start_date} {start_time}"
    end_datetime = f"{end_date} {end_time}"

# Wrapper function for caching distinct names
@st.cache_data(ttl=10)
def fetch_distinct_log_names(file_pattern: str, cache_buster: int = 0):
    return log_service.get_available_names(file_pattern)

available_names = fetch_distinct_log_names(target_path, refresh_counter)
selected_include_names = []
selected_exclude_names = []

if available_names:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Log Name Filters")
    selected_include_names = st.sidebar.multiselect("Include Names (เลือกเฉพาะ)", options=available_names)
    selected_exclude_names = st.sidebar.multiselect("Exclude Names (ยกเว้น)", options=available_names)

row_limit = st.sidebar.slider("Max Rows", min_value=100, max_value=10000, value=1000)

# --- QUERY FUNCTION (Wrapper for caching) ---
@st.cache_data(ttl=5)
def fetch_multi_log_data(file_pattern: str, search: str, levels: list, include_names: list, exclude_names: list, start_dt: str, end_dt: str, limit: int, cache_buster: int = 0):
    return log_service.get_logs(file_pattern, search, levels, include_names, exclude_names, start_dt, end_dt, limit)

# --- MAIN DISPLAY ---
if view_mode == "Live (อัตโนมัติ)":
    from datetime import datetime
    st.info(f"🟢 **Live Mode Active:** ข้อมูลกำลังรีเฟรชทุกๆ {refresh_interval} (อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')})")

try:
    df = fetch_multi_log_data(target_path, search_term, selected_levels, selected_include_names, selected_exclude_names, start_datetime, end_datetime, row_limit, refresh_counter)

    if df.empty:
        st.warning("ไม่พบข้อมูล Log ในไฟล์หรือโปรเจกต์ที่เลือก")
        if enable_time_filter:
            st.info(f"💡 คำแนะนำ: ตอนนี้คุณกำลังค้นหาข้อมูลระหว่าง `{start_datetime}` ถึง `{end_datetime}`\n\nลองตรวจสอบว่าไฟล์ Log มีข้อมูลในช่วงเวลานี้หรือไม่ หรือลองขยายวันที่ (Start Date / End Date) ให้กว้างขึ้นครับ")
    else:
        # Analytics Dashboard in Expander
        if 'timestamp' in df.columns and 'level' in df.columns:
            with st.expander("📊 Log Analytics Dashboard (Time Series & Errors)", expanded=False):
                import plotly.express as px
                
                # Copy dataframe to avoid mutating the main table display
                chart_df = df.copy()
                chart_df['parsed_dt'] = pd.to_datetime(chart_df['timestamp'], errors='coerce')
                chart_df['level_upper'] = chart_df['level'].astype(str).str.upper()
                
                valid_time_df = chart_df.dropna(subset=['parsed_dt']).copy()
                
                chart_col1, chart_col2 = st.columns([2, 1])
                
                with chart_col1:
                    if not valid_time_df.empty:
                        # Group by minute and level for Time Series
                        valid_time_df['time_bin'] = valid_time_df['parsed_dt'].dt.floor('min')
                        time_grouped = valid_time_df.groupby(['time_bin', 'level_upper']).size().reset_index(name='count')
                        
                        color_mapping = {
                            "ERROR": "#ef4444",   # Red
                            "WARN": "#f59e0b",    # Orange/Yellow
                            "WARNING": "#f59e0b", # Orange/Yellow
                            "INFO": "#10b981",    # Green
                            "DEBUG": "#3b82f6",   # Blue
                            "CRITICAL": "#7f1d1d" # Dark Red
                        }
                        
                        fig_time = px.line(
                            time_grouped,
                            x='time_bin',
                            y='count',
                            color='level_upper',
                            color_discrete_map=color_mapping,
                            markers=True,
                            title="📉 Log Volume Over Time (Per Minute)"
                        )
                        fig_time.update_layout(
                            xaxis_title="Time", 
                            yaxis_title="Log Count", 
                            margin=dict(l=20, r=20, t=40, b=20),
                            legend_title_text="Level"
                        )
                        st.plotly_chart(fig_time, use_container_width=True)
                    else:
                        st.info("No valid timestamp data available for Time Series chart.")
                
                with chart_col2:
                    error_df = chart_df[chart_df['level_upper'] == 'ERROR']
                    
                    # Choose grouping column based on availability (prefer 'name' as requested, fallback to 'service')
                    group_col = 'name' if 'name' in error_df.columns else ('service' if 'service' in error_df.columns else None)
                    
                    if not error_df.empty and group_col:
                        error_grouped = error_df[group_col].value_counts().reset_index()
                        error_grouped.columns = [group_col, 'count']
                        
                        fig_donut = px.pie(
                            error_grouped,
                            names=group_col,
                            values='count',
                            hole=0.4,
                            title=f"🛑 Error Breakdown by {group_col.capitalize()}"
                        )
                        fig_donut.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_donut, use_container_width=True)
                    else:
                        # If no errors found, show a nice success message instead of an empty chart
                        st.success("🎉 No ERROR logs found in the current dataset!")

        # Metrics & Export
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Project", selected_project)
        col2.metric("Total Logs Loaded", f"{len(df):,}")
        col3.metric("Files Involved", df['source_log_file'].nunique() if 'source_log_file' in df.columns else 1)
        
        with col4:
            # Generate CSV data for download
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export to CSV",
                data=csv_data,
                file_name=f"{selected_project}_logs.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.divider()

        # Display Columns Setup
        main_cols = [c for c in ['timestamp', 'source_log_file', 'level', 'service', 'name', 'message'] if c in df.columns]

        event = st.dataframe(
            df[main_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # JSON Detail Panel
        st.divider()
        st.subheader("🔬 Selected Log Detail")
        selected_rows = event.selection.get("rows", [])
        if selected_rows:
            import json
            raw_record = df.iloc[selected_rows[0]].to_dict()
            clean_record = {
                k: v for k, v in raw_record.items() 
                if pd.notna(v)
            }
            
            st.caption("👆 Hover at the top right of the block below to copy JSON to clipboard")
            json_string = json.dumps(clean_record, indent=2, ensure_ascii=False)
            st.code(json_string, language="json")
            
        else:
            st.info("👈 คลิกเลือกบรรทัดในตารางเพื่อดูโครงสร้าง JSON ก้อนเต็ม")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลด Log: {e}")
