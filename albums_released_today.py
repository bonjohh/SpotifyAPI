import os 
import spotipy
import json
import calendar
import datetime
from dotenv import load_dotenv
import pandas as pd

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/create_new_music_playlist')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def show_saved_tracks(saved_results, album_list):
    for item in saved_results['items']:
        track = item['track']
        temp_list = []
        temp_list.append(track['album']['release_date'])
        temp_list.append(track['album']['name'])
        temp_list.append(track['artists'][0]['name'])
        album_list.append(temp_list)
    return album_list

def main(user_id):
    scope = 'user-library-read'
    token = spotipy_token(scope, user_id)

    sp = spotipy.Spotify(auth=token)

    album_list = []

    saved_results = sp.current_user_saved_tracks(limit=50)
    album_list = show_saved_tracks(saved_results, album_list)

    while saved_results['next']:
        saved_results = sp.next(saved_results)
        album_list = show_saved_tracks(saved_results, album_list)

    df = pd.DataFrame(album_list, columns=['release_date_col', 'album_name_col', 'artist_name_col'])
    df.drop_duplicates('album_name_col', inplace=True)

    EST = pytz.timezone('America/New_York')
    today = datetime.datetime.now(EST)
    today = today.strftime("%m-%d")

    print(df[df['release_date_col'].str.contains(today)])
