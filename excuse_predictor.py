# scheduler_model.py — model training, prediction, and excuse suggestion

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from get_data_ml import load_user_excuse_data, extract_features
from generate_exucuse import excuse_generator

def train_user_model(user_id, min_samples=30):
    df = load_user_excuse_data(user_id)
    if len(df) < min_samples:
        return None
    X = extract_features(df)
    y = [1] * len(X)
    clf = DecisionTreeClassifier(max_depth=4, min_samples_split=5)
    clf.fit(X, y)
    return clf

def train_global_model():
    df = load_user_excuse_data()
    if len(df) < 50:
        return None
    X = extract_features(df)
    y = [1] * len(X)
    clf = LogisticRegression()
    clf.fit(X, y)
    return clf

def predict_excuse_need(user_id, check_time, user_model=None, global_model=None):
    test_df = pd.DataFrame([{
        "timestamp": pd.to_datetime(check_time),
        "prompt": "Placeholder"
    }])
    X_test = extract_features(test_df)

    if not user_model:
        user_model = train_user_model(user_id)
    if not user_model:
        if not global_model:
            global_model = train_global_model()
        if not global_model:
            return False
        return global_model.predict(X_test)[0] == 1

    return user_model.predict(X_test)[0] == 1

def suggest_excuse_if_needed(user_id, check_time):
    if predict_excuse_need(user_id, check_time):
        return excuse_generator("Predict and generate a realistic excuse.")
    return None

def evaluate_user_model(user_id):
    df = load_user_excuse_data(user_id)
    if len(df) < 30:
        return "Not enough data for evaluation."
    X = extract_features(df)
    y = [1] * len(X)
    clf = DecisionTreeClassifier(max_depth=4, min_samples_split=5)
    scores = cross_val_score(clf, X, y, cv=5)
    return f"Cross-validation accuracy for user {user_id}: {scores.mean():.2f}"

def evaluate_global_model():
    df = load_user_excuse_data()
    if len(df) < 50:
        return "Not enough global data for evaluation."
    X = extract_features(df)
    y = [1] * len(X)
    clf = LogisticRegression()
    scores = cross_val_score(clf, X, y, cv=5)
    return f"Global model cross-validation accuracy: {scores.mean():.2f}"
