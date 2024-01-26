from flask import Flask, request, jsonify, session
from flask_cors import CORS
from run_config import *
from ShowSuggester import *
from StateManager import StateManager
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='logs.log')  

app = Flask(__name__)
app.secret_key = 'alwlda13291@#12dknaw'
CORS(app, supports_credentials=True)
@app.route('/api/resetSession', methods=['POST'])
def reset_session():
    session['state_manager_state'] = 1
    session['state_manager_data'] = None
    
    resp = jsonify(success=True)
    return resp

@app.route('/api/prompt_liked_shows', methods=['GET'])
def prompt_liked_shows():
    session['state_manager_state'] = 1
    session['state_manager_data'] = None
    logging.debug(f"current state: {session['state_manager_state']}")
    return jsonify({'message': get_liked_shows_message_for_client})

    
@app.route('/api/message', methods=['POST'])
def handle_message():
    user_input = request.json['message']
    logging.debug(f"input: {user_input}")

    # Load the current state from the session
    state_data = session.get('state_manager_data', None)
    current_state = session.get('state_manager_state', 1)

    # initialize the state manager with the current state and saved data
    state_manager = StateManager(current_state, state_data)
    logging.debug(f"current state: {current_state}")
    reply = state_manager.get_response(user_input)
    logging.debug(f"reply: {reply}")
    # Save the updated state back to the session
    session['state_manager_state'] = state_manager.current_state
    session['state_manager_data'] = state_manager.liked_shows
    logging.debug(f"updated state: {state_manager.current_state}")


    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
