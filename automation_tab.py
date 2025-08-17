import math
from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st
import yaml
import yfinance as yf

# ---------- Caching helpers ----------
@st.cache_data(ttl=300)
def _history(ticker: str, period="6mo", interval="1d") -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.rename(columns=str.lower)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def _get_stock_price(ticker: str) -> float:
    try:
        px = yf.Ticker(ticker).history(period="1d")["Close"]
        return float(px.iloc[-1]) if len(px) else 0.0
    except Exception:
        return 0.0

# If your app.py already has get_crypto_price / get_stock_price, you can import and use those instead.

# ---------- Simple indicators ----------
def _sma(series: pd.Series, window: int) -> float:
    if len(series) < window:
        return float("nan")
    return float(series.rolling(window).mean().iloc[-1])

def _rsi(series: pd.Series, window: int = 14) -> float:
    if len(series) < window + 1:
        return 50.0
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean().replace(0, 1e-9)
    rs = roll_up / roll_down
    return float(100.0 - (100.0 / (1.0 + rs.iloc[-1])))

# ---------- Load SOP ----------
def _load_strategy() -> dict:
    with open("strategy.yaml", "r") as f:
        return yaml.safe_load(f) or {}

# ---------- Signals ----------
def _key_for(t: str) -> str:
    # map 'ES=F' -> 'es_f', 'BTC-USD' -> 'btc_usd'
    return t.lower().replace("=", "_").replace("-", "_")

def _signal_for(ticker: str, rules: dict) -> dict:
    df = _history(ticker)
    if df.empty or "close" not in df:
        return {"ticker": ticker, "action": "HOLD", "confidence": 0.0, "reason": "no data"}

    close = df["close"]
    score = 0
    reasons = []

    for cond in rules.get("buy_if", []):
        t = cond.get("type")
        if t == "price_above_sma":
            w = int(cond["window"])
            sma = _sma(close, w)
            if not math.isnan(sma) and close.iloc[-1] > sma:
                score += 1
                reasons.append(f"price>{w}SMA")
        elif t == "rsi_below":
            w = int(cond.get("window", 14))
            thr = float(cond.get("threshold", 35))
            rsi = _rsi(close, w)
            if rsi < thr:
                score += 1
                reasons.append(f"RSI{w}<{thr}")

    # simple mapping
    if score > 0:
        return {"ticker": ticker, "action": "BUY", "confidence": min(1.0, score / 2), "reason": ", ".join(reasons)}
    return {"ticker": ticker, "action": "HOLD", "confidence": 0.0, "reason": ", ".join(reasons) or "neutral"}

# ---------- Sizing ----------
def _position_targets(
    portfolio_value: float,
    cash_on_hand: float,
    long_term_pct: float,
    weights: Dict[str, float],
    prices: Dict[str, float],
    current_values: Dict[str, float],
    risk: dict,
) -> Dict[str, float]:
    total_deploy = max(0.0, cash_on_hand)
    alloc_long = total_deploy * (long_term_pct / 100.0)

    target = {t: alloc_long * (weights.get(t, 0.0)) for t in weights.keys()}

    max_pos_val = float(risk.get("max_position_pct", 0.25)) * max(1.0, portfolio_value)
    max_buy = float(risk.get("max_buy_usd", 2500))
    min_cash_reserve = float(risk.get("min_cash_reserve_usd", 5000))

    # clamp by position cap & max buy
    for t in list(target.keys()):
        px = float(prices.get(t, 0.0) or 0.0)
        cur_val = float(current_values.get(t, 0.0) or 0.0)
        room = max(0.0, max_pos_val - cur_val)
        target[t] = min(target[t], max_buy, room)
        if px <= 0:
            target[t] = 0.0

    # ensure cash buffer
    total_buys = sum(target.values())
    spare = max(0.0, cash_on_hand - min_cash_reserve)
    if total_buys > spare and total_buys > 0:
        scale = spare / total_buys
        target = {t: v * scale for t, v in target.items()}

    return target

def _build_tickets(signals: List[dict], target_dollars: Dict[str, float], prices: Dict[str, float]) -> List[dict]:
    tickets = []
    for s in signals:
        if s["action"] != "BUY":
            continue
        t = s["ticker"]
        dollars = float(target_dollars.get(t, 0.0))
        px = float(prices.get(t, 0.0))
        if px <= 0 or dollars <= 0:
            continue
        # whole shares for equities, 3dp for crypto
        qty = dollars / px
        qty = round(qty, 3) if t.endswith("-USD") else int(qty)
        if qty <= 0:
            continue
        tickets.append({
            "ticker": t,
            "action": "BUY",
            "qty": qty,
            "est_price": px,
            "dollars": dollars,
            "reason": s.get("reason", ""),
        })
    return tickets

# ---------- UI ----------
def render_automation_tab():
    st.markdown("## 🤖 Automation (SOP)")
    st.caption("Loads SOP from strategy.yaml, fetches prices, generates signals, and sizes buys within risk guards.")

    strat = _load_strategy()
    universe = strat.get("universe", [])
    weights = strat.get("weights", {})
    risk = strat.get("risk", {})
    long_term_pct = float(strat.get("allocations", {}).get("long_term_pct", 40))

    # Pull state from the main app if present
    monthly_income = float(st.session_state.get("monthly_income", 0) or 0)
    cash_on_hand = float(st.session_state.get("cash_on_hand", 0) or 0)
    portfolio_value = float(st.session_state.get("total_portfolio_value", 0) or 0)

    st.write("**Universe**:", ", ".join(universe) if universe else "—")
    st.write("**Cash on hand**: $", f"{cash_on_hand:,.2f}", " | **Portfolio**: $", f"{portfolio_value:,.2f}")

    # Prices
    prices = {t: _get_stock_price(t) for t in universe}
    st.dataframe(pd.DataFrame([{"Ticker": t, "Price": prices[t]} for t in universe]),
                 use_container_width=True, hide_index=True)

    # Current values from your core holdings table if you have it
    current_values = {}
    core_df = st.session_state.get("core_holdings_df")
    if isinstance(core_df, pd.DataFrame) and not core_df.empty:
        for _, r in core_df.iterrows():
            t = str(r.get("Ticker", "")).upper()
            qty = float(r.get("Quantity", 0) or 0)
            px = prices.get(t, 0.0)
            current_values[t] = qty * px
    else:
        current_values = {t: 0.0 for t in universe}

    # Signals
    rules = strat.get("sop", {})
    signals = []
    for t in universe:
        key = _key_for(t)
        sig = _signal_for(t, rules.get(key, {"buy_if": []}))
        signals.append(sig)
    st.write("### 📡 Signals")
    st.dataframe(pd.DataFrame(signals), use_container_width=True, hide_index=True)

    # Targets + Tickets
    targets = _position_targets(
        portfolio_value=portfolio_value,
        cash_on_hand=cash_on_hand,
        long_term_pct=long_term_pct,
        weights=weights,
        prices=prices,
        current_values=current_values,
        risk=risk,
    )
    tickets = _build_tickets(signals, targets, prices)

    st.write("### 🧾 Tickets (planned)")
    if tickets:
        df_tix = pd.DataFrame(tickets)
        st.dataframe(df_tix, use_container_width=True, hide_index=True)
        clip = " | ".join([f"{t['ticker']}: BUY {t['qty']} @ MKT (~${t['dollars']:,.0f})" for t in tickets])
        st.text_area("Copy these orders:", value=clip, height=90)
    else:
        st.info("No BUY tickets generated at current prices/rules/cash.")

# Back-compat alias if some code calls the old name
def render_automation():
    return render_automation_tab()
