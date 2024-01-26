from ShowSuggester import *
from run_config import *

class StateManager:
    
    def __init__(self, current_state, liked_shows=None):
        self.state_functions = {
            1 : {'name' : 'AWAITING_SHOWS', 'handler' : self.handle_awaiting_shows},
            2 : {'name' : 'CONFIRMING_TITLES', 'handler' : self.handle_confirming_titles},
            3 : {'name' : 'MAKING SUGGESTIONS', 'handler' : self.handle_making_suggestions},
            # Add more states and functions as needed
        }
        self.current_state = current_state
        self.liked_shows = liked_shows or []
    
    def handle_awaiting_shows(self, user_input):
        try:
            title_choices = get_title_choices(get_vectors_dict())
            liked_shows_titles = get_liked_shows(user_input=user_input, title_choices=title_choices)
            if liked_shows_titles:
                self.liked_shows = liked_shows_titles
                self.increment_state()
                return [approve_liked_shows_message_for_client(liked_shows_titles)]
            return [not_valid_input_message_for_client]
        except Exception as e:
            return str(e)

    def handle_confirming_titles(self, user_input):
        logging.error(f"user_input: {user_input}")
        match user_input:
            case "y":
                self.increment_state()
                return [approved_message_for_client]
            case "n":
                self.update_liked_shows(None)
                self.decrement_state()
                return [not_approved_message_for_client+"\n"+get_liked_shows_message_for_client]
            case _:
                return ["please choose y/n"]

    def handle_making_suggestions(self, user_input):
        try:
            suggestions, new_shows = main_func(self.liked_shows)
            return output_messages(suggestions, new_shows)
        except Exception as e:
            return ['error ' + str(e)]
        
    def get_response(self, user_input):
        handler = self.state_functions.get(self.current_state)['handler']
        if handler:
            return handler(user_input)
        else:
            return "Unknown state. Please start over."

    def update_liked_shows(self, shows):
        self.liked_shows = shows
    
    def increment_state(self):
        print(self.current_state)
        self.current_state += 1
        print(self.current_state)

    def decrement_state(self):
        self.current_state -= 1

    def set_state(self, state):
        if state in self.state_functions:
            self.current_state = state
        else:
            raise ValueError("Invalid state")
    
    # Optionally, methods to increment/decrement state if applicable
