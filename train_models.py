import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Step 1: Sample dataset
data = [
    ("I'm stressed from studying all night", "Anxious", "Study", "Exams"),
    ("Need something calm after interview prep", "Calm", "Relax", "Job Search"),
    ("So tired after midterms, but need to grind", "Tired", "Study", "Exams"),
    ("Burning out from nonstop assignments", "Overwhelmed", "Rest", "Burnout"),
    ("Let’s get pumped for leg day", "Energized", "Workout", "Gym"),
    ("Just want to chill after a long day", "Calm", "Relax", "General Stress"),
    ("Finals week is killing me", "Stressed", "Study", "Exams"),
    ("No calls back from interviews... feeling lost", "Sad", "Rest", "Job Search"),
    ("Need background music while I code", "Focused", "Study", "Work"),
    ("Let's party and forget this week", "Excited", "Party", "General Stress")
]

df = pd.DataFrame(data, columns=["sentence", "emotion", "intent", "context"])

# Step 2: Train models
emotion_model = make_pipeline(TfidfVectorizer(), LogisticRegression())
intent_model = make_pipeline(TfidfVectorizer(), LogisticRegression())
context_model = make_pipeline(TfidfVectorizer(), LogisticRegression())

emotion_model.fit(df["sentence"], df["emotion"])
intent_model.fit(df["sentence"], df["intent"])
context_model.fit(df["sentence"], df["context"])

# Step 3: Save models as .pkl files
joblib.dump(emotion_model, "emotion_model.pkl")
joblib.dump(intent_model, "intent_model.pkl")
joblib.dump(context_model, "context_model.pkl")

print("✅ All models trained and saved successfully!")
