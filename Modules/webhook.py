from Modules import universal
from Modules import secretkeys
import time
from flask import Flask, request, jsonify
import requests


app = Flask(__name__)
streamer = None
SERVER_URL = secretkeys.load_secret("WEBHOOK_URL")

app = Flask(__name__)

def webhookout(data):
    with app.app_context():
        try:

            print(f"sending data to: {SERVER_URL}")
            response = requests.post(f"{SERVER_URL}", json=data)
            response.raise_for_status()  # Handle HTTP errors
            return "OK"
        except requests.exceptions.RequestException as e:
            universal.error_code(f"Connection with server lost! {str(e)}")
            #internally log the trade data below
            return "ERROR"
    

#rewrite to modify to the above style of sending data

#send heart beat notification to server
@app.route('/send-heart', methods=["GET"])
def send_heart(data):
    global SERVER_URL
    # Post request to the other server
    try:
        
        time.sleep(30)
        response = requests.post(SERVER_URL, json=data)
        # Return the response from the other server
        return jsonify({'status': 'data sent', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the POST request
        universal.error_code("connection with server lost!")
        
        #after error code figure out design for what to do with the data that can't be sent
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Start the Flask app
     app.run(host="0.0.0.0", port=80, debug=True)