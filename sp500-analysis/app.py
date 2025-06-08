from flask import Flask, render_template, request, jsonify
from sp500_predictor import get_sp500_data, prepare_features, train_model, predict_tomorrow_return

app = Flask(__name__)

# Initialize the model
print("Initializing model...")
sp500_data = get_sp500_data()
df = prepare_features(sp500_data)
model, scaler = train_model(df)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict():
    try:
        prediction = predict_tomorrow_return(df, model, scaler)
        current_price = df['Close'].iloc[-1]
        estimated_price = current_price * (1 + prediction)
        
        return jsonify({
            'success': True,
            'prediction': f"{prediction:.4%}",
            'current_price': f"${current_price:.2f}",
            'estimated_price': f"${estimated_price:.2f}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)