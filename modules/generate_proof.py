from modules.generate_exucuse import *
import os
import re
import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from html2image import Html2Image
import spacy
from gtts import gTTS

nlp = spacy.load("en_core_web_sm")


model = genai.GenerativeModel("models/gemini-1.5-flash")
# === NLP-BASED UTILITIES ===

def infer_context_nlp(excuse):
    """
    Use NLP to infer context from the excuse text (school, work, family, social).
    """
    doc = nlp(excuse.lower())
    keywords = excuse.lower()
    people = [ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text.lower() for ent in doc.ents if ent.label_ == "ORG"]

    if "exam" in keywords or "school" in keywords or "class" in keywords:
        return "school"
    elif "office" in keywords or "meeting" in keywords or orgs:
        return "work"
    elif any(word in keywords for word in ["mother", "father", "family", "daughter", "son"]):
        return "family"
    elif any(word in keywords for word in ["party", "friend", "hangout", "wedding"]):
        return "social"
    else:
        return "general"

def extract_name_nlp(excuse):
    """
    Use spaCy NER to extract the first detected person name, fallback to 'John Doe'.
    """
    doc = nlp(excuse)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "John Doe"

# === FEATURE 3.1: FAKE DOCUMENT GENERATOR ===

def generate_fake_document(excuse, name=None, context=None, output_path="excuse_document.pdf"):
    if context is None:
        context = infer_context_nlp(excuse)
    if name is None:
        name = extract_name_nlp(excuse)

    today = datetime.date.today().strftime("%B %d, %Y")
    title_map = {
        "work": "Workplace Absence Note",
        "school": "Student Absence Certificate",
        "social": "Apology Letter",
        "family": "Family Emergency Note",
        "general": "Excuse Document"
    }
    doc_title = title_map.get(context.lower(), "Excuse Document")

    institution = ""
    if "school" in excuse.lower():
        institution = "Greenwood High School"
    elif "college" in excuse.lower():
        institution = "Riverdale College"
    elif "hospital" in excuse.lower():
        institution = "City Medical Center"
    elif "office" in excuse.lower() or "company" in excuse.lower():
        institution = "TechNova Pvt Ltd"
    elif "clinic" in excuse.lower():
        institution = "LifeCare Clinic"

    # ✍️ Try to infer if signature block is needed
    include_signature = any(word in excuse.lower() for word in ["doctor", "clinic", "hr", "principal", "manager"])

    # 🔁 Gemini-generated body text
    gemini_prompt = (
        f"Write a professional excuse note titled '{doc_title}' for someone named {name} "
        f"who couldn't attend a {context} obligation on {today}. The reason is: \"{excuse}\".\n"
        f"Make it formal and realistic, and keep it under 100 words."
    )

    try:
        response = model.generate_content(gemini_prompt)
        body = response.text.strip()
    except Exception as e:
        body = (
            f"This is to certify that {name} was unable to fulfill their responsibilities on {today} "
            f"due to the following reason:\n\n\"{excuse}\"\n\n"
            "This note serves as supporting documentation for their absence."
        )

    # 📝 Draw the document
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 800, doc_title)
    c.setFont("Helvetica", 12)

    text = c.beginText(70, 750)

    if institution:
        text.textLine(f"Institution: {institution}")
        text.textLine("")

    for line in body.split("\n"):
        for wrapped_line in re.findall('.{1,90}(?:\\s+|$)', line):  # Word-wrap manually
            text.textLine(wrapped_line.strip())
    c.drawText(text)

    if include_signature:
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(70, 140, "Authorized by:")
        c.drawString(70, 125, "Dr. AI Generator")
        c.line(70, 120, 200, 120)
        c.drawString(70, 110, f"Date: {today}")
    else:
        c.setFont("Helvetica", 12)
        c.drawString(70, 110, f"Signed: Dr. AI Generator  |  Date: {today}")

    c.save()

    return os.path.abspath(output_path)


