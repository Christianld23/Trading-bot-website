import streamlit as st
from automation_tab import render_automation  # <-- make sure this import matches the file/function

# If you already have this somewhere, don't duplicate it.
st.set_page_config(page_title="Capital Allocator", layout="wide")

# ---- Tabs ----
tab1, tab2 = st.tabs(["Dashboard", "🤖 Automation"])
with tab1:
    # Keep your existing dashboard UI here.
    st.markdown("## 📊 Capital Allocator Dashboard")
with tab2:
    render_automation()
# ---- End Tabs ---- 