import base64
import os
import pickle
import re
import logging
import numpy as np
from openai import OpenAI
import pandas as pd
from fuzzywuzzy import process as fuzzy
from PIL import Image
import requests


logging.basicConfig(level= logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='logs.log')
logger = logging.getLogger(__name__)

def init_openAI_client(api_key):
    client = OpenAI(
        api_key=api_key,
    )
    return client

def get_embedding_response(client, input, model):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return response.data[0].embedding

def get_dalle_response(client, prompt, model):
    response = client.images.generate(
        model=model,
        prompt=prompt,
        response_format = "b64_json"
    )
    return response.data[0].b64_json

def create_new_shows(client, liked_shows, recommended_shows):
    new_shows = []
    for shows in [liked_shows, recommended_shows]:
        prompt = f'''made up a new tv show.
        the new tv show sould be similar to the following tv shows: {','.join(shows)}.
        output ONLY tv show title , tv show description .
        the description should be one paragraph max and should not contain the names of the tv shows provided.
        the output format should be exactly:
        Title: show title
        Description : show description
        '''
        messages = [
        {
            "role":"user",
            "content": prompt
        }]
        response = client.chat.completions.create(
                        messages=messages,
                        model="gpt-3.5-turbo",
                    )
        try:
            response_text = response.choices[0].message.content
            logger.debug(response_text)
            # check if the response is valid
            match = re.search(r"Title: (.*?)\s*Description: (.*)", response_text, re.DOTALL)
            logger.debug(match)
            if match:
                new_show_title, new_show_description = match.groups()
                new_shows.append({"Title" : new_show_title.strip(), "Description" : new_show_description.strip()})
            else:
                raise Exception("error generating new show")
        except Exception as e:
            raise e
    return new_shows

def csv_to_df(path, columns):
    df = pd.read_csv(path)
    df = df[columns]
    return df

def pickle_save(obj, file_name):
    with open(file_name,'wb') as f:
        pickle.dump(obj, f)

def pickle_load(file_name):
    with open(file_name,'rb') as f:
        unpickled = pickle.load(f)
    return unpickled

def get_avg_vector(vectors):
    vectors_array = np.array(vectors)  # Convert the list of vectors to a numpy array
    avg_vector = np.mean(vectors_array, axis=0)
    return avg_vector

def get_similarity(vector1, vector2):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

def generate_vectors(client, embedding_model, shows_df):
    vectors_dict = {}
    for ind in shows_df.index:
        print(ind)
        title, description = shows_df['Title'][ind], shows_df['Description'][ind]
        response = get_embedding_response(client=client, model=embedding_model, input=description)
        vectors_dict[title] = response
    return vectors_dict

def get_top_similar_vectors(avg_vector, vectors_dict, top_n=5):
    similarities = {}
    for title, vec in vectors_dict.items():
        similarity = get_similarity(avg_vector, vec)
        similarities[title] = similarity
    
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    max_similarity, min_similarity = sorted_similarities[0][1], sorted_similarities[-1][1]
    sorted_similarities = dict(sorted_similarities[:top_n])
    sorted_similarities_percentage = {title : int((similarity-min_similarity)/(max_similarity-min_similarity)*100) for title, similarity in sorted_similarities.items()}
    
    return sorted_similarities_percentage

def match_title(input, choices):
    logger.debug(f"{type(input)}, {type(choices)}")
    return fuzzy.extractOne(input, choices)[0]

############## new function ##############
def check_correct_titles(liked_shows, title_choices):
    shows_titles = []
    for liked_show in liked_shows:
        shows_titles.append(match_title(liked_show, title_choices))
    return shows_titles

############## new function ##############

def get_liked_shows(title_choices, user_input):
    liked_shows = []
    
    liked_shows = user_input.split(",")
    if len(liked_shows) < 2 or "" in liked_shows:
        return None

    liked_shows = check_correct_titles(liked_shows, title_choices)
    if liked_shows:
        return liked_shows
    return None

def create_new_shows_posters(client, new_shows, model="dall-e-2"):
    for index, new_show in enumerate(new_shows):
        prompt = f"tv show poster for {new_show['Title']}: {new_show['Description']}"   
        new_show_image_base64 =  get_dalle_response(client, prompt, model)
        new_show_image_path = f"server/images/{new_show['Title']}.png"
        # print(new_show_image_base64)
        with open(new_show_image_path, "wb") as fh:
            fh.write(base64.b64decode(new_show_image_base64))
        new_shows[index]["IMAGE"] = new_show_image_path
        
    return new_shows
