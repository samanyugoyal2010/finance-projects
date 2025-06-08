How to Start it
python3 app.py runs the entire thing lets go

# Stock Return Predictor

This project implements a machine learning model that predicts expected returns for stocks using historical data and technical indicators.

## Features

- Fetches historical stock data using yfinance
- Implements technical analysis indicators (RSI, MACD, Bollinger Bands, etc.)
- Uses LSTM neural network for prediction
- Provides a REST API for easy integration

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the API server:
```bash
python app.py
```

2. Make predictions using the API:
```bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"symbol": "AAPL"}'
```

## Model Details

The model uses:
- 5 years of historical data
- Technical indicators including RSI, MACD, Bollinger Bands, and Moving Averages
- LSTM neural network architecture
- 60-day lookback window for predictions

## Disclaimer

This tool is for educational purposes only. Stock market predictions are inherently uncertain, and this model should not be used as the sole basis for investment decisions. Always do your own research and consult with financial advisors before making investment decisions. 

import joblib
import os

# After fitting the scaler
scaler.fit(X_train)
joblib.dump(scaler, f'scaler_{symbol}.pkl')

scaler = joblib.load(f'scaler_{symbol}.pkl') 