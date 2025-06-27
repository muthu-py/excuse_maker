from twilio.rest import Client
from generate_exucuse import *

def generate_emergency_sms_and_call_text(excuse_text):
    """
    Uses Gemini to generate a realistic SMS and TTS call message based on an excuse.
    Returns a tuple: (sms_text, call_text)
    """
    prompt = (
        f"Generate two outputs for this emergency excuse:\n"
        f"Excuse: \"{excuse_text}\"\n\n"
        f"1. An EMERGENCY SMS (under 20 words, casual tone, must sound urgent).\n"
        f"2. A CALL SCRIPT for an automated phone call (under 30 words, formal or emotional tone).\n\n"
        f"Format:\n"
        f"SMS: <text>\n"
        f"CALL: <text>"
    )

    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split("\n")
        sms = ""
        call = ""
        for line in lines:
            if line.lower().startswith("sms:"):
                sms = line[4:].strip()
            elif line.lower().startswith("call:"):
                call = line[5:].strip()
        return sms, call
    except Exception as e:
        return "Emergency! Come now!", "There is an urgent situation. Please respond immediately."


def send_real_emergency_sms(to_number, excuse_text, sid, token, from_number):
    """
    Sends an excuse-based emergency SMS using Twilio.
    """
    client = Client(sid, token)
    message_body,_ = generate_emergency_sms_and_call_text(excuse_text)
    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        return f"SMS sent to {to_number} | SID: {message.sid}"
    except Exception as e:
        return f"❌ SMS Error: {e}"

def trigger_emergency_call(to_number, excuse_text, sid, token, from_number):
    """
    Initiates a call using Twilio and reads the excuse via text-to-speech.
    """
    _, call_text = generate_emergency_sms_and_call_text(excuse_text)
    client = Client(sid, token)
    twiml = f'<Response><Say voice="alice">{call_text}</Say></Response>'
    try :
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=from_number
        )
        return f"Call placed to {to_number} | Call SID: {call.sid}"
    except Exception as e:
        return f"❌ Call Error: {e}"

sid = os.getenv("sid")
token = os.getenv("token")
from_number = os.getenv("from_number")
to_number = os.getenv("to_number")


if __name__ == "__main__" :
    excuse = "My brother had a seizure and I had to take him to the emergency room."

    # Send SMS
    print(send_real_emergency_sms(to_number, excuse, sid, token, from_number))

    # Trigger Call
    print(trigger_emergency_call(to_number, excuse, sid, token, from_number))
