import os
import joblib

# Setup directories
MODEL_DIR = "models"
USER_MODEL_DIR = os.path.join(MODEL_DIR, "user_models")
GLOBAL_MODEL_PATH = os.path.join(MODEL_DIR, "global_model.pkl")

os.makedirs(USER_MODEL_DIR, exist_ok=True)

def save_model(model, path):
    joblib.dump(model, path)

def load_model(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None
