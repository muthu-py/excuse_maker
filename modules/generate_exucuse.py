import google.generativeai as genai
import spacy
import os
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API = os.getenv("API")

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# Configure Gemini
genai.configure(api_key=API)  # Keep this secret in real use
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# NLP-based parameter extraction
def infer_parameters_from_prompt(prompt: str):
    prompt = prompt.lower()
    doc = nlp(prompt)

    # Context
    if any(word in prompt for word in ["school", "exam", "class", "assignment"]):
        context = "school"
    elif any(word in prompt for word in ["office", "meeting", "boss", "client", "work", "project"]):
        context = "work"
    elif any(word in prompt for word in ["mother", "father", "family", "sister", "daughter", "son"]):
        context = "family"
    elif any(word in prompt for word in ["friend", "party", "hangout", "wedding"]):
        context = "social"
    else:
        context = "general"

    # Urgency
    if "urgent" in prompt or "emergency" in prompt or "critical" in prompt:
        urgency = "high"
    elif "not serious" in prompt or "low priority" in prompt:
        urgency = "low"
    else:
        urgency = "moderate"

    # Tone
    if "funny" in prompt or "joke" in prompt:
        tone = "funny"
    elif "emotional" in prompt or "sad" in prompt:
        tone = "emotional"
    elif "professional" in prompt or "formal" in prompt:
        tone = "professional"
    else:
        tone = "neutral"

    # Believability
    if "make it real" in prompt or "believable" in prompt:
        believability = "realistic"
    elif "make it interesting" in prompt or "creative" in prompt:
        believability = "creative"
    elif "exaggerate" in prompt or "over the top" in prompt:
        believability = "exaggerated"
    else:
        believability = "realistic"

    return context, urgency, tone, believability

# Unified function
def excuse_generator(prompt_text, language="en"):
    context, urgency, tone, believability = infer_parameters_from_prompt(prompt_text)

    prompt = (
        f"You are an AI excuse generator. Create a believable excuse using the following settings:\n"
        f"Respond only in this language: {language}.\n"
        f"- Context: {context}\n"
        f"- Urgency: {urgency}\n"
        f"- Tone: {tone}\n"
        f"- Believability: {believability}\n\n"
        f"Instructions:\n"
        f"- Keep the excuse under 60 words.\n"
        f"- Match the tone and urgency appropriately.\n"
        f"- For 'realistic' believability, keep things subtle.\n"
        f"- For 'creative', invent something interesting but possible.\n"
        f"- For 'exaggerated', allow some over-the-top storytelling.\n"
        f"- Make sure the excuse fits naturally in a real-life situation."
        f"also use this for clarification {prompt_text}"
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating excuse: {e}"
    

# === Apology Generator (Feature 5) ===

def infer_apology_tone_from_excuse(excuse):
    excuse = excuse.lower()
    if any(word in excuse for word in ["manager", "boss", "work", "office", "project", "meeting"]):
        return "professional"
    elif any(word in excuse for word in ["mother", "father", "sick", "daughter", "grandpa", "emergency"]):
        return "emotional"
    elif any(word in excuse for word in ["fire", "accident", "collapsed", "fainted"]):
        return "dramatic"
    elif any(word in excuse for word in ["party", "hangout", "birthday", "overslept", "netflix"]):
        return "funny"
    else:
        return "neutral"

def generate_apology(prompt_text, language="en"):
    excuse = excuse_generator(prompt_text, language=language)
    tone = infer_apology_tone_from_excuse(excuse)

    prompt = (
        f"Write an apology message for this excuse:\n"
        f"Respond only in this language: {language}.\n"
        f"\"{excuse}\"\n"
        f"The tone should be: {tone}\n"
        f"It should sound realistic, slightly guilt-tripping, and sincere. Keep it under 80 words."
        f"also use this for clarification {prompt_text}"
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating apology: {e}"

def save_excuse_audio(text, output_path="excuse_audio.mp3", language="en"):
    """
    Converts the given text into speech and saves it as an MP3.
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        return f"Audio saved at: {output_path}"
    except Exception as e:
        return f"Error generating audio: {e}"



if __name__ == "__main__":
    prompt_input = "I need a funny excuse for missing my friend's birthday party. Make it exaggerated."
    
    print("=== Excuse ===")
    excuse = excuse_generator(prompt_input)
    print(excuse)

    print("\n=== Apology ===")
    apology = generate_apology(prompt_input)
    print(apology)

    print(save_excuse_audio(excuse, output_path="excuse_voice.mp3"))
    #print(excuse_generator("Make me a formal excuse for skipping my boss's meeting due to an emergency."))

    #print(excuse_generator("Give me a creative but believable excuse for missing class today."))
