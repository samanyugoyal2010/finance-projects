import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import axios from 'axios';

const StockPredictor = () => {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await axios.post('http://localhost:8000/predict', { symbol });
      setPrediction(response.data);
      
      // Fetch historical data for the chart
      const historicalResponse = await axios.get(`http://localhost:8000/historical/${symbol}`);
      setHistoricalData(historicalResponse.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while fetching the prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader
        title="Stock Return Predictor"
        titleTypographyProps={{ variant: 'h4', align: 'center' }}
      />
      <CardContent>
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Stock Symbol"
              variant="outlined"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., AAPL"
              required
            />
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
            >
              Predict Return
            </Button>
          </Box>
        </form>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}

        {prediction && (
          <Paper elevation={3} sx={{ p: 3, my: 2 }}>
            <Typography variant="h6" gutterBottom>
              Prediction Result
            </Typography>
            <Typography variant="body1">
              Stock: {prediction.symbol}
            </Typography>
            <Typography variant="body1">
              Predicted Return: {prediction.predicted_return}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {prediction.confidence}
            </Typography>
          </Paper>
        )}

        {historicalData.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Historical Performance
            </Typography>
            <LineChart
              width={800}
              height={400}
              data={historicalData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="close" stroke="#8884d8" name="Close Price" />
            </LineChart>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default StockPredictor; 