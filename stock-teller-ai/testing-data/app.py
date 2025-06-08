from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from stock_predictor import StockPredictor
import uvicorn
from datetime import datetime, timedelta

app = FastAPI(title="Stock Return Predictor")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

predictor = StockPredictor()

class StockRequest(BaseModel):
    symbol: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_return(request: StockRequest):
    try:
        # Get prediction
        predicted_return = predictor.predict_return(request.symbol)
        
        # Convert to percentage
        predicted_return_percent = predicted_return * 100
        
        return {
            "symbol": request.symbol,
            "predicted_return": f"{predicted_return_percent:.2f}%",
            "confidence": "This prediction is based on historical data and technical indicators. Please use it as one of many factors in your investment decisions."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/historical/{symbol}")
async def get_historical_data(symbol: str):
    try:
        # Fetch historical data
        df = predictor.fetch_stock_data(symbol, period='1y')
        
        # Convert to list of dictionaries for JSON response
        historical_data = []
        for index, row in df.iterrows():
            historical_data.append({
                'date': index.strftime('%Y-%m-%d'),
                'close': float(row['Close']),
                'volume': float(row['Volume']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low'])
            })
        
        return historical_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/trained-models")
async def get_trained_models():
    """Get list of trained models"""
    models = [f.replace('model_', '').replace('.pth', '') 
             for f in os.listdir('.') 
             if f.startswith('model_') and f.endswith('.pth')]
    return {"models": models}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)