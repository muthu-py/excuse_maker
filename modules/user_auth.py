# user_auth.py — user registration and authentication

import bcrypt
from modules.db import get_connection

# === Password Utilities ===
def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

# === Register New User ===
def register_user(user_id, username, email, plain_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = %s OR username = %s", (user_id, username))
    if c.fetchone():
        conn.close()
        return "User already exists."
    password_hash = hash_password(plain_password)
    c.execute("""
        INSERT INTO users (user_id, username, email, password_hash)
        VALUES (%s, %s, %s, %s)
    """, (user_id, username, email, password_hash))
    conn.commit()
    conn.close()
    return "User registered successfully."

# === Authenticate User ===
def authenticate_user(user_id, plain_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE user_id = %s OR username = %s OR email = %s", (user_id, user_id, user_id))
    result = c.fetchone()
    conn.close()
    if not result:
        return False
    return check_password(plain_password, result[0])

# === Fetch User Info ===
def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, email FROM users WHERE user_id = %s", (user_id,))
    user = c.fetchone()
    conn.close()
    return user
