get_liked_shows_message_for_client = "Which TV shows did you love watching?\nSeparate them by a comma.\nMake sure to enter more than 1 show.\n"
not_valid_input_message_for_client = "Please enter at least 2 shows separated by commas."
def approve_liked_shows_message_for_client(shows_titles):
    return f"Just to make sure, do you mean {','.join(shows_titles)}?(y/n)"

not_approved_message_for_client = "Sorry about that. Lets try again, please make sure to write the names of the tv shows correctly."
# approved_message_for_client = "Great! I'll find you some shows you'll love."
finished_message_for_client = ["Thank you for using our service. Hope you enjoyed it!", "refresh to start over."]

def output_messages(suggestions, new_shows):
    messages = []

    # Text messages
    messages.append({"type": "text", "content": "Here are the tv shows that I think you would love:"})
    for title in suggestions:
        messages.append({"type": "text", "content": f"{title} ({suggestions[title]}%)"})
    
    # new shows and their images
    messages.append({"type": "text", "content": "I have also created just for you two shows which I think you would love."})
    messages.append({"type": "text", "content": f"Show #1 is based on the fact that you loved the input shows that you gave me. Its name is {new_shows[0]['Title']} and it is about {new_shows[0]['Description']}.\n\n"})
    messages.append({"type": "image", "content": new_shows[0]["URL"]}) 
    messages.append({"type": "text", "content": f"Show #2 is based on the shows that I recommended for you. Its name is {new_shows[1]['Title']} and it is about {new_shows[1]['Description']}.\n\n"})
    messages.append({"type": "image", "content": new_shows[1]["URL"]}) 
    

    return messages

def create_response_messages(messages , type = "text"):
    if isinstance(messages, str):
        messages = [{"type": type, "content": messages}]
    else:
        messages = [{"type": type, "content": message} for message in messages]
    return messages