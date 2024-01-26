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

from dotenv import load_dotenv

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
    )
    return response.data[0].url

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
            match = re.search(r"Title: (.*?)\n?Description: (.*)", response_text)
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
        new_show_image_url =  get_dalle_response(client, prompt, model)
        new_shows[index]["URL"] = new_show_image_url
        
    return new_shows
############## new function ##############
def get_vectors_dict():
    try:
        # if not os.path.exists(os.environ.get("PICKELE_PATH")):
        #     logger.error("pkl not found, generating embeddings")
        #     client = init_openAI_client(os.environ.get("OPENAI_API_KEY"))
        #     embedding_model = os.environ.get("MODEL_EMBEDDING")
        #     shows_df = csv_to_df(os.environ.get("SHOWS_CSV_PATH"), ["Title", "Description"])
        #     vectors_dict = generate_vectors(client, embedding_model, shows_df)
        #     pickle_save(vectors_dict, os.environ.get("PICKELE_PATH"))
        # else:
        vectors_dict = pickle_load("server/vectors_dict.pkl")
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
def main_func(liked_shows, client=None):
    load_dotenv()
    vectors_dict = get_vectors_dict()
    vectors_dict_without_liked = {title : vector for title, vector in vectors_dict.items() if title not in liked_shows}
    
    liked_shows_vectors = [vectors_dict.get(show) for show in liked_shows]
    
    avg_vector = get_avg_vector(liked_shows_vectors)
    suggestions = get_top_similar_vectors(avg_vector=avg_vector, vectors_dict=vectors_dict_without_liked)
    recommended_shows = [title for title in suggestions]
    if client == None:
        client = init_openAI_client(os.environ.get("OPENAI_API_KEY"))
    new_shows = create_new_shows(client, liked_shows, recommended_shows)
    new_shows = create_new_shows_posters(client, new_shows, os.environ.get("MODEL_IMAGE_GEN"))
    return suggestions, new_shows


