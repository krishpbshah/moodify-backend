import requests
import os

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "fb7ea60b500d41b8b3edb920f750e08f")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "https://moodify-krish.vercel.app/callback")
TOKEN_URL = "https://accounts.spotify.com/api/token"

def exchange_code_for_token(code, code_verifier):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    try:
        return response.json()
    except Exception as e:
        return {"error": "Failed to parse token response", "details": str(e)}
