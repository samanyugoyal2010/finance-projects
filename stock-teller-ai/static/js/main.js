let predictionChart = null;
let trainedStocks = ['NVDA', 'AAPL']; // This should be populated from the backend

// Initialize trained stocks display
window.addEventListener('DOMContentLoaded', () => {
    displayTrainedStocks();
});

function displayTrainedStocks() {
    const stockGrid = document.getElementById('trainedStocks');
    stockGrid.innerHTML = '';
    
    trainedStocks.forEach(symbol => {
        const card = createStockCard(symbol);
        stockGrid.appendChild(card);
    });
}

function createStockCard(symbol) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => {
        document.getElementById('stockSymbol').value = symbol;
        predictReturn();
    };
    
    card.innerHTML = `
        <div class="symbol">${symbol}</div>
        <div class="name">Trained Model Available</div>
        <div class="metrics">
            <span>Click to predict</span>
            <span>→</span>
        </div>
    `;
    
    return card;
}

async function predictReturn() {
    const symbolInput = document.getElementById('stockSymbol');
    const symbol = symbolInput.value.toUpperCase().trim();
    
    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    showLoading();
    hideError();
    hideResult();

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol: symbol })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get prediction');
        }

        const data = await response.json();
        showResult(data);
        updateChart(data);
        updateLastUpdated();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Fetch trained models on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/trained-models');
        if (response.ok) {
            const data = await response.json();
            trainedStocks = data.models;
            displayTrainedStocks();
        }
    } catch (error) {
        console.error('Failed to fetch trained models:', error);
    }
});

function showResult(data) {
    document.getElementById('symbolResult').textContent = data.symbol;
    const returnElement = document.getElementById('returnResult');
    returnElement.textContent = data.predicted_return;
    
    // Add color based on prediction
    const returnValue = parseFloat(data.predicted_return);
    returnElement.style.color = returnValue >= 0 ? '#34c759' : '#ff3b30';
    
    // Add current price if available
    if (data.current_price) {
        const priceElement = document.createElement('div');
        priceElement.className = 'current-price';
        priceElement.textContent = `Current Price: ${data.current_price}`;
        returnElement.parentElement.appendChild(priceElement);
    }
    
    document.getElementById('confidenceText').textContent = data.confidence;
    document.getElementById('result').classList.remove('hidden');
}

function updateChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    if (predictionChart) {
        predictionChart.destroy();
    }
    
    const returnValue = parseFloat(data.predicted_return);
    const datasets = [{
        label: 'Predicted Return',
        data: [0, returnValue],
        borderColor: returnValue >= 0 ? '#34c759' : '#ff3b30',
        backgroundColor: returnValue >= 0 ? 'rgba(52, 199, 89, 0.1)' : 'rgba(255, 59, 48, 0.1)',
        fill: true
    }];
    
    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Current', 'Predicted'],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

function updateLastUpdated() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleString();
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}

function hideResult() {
    document.getElementById('result').classList.add('hidden');
}

// Add enter key support
document.getElementById('stockSymbol').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        predictReturn();
    }
});