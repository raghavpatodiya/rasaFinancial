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
        rasa_response.raise_for_status()  # Raise an exception for HTTP errors
        rasa_response_json = rasa_response.json()

        print("Rasa Response:", rasa_response_json)
        bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that.'

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeout errors, etc.
        print("An error occurred while sending the request to Rasa:", e)
        bot_response = 'Sorry, I am currently unable to process your request. Please try again later.'

    except Exception as e:
        # Handle other exceptions gracefully
        print("An error occurred:", e)
        bot_response = 'An unexpected error occurred while processing your request.'

    return jsonify({'response': bot_response})

@app.route('/loc', methods=['GET'])
def loc():
    try:
        # Read the LOC value from the loc.txt file
        with open("loc.txt", "r") as f:
            loc = f.read()
            return jsonify({'loc': loc})
    except Exception as e:
        print("An error occurred while fetching LOC:", e)
        return jsonify({'loc': 'Error fetching LOC'}), 500  # Return a 500 status code for internal server error

if __name__ == "__main__":
    app.run(debug=True, port=3000)



