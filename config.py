import os
import streamlit as st

# Environment label (prod by default)
APP_ENV = os.getenv("APP_ENV", "prod")

# Centralized defaults
DEFAULT_TICKERS = ["PLTR", "CRWD", "BTC-USD", "XRP-USD"]
ALLOCATION_RULES = {
    "long_term_pct": 40,
    "swing_pct": 30,
    "real_estate_pct": 30,
}

def get_secret(path: str, default: str | None = None):
    """
    Read nested secrets with 'section.key' syntax from st.secrets,
    then env vars as a fallback, else default.
    Example: get_secret("api.coinapi_key")
    """
    try:
        node = st.secrets
        for part in path.split("."):
            node = node[part]
        return node
    except Exception:
        env_key = path.replace(".", "_").upper()  # api.coinapi_key -> API_COINAPI_KEY
        return os.getenv(env_key, default)

# example future use: coinapi_key = get_secret("api.coinapi_key")
