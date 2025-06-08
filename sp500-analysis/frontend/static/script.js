document.addEventListener('DOMContentLoaded', function() {
    const predictBtn = document.getElementById('predict-btn');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const prediction = document.getElementById('prediction');
    const currentPrice = document.getElementById('current-price');
    const estimatedPrice = document.getElementById('estimated-price');

    predictBtn.addEventListener('click', async function() {
        try {
            predictBtn.disabled = true;
            predictBtn.textContent = 'Loading...';
            
            const response = await fetch('/predict');
            const data = await response.json();
            
            if (data.success) {
                prediction.textContent = data.prediction;
                currentPrice.textContent = data.current_price;
                estimatedPrice.textContent = data.estimated_price;
                
                results.classList.remove('hidden');
                error.classList.add('hidden');
            } else {
                throw new Error(data.error);
            }
        } catch (err) {
            results.classList.add('hidden');
            error.classList.remove('hidden');
            error.querySelector('.error-message').textContent = 
                'Error getting prediction: ' + err.message;
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = 'Get Tomorrow\'s Prediction';
        }
    });
});