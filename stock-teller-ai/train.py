import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from stock_predictor import StockPredictor
from models import LSTMModel
import argparse

def train_model(symbol, epochs=100, batch_size=32, learning_rate=0.001):
    # Enable parallel processing for PyTorch
    torch.set_num_threads(8)  # Adjust based on your CPU cores
    
    # Get data
    predictor = StockPredictor()
    df = predictor.fetch_stock_data(symbol)
    df = predictor.add_technical_indicators(df)
    X, y = predictor.prepare_data(df)
    
    # Convert to PyTorch tensors and move to device
    X = torch.FloatTensor(X)
    y = torch.FloatTensor(y)
    
    # Split data into training and validation sets
    train_size = int(0.8 * len(X))
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]
    
    # Create model
    input_dim = X.shape[2]
    model = LSTMModel(input_dim=input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    print(f"Training model for {symbol}...")
    print(f"Input dimensions: {X.shape}")
    
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    
    # Training loop with validation
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(X_train)
        loss = criterion(outputs.squeeze(), y_train)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs.squeeze(), y_val)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': loss,
                    'val_loss': val_loss,
                }, f'model_{symbol}.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                print(f'Early stopping at epoch {epoch}')
                break
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], '
                  f'Loss: {loss.item():.4f}, '
                  f'Val Loss: {val_loss.item():.4f}')
    
    return model

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, required=True, help='Stock symbol to train on')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()
    
    model = train_model(
        args.symbol,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )