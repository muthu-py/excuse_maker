# excuse_history.py — excuse and apology tracking per user

from db import get_connection
from datetime import datetime

# === Save Excuse to DB ===
def save_excuse(user_id, prompt, excuse, apology, pdf_path=None, chat_image_path=None, voice_path=None, favorite=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO excuses (user_id, prompt, excuse, apology, pdf_path, chat_image_path, voice_path, favorite)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, prompt, excuse, apology, pdf_path, chat_image_path, voice_path, int(favorite)))
    conn.commit()
    conn.close()
    return "Excuse saved successfully."


# === Retrieve All Excuses for User ===
def get_user_excuses(user_id, favorites_only=False):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM excuses WHERE user_id = %s"
    if favorites_only:
        query += " AND favorite = TRUE"
    c.execute(query, (user_id,))
    data = c.fetchall()
    conn.close()
    return data

# === Mark Excuse as Favorite ===
def mark_excuse_favorite(excuse_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE excuses SET favorite = TRUE WHERE excuse_id = %s", (excuse_id,))
    conn.commit()
    conn.close()
    return f"Excuse ID {excuse_id} marked as favorite."

def rank_excuses(user_id, context=None):
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT excuse_id, excuse, context, favorite FROM excuses WHERE user_id = %s"
    params = [user_id]
    if context:
        query += " AND prompt LIKE %s"
        params.append(f"%{context}%")

    c.execute(query, tuple(params))
    results = c.fetchall()
    conn.close()

    ranked = []
    for row in results:
        excuse_id, text, ctx, favorite = row
        score = 1.0
        if favorite:
            score += 1.5
        if context and context in ctx:
            score += 0.5
        ranked.append((score, text))

    ranked.sort(reverse=True)
    return [text for score, text in ranked]

def save_emergency_log(user_id, method, phone, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO emergency_logs (user_id, method, phone, message)
        VALUES (%s, %s, %s, %s)
    """, (user_id, method, phone, message))
    conn.commit()
    conn.close()
    return "Emergency log saved."

def get_emergency_logs(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM emergency_logs WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    data = c.fetchall()
    conn.close()
    return data
