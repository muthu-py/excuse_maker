# scheduler_utils.py — shared logic for excuse ML scheduling

import pandas as pd
from modules.db import get_connection
from modules.generate_proof import infer_context_nlp  # assumes NLP context extraction

def load_user_excuse_data(user_id=None):
    conn = get_connection()
    c = conn.cursor()
    if user_id:
        c.execute("SELECT user_id, prompt, timestamp FROM excuses WHERE user_id = %s", (user_id,))
    else:
        c.execute("SELECT user_id, prompt, timestamp FROM excuses")
    rows = c.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=["user_id", "prompt", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def extract_features(df):
    df["weekday"] = df["timestamp"].dt.weekday
    df["hour"] = df["timestamp"].dt.hour
    df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)
    df["is_morning"] = (df["hour"] < 12).astype(int)
    df["context"] = df["prompt"].apply(infer_context_nlp)
    context_dummies = pd.get_dummies(df["context"])
    features = pd.concat([df[["weekday", "hour", "is_weekend", "is_morning"]], context_dummies], axis=1)
    return features
