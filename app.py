from flask import Flask, render_template, request, jsonify
import requests

# URL of Rasa's server
RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'
ACTION_SERVER_URL = 'http://localhost:5055/webhook'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        user_message = request.json.get('message', '')  # Safely get the message from JSON data
        print("User message:", user_message)

        # Send the user's message to RASA and get the bot's response
        rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
        rasa_response_json = rasa_response.json()

        print("Rasa Response:", rasa_response_json)
        bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that.'

    except Exception as e:
        # Handle exceptions gracefully
        print("An error occurred:", e)
        bot_response = 'An error occurred while processing your request.'

    return jsonify({'response': bot_response})

if __name__ == "__main__":
    app.run(debug=True, port=3000)