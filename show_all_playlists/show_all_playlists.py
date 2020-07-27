import spotipy
from dotenv import load_dotenv
import os
import json

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/create_new_music_playlist')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def show_all_playlists(user_id):
    scope = 'playlist-read-private'
    token = spotipy_token(scope, user_id)    
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(user_id)
    playlist_list = []
    i = 1
    while playlists:
        for playlist in playlists['items']:
            playlist_name =  "%s" % (playlist['name'])
            playlist_uri = "%s" % (playlist['uri'])
            playlist_owner = "%s" % (playlist['owner']['id'])
            total_tracks = "%d" % (playlist['tracks']['total'])
            playlist_output = "%3d %35.35s %45.45s %15.15s %15.15s" % (i, playlist_name, playlist_uri, playlist_owner, total_tracks)
            playlist_list.append(playlist_output)
            i += 1
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
            
    return json.dumps(playlist_list, indent=4, sort_keys=True)