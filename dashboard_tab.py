# dashboard_tab.py
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Import helper functions from other modules
try:
    from app import get_stock_price, get_crypto_price, save_data, load_data
except ImportError:
    # Fallback if functions don't exist in app.py
    def get_stock_price(ticker):
        try:
            return float(yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1])
        except:
            return None
    
    def get_crypto_price(symbol):
        # Simple fallback for crypto prices
        return None
    
    def save_data():
        return True
    
    def load_data():
        return None

def render_dashboard():
    # ⬇️ paste your whole previous dashboard UI here ⬇️
    
    st.title("📊 Capital Allocator Dashboard")
    st.markdown("---")
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Portfolio inputs
    st.sidebar.subheader("💰 Portfolio Inputs")
    monthly_income = st.sidebar.number_input(
        "Monthly Income ($)", 
        min_value=0, 
        value=10000, 
        step=1000,
        help="Your monthly construction income"
    )
    
    cash_on_hand = st.sidebar.number_input(
        "Cash on Hand ($)", 
        min_value=0, 
        value=50000, 
        step=1000,
        help="Current cash reserves"
    )
    
    # Allocation percentages
    st.sidebar.subheader("🎯 Target Allocations")
    long_term_pct = st.sidebar.slider("Long-term (%)", 0, 100, 40)
    swing_trades_pct = st.sidebar.slider("Swing Trades (%)", 0, 100, 30)
    real_estate_pct = st.sidebar.slider("Real Estate (%)", 0, 100, 30)
    
    # Calculate total allocation
    total_allocation = long_term_pct + swing_trades_pct + real_estate_pct
    
    if total_allocation != 100:
        st.sidebar.warning(f"⚠️ Total: {total_allocation}% (should be 100%)")
    else:
        st.sidebar.success(f"✅ Total: {total_allocation}%")
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Capital", f"${monthly_income + cash_on_hand:,.0f}")
    
    with col2:
        long_term_dollars = (long_term_pct / 100) * (monthly_income + cash_on_hand)
        st.metric("📈 Long-term", f"${long_term_dollars:,.0f}")
    
    with col3:
        swing_dollars = (swing_trades_pct / 100) * (monthly_income + cash_on_hand)
        st.metric("⚡ Swing Trades", f"${swing_dollars:,.0f}")
    
    with col4:
        real_estate_dollars = (real_estate_pct / 100) * (monthly_income + cash_on_hand)
        st.metric("🏠 Real Estate", f"${real_estate_dollars:,.0f}")
    
    st.markdown("---")
    
    # Portfolio Holdings Section
    st.header("📈 Portfolio Holdings")
    
    # Sample portfolio data (you can replace with real data)
    portfolio_data = {
        'Ticker': ['PLTR', 'CRWD', 'BTC-USD', 'XRP-USD'],
        'Quantity': [100, 50, 0.5, 1000],
        'Cost Basis': [15.50, 180.00, 45000, 0.45],
        'Current Price': [18.75, 195.50, 52000, 0.52],
        'Market Value': [1875, 9775, 26000, 520],
        'P&L': [325, 775, 7000, 70],
        'P&L %': [21.0, 4.3, 15.6, 15.6]
    }
    
    df = pd.DataFrame(portfolio_data)
    
    # Calculate totals
    total_cost = sum(df['Cost Basis'] * df['Quantity'])
    total_value = sum(df['Market Value'])
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    
    # Display portfolio summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Portfolio Value", f"${total_value:,.0f}")
    
    with col2:
        pnl_color = "🟢" if total_pnl > 0 else "🔴" if total_pnl < 0 else "⚪"
        st.metric(f"{pnl_color} Total P&L", f"${total_pnl:,.0f}")
    
    with col3:
        st.metric("📈 P&L %", f"{total_pnl_pct:.1f}%")
    
    # Display portfolio table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Market Overview Section
    st.header("🌍 Market Overview")
    
    # Sample market data
    market_tickers = ['SPY', 'QQQ', 'IWM', 'GLD']
    market_data = []
    
    for ticker in market_tickers:
        try:
            # Get current price (simulated for demo)
            current_price = 450 + (hash(ticker) % 100)  # Simulated price
            change = (hash(ticker) % 20) - 10  # Simulated change
            change_pct = (change / current_price) * 100
            
            market_data.append({
                'Ticker': ticker,
                'Price': current_price,
                'Change': change,
                'Change %': change_pct
            })
        except:
            continue
    
    market_df = pd.DataFrame(market_data)
    
    # Display market overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Major Indices")
        st.dataframe(market_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📈 Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.success("Data refreshed!")
        
        if st.button("📊 View Charts"):
            st.info("Chart view coming soon...")
        
        if st.button("📋 Export Data"):
            st.info("Export functionality coming soon...")
    
    st.markdown("---")
    
    # Trading Opportunities Section
    st.header("🎯 Trading Opportunities")
    
    # Sample opportunities based on your strategy
    opportunities = [
        {
            'Asset': 'PLTR',
            'Signal': 'BUY',
            'Reason': 'Price above 50-day SMA',
            'Confidence': 'High',
            'Target': '$20.00'
        },
        {
            'Asset': 'CRWD',
            'Signal': 'HOLD',
            'Reason': 'Neutral RSI',
            'Confidence': 'Medium',
            'Target': '$200.00'
        },
        {
            'Asset': 'BTC-USD',
            'Signal': 'BUY',
            'Reason': 'RSI below 35 (oversold)',
            'Confidence': 'High',
            'Target': '$55,000'
        }
    ]
    
    opp_df = pd.DataFrame(opportunities)
    st.dataframe(opp_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Real Estate Planning Section
    st.header("🏠 Real Estate Planning")
    
    monthly_real_estate = (real_estate_pct / 100) * monthly_income
    current_real_estate = (real_estate_pct / 100) * cash_on_hand
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Monthly Savings", f"${monthly_real_estate:,.0f}")
    
    with col2:
        st.metric("🏦 Current Allocation", f"${current_real_estate:,.0f}")
    
    with col3:
        # Example: $500k property with 20% down
        target_property = 500000
        down_payment_needed = target_property * 0.20
        months_to_goal = down_payment_needed / monthly_real_estate if monthly_real_estate > 0 else 0
        st.metric("📅 Months to $100k Down", f"{months_to_goal:.1f}")
    
    # Progress bar for real estate goal
    progress = min(1.0, (current_real_estate / down_payment_needed) if down_payment_needed > 0 else 0)
    st.progress(progress)
    st.caption(f"Progress toward $100k down payment: {progress*100:.1f}%")
    
    st.markdown("---")
    
    # Footer
    st.markdown("*Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")
    st.caption("Capital Allocator Dashboard - Built with Streamlit")
