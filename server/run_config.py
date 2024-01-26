get_liked_shows_message_for_client = "Which TV shows did you love watching?\nSeparate them by a comma.\nMake sure to enter more than 1 show.\n"
not_valid_input_message_for_client = "Please enter at least 2 shows separated by commas."
def approve_liked_shows_message_for_client(shows_titles):
    return f"Just to make sure, do you mean {','.join(shows_titles)}?(y/n)"

not_approved_message_for_client = "Sorry about that. Lets try again, please make sure to write the names of the tv shows correctly."
# approved_message_for_client = "Great! I'll find you some shows you'll love."
finished_message_for_client = ["Thank you for using our service. Hope you enjoyed it!", "refresh to start over."]

def output_messages(suggestions, new_shows):
    messages = []
    messages.append("Here are the tv shows that i think you would love:")
    for title in suggestions:
        messages.append(f"{title} ({suggestions[title]}%)")
    
    messages.append("I have also created just for you two shows which I think you would love.")
    messages.append(f"Show #1 is based on the fact that you loved the input shows that you gave me.\nIts name is {new_shows[0]['Title']}\nand it is about {new_shows[0]['Description']}.\n\n")
    messages.append(f"Show #2 is based on the shows that I recommended for you.\nIts name is {new_shows[1]['Title']}\nand it is about {new_shows[1]['Description']}.\n\n")
    messages.append("Here are also the 2 tv show ads. Hope you like them!")
    return messages
    # for new_show in new_shows:
    #     img = Image.open(requests.get(new_show["URL"], stream=True).raw)
    #     img.show() 