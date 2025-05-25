import axios from 'axios';
import { Prediction, RecommendationResponse, SpotifyToken } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const exchangeCodeForToken = async (code: string, codeVerifier: string): Promise<SpotifyToken> => {
  const response = await api.post<SpotifyToken>('/callback', { code, code_verifier: codeVerifier });
  return response.data;
};

export const getPrediction = async (text: string): Promise<Prediction> => {
  const response = await api.post<Prediction>('/predict', { text });
  return response.data;
};

export const getRecommendation = async (text: string, accessToken: string): Promise<RecommendationResponse> => {
  const response = await api.post<RecommendationResponse>('/recommend', { text, access_token: accessToken });
  return response.data;
}; 