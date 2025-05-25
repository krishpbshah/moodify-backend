from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
import joblib
import os
import uuid
import requests
import logging
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, 
     origins=["http://localhost:3000", "https://moodify-krish.vercel.app"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
    return wrapper

# Load ML models with error handling
try:
    emotion_model = joblib.load("emotion_model.pkl")
    intent_model = joblib.load("intent_model.pkl")
    context_model = joblib.load("context_model.pkl")
except Exception as e:
    logger.error(f"Failed to load ML models: {str(e)}")
    raise

# Spotify API credentials with validation
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise ValueError("Missing required Spotify API credentials")

@app.route("/")
def home():
    return "🎧 Moodify API is running!"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    code = data.get("code")
    verifier = data.get("code_verifier")

    if not code or not verifier:
        return jsonify({"error": "Missing code or code_verifier"}), 400

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        return jsonify({"error": "Token exchange failed", "details": response.json()}), 400

    return jsonify(response.json())

@app.route("/predict", methods=["POST"])
@handle_errors
@limiter.limit("10 per minute")
def predict():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400
        
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Missing or empty text input"}), 400

    try:
        emotion = emotion_model.predict([text])[0]
        intent = intent_model.predict([text])[0]
        context = context_model.predict([text])[0]

        logger.info(f"Prediction successful - Emotion: {emotion}, Intent: {intent}, Context: {context}")
        
        return jsonify({
            "emotion": emotion,
            "intent": intent,
            "context": context,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500

@app.route("/recommend", methods=["POST"])
@handle_errors
@limiter.limit("10 per minute")
def recommend():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400

    text = data.get("text", "").strip()
    token = data.get("access_token")

    if not token or not text:
        return jsonify({"error": "Missing access_token or text"}), 400

    try:
        # Predict mood/intent with error handling
        emotion = emotion_model.predict([text])[0]
        intent = intent_model.predict([text])[0]
        context = context_model.predict([text])[0]

        sp = spotipy.Spotify(auth=token)
        
        # Get user's top tracks and liked tracks
        top_tracks = sp.current_user_top_tracks(limit=50)["items"]
        liked_tracks = sp.current_user_saved_tracks(limit=50)["items"]
        
        # Combine and deduplicate tracks
        all_tracks = {track["track"]["id"]: track["track"] for track in top_tracks + liked_tracks}
        
        if not all_tracks:
            return jsonify({"error": "No tracks found for recommendations"}), 400

        track_ids = list(all_tracks.keys())
        features = sp.audio_features(tracks=track_ids)

        # Enhanced scoring system
        scored_tracks = []
        for track, feature in zip(all_tracks.values(), features):
            if not feature:
                continue
                
            # Calculate score based on multiple factors
            score = (
                feature["valence"] * 0.3 +  # Mood
                feature["energy"] * 0.2 +   # Energy level
                feature["danceability"] * 0.2 +  # Danceability
                feature["tempo"] / 200.0 * 0.15 +  # Tempo (normalized)
                feature["popularity"] / 100.0 * 0.15  # Popularity
            )
            
            scored_tracks.append((track, score))

        # Sort by score and get top recommendation
        top_track = max(scored_tracks, key=lambda x: x[1])[0]
        
        return jsonify({
            "recommendation": {
                "name": top_track["name"],
                "artist": top_track["artists"][0]["name"],
                "url": top_track["external_urls"]["spotify"],
                "mood": emotion,
                "intent": intent,
                "context": context,
                "preview_url": top_track.get("preview_url"),
                "album_art": top_track["album"]["images"][0]["url"] if top_track["album"]["images"] else None
            },
            "status": "success"
        })

    except spotipy.SpotifyException as e:
        logger.error(f"Spotify API error: {str(e)}")
        return jsonify({"error": "Spotify access failed", "details": str(e)}), 401
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify({"error": "Recommendation failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)  # Set to False in production
