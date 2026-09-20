import streamlit as st
import pandas as pd
import plotly.express as px

def render_analytics_dashboard(df: pd.DataFrame, color_mapping: dict):
    """Render the analytics dashboard with Time Series and Donut charts."""
    if 'timestamp' not in df.columns or 'level' not in df.columns:
        return

    with st.expander("📊 Log Analytics Dashboard (Time Series & Errors)", expanded=False):
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
            
            # Choose grouping column based on availability
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
                st.success("🎉 No ERROR logs found in the current dataset!")
