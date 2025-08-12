# 📈 Mid-Term Options Screener

A dedicated, professional-grade options screening tool built with Streamlit for identifying high-quality mid-term options contracts.

## Overview

The Mid-Term Options Screener is a focused application designed specifically for options traders who want to quickly identify the best options contracts based on multiple criteria including liquidity, volatility, and risk metrics.

## Features

### 🎯 Core Functionality
- **Real-time Options Data**: Live options chains from Yahoo Finance
- **Intelligent Scoring**: AI-powered contract ranking based on multiple criteria
- **Advanced Filtering**: Customizable filters for volume, open interest, IV, and delta
- **Professional Analysis**: Comprehensive metrics and statistical analysis

### 📊 Screening Criteria
- **Volume/OI Ratio (40%)**: Higher ratio indicates better liquidity
- **Implied Volatility (30%)**: Lower IV suggests better pricing
- **Delta (30%)**: Closer to 0.5 indicates balanced risk/reward

### 🔧 Filtering Options
- **Minimum Volume**: Filter by trading volume
- **Minimum Open Interest**: Filter by open interest
- **Maximum IV**: Filter by implied volatility percentage
- **Minimum Delta**: Filter by delta value
- **Out-of-the-money calls only**: Focus on growth potential

### 📈 Analysis Features
- **Top 20 Ranked Contracts**: Automatically sorted by composite score
- **Summary Statistics**: Key metrics for filtered contracts
- **Expiration Analysis**: Distribution across expiration dates
- **Advanced Charts**: IV, Delta, and Price distributions

## Installation

1. Ensure you have the required dependencies:
   ```bash
   pip install streamlit pandas yfinance
   ```

2. Run the options screener:
   ```bash
   streamlit run options_screener.py
   ```

## Usage

### Basic Screening
1. **Enter Ticker**: Type a stock symbol (e.g., PLTR, AAPL, TSLA)
2. **Adjust Filters**: Set your preferred volume, OI, IV, and delta thresholds
3. **Load Data**: Click "Load & Analyze Options" to fetch and score contracts
4. **Review Results**: View the top 20 ranked contracts with detailed metrics

### Advanced Analysis
- **Summary Statistics**: View total contracts, average IV, score, and delta
- **Expiration Analysis**: See distribution of contracts across expiration dates
- **Distribution Charts**: Analyze IV, delta, and price distributions

### Filter Settings
- **Min Volume**: Minimum trading volume (default: 10)
- **Min Open Interest**: Minimum open interest (default: 50)
- **Max IV %**: Maximum implied volatility percentage (default: 100%)
- **Min Delta**: Minimum delta value (default: 0.1)

## Scoring Algorithm

The screener uses a sophisticated scoring algorithm that combines:

```python
score = (volume/OI ratio × 0.4) + (1 - IV × 0.3) + (1 - |0.5 - delta| × 0.3)
```

### Scoring Components:
- **Volume/OI Ratio (40%)**: Measures liquidity and market interest
- **Implied Volatility (30%)**: Lower IV = better pricing, less premium decay
- **Delta (30%)**: Closer to 0.5 = balanced risk/reward profile

## Output Columns

The results table includes:
- **Contract**: Option contract symbol
- **Strike**: Strike price
- **Expiration**: Expiration date
- **Price**: Last traded price
- **IV %**: Implied volatility percentage
- **Volume**: Trading volume
- **OI**: Open interest
- **Vol/OI**: Volume to open interest ratio
- **Delta**: Delta value
- **Score**: Composite score (higher = better)

## Supported Tickers

All major stock tickers with options available on Yahoo Finance, including:
- **Large Caps**: AAPL, MSFT, GOOGL, AMZN, TSLA
- **ETFs**: SPY, QQQ, IWM, TLT
- **Growth Stocks**: PLTR, NVDA, AMD, META
- **And many more...**

## Performance Features

- **Cached Data**: Efficient data loading with Streamlit caching
- **Real-time Updates**: Live market data from Yahoo Finance
- **Error Handling**: Graceful handling of API failures
- **Responsive UI**: Fast loading and smooth interactions

## Use Cases

### Swing Trading
- Identify high-quality options for swing trades
- Find contracts with good liquidity and reasonable pricing
- Screen for balanced risk/reward profiles

### Research
- Analyze options market conditions
- Compare contracts across different expirations
- Study IV and delta distributions

### Portfolio Management
- Find suitable options for portfolio hedging
- Identify opportunities for covered calls
- Screen for potential income-generating trades

## Technical Details

### Data Sources
- **Options Data**: Yahoo Finance API via yfinance
- **Stock Prices**: Real-time price feeds
- **Market Data**: Volume, open interest, and Greeks

### Performance Optimizations
- **Caching**: Reduces API calls and improves speed
- **Filtering**: Efficient data processing
- **Memory Management**: Optimized for large datasets

## Comparison with Main Dashboard

| Feature | Options Screener | Main Dashboard |
|---------|------------------|----------------|
| **Focus** | Options-only | Portfolio management |
| **Complexity** | Simple, focused | Comprehensive |
| **Use Case** | Options research | Full portfolio tracking |
| **Data** | Options chains | Stocks, crypto, options |
| **Analysis** | Contract scoring | Portfolio analytics |

## Future Enhancements

- **Puts Screening**: Add puts analysis and scoring
- **Strategy Builder**: Combine multiple contracts
- **Backtesting**: Historical performance analysis
- **Alerts**: Price and IV alerts
- **Export**: CSV/Excel export functionality

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- yfinance 0.2.0+

## File Structure

```
Trading-bot-website/
├── app.py                    # Main Capital Allocator Dashboard
├── options_screener.py       # Dedicated Options Screener
├── requirements.txt          # Python dependencies
├── README.md                # Main dashboard documentation
├── OPTIONS_SCREENER_README.md # This file
└── portfolio_data.json      # Saved portfolio data
```

## Running Both Apps

You can run both applications simultaneously:

```bash
# Terminal 1 - Main Dashboard
streamlit run app.py

# Terminal 2 - Options Screener
streamlit run options_screener.py
```

The main dashboard will run on `http://localhost:8501` and the options screener on `http://localhost:8502`.

---

*Mid-Term Options Screener - Professional options analysis made simple*
