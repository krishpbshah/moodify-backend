import React, { useState, useEffect } from 'react';
import { FaSpotify } from 'react-icons/fa';
import { getPrediction, getRecommendation } from '../services/api';
import { Prediction, Recommendation } from '../types';
import { generateCodeChallenge, generateCodeVerifier } from '../utils/pkce';

// Spotify Client ID from your dashboard
const SPOTIFY_CLIENT_ID = process.env.REACT_APP_SPOTIFY_CLIENT_ID || '01cbfb648a2f48568db1901f1631921a';
const REDIRECT_URI = 'https://moodify-backend-ten.vercel.app/callback';

// Create a wrapper component for the Spotify icon
const SpotifyIcon: React.FC = () => {
  return <span style={{ display: 'inline-flex', alignItems: 'center' }}><FaSpotify size={20} /></span>;
};

const Home: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [text, setText] = useState('');
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('spotify_access_token');
    if (token) {
      setAccessToken(token);
    }
  }, []);

  const handleSpotifyLogin = async () => {
    if (!SPOTIFY_CLIENT_ID) {
      setError('Spotify Client ID is missing');
      return;
    }

    try {
      const codeVerifier = generateCodeVerifier();
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      const state = Math.random().toString(36).substring(7);
      
      localStorage.setItem('code_verifier', codeVerifier);
      localStorage.setItem('state', state);

      const scope = 'user-read-private user-read-email user-top-read user-library-read';
      const authUrl = new URL('https://accounts.spotify.com/authorize');
      const params = {
        response_type: 'code',
        client_id: SPOTIFY_CLIENT_ID,
        scope,
        redirect_uri: REDIRECT_URI,
        state,
        code_challenge_method: 'S256',
        code_challenge: codeChallenge,
      };

      authUrl.search = new URLSearchParams(params).toString();
      window.location.href = authUrl.toString();
    } catch (error) {
      setError('Failed to initialize Spotify login');
      console.error('Spotify login error:', error);
    }
  };

  const handleSubmit = async () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const predictionResult = await getPrediction(text);
      setPrediction(predictionResult);

      if (accessToken) {
        const recommendationResult = await getRecommendation(text, accessToken);
        setRecommendation(recommendationResult.recommendation);
      }
    } catch (error) {
      setError('Failed to get prediction or recommendation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="stack">
        <h1 className="heading">🎧 Moodify</h1>
        <p className="text">Tell us how you're feeling and get personalized music recommendations</p>

        {error && (
          <div className="card" style={{ backgroundColor: '#FED7D7', color: '#C53030' }}>
            {error}
          </div>
        )}

        {!accessToken ? (
          <button
            className="button button--green"
            onClick={handleSpotifyLogin}
          >
            <span style={{ marginRight: '0.5rem' }}>
              <SpotifyIcon />
            </span>
            Connect with Spotify
          </button>
        ) : (
          <div className="stack">
            <textarea
              className="textarea"
              placeholder="How are you feeling today?"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <button
              className="button"
              onClick={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Get Recommendation'}
            </button>
          </div>
        )}

        {prediction && (
          <div className="card">
            <div className="stack">
              <h2 className="heading" style={{ fontSize: '1.5rem' }}>Your Mood Analysis</h2>
              <div className="stack--horizontal">
                <span style={{ fontWeight: 'bold' }}>Emotion:</span>
                <span>{prediction.emotion}</span>
              </div>
              <div className="stack--horizontal">
                <span style={{ fontWeight: 'bold' }}>Intent:</span>
                <span>{prediction.intent}</span>
              </div>
              <div className="stack--horizontal">
                <span style={{ fontWeight: 'bold' }}>Context:</span>
                <span>{prediction.context}</span>
              </div>
            </div>
          </div>
        )}

        {recommendation && (
          <div className="card">
            <div className="stack">
              {recommendation.album_art && (
                <img
                  src={recommendation.album_art}
                  alt={recommendation.name}
                  className="image"
                  style={{ width: '200px', height: '200px', objectFit: 'cover' }}
                />
              )}
              <h2 className="heading" style={{ fontSize: '1.5rem' }}>{recommendation.name}</h2>
              <p className="text">{recommendation.artist}</p>
              <a
                href={recommendation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="button"
              >
                Open in Spotify
              </a>
              {recommendation.preview_url && (
                <audio controls src={recommendation.preview_url} className="audio" />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 