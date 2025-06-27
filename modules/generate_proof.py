from generate_exucuse import *
import os
import re
import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from html2image import Html2Image
import spacy

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
        "general": "Excuse Note"
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

    Parameters:
    - excuse_text (str): The excuse message
    - output_path (str): Screenshot output path
    - user_name (str): Display name for user messages (default: 'You')
    - friend_name (str): Display name for the friend (default: 'Friend')

    Returns:
    - str: Path to the saved image
    """

    prompt = (
        f"Simulate a short WhatsApp-style chat between {friend_name} and {user_name} about this excuse:\n"
        f"\"{excuse_text}\"\n\n"
        f"Format as:\n{friend_name}: message\n{user_name}: message\n"
        f"Limit to 6-8 lines."
    )

    try:
        response = model.generate_content(prompt)
        dialogue = response.text.strip()

        # Parse lines and prepare HTML
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

        # Generate HTML with ticks and timestamps
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

        # Final HTML with styles
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
                .right {{
                    background-color: #dcf8c6;
                    float: right;
                    border-bottom-right-radius: 0;
                }}
                .left {{
                    background-color: #ffffff;
                    float: left;
                    border-bottom-left-radius: 0;
                }}
                .meta {{
                    font-size: 10px;
                    color: #666;
                    margin-top: 5px;
                    text-align: right;
                }}
            </style>
        </head>
        <body>
            {html_messages}
        </body>
        </html>
        """

        html_file = "gemini_chat_temp.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        hti = Html2Image()
        hti.screenshot(html_file=html_file, save_as=output_path)
        return output_path

    except Exception as e:
        return f"Error generating conversation: {e}"


# === FEATURE 3.3: FAKE LOCATION LOG GENERATOR ===

def infer_location_sequence_from_excuse(excuse_text):
    excuse_lower = excuse_text.lower()

    if "hospital" in excuse_lower or "fever" in excuse_lower or "doctor" in excuse_lower:
        return ["Home", "Local Clinic", "Pharmacy", "Hospital Lobby", "Emergency Room"]

    elif "family" in excuse_lower or "mother" in excuse_lower or "daughter" in excuse_lower:
        return ["Home", "Parent's House", "Grandparent's House", "Community Center", "Grocery Store"]

    elif "internet" in excuse_lower or "power" in excuse_lower:
        return ["Home", "Electric Office", "Cafe", "Wi-Fi Repair Station", "Back Home"]

    elif "traffic" in excuse_lower or "car" in excuse_lower:
        return ["Home", "Highway Exit 17", "Gas Station", "Towing Center", "Mechanic Shop"]

    elif "pet" in excuse_lower or "dog" in excuse_lower or "cat" in excuse_lower:
        return ["Home", "Veterinary Clinic", "Pet Store", "Animal Shelter", "Home Again"]

    return ["Home", "Local Area", "Grocery", "Park", "Back Home"]

def generate_fake_location(excuse_text, name=None):
    if name is None:
        name = extract_name_nlp(excuse_text)

    log = f"Location Log for {name} (supporting the excuse):\n\n"
    current_time = datetime.datetime.now()
    locations = infer_location_sequence_from_excuse(excuse_text)

    for i, place in enumerate(locations):
        timestamp = current_time - datetime.timedelta(minutes=15 * i)
        log += f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {place}\n"

    return log

if __name__ == "__main__":
    excuse = excuse_generator("I need a funny excuse for missing my friend's birthday party. Make it exaggerated.")
    print(generate_fake_document(excuse))
    print(generate_fake_chat_image(excuse))
    print(generate_fake_location(excuse))