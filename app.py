import streamlit as st

# (Optional) global galaxy CSS, safe to keep
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top left,#0b0c10,#1f2833,#0b0c10); color: white; }
h1 { color: white !important; } h2,h3,h4 { color: #FFD700 !important; }
</style>
""", unsafe_allow_html=True)

from dashboard_tab import render_dashboard
from automation_tab import render_automation_tab  # your 'Crystal Ball' tab

tab1, tab2 = st.tabs(["Dashboard", "🔮 Crystal Ball"])

with tab1:
    render_dashboard()

with tab2:
    render_automation_tab() 