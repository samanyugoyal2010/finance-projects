import json
import yfinance as yf

WATCHLIST = 'watchlist.json'

def save_watchlist(tickers):
    with open(WATCHLIST, 'w') as f:
        json.dump(tickers, f)

def load_watchlist():
    try:
        with open(WATCHLIST, 'r') as f:
            tickers = json.loads(f)
        return tickers
    except FileNotFoundError as e:
        return []

def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info  # Fetch stock information
        data = stock.history(period='1d')
        if not data.empty:
            row = data.iloc[-1]
            price = row['Close']
            high = row['High']
            low = row['Low']
            volume = row['Volume']
            prev_close = stock_info.get('previousClose', price)  # Use stock_info here
            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0  # Fixed percentage calculation
            data_time = row.name.strftime("%Y-%m-%d %H:%M:%S")

            return {
                'ticker': ticker,
                'price': f'${price:.2f}',
                'date_time': data_time,
                'change': change,
                'change_pct': change_pct,
                'high': f'${high:.2f}',
                'low': f'${low:.2f}',
                'volume': f'{volume:,}'
            }
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None
    




                     