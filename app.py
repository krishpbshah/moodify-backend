from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
import joblib
import os
import uuid
import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://moodify-krish.vercel.app"], supports_credentials=True)



# Load ML models
emotion_model = joblib.load("emotion_model.pkl")
intent_model = joblib.load("intent_model.pkl")
context_model = joblib.load("context_model.pkl")

# Spotify API credentials
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")  # e.g., https://moodify-krish.vercel.app/callback

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
def predict():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Missing input"}), 400

    emotion = emotion_model.predict([text])[0]
    intent = intent_model.predict([text])[0]
    context = context_model.predict([text])[0]

    return jsonify({
        "emotion": emotion,
        "intent": intent,
        "context": context
    })

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    text = data.get("text")
    token = data.get("access_token")

    if not token or not text:
        return jsonify({"error": "Missing access_token or text"}), 400

    # Predict mood/intent
    emotion = emotion_model.predict([text])[0]
    intent = intent_model.predict([text])[0]
    context = context_model.predict([text])[0]

    try:
        sp = spotipy.Spotify(auth=token)
        liked_tracks = sp.current_user_saved_tracks(limit=50)["items"]
        if not liked_tracks:
            return jsonify({"error": "No liked tracks found."}), 400

        track_ids = [item["track"]["id"] for item in liked_tracks if item["track"]["id"]]
        features = sp.audio_features(tracks=track_ids)

        # Example: Score and sort tracks by energy or valence (simplified logic)
        scored = sorted(
            zip(liked_tracks, features),
            key=lambda x: (x[1]["valence"], x[1]["energy"]),
            reverse=True
        )

        top_track = scored[0][0]["track"]
        return jsonify({
            "recommendation": {
                "name": top_track["name"],
                "artist": top_track["artists"][0]["name"],
                "url": top_track["external_urls"]["spotify"],
                "mood": emotion,
                "intent": intent,
                "context": context
            }
        })

    except spotipy.SpotifyException as e:
        return jsonify({"error": "Spotify access failed", "details": str(e)}), 401

if __name__ == "__main__":
    app.run(debug=True)
