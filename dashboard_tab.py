# dashboard_tab.py
from __future__ import annotations
import pandas as pd
import streamlit as st
import yfinance as yf

st.cache_data.clear  # noop to quiet linters; real clear is called from app via button if you have one.

@st.cache_data(ttl=300)
def _get_last_close(ticker: str) -> float | None:
    """Fetch last close for any ticker supported by Yahoo (stocks/ETFs/crypto)."""
    try:
        df = yf.Ticker(ticker).history(period="1d")
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except Exception:
        return None

def _default_holdings() -> pd.DataFrame:
    # Only used the first time; editable afterwards.
    return pd.DataFrame(
        [
            {"Ticker": "PLTR", "Quantity": 10.0, "Cost Basis": 14.50},
            {"Ticker": "CRWD", "Quantity": 5.0, "Cost Basis": 180.00},
            {"Ticker": "BTC-USD", "Quantity": 0.05, "Cost Basis": 40000.00},
            {"Ticker": "XRP-USD", "Quantity": 200.0, "Cost Basis": 0.55},
        ]
    )

def _compute_metrics(rows: pd.DataFrame) -> pd.DataFrame:
    out_rows = []
    for _, r in rows.iterrows():
        ticker = str(r.get("Ticker", "")).strip().upper()
        try:
            qty = float(r.get("Quantity", 0) or 0)
            cost = float(r.get("Cost Basis", 0) or 0)
        except Exception:
            qty, cost = 0.0, 0.0

        price = _get_last_close(ticker) if ticker else None
        if price and qty is not None:
            market_val = qty * price
            cost_val = qty * cost
            pnl = market_val - cost_val
            pnl_pct = (pnl / cost_val * 100.0) if cost_val else 0.0
        else:
            market_val = None
            pnl = None
            pnl_pct = None

        out_rows.append(
            {
                "Ticker": ticker,
                "Quantity": qty,
                "Cost Basis": cost,
                "Market Price": price,
                "Market Value": market_val,
                "P&L": pnl,
                "P&L %": pnl_pct,
            }
        )
    return pd.DataFrame(out_rows)

def render_dashboard():
    # safe fallback if config import ever fails
    try:
        from config import ALLOCATION_RULES
        default_long = int(ALLOCATION_RULES.get("long_term_pct", 40))
        default_swing = int(ALLOCATION_RULES.get("swing_pct", 30))
        default_re = int(ALLOCATION_RULES.get("real_estate_pct", 30))
    except Exception:
        default_long, default_swing, default_re = 40, 30, 30

    # ---------- LEFT CONTROL PANEL (restored) ----------
    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown("### ⚙️ Portfolio Inputs")

        monthly_income = st.number_input(
            "Monthly Construction Income ($)",
            min_value=0.0,
            value=float(st.session_state.get("monthly_income", 10000.0)),
            step=100.0,
            format="%.2f",
        )
        cash_on_hand = st.number_input(
            "Cash on Hand ($)",
            min_value=0.0,
            value=float(st.session_state.get("cash_on_hand", 50000.0)),
            step=100.0,
            format="%.2f",
        )

        st.markdown("### 🎯 Target Allocations")

        long_pct = st.slider(
            "Long-term Plays (%)", 0, 100, int(st.session_state.get("alloc_long", default_long))
        )
        swing_pct = st.slider(
            "Swing Trades (%)", 0, 100, int(st.session_state.get("alloc_swing", default_swing))
        )
        re_pct = st.slider(
            "Real Estate Savings (%)", 0, 100, int(st.session_state.get("alloc_re", default_re))
        )

        total_pct = long_pct + swing_pct + re_pct
        if total_pct != 100:
            st.warning(f"Allocations total **{total_pct}%**. Adjust to equal **100%**.")

        # persist to session_state for other tabs/modules
        st.session_state["monthly_income"] = monthly_income
        st.session_state["cash_on_hand"] = cash_on_hand
        st.session_state["alloc_long"] = long_pct
        st.session_state["alloc_swing"] = swing_pct
        st.session_state["alloc_re"] = re_pct

        st.markdown("### 💰 Summary")
        st.metric("Monthly Income", f"${monthly_income:,.0f}")
        st.metric("Cash on Hand", f"${cash_on_hand:,.0f}")
        st.metric("Total Capital", f"${(monthly_income + cash_on_hand):,.0f}")

    # ---------- RIGHT SIDE (keep your existing holdings/results below this) ----------
    with col_right:
        st.markdown("### 📈 Core Holdings")
        
        # ---------- Editable Portfolio Holdings ----------
        st.subheader("💼 Portfolio Holdings")

    if "holdings" not in st.session_state:
        st.session_state["holdings"] = _default_holdings()

    edited = st.data_editor(
        st.session_state["holdings"],
        num_rows="dynamic",
        use_container_width=True,
        key="holdings_editor",
        column_config={
            "Ticker": st.column_config.TextColumn(help="e.g., AAPL, SPY, BTC-USD, ETH-USD"),
            "Quantity": st.column_config.NumberColumn(min_value=0.0, step=0.001, format="%.6f"),
            "Cost Basis": st.column_config.NumberColumn(min_value=0.0, step=0.01, format="%.4f"),
        },
    )

    # Persist user edits in session
    st.session_state["holdings"] = edited

    # ---------- Live Prices & PnL ----------
    results_df = _compute_metrics(edited)
    if not results_df.empty:
        # Save for other tabs if needed
        st.session_state["core_holdings_df"] = results_df.copy()

        # Nice number formatting
        fmt = results_df.copy()
        for col in ("Market Price", "Market Value", "P&L"):
            if col in fmt.columns:
                fmt[col] = fmt[col].map(lambda v: f"${v:,.2f}" if pd.notna(v) else "—")
        if "P&L %" in fmt.columns:
            fmt["P&L %"] = fmt["P&L %"].map(lambda v: f"{v:,.2f}%" if pd.notna(v) else "—")

        st.dataframe(fmt, use_container_width=True, hide_index=True)
    else:
        st.info("Add tickers to begin calculating live values.")
