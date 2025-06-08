import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import joblib
from concurrent.futures import ProcessPoolExecutor
import warnings
warnings.filterwarnings('ignore')

def get_sp500_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3650)
    return yf.download('^GSPC', start=start_date, end=end_date)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ma(data, window):
    return data.rolling(window=window).mean()

def calculate_volatility(data, window):
    return data.rolling(window=window).std()

def prepare_features(df):
    # Calculate all features first
    df['Returns'] = df['Close'].pct_change()
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    df['RSI'] = calculate_rsi(df['Close'])
    
    # Create target variable (next day's return)
    df['Target'] = df['Returns'].shift(-1)
    
    # Drop all NaN values after all calculations are done
    return df.dropna()

def train_model_parallel(X_train, y_train, n_estimators=1000):
    # Create multiple Random Forest models in parallel
    n_jobs = -1  # Use all available CPU cores
    chunk_size = n_estimators // 4
    
    models = []
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(4):
            model = RandomForestRegressor(
                n_estimators=chunk_size,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42 + i,
                n_jobs=2  # Use 2 cores per model
            )
            model.fit(X_train, y_train)
            models.append(model)
    
    return models

def train():
    print("Fetching S&P 500 data...")
    sp500_data = get_sp500_data()
    
    print("Preparing features...")
    df = prepare_features(sp500_data)
    
    features = ['Returns', 'MA5', 'MA20', 'MA50', 'Volatility', 'RSI']
    X = df[features]
    y = df['Target']
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training models in parallel...")
    models = train_model_parallel(X_train_scaled, y_train)
    
    print("Saving models and scaler...")
    joblib.dump(models, 'data/models.joblib')
    joblib.dump(scaler, 'data/scaler.joblib')
    
    print("Training complete!")

if __name__ == "__main__":
    train()