############## new function ##############
def get_vectors_dict(pickele_path):
    try:
        if not os.path.exists(os.environ.get("PICKELE_PATH")):
            logger.error("pkl not found, generating embeddings")
            raise Exception("pkl not found, generating embeddings")
            client = init_openAI_client(os.environ.get("OPENAI_API_KEY"))
            embedding_model = os.environ.get("MODEL_EMBEDDING")
            shows_df = csv_to_df(os.environ.get("SHOWS_CSV_PATH"), ["Title", "Description"])
            vectors_dict = generate_vectors(client, embedding_model, shows_df)
            pickle_save(vectors_dict, os.environ.get("PICKELE_PATH"))
        else:
            vectors_dict = pickle_load(pickele_path)
        return vectors_dict
    except Exception as e:
        raise e
############## new function ##############
def get_title_choices(vectors_dict):
    try:
        title_choices = [show_title for show_title in vectors_dict.keys()]
        return title_choices
    except Exception as e:
        raise e
############## new function ##############
def main_func(liked_shows, openai_key, model_image_gen, pickele_path, client=None):
    logging.debug(openai_key + " " + model_image_gen + " " + pickele_path)
    vectors_dict = get_vectors_dict(pickele_path)
    vectors_dict_without_liked = {title : vector for title, vector in vectors_dict.items() if title not in liked_shows}
    
    liked_shows_vectors = [vectors_dict.get(show) for show in liked_shows]
    
    avg_vector = get_avg_vector(liked_shows_vectors)
    suggestions = get_top_similar_vectors(avg_vector=avg_vector, vectors_dict=vectors_dict_without_liked)
    recommended_shows = [title for title in suggestions]
    if client == None:
        client = init_openAI_client(openai_key)
    # need to implement - check in new_shoes.pkl if already generated from same liked shows and recommended shows
    new_shows = create_new_shows(client, liked_shows, recommended_shows)
    # for testing - uncomment the following line
    # new_shows = [{"Title" : "Kingdoms and Bloodlines", "Description" : "somthing about the show", "URL" : "https://oaidalleapiprodscus.blob.core.windows.net/private/org-2CwskBzgGP5OnJE5rJP2GrIS/user-xPA8l8GEYMhBTtbf6jwfHEqa/img-0VUfIGKWTllYDWtbf8G1waCd.png?st=2024-01-26T21%3A42%3A02Z&se=2024-01-26T23%3A42%3A02Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-26T22%3A31%3A44Z&ske=2024-01-27T22%3A31%3A44Z&sks=b&skv=2021-08-06&sig=qaV07gg6FDKnvQKr85eQllN0AwRyTViQtjCzlOLaNjM%3D"}, {"Title" : "Shadows of Deception", "Description" : "In a small mysterious town, a group of seemingly ordinary individuals discover dark secrets hidden beneath the surface of their idyllic lives. As they delve deeper into the enigma, they unravel a web of intrigue and lies that connects them in unforeseen ways. Betrayal, deceit, and treacherous alliances become their daily reality as they struggle to uncover the truth and save those they hold dear. Will they succumb to the shadows of deception, or will they find the strength to fight for justice? Step into a world where nothing is as it seems, and trust is a luxury they can't afford..", "URL" : "https://oaidalleapiprodscus.blob.core.windows.net/private/org-2CwskBzgGP5OnJE5rJP2GrIS/user-xPA8l8GEYMhBTtbf6jwfHEqa/img-vOVbRUMYFblb7yi4DYk6mWh6.png?st=2024-01-26T21%3A42%3A14Z&se=2024-01-26T23%3A42%3A14Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-26T22%3A40%3A32Z&ske=2024-01-27T22%3A40%3A32Z&sks=b&skv=2021-08-06&sig=DiGv%2B5SkDVudKbgLen810ZVi5uGksc0GAHQcKhniTEM%3D"}]
    new_shows = create_new_shows_posters(client, new_shows, model_image_gen) 
    return suggestions, new_shows


