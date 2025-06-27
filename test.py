from user_auth import register_user, authenticate_user, get_user_by_id
from excuse_history import save_excuse, get_user_excuses, mark_excuse_favorite

# === Sample Test Values ===
user_id = "muthu3"
username = "Muthuv"
email = "muthu@example.com"
password = "Muthu@0205"

prompt = "Need a funny excuse for skipping class."
excuse = "I got stuck in a human-sized vending machine at the mall."
apology = "I’m truly sorry, I never expected this kind of situation."

pdf_path = "docs/muthu_excuse.pdf"
chat_path = "images/muthu_chat.png"
voice ="audio/muthu_excuse.mp3"

# === 1. Register User ===
print("\n[1] Registering User...")
print(register_user(user_id, username, email, password))

# === 2. Authenticate Login ===
print("\n[2] Authenticating Login...")
if authenticate_user(user_id, password):
    print("✅ Login successful")
else:
    print("❌ Login failed")

# === 3. Save Excuse ===
print("\n[3] Saving Excuse...")
print(save_excuse(user_id, prompt, excuse, apology, pdf_path, chat_path,voice))

# === 4. Retrieve User History ===
print("\n[4] Fetching User History...")
excuses = get_user_excuses(user_id)
for row in excuses:
    print(row)

# === 5. Mark First Excuse as Favorite ===
if excuses:
    first_excuse_id = excuses[0][0]
    print(f"\n[5] Marking Excuse ID {first_excuse_id} as Favorite...")
    print(mark_excuse_favorite(first_excuse_id))

# === 6. View Favorites ===
print("\n[6] Fetching Favorites Only...")
favorites = get_user_excuses(user_id, favorites_only=True)
for fav in favorites:
    print(fav)
