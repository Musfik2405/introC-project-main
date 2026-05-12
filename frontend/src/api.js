import axios from 'axios';

// Base URL for your FastAPI backend
const API_BASE = "http://localhost:8000/api";

// Map the active card IDs to their specific backend endpoints
const ENDPOINTS = {
  substitution: "/classical/substitution",
  transposition: "/classical/transposition",
  des: "/symmetric/des",
  aes: "/symmetric/aes",
  rsa: "/public_key/rsa/execute",
  ecc: "/public_key/ecc/execute"
};

/**
 * Executes the selected cryptographic algorithm.
 * @param {string} activeCard - The ID of the current algorithm (e.g., 'aes', 'rsa')
 * @param {object} payload - The data payload containing text, keys, mode, etc.
 * @returns {Promise<object>} - The JSON response from the backend
 */
export const executeCipher = async (activeCard, payload) => {
  const endpoint = ENDPOINTS[activeCard];
  
  if (!endpoint) {
    throw new Error("Invalid algorithm selected.");
  }

  try {
    const response = await axios.post(`${API_BASE}${endpoint}`, payload);
    return response.data;
  } catch (error) {
    // Return the specific error detail from FastAPI if it exists
    throw new Error(error.response?.data?.detail || "Execution failed. Check backend connection.");
  }
};

/**
 * Generates RSA Public and Private keys based on the selected bit size.
 * @param {number} bits - The key size (e.g., 512 or 1024)
 * @returns {Promise<object>} - The generated keys and attack analysis
 */
export const generateRSAKeys = async (bits) => {
  try {
    const response = await axios.get(`${API_BASE}/public_key/rsa/setup?bits=${bits}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || "RSA Setup failed. Is the backend running?");
  }
};