export interface SpotifyToken {
  access_token: string;
  token_type: string;
  scope: string;
  expires_in: number;
  refresh_token: string;
}

export interface Prediction {
  emotion: string;
  intent: string;
  context: string;
  status: string;
}

export interface Recommendation {
  name: string;
  artist: string;
  url: string;
  mood: string;
  intent: string;
  context: string;
  preview_url: string | null;
  album_art: string | null;
}

export interface RecommendationResponse {
  recommendation: Recommendation;
  status: string;
}

export interface ErrorResponse {
  error: string;
  details?: string;
} 