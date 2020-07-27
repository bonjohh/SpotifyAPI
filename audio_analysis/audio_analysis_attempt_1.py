import spotipy
from dotenv import load_dotenv
import os
import json

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/SpotifyAPI')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def main(user_id):
    scope = 'playlist-read-private'
    token = spotipy_token(scope, user_id)    
    sp = spotipy.Spotify(auth=token)

    # results = sp.