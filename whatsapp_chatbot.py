import os
import openai
import requests
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VONAGE_API_KEY = os.getenv("VONAGE_API_KEY")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")

# Debugging: Print keys (WARNING: Remove these in production)
print("DEBUG: OPENAI_API_KEY =", OPENAI_API_KEY)
print("DEBUG: VONAGE_API_KEY =", VONAGE_API_KEY)
print("DEBUG: VONAGE_API_SECRET =", VONAGE_API_SECRET)
print("DEBUG: WHATSAPP_NUMBER =", WHATSAPP_NUMBER)

# Ensure all keys are set
if not all([OPENAI_API_KEY, VONAGE_API_KEY, VONAGE_API_SECRET, WHATSAPP_NUMBER]):
    raise ValueError("Missing API keys. Please check your environment variables.")

# Initialize OpenAI Client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def chat_with_gpt(user_message):
    """Send user message to OpenAI and return the response."""
    response = openai_client.chat.completions.create(
        model="gpt-4o",  # Update this if needed
        messages=[
            {"role": "system", "content": "You are Nyx, a dynamic AI assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming WhatsApp messages and generates a response."""
    data = request.get_json()

    if "message" in data and "content" in data["message"]:
        user_message = data["message"]["content"]
        sender = data["from"]

        chatgpt_response = chat_with_gpt(user_message)
        send_whatsapp_message(sender, chatgpt_response)

    return jsonify({"status": "ok"}), 200

def send_whatsapp_message(to, message):
    """Send a WhatsApp message using the Vonage API."""
    url = "https://messages-sandbox.nexmo.com/v1/messages"

    # Encode API Key and Secret for authentication
    auth_header = base64.b64encode(f"{VONAGE_API_KEY}:{VONAGE_API_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "14157386102",  # Vonage WhatsApp sandbox number
        "to": "447903372740",  # Recipient phone number (no + sign)
        "message_type": "text",
        "text": message,
        "channel": "whatsapp"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Sent message to {to}: {response.status_code}, {response.json()}")

if __name__ == "__main__":
    app.run(port=5000)
