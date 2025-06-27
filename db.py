import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

# === MySQL Connection ===
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # change as needed
        password=os.getenv("db_pass"),     # change as needed
        database="excusegen"   # ensure this DB is created
    )

if get_connection():
    print(999)
