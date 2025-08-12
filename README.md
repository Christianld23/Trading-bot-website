# Capital Allocator Dashboard

A Streamlit-based dashboard for optimizing capital allocation across different investment strategies with live market data integration, persistent data storage, intelligent guidance, real-time options analysis, and AI-powered options recommendations.

## Features

- **Portfolio Inputs**: Monthly construction income and cash on hand tracking
- **Core Holdings**: Add and manage long-term stock positions with live price updates
- **Swing Trades**: Track options trades with strike prices, expiration dates, and days to expiry
- **Options Data Explorer**: Real-time options chain data with calls and puts analysis
- **AI-Powered Options Recommendations**: Intelligent scoring and filtering of options contracts
- **Target Allocations**: Set allocation percentages for different investment strategies
- **Live Data Integration**: Real-time stock prices via yfinance and crypto prices via CoinGecko API
- **Portfolio Analytics**: Calculate market values, unrealized gains/losses, and portfolio health
- **Allocation Recommendations**: Dollar-based deployment recommendations based on your targets
- **Real Estate Planning**: Track savings progress and calculate timelines for property investments
- **Data Persistence**: Save and load portfolio data using JSON file storage
- **Smart Guidance**: Personalized recommendations and milestone tracking
- **Enhanced Formatting**: Color-coded tables, bold text for key metrics, and clear visual hierarchy

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

To run the Capital Allocator Dashboard:

```bash
python -m streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`.

## Usage

1. **Your Move This Month**: View the summary box at the top for key metrics and personalized guidance
2. **Enter Portfolio Data**: Input your monthly construction income and current cash on hand
3. **Add Core Holdings**: Enter ticker symbols, quantities, and cost basis for long-term positions
   - Supports both stocks (via yfinance) and cryptocurrencies (via CoinGecko)
   - Automatically calculates current market value and unrealized P&L with color coding
4. **Explore Options Data**: Use the Options Data Explorer to view real-time options chains
   - **Raw Options Data**: Browse calls and puts by expiration date with detailed metrics
   - **Smart Recommendations**: AI-powered scoring of options contracts based on multiple criteria
   - **Options Analysis**: Comprehensive analysis of IV, volume, and open interest
   - Quick-add buttons for top recommended options to your swing trades
5. **Track Swing Trades**: Add options trades with strike prices, expiration dates, and premiums
   - Shows days until expiration and status indicators with color coding
   - Use options data to make informed trade decisions
6. **Set Target Allocations**: Use the sliders to set your desired allocation percentages
7. **Save/Load Data**: Use the sidebar buttons to persist your portfolio data between sessions
8. **View Live Results**: 
   - **Recommended Deployment**: Dollar amounts for each allocation category
   - **Position Health**: Portfolio performance metrics and P&L analysis
   - **Real Estate War Chest**: Savings progress and investment timeline

## Data Persistence

The app automatically saves your data to `portfolio_data.json` when you:
- Add or remove holdings/trades
- Change allocation percentages
- Update income or cash amounts

You can also manually save/load data using the buttons in the sidebar.

## Supported Assets

### Stocks
All major stock tickers supported via Yahoo Finance (yfinance)

### Cryptocurrencies
- BTC (Bitcoin)
- ETH (Ethereum)
- XRP (Ripple)
- ADA (Cardano)
- DOT (Polkadot)
- LINK (Chainlink)
- LTC (Litecoin)
- BCH (Bitcoin Cash)
- XLM (Stellar)
- VET (VeChain)

### Options Data
- Real-time options chains for all major stocks
- Calls and puts data with expiration dates
- Strike prices, bid/ask spreads, volume, and open interest
- Implied volatility, delta, and other Greeks
- Cached data for improved performance

## AI-Powered Options Recommendations

The dashboard includes an intelligent options scoring system that analyzes contracts based on:

### Scoring Criteria
- **Volume/OI Ratio (40%)**: Higher ratio indicates better liquidity and market interest
- **Implied Volatility (30%)**: Lower IV suggests better pricing and less premium decay
- **Delta (30%)**: Closer to 0.5 indicates balanced risk/reward profile

### Filtering Criteria
- **Out-of-the-money calls only**: Focuses on growth potential
- **Reasonable IV**: Excludes contracts with extreme volatility (>100%)
- **Minimum liquidity**: Volume > 10 and Open Interest > 50
- **Quality scoring**: Composite score based on multiple factors

### Features
- **Top 10 Recommendations**: Automatically ranked by score
- **Quick Add Buttons**: One-click addition of top 3 recommendations to swing trades
- **Detailed Analysis**: IV, volume, open interest, and delta metrics
- **Real-time Updates**: Recommendations update with live market data

## Visual Features

### Color Coding
- 🟢 **Green**: Positive gains, active trades, profitable positions
- 🔴 **Red**: Losses, expired trades, negative performance
- ⚪ **White**: Neutral/breakeven positions
- ⚠️ **Warning**: Expiring soon trades

### Formatting
- **Bold text** for key numbers and metrics
- Clear section headers with emojis
- Organized tables with proper alignment
- Status indicators for trade expiration

## Current Status

This is Step 5 of the development process. The app now includes:
- ✅ Live data fetching for stocks and cryptocurrencies
- ✅ Real-time portfolio calculations and P&L tracking
- ✅ Allocation recommendations based on target percentages
- ✅ Position health monitoring with expiration tracking
- ✅ Real estate savings planning and timeline calculations
- ✅ Data persistence with JSON file storage
- ✅ Enhanced visual formatting with color coding
- ✅ Smart guidance system with personalized recommendations
- ✅ Modular code structure for easy expansion
- ✅ Real-time options data explorer with calls and puts analysis
- ✅ AI-powered options scoring and intelligent recommendations
- ✅ Quick-add functionality for recommended options trades

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- yfinance 0.2.0+
- requests 2.31.0+

## Data Sources

- **Stock Prices**: Yahoo Finance API via yfinance
- **Cryptocurrency Prices**: CoinGecko Public API
- **Options Data**: Yahoo Finance Options API via yfinance
- **Real-time Updates**: Data refreshes on each page interaction
- **Local Storage**: JSON file for persistent data

## File Structure

```
Trading-bot-website/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── portfolio_data.json   # Saved portfolio data (created automatically)
└── .git/                 # Git repository
```

## Options Data Features

The Options Data Explorer provides:
- **Real-time options chains** for any stock ticker
- **Expiration date selection** to view specific timeframes
- **Calls and puts data** in separate tabs for easy analysis
- **Key metrics** including strike price, last price, bid/ask, volume, and open interest
- **Implied volatility and delta** for advanced options analysis
- **Cached data** for improved performance and reduced API calls
- **Error handling** for tickers without options data
- **AI-powered recommendations** based on liquidity, IV, and risk metrics
- **Quick-add functionality** for seamless trade execution 