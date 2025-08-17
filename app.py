import importlib
import streamlit as st

st.set_page_config(page_title="Capital Allocator", layout="wide")

# --- Galaxy theme (kept minimal so it won't break) ---
def inject_galaxy_theme():
    st.markdown("""
    <style>
      .stApp {
        background: radial-gradient(1200px 600px at 10% 10%, #0b0f1c 0%, #0b0f1c 30%, #0a0d18 60%, #070a12 100%),
                    radial-gradient(900px 500px at 90% 20%, rgba(24,31,55,0.9) 0%, rgba(7,10,18,0.0) 60%),
                    radial-gradient(700px 400px at 30% 90%, rgba(58,20,87,0.5) 0%, rgba(7,10,18,0.0) 60%),
                    linear-gradient(180deg, #0b0f1c 0%, #070a12 100%);
        color: #E6EAF2;
      }
      [data-testid="stAppViewContainer"], .block-container { background: transparent !important; }
      .stApp::before {
        content:""; position:fixed; inset:0; pointer-events:none; z-index:-1;
        background-image:
          radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.32) 0%, rgba(255,255,255,0) 100%),
          radial-gradient(1.6px 1.6px at 70% 10%, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 100%),
          radial-gradient(1.2px 1.2px at 40% 80%, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0) 100%),
          radial-gradient(1.8px 1.8px at 85% 70%, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0) 100%);
      }
    </style>
    """, unsafe_allow_html=True)

inject_galaxy_theme()

# --- Safe import helpers ---
def import_or_none(module_name, func_name):
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name, None)
        return fn
    except Exception as e:
        st.sidebar.warning(f"Module '{module_name}' not loaded: {e}")
        return None

# Try to load optional tabs; don't crash if missing
render_dashboard = import_or_none("dashboard_tab", "render_dashboard")
render_crystal = import_or_none("crystal_ball_tab", "render_crystal_ball_tab")
if render_crystal is None:
    # backward compat if file is still named automation_tab.py
    render_crystal = import_or_none("automation_tab", "render_automation_tab")

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Dashboard", "🔮 Crystal Ball"])

with tab1:
    if render_dashboard:
        try:
            render_dashboard()
        except Exception as e:
            st.error(f"Dashboard error: {e}")
            st.markdown("## 📊 Capital Allocator Dashboard (fallback)")
    else:
        st.markdown("## 📊 Capital Allocator Dashboard (fallback)")

with tab2:
    if render_crystal:
        try:
            render_crystal()
        except Exception as e:
            st.error(f"Crystal Ball error: {e}")
            st.info("Using stub content while we fix it.")
            st.markdown("### 🤖 SOP stub online.")
    else:
        st.markdown("### 🔮 Crystal Ball")
        st.caption("Tab is live. Add `crystal_ball_tab.py` with `render_crystal_ball_tab()` to enable features.") 