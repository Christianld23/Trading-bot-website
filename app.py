import streamlit as st
from automation_tab import render_automation_tab
# Only include this next import if you created dashboard_tab.py with a function:
from dashboard_tab import render_dashboard  # comment out if you didn't make this

st.set_page_config(page_title="Capital Allocator", layout="wide")

tab1, tab2 = st.tabs(["Dashboard", "🤖 Automation"])
with tab1:
    # If you made dashboard_tab.py:
    try:
        render_dashboard()
    except Exception:
        st.markdown("## 📊 Capital Allocator Dashboard")
with tab2:
    render_automation_tab() 