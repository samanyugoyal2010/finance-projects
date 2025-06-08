import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
from models import LSTMModel
import ta
import requests
from bs4 import BeautifulSoup

class StockPredictor:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def fetch_stock_data(self, symbol, period='5y'):
        """Fetch historical stock data using yfinance"""
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        # Add market sentiment data
        try:
            sentiment = self.get_market_sentiment(symbol)
            df['Sentiment'] = sentiment
        except:
            df['Sentiment'] = 0.5  # Neutral sentiment if not available
            
        return df
    
    def get_market_sentiment(self, symbol):
        """Get market sentiment from news headlines"""
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            headlines = soup.find_all('h3')
            sentiment_score = 0
            count = 0
            
            for headline in headlines:
                text = headline.get_text().lower()
                # Simple sentiment analysis
                positive_words = ['up', 'rise', 'gain', 'bullish', 'positive', 'strong', 'beat']
                negative_words = ['down', 'fall', 'drop', 'bearish', 'negative', 'weak', 'miss']
                
                for word in positive_words:
                    if word in text:
                        sentiment_score += 1
                        count += 1
                for word in negative_words:
                    if word in text:
                        sentiment_score -= 1
                        count += 1
            
            if count > 0:
                return (sentiment_score / count + 1) / 2  # Normalize to 0-1
            return 0.5
        except:
            return 0.5
    
    def add_technical_indicators(self, df):
        """Add technical indicators to the dataset"""
        # Add RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # Add MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        # Add Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bollinger.bollinger_hband()
        df['BB_Lower'] = bollinger.bollinger_lband()
        
        # Add Moving Averages
        df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        df['SMA_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
        
        # Add Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Add Price Momentum
        df['Momentum'] = df['Close'].pct_change(periods=10)
        
        # Add Volatility
        df['Volatility'] = df['Close'].pct_change().rolling(window=20).std()
        
        return df
    
    def prepare_data(self, df, lookback=60):
        """Prepare data for LSTM model"""
        # Create target variable (next day's return)
        df['Target'] = df['Close'].shift(-1) / df['Close'] - 1
        
        # Drop rows with NaN values
        df = df.dropna()
        
        # Select features
        features = ['Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 
                   'BB_Upper', 'BB_Lower', 'SMA_20', 'SMA_50', 'SMA_200',
                   'Volume_SMA', 'Volume_Ratio', 'Momentum', 'Volatility',
                   'Sentiment']
        
        # Scale features
        scaled_data = self.scaler.fit_transform(df[features])
        
        # Create sequences
        X, y = [], []
        for i in range(len(scaled_data) - lookback):
            X.append(scaled_data[i:(i + lookback)])
            y.append(df['Target'].iloc[i + lookback])
            
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build LSTM model"""
        model = Sequential([
            LSTM(units=100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=100, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
        return model
    
    def train_model(self, symbol):
        """Train the model on historical data"""
        from train import train_model
        self.model = train_model(symbol)
        return self.model
    
    def predict_return(self, symbol):
        """Predict expected return for the next day"""
        if self.model is None:
            self.train_model(symbol)
            
        # Fetch recent data
        df = self.fetch_stock_data(symbol, period='60d')
        df = self.add_technical_indicators(df)
        
        # Prepare data for prediction
        features = ['Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 
                   'BB_Upper', 'BB_Lower', 'SMA_20', 'SMA_50', 'SMA_200',
                   'Volume_SMA', 'Volume_Ratio', 'Momentum', 'Volatility',
                   'Sentiment']
        scaled_data = self.scaler.transform(df[features])
        
        # Convert to PyTorch tensor
        data_tensor = torch.FloatTensor(scaled_data).unsqueeze(0)  # Add batch dimension
        
        # Make prediction
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(data_tensor)
        
        return prediction.item()