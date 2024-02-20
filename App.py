from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Environment variables for API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_ENDPOINT = "https://api.google.com/generativeai/"
DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1/completions"

@app.route('/v1/completions', methods=['POST'])
def handle_request():
    # Retrieve the custom OpenAI endpoint if provided, else use the default
    custom_openai_endpoint = request.args.get('openai_endpoint', DEFAULT_OPENAI_ENDPOINT)
    
    data = request.json
    prompt = data.get("prompt")
    max_tokens = data.get("max_tokens", 2048)
    # Extract other necessary parameters from the request

    # Translate to Google's format and send the request
    response = translate_and_forward_request(prompt, max_tokens, custom_openai_endpoint)
    return jsonify(response)

def translate_and_forward_request(prompt, max_tokens, custom_openai_endpoint):
    # Translate request to Google's format
    google_request_data = {
        "prompt": prompt,
        "max_output_tokens": max_tokens,
        # Add other necessary parameters and safety settings
    }

    # Call Google's API
    headers = {"Authorization": f"Bearer {GOOGLE_API_KEY}"}
    response = requests.post(GOOGLE_ENDPOINT, json=google_request_data, headers=headers)
    
    if response.status_code == 200:
        google_response = response.json()
        # Translate Google's response to OpenAI's expected format
        openai_compatible_response = translate_response(google_response)
        
        # Forward the translated response to the custom OpenAI endpoint
        forward_response = forward_to_custom_openai_endpoint(openai_compatible_response, custom_openai_endpoint)
        return forward_response
    else:
        return {"error": "Failed to get response from Google's API"}

def translate_response(google_response):
    # Implement translation logic based on the structure of Google's response
    translated_text = google_response.get("generated_text")
    return {
        "choices": [
            {"text": translated_text}
        ]
    }

def forward_to_custom_openai_endpoint(openai_compatible_response, custom_openai_endpoint):
    # For simplicity, this example forwards the response as-is
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.post(custom_openai_endpoint, json=openai_compatible_response, headers=headers)
    
    if response.status_code == 200:
        # Directly return the response from the custom OpenAI endpoint
        return response.json()
    else:
        return {"error": "Failed to forward response to custom OpenAI endpoint"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