# === FEATURE 3.2: FAKE CHAT SCREENSHOT GENERATOR ===
def generate_fake_chat_image(excuse_text, output_path="full_chat.png", user_name="You", friend_name="Friend"):
    """
    Uses Gemini to generate a realistic WhatsApp-style chat conversation and renders it as a screenshot.
    """
    try:
        prompt = (
            f"Simulate a short WhatsApp-style chat between {friend_name} and {user_name} about this excuse:\n"
            f'"{excuse_text}"\n\n'
            f"Format as:\n{friend_name}: message\n{user_name}: message\n"
            f"Limit to 6-8 lines."
        )
        response = model.generate_content(prompt)
        dialogue = response.text.strip()
        messages = []
        for line in dialogue.split("\n"):
            if ":" in line:
                sender, text = line.split(":", 1)
                sender = sender.strip()
                text = text.strip()
                if sender.lower() == user_name.lower():
                    messages.append({"sender": "you", "text": text})
                else:
                    messages.append({"sender": "them", "text": text})
        html_messages = ""
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        for msg in messages:
            side = "right" if msg["sender"] == "you" else "left"
            tick = "✓✓" if msg["sender"] == "you" else ""
            html_messages += f'''
            <div class="bubble {side}">
                <div class="text">{msg["text"]}</div>
                <div class="meta">{timestamp} {tick}</div>
            </div>
            '''
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #e5ddd5;
                    margin: 0;
                    padding: 15px;
                }}
                .bubble {{
                    max-width: 60%;
                    padding: 10px;
                    margin: 8px;
                    border-radius: 10px;
                    position: relative;
                    font-size: 14px;
                    line-height: 1.4;
                    display: inline-block;
                    clear: both;
                }}
                .bubble.left {{
                    background-color: #fff;
                    float: left;
                }}
                .bubble.right {{
                    background-color: #dcf8c6;
                    float: right;
                }}
                .text {{
                    margin-bottom: 5px;
                }}
                .meta {{
                    font-size: 11px;
                    color: #999;
                    text-align: right;
                }}
            </style>
        </head>
        <body>
            {html_messages}
        </body>
        </html>
        """
        # Ensure output_path is absolute and directory exists
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_dir = os.path.dirname(output_path)
        output_file = os.path.basename(output_path)
        hti = Html2Image(browser_executable='C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe')
        hti.output_path = output_dir
        hti.screenshot(html_str=html_content, save_as=output_file)
        print(f"[generate_fake_chat_image] Chat image saved to: {os.path.join(output_dir, output_file)}")
        return os.path.join(output_dir, output_file)
    except Exception as e:
        print(f"[generate_fake_chat_image] Error generating chat image: {e}")
        return None

# === FEATURE 3.3: FAKE LOCATION SEQUENCE GENERATOR ===

def infer_location_sequence_from_excuse(excuse_text):
    """
    Use NLP to infer a realistic location sequence based on the excuse.
    """
    excuse_lower = excuse_text.lower()
    
    if "hospital" in excuse_lower or "emergency" in excuse_lower:
        return ["Home", "Hospital", "Pharmacy", "Home"]
    elif "school" in excuse_lower or "exam" in excuse_lower:
        return ["Home", "School", "Library", "Home"]
    elif "office" in excuse_lower or "meeting" in excuse_lower:
        return ["Home", "Office", "Coffee Shop", "Home"]
    elif "family" in excuse_lower or "mother" in excuse_lower or "father" in excuse_lower:
        return ["Home", "Family House", "Grocery Store", "Home"]
    else:
        return ["Home", "Unknown Location", "Home"]

def generate_fake_location(excuse_text, name=None):
    """
    Generate a fake location sequence based on the excuse context.
    """
    if name is None:
        name = extract_name_nlp(excuse_text)
    
    locations = infer_location_sequence_from_excuse(excuse_text)
    current_time = datetime.datetime.now()
    
    location_data = []
    for i, location in enumerate(locations):
        timestamp = current_time + datetime.timedelta(hours=i)
        location_data.append({
            "name": name,
            "location": location,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active"
        })
    
    return location_data

# === FEATURE 3.4: AUDIO GENERATOR ===
def save_excuse_audio(excuse_text, output_path="excuse_audio.mp3", language='en'):
    """
    Generate audio file from excuse text using Google Text-to-Speech.
    
    Parameters:
    - excuse_text (str): The excuse text to convert to audio
    - output_path (str): Output path for the audio file
    - language (str): Language code (default: 'en' for English)
    
    Returns:
    - str: Path to the saved audio file
    """
    try:
        # Create gTTS object
        tts = gTTS(text=excuse_text, lang=language, slow=False)
        
        # Save the audio file
        tts.save(output_path)
        
        return os.path.abspath(output_path)
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# === FEATURE 3.5: COMPREHENSIVE PROOF GENERATOR ===
def generate_all_proofs(excuse_text, user_id, output_dir="static/proofs"):
    """
    Generate all types of proof for an excuse: document, chat image, audio, and location data.
    
    Parameters:
    - excuse_text (str): The excuse text
    - user_id (str): User ID for file naming
    - output_dir (str): Directory to save proof files
    
    Returns:
    - dict: Dictionary containing paths to all generated proof files
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename prefix
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{user_id}_{timestamp}"
    
    proofs = {}
    
    try:
        # Generate document
        pdf_path = os.path.join(output_dir, f"{prefix}_document.pdf")
        proofs['document'] = generate_fake_document(excuse_text, output_path=pdf_path)
        
        # Generate chat image
        chat_path = os.path.join(output_dir, f"{prefix}_chat.png")
        proofs['chat_image'] = generate_fake_chat_image(excuse_text, output_path=chat_path)
        
        # Generate audio
        audio_path = os.path.join(output_dir, f"{prefix}_audio.mp3")
        proofs['audio'] = save_excuse_audio(excuse_text, output_path=audio_path)
        
        # Generate location data
        proofs['location_data'] = generate_fake_location(excuse_text)
        
        return proofs
        
    except Exception as e:
        print(f"Error generating proofs: {e}")
        return proofs

if __name__ == "__main__":
    excuse = excuse_generator("I need a funny excuse for missing my friend's birthday party. Make it exaggerated.")
    print(generate_fake_document(excuse))
    print(generate_fake_chat_image(excuse))
    print(generate_fake_location(excuse))