# app.py

import streamlit as st
import importlib

# ----- GLOBAL STYLING -----
st.markdown(
    """
    <style>
    /* Galaxy gradient background with subtle stars */
    .stApp {
        background: radial-gradient(circle at top left, #0b0c10, #1f2833, #0b0c10);
        color: white;
    }

    /* Star sprinkle effect */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
        opacity: 0.2;
        z-index: -1;
    }

    /* Make subheaders gold */
    h2, h3, h4 {
        color: #FFD700 !important;
    }

    /* Keep main big headers white for contrast */
    h1 {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----- NORMAL TAB LOGIC -----
tabs = st.tabs(["Dashboard", "Crystal Ball"])

with tabs[0]:
    st.title("📊 Dashboard")
    st.write("Your normal dashboard goes here.")

with tabs[1]:
    st.title("🔮 Crystal Ball")
    st.write("Upload a stock screenshot here (next step).") 