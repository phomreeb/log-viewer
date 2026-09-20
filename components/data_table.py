import streamlit as st
import pandas as pd
from typing import List

def render_metrics_and_export(df: pd.DataFrame, selected_project: str):
    """Render top metric cards and the export to CSV button."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Project", selected_project)
    col2.metric("Total Logs Loaded", f"{len(df):,}")
    col3.metric("Files Involved", df['source_log_file'].nunique() if 'source_log_file' in df.columns else 1)
    
    with col4:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name=f"{selected_project}_logs.csv",
            mime="text/csv",
            use_container_width=True
        )
    st.divider()

def render_log_table(df: pd.DataFrame) -> dict:
    """Render the main log dataframe and return selected rows."""
    main_cols = [c for c in ['timestamp', 'source_log_file', 'level', 'service', 'name', 'message'] if c in df.columns]

    event = st.dataframe(
        df[main_cols],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    return event.selection.get("rows", [])

def render_json_detail(df: pd.DataFrame, selected_rows: List[int]):
    """Render the JSON detail panel for a selected log row."""
    st.divider()
    st.subheader("🔬 Selected Log Detail")
    
    if selected_rows:
        import json
        import uuid
        from datetime import datetime, date
        
        raw_record = df.iloc[selected_rows[0]].to_dict()
        clean_record = {
            k: v for k, v in raw_record.items() 
            if pd.notna(v)
        }
        
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, uuid.UUID):
                    return str(obj)
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                return super().default(obj)
        
        st.caption("👆 Hover at the top right of the block below to copy JSON to clipboard")
        json_string = json.dumps(clean_record, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        st.code(json_string, language="json")
    else:
        st.info("👈 คลิกเลือกบรรทัดในตารางเพื่อดูโครงสร้าง JSON ก้อนเต็ม")
