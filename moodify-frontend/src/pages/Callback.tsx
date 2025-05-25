import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { exchangeCodeForToken } from '../services/api';

const Callback: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      const state = params.get('state');
      const storedState = localStorage.getItem('state');
      const codeVerifier = localStorage.getItem('code_verifier');

      if (!code || !state || !storedState || state !== storedState || !codeVerifier) {
        navigate('/');
        return;
      }

      try {
        await exchangeCodeForToken(code, codeVerifier);
        navigate('/');
      } catch (error) {
        console.error('Error exchanging code for token:', error);
        navigate('/');
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="container">
      <div className="stack" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h2 className="heading" style={{ fontSize: '1.5rem' }}>Connecting to Spotify...</h2>
          <p className="text">Please wait while we establish your connection.</p>
        </div>
      </div>
    </div>
  );
};

export default Callback; 