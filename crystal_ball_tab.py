import streamlit as st
from datetime import datetime

def render_crystal_ball_tab():
    st.markdown("### 🔮 Crystal Ball")
    st.caption(f"Tab online at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.info("Upload a chart screenshot here (we'll add analysis next).")
    up = st.file_uploader("Upload chart screenshot (PNG/JPG)", type=["png","jpg","jpeg"])
    if up:
        st.image(up, caption="Uploaded chart", use_container_width=True)
        st.success("Image received. Next: wire SOP analysis.")
