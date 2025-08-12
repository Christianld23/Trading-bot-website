import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Mid-Term Options Screener",
    page_icon="📈",
    layout="wide"
)

# Function to load option chains with caching
@st.cache_data
def load_option_chain(ticker_symbol):
    """Load option chain data for a given ticker with caching"""
    ticker = yf.Ticker(ticker_symbol)
    try:
        expirations = ticker.options
        options_data = {}
        for date in expirations:
            calls = ticker.option_chain(date).calls
            puts = ticker.option_chain(date).puts
            options_data[date] = {"calls": calls, "puts": puts}
        return options_data
    except Exception as e:
        st.error(f"Failed to load options data for {ticker_symbol}: {e}")
        return {}

# Function to filter and score options
def filter_and_score_options(options_data):
    """Filter and score options contracts based on multiple criteria"""
    scored_contracts = []

    for exp_date, chains in options_data.items():
        calls = chains["calls"]

        # Filter for out-of-the-money calls with reasonable IV and liquidity
        filtered = calls[
            (calls["inTheMoney"] == False) &
            (calls["impliedVolatility"] < 1.0) &  # remove crazy IVs
            (calls["volume"] > 10) &
            (calls["openInterest"] > 50)
        ]

        for _, row in filtered.iterrows():
            # Calculate composite score based on volume/OI ratio, IV, and delta
            score = (
                (row["volume"] / row["openInterest"]) * 0.4 +
                (1 - row["impliedVolatility"]) * 0.3 +
                (1 - abs(0.5 - row["delta"])) * 0.3
            )
            scored_contracts.append({
                "contractSymbol": row["contractSymbol"],
                "strike": row["strike"],
                "expiration": exp_date,
                "lastPrice": row["lastPrice"],
                "IV": row["impliedVolatility"],
                "volume": row["volume"],
                "openInterest": row["openInterest"],
                "delta": row["delta"],
                "score": round(score, 4)
            })

    df = pd.DataFrame(scored_contracts)
    return df.sort_values("score", ascending=False)

# Function to get stock price
def get_stock_price(symbol):
    """Get stock price from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('regularMarketPrice', None)
    except Exception as e:
        st.error(f"Error fetching {symbol} price: {str(e)}")
        return None

# Title and description
st.title("📈 Mid-Term Options Screener")
st.markdown("---")
st.markdown("**Professional options screening tool for identifying high-quality mid-term options contracts**")

# Sidebar for filters and settings
st.sidebar.title("🔧 Screener Settings")
st.sidebar.markdown("---")

# Input section
st.header("🎯 Options Screening")
col1, col2 = st.columns([2, 1])

with col1:
    ticker = st.text_input("Enter Ticker Symbol", value="PLTR", placeholder="AAPL, TSLA, SPY...")
    
    # Additional filters
    st.subheader("📊 Filter Settings")
    col_a, col_b = st.columns(2)
    
    with col_a:
        min_volume = st.number_input("Min Volume", min_value=0, value=10, help="Minimum trading volume")
        min_oi = st.number_input("Min Open Interest", min_value=0, value=50, help="Minimum open interest")
    
    with col_b:
        max_iv = st.slider("Max IV %", min_value=0, max_value=200, value=100, help="Maximum implied volatility")
        min_delta = st.slider("Min Delta", min_value=0.0, max_value=1.0, value=0.1, step=0.1, help="Minimum delta value")

with col2:
    # Stock info
    if ticker:
        current_price = get_stock_price(ticker.upper())
        if current_price:
            st.metric("Current Price", f"${current_price:.2f}")
            
            # Calculate days to next expiration
            options_data = load_option_chain(ticker.upper())
            if options_data:
                next_exp = min(options_data.keys())
                exp_date = datetime.strptime(next_exp, '%Y-%m-%d').date()
                days_to_exp = (exp_date - datetime.now().date()).days
                st.metric("Days to Next Exp", days_to_exp)
        else:
            st.warning("Unable to fetch stock price")

# Load and analyze options
if st.button("🚀 Load & Analyze Options", type="primary"):
    if ticker:
        with st.spinner("Loading options data..."):
            raw_data = load_option_chain(ticker.upper())

        if raw_data:
            st.success(f"✅ Data loaded for {ticker.upper()}!")
            
            # Get scored options
            scored_df = filter_and_score_options(raw_data)
            
            if not scored_df.empty:
                # Apply additional filters
                filtered_df = scored_df[
                    (scored_df['volume'] >= min_volume) &
                    (scored_df['openInterest'] >= min_oi) &
                    (scored_df['IV'] <= max_iv / 100) &
                    (scored_df['delta'] >= min_delta)
                ]
                
                if not filtered_df.empty:
                    # Display results
                    st.header("🏆 Top Ranked Options Contracts")
                    
                    # Format display
                    display_df = filtered_df.head(20).copy()
                    display_df['Strike'] = display_df['strike'].round(2)
                    display_df['Last Price'] = display_df['lastPrice'].round(2)
                    display_df['IV %'] = (display_df['IV'] * 100).round(1)
                    display_df['Delta'] = display_df['delta'].round(3)
                    display_df['Score'] = display_df['score'].round(4)
                    display_df['Volume/OI'] = (display_df['volume'] / display_df['openInterest']).round(3)
                    
                    # Reorder columns
                    display_df = display_df[['contractSymbol', 'Strike', 'expiration', 'Last Price', 'IV %', 'volume', 'openInterest', 'Volume/OI', 'Delta', 'Score']]
                    display_df.columns = ['Contract', 'Strike', 'Expiration', 'Price', 'IV %', 'Volume', 'OI', 'Vol/OI', 'Delta', 'Score']
                    
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Summary statistics
                    st.subheader("📊 Summary Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Contracts", len(filtered_df))
                    with col2:
                        avg_iv = filtered_df['IV'].mean() * 100
                        st.metric("Avg IV %", f"{avg_iv:.1f}%")
                    with col3:
                        avg_score = filtered_df['score'].mean()
                        st.metric("Avg Score", f"{avg_score:.3f}")
                    with col4:
                        avg_delta = filtered_df['delta'].mean()
                        st.metric("Avg Delta", f"{avg_delta:.3f}")
                    
                    # Expiration analysis
                    st.subheader("📅 Expiration Analysis")
                    exp_counts = filtered_df['expiration'].value_counts().head(5)
                    st.bar_chart(exp_counts)
                    
                else:
                    st.warning("No contracts meet the current filter criteria. Try adjusting your filters.")
            else:
                st.warning("No options data available or no contracts meet basic criteria.")
        else:
            st.error(f"No options data available for {ticker.upper()}")
    else:
        st.warning("Please enter a ticker symbol")

# Additional analysis section
if 'scored_df' in locals() and not scored_df.empty:
    st.markdown("---")
    st.header("🔍 Advanced Analysis")
    
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        st.subheader("📈 IV Distribution")
        if not scored_df.empty:
            iv_data = scored_df['IV'] * 100
            st.histogram_chart(iv_data)
    
    with tab2:
        st.subheader("📊 Delta Distribution")
        if not scored_df.empty:
            delta_data = scored_df['delta']
            st.histogram_chart(delta_data)
    
    with tab3:
        st.subheader("💰 Price Distribution")
        if not scored_df.empty:
            price_data = scored_df['lastPrice']
            st.histogram_chart(price_data)

# Footer
st.markdown("---")
st.markdown("*Mid-Term Options Screener - Powered by Streamlit & yfinance*")

# Debug info
if st.checkbox("Show Debug Info"):
    st.write("Debug information can be added here")
