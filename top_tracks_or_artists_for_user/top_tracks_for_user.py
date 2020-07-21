import json
import spotipy
from dotenv import load_dotenv
import os

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/create_new_music_playlist')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def top_tracks_for_user(username, event=None, context=None):
    scope = 'user-top-read'
    token = spotipy_token(scope, username)
    sp = spotipy.Spotify(auth=token)
    
    ranges = ['short_term', 'medium_term', 'long_term']
    printed_thing = []
    
    for sp_range in ranges:
        printed = ("range:", sp_range)
        printed_thing.append(printed)
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            printed = (i + 1, item['name'], '//', item['artists'][0]['name'])
            printed_thing.append(printed)
    return json.dumps(printed_thing, indent=4, sort_keys=True)
