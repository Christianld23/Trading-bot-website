# dashboard_tab.py
import streamlit as st
import pandas as pd

def render_dashboard():
    st.title("📊 Portfolio Dashboard")

    # Sidebar inputs (monthly income, sliders, etc.)
    st.sidebar.header("Financial Inputs")
    monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, step=100)
    cash_on_hand = st.sidebar.number_input("Cash on Hand ($)", min_value=0, step=100)
    long_term = st.sidebar.slider("Long Term Allocation (%)", 0, 100, 40)
    short_term = st.sidebar.slider("Short Term Allocation (%)", 0, 100, 30)
    real_estate = st.sidebar.slider("Real Estate Fund Allocation (%)", 0, 100, 30)

    st.write(f"**Monthly Income:** ${monthly_income}")
    st.write(f"**Cash on Hand:** ${cash_on_hand}")

    # Editable portfolio table
    st.subheader("📂 Portfolio Holdings")
    default_data = {
        "Ticker": ["PLTR", "CRWD", "BTC", "XRP"],
        "Quantity": [10, 5, 2, 100],
        "Cost Basis": [15, 200, 30000, 0.5]
    }
    df = pd.DataFrame(default_data)

    edited_df = st.data_editor(df, num_rows="dynamic")

    # Show summary
    st.subheader("📈 Current Portfolio")
    st.dataframe(edited_df)
