import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
import os
from datetime import datetime, timezone
from config import APP_ENV, DEFAULT_TICKERS, ALLOCATION_RULES, get_secret

# File path for saving data
DATA_FILE = "portfolio_data.json"

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

@st.cache_data(ttl=300)
def load_option_chain(ticker: str):
    """Load option chain data for a given ticker with caching"""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options or []
        chains = {}
        for exp in expirations:
            try:
                oc = t.option_chain(exp)
                chains[exp] = {"calls": oc.calls, "puts": oc.puts}
            except Exception:
                continue
        return chains
    except Exception:
        return {}

# Function to save data to JSON file
def save_data():
    """Save portfolio data to JSON file"""
    data = {
        'core_holdings': st.session_state.get('core_holdings', []),
        'swing_trades': st.session_state.get('swing_trades', []),
        'long_term_pct': st.session_state.get('long_term_pct', 40),
        'swing_trades_pct': st.session_state.get('swing_trades_pct', 30),
        'real_estate_pct': st.session_state.get('real_estate_pct', 30),
        'monthly_income': st.session_state.get('monthly_income', 10000.0),
        'cash_on_hand': st.session_state.get('cash_on_hand', 50000.0)
    }
    
    # Convert datetime objects to strings for JSON serialization
    for trade in data['swing_trades']:
        if 'expiration_date' in trade:
            trade['expiration_date'] = trade['expiration_date'].isoformat()
    
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Function to load data from JSON file
def load_data():
    """Load portfolio data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
            
            # Convert string dates back to datetime objects
            for trade in data.get('swing_trades', []):
                if 'expiration_date' in trade:
                    data['swing_trades'][data['swing_trades'].index(trade)]['expiration_date'] = datetime.fromisoformat(trade['expiration_date']).date()
            
            return data
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    return None

@st.cache_data(ttl=300)
def get_stock_price(ticker: str) -> float | None:
    """Get stock price from yfinance with caching"""
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if hist is None or hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_crypto_price(symbol: str) -> float | None:
    """Get crypto price from CoinGecko API with caching"""
    # Example: map 'BTC-USD' -> CoinGecko 'bitcoin'
    mapping = {"BTC-USD": "bitcoin", "ETH-USD": "ethereum", "XRP-USD": "ripple"}
    coin = mapping.get(symbol.upper())
    if not coin:
        return None
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin, "vs_currencies": "usd"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return float(data.get(coin, {}).get("usd")) if data else None
    except Exception:
        return None

# Function to calculate days until expiration
def days_until_expiration(expiration_date):
    """Calculate days until expiration"""
    today = datetime.now().date()
    delta = expiration_date - today
    return delta.days

# Function to format currency with color coding
def format_currency_with_color(value, is_percentage=False):
    """Format currency with color coding for positive/negative values"""
    if value is None or value == "N/A":
        return "N/A"
    
    if is_percentage:
        if value > 0:
            return f"🟢 **+{value:.1f}%**"
        elif value < 0:
            return f"🔴 **{value:.1f}%**"
        else:
            return f"⚪ **{value:.1f}%**"
    else:
        if value > 0:
            return f"🟢 **${value:,.0f}**"
        elif value < 0:
            return f"🔴 **${value:,.0f}**"
        else:
            return f"⚪ **${value:,.0f}**"

# Function to create summary guidance
def create_summary_guidance(monthly_income, cash_on_hand, real_estate_pct, total_core_pnl):
    """Create one-sentence guidance for the summary box"""
    total_capital = monthly_income + cash_on_hand
    monthly_real_estate = (real_estate_pct / 100) * monthly_income
    
    # Real estate milestone guidance
    if monthly_real_estate > 0:
        example_property_value = 500000
        down_payment_needed = example_property_value * 0.20
        months_to_down_payment = down_payment_needed / monthly_real_estate
        
        if months_to_down_payment <= 12:
            guidance = f"You're **{months_to_down_payment:.1f} months** away from a $100k down payment for real estate."
        elif months_to_down_payment <= 24:
            guidance = f"You're **{months_to_down_payment:.1f} months** away from your next real estate milestone."
        else:
            guidance = "Consider increasing your real estate allocation to reach property goals faster."
    
    # Portfolio performance guidance
    elif total_core_pnl > 0:
        guidance = f"Your portfolio is up **${total_core_pnl:,.0f}** - consider taking some profits."
    elif total_core_pnl < 0:
        guidance = f"Your portfolio is down **${abs(total_core_pnl):,.0f}** - review your positions."
    else:
        guidance = "Ready to deploy capital according to your allocation strategy."
    
    return guidance

def render_dashboard():
    """Render the main dashboard"""
    
    # ENV badge + Refresh + Last updated
    st.markdown("🧪 **Environment: DEV**" if APP_ENV == "dev" else "🟢 **Environment: PROD**")

    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_r:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state["last_updated_utc"] = datetime.now(timezone.utc)

    last = st.session_state.get("last_updated_utc", datetime.now(timezone.utc))
    st.caption(f"Last updated: {last.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Initialize session state with loaded data
    if 'data_loaded' not in st.session_state:
        loaded_data = load_data()
        if loaded_data:
            st.session_state.update(loaded_data)
            st.session_state.data_loaded = True
        else:
            # Default values using centralized configuration
            st.session_state.core_holdings = []
            st.session_state.swing_trades = []
            st.session_state.long_term_pct = ALLOCATION_RULES["long_term_pct"]
            st.session_state.swing_trades_pct = ALLOCATION_RULES["swing_pct"]
            st.session_state.real_estate_pct = ALLOCATION_RULES["real_estate_pct"]
            st.session_state.monthly_income = 10000.0
            st.session_state.cash_on_hand = 50000.0
            st.session_state.data_loaded = True

    # Title and description
    st.title("💰 Capital Allocator Dashboard")
    st.markdown("---")

    # Sidebar for navigation and save/load
    st.sidebar.title("Navigation")
    st.sidebar.info("Dashboard for optimizing capital allocation across different investment strategies.")

    # Save/Load buttons in sidebar
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("💾 Save Data"):
            if save_data():
                st.success("Data saved successfully!")
            else:
                st.error("Failed to save data")

    with col2:
        if st.button("🔄 Load Data"):
            loaded_data = load_data()
            if loaded_data:
                st.session_state.update(loaded_data)
                st.success("Data loaded successfully!")
                st.rerun()
            else:
                st.error("No saved data found")

    # Calculate portfolio metrics for summary
    total_core_value = 0
    total_core_cost = 0
    total_core_pnl = 0

    for holding in st.session_state.core_holdings:
        ticker_symbol = holding['ticker']
        if ticker_symbol in ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XLM', 'VET']:
            # Convert to format expected by get_crypto_price
            crypto_symbol = f"{ticker_symbol}-USD"
            current_price = get_crypto_price(crypto_symbol)
        else:
            current_price = get_stock_price(ticker_symbol)
        
        if current_price:
            market_value = holding['quantity'] * current_price
            total_cost = holding['quantity'] * holding['cost_basis']
            pnl = market_value - total_cost
            
            total_core_value += market_value
            total_core_cost += total_cost
            total_core_pnl += pnl

    # Summary Box - "Your Move This Month"
    st.header("🎯 Your Move This Month")
    summary_container = st.container()

    with summary_container:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Total Portfolio Value", f"${total_core_value:,.0f}")
        
        with col2:
            pnl_color = "🟢" if total_core_pnl > 0 else "🔴" if total_core_pnl < 0 else "⚪"
            st.metric(f"{pnl_color} Total P&L", f"${total_core_pnl:,.0f}")
        
        with col3:
            total_capital = st.session_state.monthly_income + st.session_state.cash_on_hand
            long_term_dollars = (st.session_state.long_term_pct / 100) * total_capital
            st.metric("💼 Long-term Allocation", f"${long_term_dollars:,.0f}")
        
        with col4:
            swing_dollars = (st.session_state.swing_trades_pct / 100) * total_capital
            st.metric("⚡ Swing Trade Allocation", f"${swing_dollars:,.0f}")
        
        # Guidance message
        guidance = create_summary_guidance(
            st.session_state.monthly_income, 
            st.session_state.cash_on_hand, 
            st.session_state.real_estate_pct, 
            total_core_pnl
        )
        
        st.info(f"**💡 Guidance:** {guidance}")

    st.markdown("---")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📊 Portfolio Inputs")
        
        # Monthly Construction Income
        monthly_income = st.number_input(
            "Monthly Construction Income ($)",
            min_value=0.0,
            value=st.session_state.monthly_income,
            step=1000.0,
            help="Enter your monthly construction income",
            key="monthly_income_input"
        )
        
        # Update session state
        if monthly_income != st.session_state.monthly_income:
            st.session_state.monthly_income = monthly_income
            save_data()
        
        # Cash on Hand
        cash_on_hand = st.number_input(
            "Cash on Hand ($)",
            min_value=0.0,
            value=st.session_state.cash_on_hand,
            step=1000.0,
            help="Enter your current cash reserves",
            key="cash_on_hand_input"
        )
        
        # Update session state
        if cash_on_hand != st.session_state.cash_on_hand:
            st.session_state.cash_on_hand = cash_on_hand
            save_data()

    with col2:
        st.header("💰 Summary")
        st.metric("Monthly Income", f"${monthly_income:,.0f}")
        st.metric("Cash on Hand", f"${cash_on_hand:,.0f}")
        st.metric("Total Capital", f"${monthly_income + cash_on_hand:,.0f}")

    # Core Holdings Section
    st.header("📈 Core Holdings")
    st.markdown("Add your long-term stock positions")

    # Core holdings input
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.text_input("Ticker", key="core_ticker", placeholder="AAPL")
    with col2:
        quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.01, key="core_quantity", help="Enter fractional shares (e.g., 0.5, 1.25, 2.75)")
    with col3:
        cost_basis = st.number_input("Cost Basis ($)", min_value=0.01, value=150.0, key="core_cost")

    # Add buttons for core holdings
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Add Core Holding", key="add_core"):
            if ticker and quantity > 0 and cost_basis > 0:
                st.session_state.core_holdings.append({
                    'ticker': ticker.upper(),
                    'quantity': quantity,
                    'cost_basis': cost_basis
                })
                save_data()
                st.success(f"Added {ticker.upper()} - {quantity:.4f} shares at ${cost_basis}")

    with col2:
        if st.button("Add Default Tickers", key="add_defaults"):
            # Add default tickers with placeholder values
            for default_ticker in DEFAULT_TICKERS:
                # Check if ticker already exists
                if not any(holding['ticker'] == default_ticker.upper() for holding in st.session_state.core_holdings):
                    st.session_state.core_holdings.append({
                        'ticker': default_ticker.upper(),
                        'quantity': 1.0,
                        'cost_basis': 100.0  # Placeholder cost basis
                    })
            save_data()
            st.success(f"Added default tickers: {', '.join(DEFAULT_TICKERS)}")

    # Display core holdings with live data
    if st.session_state.core_holdings:
        st.subheader("Current Core Holdings")
        
        # Calculate live data for core holdings
        core_data = []
        for holding in st.session_state.core_holdings:
            ticker_symbol = holding['ticker']
            
            # Determine if it's crypto or stock
            if ticker_symbol in ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XLM', 'VET']:
                # Convert to format expected by get_crypto_price
                crypto_symbol = f"{ticker_symbol}-USD"
                current_price = get_crypto_price(crypto_symbol)
            else:
                current_price = get_stock_price(ticker_symbol)
            
            if current_price:
                market_value = holding['quantity'] * current_price
                total_cost = holding['quantity'] * holding['cost_basis']
                unrealized_pnl = market_value - total_cost
                pnl_percentage = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
                
                core_data.append({
                    'Ticker': f"**{ticker_symbol}**",
                    'Quantity': f"**{holding['quantity']:.4f}**",
                    'Cost Basis': f"**${holding['cost_basis']:.2f}**",
                    'Current Price': f"**${current_price:.2f}**",
                    'Market Value': f"**${market_value:,.2f}**",
                    'Unrealized P&L': format_currency_with_color(unrealized_pnl),
                    'P&L %': format_currency_with_color(pnl_percentage, is_percentage=True)
                })
            else:
                core_data.append({
                    'Ticker': f"**{ticker_symbol}**",
                    'Quantity': f"**{holding['quantity']:.4f}**",
                    'Cost Basis': f"**${holding['cost_basis']:.2f}**",
                    'Current Price': "**N/A**",
                    'Market Value': "**N/A**",
                    'Unrealized P&L': "**N/A**",
                    'P&L %': "**N/A**"
                })
        
        core_df = pd.DataFrame(core_data)
        st.dataframe(core_df, use_container_width=True, hide_index=True)
        
        # Remove button
        if st.button("Clear All Core Holdings"):
            st.session_state.core_holdings = []
            save_data()
            st.rerun()

    # Swing Trades Section
    st.header("⚡ Swing Trades")
    st.markdown("Add your options swing trades")

    # Options data viewer and recommendations
    st.subheader("📊 Options Data Explorer & Recommendations")
    options_ticker = st.text_input("Enter ticker to view options data", key="options_ticker", placeholder="SPY")

    if options_ticker:
        options_data = load_option_chain(options_ticker.upper())
        
        if options_data:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📈 Raw Options Data", "🎯 Smart Recommendations", "📊 Analysis"])
            
            with tab1:
                # Select expiration date
                expiration_dates = list(options_data.keys())
                selected_date = st.selectbox("Select expiration date", expiration_dates, key="raw_data_date")
                
                if selected_date:
                    calls = options_data[selected_date]["calls"]
                    puts = options_data[selected_date]["puts"]
                    
                    # Display calls and puts in sub-tabs
                    sub_tab1, sub_tab2 = st.tabs(["📈 Calls", "📉 Puts"])
                    
                    with sub_tab1:
                        if not calls.empty:
                            # Filter and format calls data (handle missing columns like 'delta')
                            base_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'delta']
                            cols = [c for c in base_cols if c in calls.columns]
                            calls_display = calls[cols].copy()
                            rename_map = {
                                'strike': 'Strike',
                                'lastPrice': 'Last Price',
                                'bid': 'Bid',
                                'ask': 'Ask',
                                'volume': 'Volume',
                                'openInterest': 'Open Interest',
                                'impliedVolatility': 'IV',
                                'delta': 'Delta'
                            }
                            calls_display = calls_display.rename(columns=rename_map)
                            calls_display = calls_display.round(4)
                            st.dataframe(calls_display, use_container_width=True)
                        else:
                            st.info("No calls data available")
                    
                    with sub_tab2:
                        if not puts.empty:
                            # Filter and format puts data (handle missing columns like 'delta')
                            base_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'delta']
                            cols = [c for c in base_cols if c in puts.columns]
                            puts_display = puts[cols].copy()
                            rename_map = {
                                'strike': 'Strike',
                                'lastPrice': 'Last Price',
                                'bid': 'Bid',
                                'ask': 'Ask',
                                'volume': 'Volume',
                                'openInterest': 'Open Interest',
                                'impliedVolatility': 'IV',
                                'delta': 'Delta'
                            }
                            puts_display = puts_display.rename(columns=rename_map)
                            puts_display = puts_display.round(4)
                            st.dataframe(puts_display, use_container_width=True)
                        else:
                            st.info("No puts data available")
            
            with tab2:
                st.subheader("🎯 Smart Options Recommendations")
                st.info("""
                **Scoring Criteria:**
                - **Volume/OI Ratio (40%)**: Higher ratio indicates better liquidity
                - **Implied Volatility (30%)**: Lower IV suggests better pricing
                - **Delta (30%)**: Closer to 0.5 indicates balanced risk/reward
                """)
                
                # Get scored recommendations
                try:
                    scored_options = filter_and_score_options(options_data)
                    
                    if not scored_options.empty:
                        # Display top 10 recommendations
                        st.subheader("🏆 Top 10 Recommended Calls")
                        
                        # Format the display
                        display_df = scored_options.head(10).copy()
                        display_df['Strike'] = display_df['strike'].round(2)
                        display_df['Last Price'] = display_df['lastPrice'].round(2)
                        display_df['IV'] = (display_df['IV'] * 100).round(1)
                        display_df['Delta'] = display_df['delta'].round(3)
                        display_df['Score'] = display_df['score'].round(4)
                        
                        # Reorder columns for better display
                        display_df = display_df[['contractSymbol', 'Strike', 'expiration', 'Last Price', 'IV', 'volume', 'openInterest', 'Delta', 'Score']]
                        display_df.columns = ['Contract', 'Strike', 'Expiration', 'Price', 'IV %', 'Volume', 'OI', 'Delta', 'Score']
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                        # Add quick trade buttons for top 3
                        st.subheader("⚡ Quick Add to Swing Trades")
                        col1, col2, col3 = st.columns(3)
                        
                        for i, (_, row) in enumerate(display_df.head(3).iterrows()):
                            with [col1, col2, col3][i]:
                                if st.button(f"Add {row['Contract']}", key=f"quick_add_{i}"):
                                    # Parse expiration date
                                    exp_date = datetime.strptime(row['Expiration'], '%Y-%m-%d').date()
                                    
                                    st.session_state.swing_trades.append({
                                        'ticker': options_ticker.upper(),
                                        'strike_price': row['Strike'],
                                        'expiration_date': exp_date,
                                        'premium_paid': row['Price']
                                    })
                                    save_data()
                                    st.success(f"Added {row['Contract']} to swing trades!")
                                    st.rerun()
                    else:
                        st.warning("No options meet the filtering criteria. Try a different ticker or check the raw data.")
                        
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
            
            with tab3:
                st.subheader("📊 Options Analysis")
                
                # Get current stock price
                current_price = get_stock_price(options_ticker.upper())
                if current_price:
                    st.metric("Current Stock Price", f"${current_price:.2f}")
                    
                    # Analyze options data
                    all_calls = pd.concat([chains["calls"] for chains in options_data.values()])
                    all_puts = pd.concat([chains["puts"] for chains in options_data.values()])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 Calls Analysis")
                        if not all_calls.empty:
                            avg_iv = all_calls['impliedVolatility'].mean() * 100
                            total_volume = all_calls['volume'].sum()
                            total_oi = all_calls['openInterest'].sum()
                            
                            st.metric("Average IV", f"{avg_iv:.1f}%")
                            st.metric("Total Volume", f"{total_volume:,}")
                            st.metric("Total Open Interest", f"{total_oi:,}")
                    
                    with col2:
                        st.subheader("📉 Puts Analysis")
                        if not all_puts.empty:
                            avg_iv = all_puts['impliedVolatility'].mean() * 100
                            total_volume = all_puts['volume'].sum()
                            total_oi = all_puts['openInterest'].sum()
                            
                            st.metric("Average IV", f"{avg_iv:.1f}%")
                            st.metric("Total Volume", f"{total_volume:,}")
                            st.metric("Total Open Interest", f"{total_oi:,}")
        else:
            st.warning(f"No options data available for {options_ticker.upper()}")

    # Swing trades input
    st.subheader("Add New Swing Trade")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        swing_ticker = st.text_input("Ticker", key="swing_ticker", placeholder="SPY")
    with col2:
        strike_price = st.number_input("Strike Price ($)", min_value=0.0, value=400.0, key="swing_strike")
    with col3:
        expiration_date = st.date_input("Expiration Date", key="swing_expiry")
    with col4:
        premium_paid = st.number_input("Premium Paid ($)", min_value=0.0, value=5.0, key="swing_premium")

    # Add button for swing trades
    if st.button("Add Swing Trade", key="add_swing"):
        if swing_ticker and strike_price > 0 and premium_paid > 0:
            st.session_state.swing_trades.append({
                'ticker': swing_ticker.upper(),
                'strike_price': strike_price,
                'expiration_date': expiration_date,
                'premium_paid': premium_paid
            })
            save_data()
            st.success(f"Added {swing_ticker.upper()} swing trade")

    # Display swing trades with expiration data
    if st.session_state.swing_trades:
        st.subheader("Current Swing Trades")
        
        # Calculate days until expiration for swing trades
        swing_data = []
        for trade in st.session_state.swing_trades:
            days_to_expiry = days_until_expiration(trade['expiration_date'])
            
            # Color code the status
            if days_to_expiry <= 7:
                status = "⚠️ **Expiring Soon**"
            elif days_to_expiry > 0:
                status = "✅ **Active**"
            else:
                status = "❌ **Expired**"
            
            swing_data.append({
                'Ticker': f"**{trade['ticker']}**",
                'Strike Price': f"**${trade['strike_price']:.2f}**",
                'Expiration Date': f"**{trade['expiration_date'].strftime('%Y-%m-%d')}**",
                'Premium Paid': f"**${trade['premium_paid']:.2f}**",
                'Days to Expiry': f"**{days_to_expiry}**",
                'Status': status
            })
        
        swing_df = pd.DataFrame(swing_data)
        st.dataframe(swing_df, use_container_width=True, hide_index=True)
        
        # Remove button
        if st.button("Clear All Swing Trades"):
            st.session_state.swing_trades = []
            save_data()
            st.rerun()

    # Target Allocations Section
    st.header("🎯 Target Allocations")
    st.markdown("Set your target allocation percentages (must total 100%)")

    # Allocation sliders
    col1, col2, col3 = st.columns(3)

    with col1:
        long_term_pct = st.slider(
            "Long-term Plays (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.long_term_pct,
            key="long_term_slider"
        )
        if long_term_pct != st.session_state.long_term_pct:
            st.session_state.long_term_pct = long_term_pct
            save_data()

    with col2:
        swing_trades_pct = st.slider(
            "Swing Trades (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.swing_trades_pct,
            key="swing_slider"
        )
        if swing_trades_pct != st.session_state.swing_trades_pct:
            st.session_state.swing_trades_pct = swing_trades_pct
            save_data()

    with col3:
        real_estate_pct = st.slider(
            "Real Estate Savings (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.real_estate_pct,
            key="real_estate_slider"
        )
        if real_estate_pct != st.session_state.real_estate_pct:
            st.session_state.real_estate_pct = real_estate_pct
            save_data()

    # Calculate total allocation
    total_allocation = long_term_pct + swing_trades_pct + real_estate_pct

    # Display allocation summary
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Allocation Summary")
        st.write(f"**Long-term Plays:** {long_term_pct}%")
        st.write(f"**Swing Trades:** {swing_trades_pct}%")
        st.write(f"**Real Estate Savings:** {real_estate_pct}%")

    with col2:
        if total_allocation == 100:
            st.success(f"✅ Total: {total_allocation}%")
        elif total_allocation < 100:
            st.warning(f"⚠️ Total: {total_allocation}% (Under 100%)")
        else:
            st.error(f"❌ Total: {total_allocation}% (Over 100%)")

    # Calculate dollar allocations
    total_capital = monthly_income + cash_on_hand
    long_term_dollars = (long_term_pct / 100) * total_capital
    swing_trades_dollars = (swing_trades_pct / 100) * total_capital
    real_estate_dollars = (real_estate_pct / 100) * total_capital

    # Results Section
    st.header("📋 Results")
    st.markdown("---")

    # Create three columns for results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🎯 Recommended Deployment This Month")
        
        if total_allocation == 100:
            st.success("**Allocation Recommendations:**")
            st.write(f"**Long-term Plays:** ${long_term_dollars:,.0f}")
            st.write(f"**Swing Trades:** ${swing_trades_dollars:,.0f}")
            st.write(f"**Real Estate Savings:** ${real_estate_dollars:,.0f}")
            
            st.info("**Next Steps:**")
            st.write("• Review current positions before deploying new capital")
            st.write("• Consider market conditions for swing trade timing")
            st.write("• Set up automatic transfers for real estate savings")
        else:
            st.warning("Please adjust allocation percentages to total 100% for recommendations")

    with col2:
        st.subheader("📊 Position Health")
        
        if st.session_state.core_holdings or st.session_state.swing_trades:
            # Calculate total portfolio metrics
            total_core_value = 0
            total_core_cost = 0
            total_core_pnl = 0
            
            for holding in st.session_state.core_holdings:
                ticker_symbol = holding['ticker']
                if ticker_symbol in ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XLM', 'VET']:
                    # Convert to format expected by get_crypto_price
                    crypto_symbol = f"{ticker_symbol}-USD"
                    current_price = get_crypto_price(crypto_symbol)
                else:
                    current_price = get_stock_price(ticker_symbol)
                
                if current_price:
                    market_value = holding['quantity'] * current_price
                    total_cost = holding['quantity'] * holding['cost_basis']
                    pnl = market_value - total_cost
                    
                    total_core_value += market_value
                    total_core_cost += total_cost
                    total_core_pnl += pnl
            
            if total_core_cost > 0:
                portfolio_pnl_pct = (total_core_pnl / total_core_cost) * 100
                st.metric("Total Portfolio Value", f"${total_core_value:,.0f}")
                st.metric("Total Unrealized P&L", f"${total_core_pnl:,.0f}")
                st.metric("Portfolio P&L %", f"{portfolio_pnl_pct:.1f}%")
                
                # Color code the P&L
                if total_core_pnl > 0:
                    st.success("📈 Portfolio is profitable!")
                elif total_core_pnl < 0:
                    st.error("📉 Portfolio is at a loss")
                else:
                    st.info("📊 Portfolio is at breakeven")
        else:
            st.info("No positions to analyze. Add some holdings to see portfolio health.")

    with col3:
        st.subheader("🏠 Real Estate War Chest")
        
        # Calculate real estate savings progress
        monthly_real_estate = (real_estate_pct / 100) * monthly_income
        current_real_estate = (real_estate_pct / 100) * cash_on_hand
        
        st.metric("Monthly Real Estate Savings", f"${monthly_real_estate:,.0f}")
        st.metric("Current Real Estate Allocation", f"${current_real_estate:,.0f}")
        st.metric("Total Real Estate Capital", f"${monthly_real_estate + current_real_estate:,.0f}")
        
        # Example down payment calculation (assuming 20% down payment)
        example_property_value = 500000  # $500k example property
        down_payment_needed = example_property_value * 0.20
        months_to_down_payment = down_payment_needed / monthly_real_estate if monthly_real_estate > 0 else 0
        
        st.info("**Example Timeline:**")
        st.write(f"• Target property: ${example_property_value:,.0f}")
        st.write(f"• Down payment needed: ${down_payment_needed:,.0f}")
        st.write(f"• Months to save: {months_to_down_payment:.1f}")

    # Footer
    st.markdown("---")
    st.markdown("*Capital Allocator Dashboard - Built with Streamlit*")

    # Debug information (can be removed later)
    if st.checkbox("Show Debug Info"):
        st.write("Session State:", st.session_state)
