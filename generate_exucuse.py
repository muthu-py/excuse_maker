import google.generativeai as genai
import spacy
import os
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
def excuse_generator(prompt_text):
    context, urgency, tone, believability = infer_parameters_from_prompt(prompt_text)

    prompt = (
        f"You are an AI excuse generator. Create a believable excuse using the following settings:\n"
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
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating excuse: {e}"

if __name__ == "__main__":
    print(excuse_generator("I need a funny excuse for missing my friend's birthday party. Make it exaggerated."))

    #print(excuse_generator("Make me a formal excuse for skipping my boss’s meeting due to an emergency."))

    #print(excuse_generator("Give me a creative but believable excuse for missing class today."))
