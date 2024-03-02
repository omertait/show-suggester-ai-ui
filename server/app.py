from flask import Flask, request, jsonify, session
from flask_cors import CORS
from run_config import *
from ShowSuggester import *
from StateManager import StateManager
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='logs.log')  

def get_new_shows(end_point, image_dir):
    if not os.path.exists(os.environ.get("NEW_SHOWS_PICKELE_PATH")):
        return []
    
    try:
        new_shows = pickle_load(os.environ.get("NEW_SHOWS_PICKELE_PATH"))
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        logging.error("error in loading new shows")
        return []
    
    shows = []
    for key in new_shows:
        
        logging.info(new_shows[key])   
        if "Title" in new_shows[key] and "Description" in new_shows[key]:
            show_data = {
                'Title': new_shows[key]['Title'],
                'Description': new_shows[key]['Description'],
                'Image': url_for(end_point, filename=f"{image_dir}/{new_shows[key]["Title"]}.png", _external=True) 
            }
            shows.append(show_data)

    return shows

app = Flask(__name__)
app.secret_key = 'alwlda13291@#12dknaw'
CORS(app, supports_credentials=True)
@app.route('/api/resetSession', methods=['POST'])
def reset_session():
    session['state_manager_state'] = 1
    session['state_manager_liked_shows'] = None
    session['state_manager_suggestions'] = None
    
    resp = jsonify(success=True)
    return resp

@app.route('/api/prompt_liked_shows', methods=['GET'])
def prompt_liked_shows():
    session['state_manager_state'] = 1
    session['state_manager_liked_shows'] = None
    session['state_manager_suggestions'] = None
    logging.debug(f"current state: {session['state_manager_state']}")
    logging.debug(f"liked shows: {session['state_manager_liked_shows']}")
    logging.debug(f"suggestions: {session['state_manager_suggestions']}")
    return jsonify({'reply': create_response_messages(get_liked_shows_message_for_client)})

    
@app.route('/api/message', methods=['POST'])
def handle_message():
    user_input = request.json['message']
    logging.debug(f"input: {user_input}")

    # Load the current state from the session
    state_manager_liked_shows = session.get('state_manager_liked_shows', None)
    state_manager_suggestions = session.get('state_manager_suggestions', None)
    current_state = session.get('state_manager_state', 1)

    # initialize the state manager with the current state and saved data
    state_manager = StateManager(current_state=current_state, liked_shows=state_manager_liked_shows, suggestions=state_manager_suggestions)
    logging.debug(f"current state: {current_state} suggestions: {state_manager.suggestions}")
    reply = state_manager.get_response(user_input)
    logging.debug(f"reply: {reply}")
    # Save the updated state back to the session
    session['state_manager_state'] = state_manager.current_state
    session['state_manager_liked_shows'] = state_manager.liked_shows
    session['state_manager_suggestions'] = state_manager.suggestions
    logging.debug(f"current state: {session['state_manager_state']}")
    logging.debug(f"liked shows: {session['state_manager_liked_shows']}")
    logging.debug(f"suggestions: {session['state_manager_suggestions']}")
    logging.debug(f"updated state: {state_manager.current_state}")


    return jsonify({'reply': reply})


@app.route('/api/shows', methods=['GET'])
def get_shows():
    new_shows = get_new_shows(end_point=os.environ.get("IMAGES_ENDPOINT"), image_dir=os.environ.get("IMAGES_DIR"))  # This should return a list of shows
    return jsonify(new_shows)

if __name__ == '__main__':
    app.run(debug=True)
