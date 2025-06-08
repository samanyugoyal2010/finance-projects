document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const symbol = document.getElementById('symbol').value.toUpperCase();
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    
    // Hide previous results and errors
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to get prediction');
        }
        
        const data = await response.json();
        
        // Update result display
        document.getElementById('resultSymbol').textContent = data.symbol;
        document.getElementById('resultReturn').textContent = data.predicted_return;
        document.getElementById('resultConfidence').textContent = data.confidence;
        
        // Show results
        loadingDiv.style.display = 'none';
        resultDiv.style.display = 'block';
        
    } catch (error) {
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = `Error: ${error.message}`;
    }
}); 