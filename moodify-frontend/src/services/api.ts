import axios from 'axios';
import { Prediction, RecommendationResponse, SpotifyToken } from '../types';

const API_URL = 'https://moodify-backend-ten.vercel.app';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const exchangeCodeForToken = async (code: string, codeVerifier: string): Promise<SpotifyToken> => {
  const response = await api.post<SpotifyToken>('/callback', { code, code_verifier: codeVerifier });
  return response.data;
};

export const getPrediction = async (text: string): Promise<Prediction> => {
  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to get prediction');
  }

  return response.json();
};

export const getRecommendation = async (text: string, accessToken: string): Promise<RecommendationResponse> => {
  const response = await fetch(`${API_URL}/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to get recommendation');
  }

  return response.json();
}; 