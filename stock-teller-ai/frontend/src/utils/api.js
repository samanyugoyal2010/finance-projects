import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const predictStock = async (symbol) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/predict`, { symbol });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get prediction');
  }
};

export const getHistoricalData = async (symbol) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/historical/${symbol}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get historical data');
  }
}; 