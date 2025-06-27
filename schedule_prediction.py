# task_scheduler.py — periodic excuse predictor

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from excuse_predictor import suggest_excuse_if_needed
from db import get_connection

# Fetch distinct users from excuses table
def fetch_active_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT user_id FROM excuses")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=60)
def scheduled_prediction_job():
    print(f"[AutoCheck] Running excuse prediction at {datetime.now()}")
    user_ids = fetch_active_users()
    for user_id in user_ids:
        excuse = suggest_excuse_if_needed(user_id, datetime.now())
        if excuse:
            print(f"[{user_id}] Suggested Excuse: {excuse}")
        else:
            print(f"[{user_id}] No excuse needed at this time.")

if __name__ == "__main__":
    print("🔁 Starting auto-scheduling service (checks every hour)...")
    scheduler.start()
