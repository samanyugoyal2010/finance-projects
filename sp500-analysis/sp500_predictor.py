import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_sp500_data():
    # Get S&P 500 data for the last 10 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3650)  # 10 years
    
    # Download S&P 500 data
    sp500 = yf.download('^GSPC', start=start_date, end=end_date)
    return sp500

def prepare_features(df):
    # Calculate daily returns
    df['Returns'] = df['Close'].pct_change()
    
    # Create features
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    df['RSI'] = calculate_rsi(df['Close'])
    
    # Create target variable (next day's return)
    df['Target'] = df['Returns'].shift(-1)
    
    return df

def calculate_rsi(prices, period=14):
    # Calculate RSI
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def train_model(df):
    # Prepare features and target
    features = ['Returns', 'MA5', 'MA20', 'MA50', 'Volatility', 'RSI']
    X = df[features].dropna()
    y = df['Target'].dropna()
    
    # Align X and y
    X = X[:-1]  # Remove last row since we don't have target for it
    y = y[:-1]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    return model, scaler

def predict_tomorrow_return(df, model, scaler):
    # Prepare latest data for prediction
    latest_data = df[['Returns', 'MA5', 'MA20', 'MA50', 'Volatility', 'RSI']].iloc[-1:]
    
    # Scale the data
    latest_data_scaled = scaler.transform(latest_data)
    
    # Make prediction
    prediction = model.predict(latest_data_scaled)[0]
    return prediction

def main():
    # Get data
    print("Fetching S&P 500 data...")
    sp500_data = get_sp500_data()
    
    # Prepare features
    print("Preparing features...")
    df = prepare_features(sp500_data)
    
    # Train model
    print("Training model...")
    model, scaler = train_model(df)
    
    # Make prediction for tomorrow
    prediction = predict_tomorrow_return(df, model, scaler)
    
    # Print results
    print("\nPrediction Results:")
    print(f"Estimated S&P 500 return for tomorrow: {prediction:.4%}")
    print(f"Current S&P 500 price: ${df['Close'].iloc[-1]:.2f}")
    print(f"Estimated tomorrow's price: ${df['Close'].iloc[-1] * (1 + prediction):.2f}")

if __name__ == "__main__":
    main()