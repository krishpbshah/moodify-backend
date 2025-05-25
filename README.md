# 🎧 Moodify Backend

Moodify is a full-stack web application that recommends personalized Spotify songs based on the **user's detected emotion, intent, and contextual cues** from their input. This backend handles ML-driven mood classification, token-based Spotify integration, and playlist logic.

## 🔍 Project Overview

- **Input:** A text describing the user's current state (e.g., "I'm tired after school and work").
- **Output:** Spotify track recommendations aligned with emotion and intent.

## 🚀 Features

- 🎭 Emotion & Intent Classification using trained ML models
- 🎯 Personalized recommendation algorithm (valence, energy, danceability)
- 🔐 Spotify OAuth2 PKCE Authorization Flow (secure, token-based)
- 🌐 API endpoints for `/recommend` and `/callback`

## 🧠 Machine Learning

Trained models:
- `emotion_model.pkl` — Predicts emotion from user text
- `intent_model.pkl` — Extracts the intent (e.g., focus, relax)
- `context_model.pkl` — Adds contextual understanding to refine recommendations

Frameworks:
- `scikit-learn`
- `Flask`
- `spotipy` (Spotify Web API)

## 📦 Project Structure

moodify-backend/
│
├── app.py # Flask backend server
├── spotify_pkce_helper.py # Handles secure PKCE token exchange
├── emotion_model.pkl # Trained model for emotion classification
├── intent_model.pkl # Trained model for intent classification
├── context_model.pkl # Trained model for contextual cues
├── train_models.py # Model training script (optional)
├── requirements.txt # Dependencies
└── .gitignore

bash
Copy
Edit

## 🔧 Running Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/moodify-backend.git
   cd moodify-backend
Set up a virtual environment:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the backend:

bash
Copy
Edit
python app.py
Make sure to include the .pkl models in the root directory for full functionality.

🔑 Environment Variables
Create a .env file or set directly:

ini
Copy
Edit
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
REDIRECT_URI=https://moodify-krish.vercel.app/callback

📫 Contact
Built by Krish Shah
Intended for showcasing applied ML and full-stack integration for music recommendation.


