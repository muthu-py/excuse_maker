#!/usr/bin/env python3
"""
Database initialization script for ExcuseGenie
Creates necessary tables if they don't exist
"""

from modules.db import get_connection
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create emergency_logs table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                method VARCHAR(10) NOT NULL,  -- 'sms' or 'call'
                phone VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        print("✅ emergency_logs table created/verified successfully")
        
        # Check if excuses table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS excuses (
                excuse_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                prompt TEXT NOT NULL,
                excuse TEXT NOT NULL,
                apology TEXT,
                pdf_path VARCHAR(255),
                chat_image_path VARCHAR(255),
                voice_path VARCHAR(255),
                favorite BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_favorite (favorite),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        print("✅ excuses table created/verified successfully")
        
        # Check if users table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        """)
        
        print("✅ users table created/verified successfully")
        
        conn.commit()
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Initializing ExcuseGenie database...")
    init_database() 