import spotipy
from dotenv import load_dotenv
import os
import json
import pprint
from time import time

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/SpotifyAPI')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = 'BQATt35y9lFYl3uq5pcNJey65-gqGPMfikxnS72xVyhMMn59DPtV-vNrq7gZu2iOk19XstCVPv5i1MshCbOQhGPwEMUlgQcZtkcV_eXkIW8fNrU9kPOMUphy2teYhSXOrQF_CiQt6tGrFFI0IeZcIx-x_EzfkjfrZk1zn6FDTTXyR5Rh42-dzKOyGeFOqYOrRTjwADDIYG4NDUVNOjGJXhY5MLo0Cr6OEw'#spotipy.util.prompt_for_user_token(username, scope)
    return token

def populate_total_track_list(results, total_tracks_list):
    for item in results['items']:
        track = item['track']
        total_tracks_list.append(track['uri'])
    return total_tracks_list 

def split_set(total_tracks_set, i, x):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:x]
    elif len(tracks_list) > x:
        split = tracks_list[x*i:x+x*i]
    else:
        split = tracks_list[x*i:len(tracks_list)]
    return split

def create_playlist(sp, user_id, new_playlist_name):
    return_string = sp.user_playlist_create(user_id, new_playlist_name, public=True)    
    return return_string['uri']

def get_playlist_id(sp, new_playlist_name, user_id):
    playlists = sp.current_user_playlists(limit=50) # must keep the new music playlist at the top if you're going to run it again
    playlist_id = ''
    for playlist in playlists['items']:
        if playlist['name'] == new_playlist_name:
            playlist_id = playlist['uri']
            break
    if playlist_id == '':
        playlist_id = create_playlist(sp, user_id, new_playlist_name)
    return playlist_id

def add_playlist_desc(sp, user_id, playlist_id, setting):
    playlist_id = playlist_id[17:]
    playlist_desc1 = "This is a playlist created from code by John Wilson (bonjohh on spotify). It was created "
    playlist_desc2 = "based on songs that match the setting: " + str.title(setting) + "."
    playlist_desc = playlist_desc1 + playlist_desc2
    sp.user_playlist_change_details(user_id, playlist_id, description=playlist_desc)

def add_tracks_already_on_playlist(sp, playlist_id):
    already_on_list = []
    response = sp.playlist_tracks(playlist_id, fields='items.track.uri,total,next')
    if response['total'] > 0:
        for track in response['items']:
            already_on_list.append(track['track']['uri'])
        while response['next']:
            response = sp.next(response)
            for track in response['items']:
                already_on_list.append(track['track']['uri'])
    else:
        return already_on_list
    return already_on_list

def print_track_details(sp, track, score):
    track_details = sp.track(track)
    print(track_details['name'] + " ----- " + track_details['album']['name'] + " ------ " \
        + track_details['artists'][0]['name'] + " ------ " + str(score))

def morning_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    popularity = results['popularity']
    audio_features_result = sp.audio_features(track)     
    acousticness = audio_features_result[0]['acousticness']
    energy = audio_features_result[0]['energy']
    loudness = audio_features_result[0]['loudness']
    tempo = audio_features_result[0]['tempo']
    morning_score = 3 * (popularity / 100) \
        + 2 * acousticness \
        + 1.5 * energy \
        + 2 * (abs(loudness) / 100) \
        + 1.5 * (tempo / 100)
    # print_track_details(sp, track, morning_score)
    return morning_score
    
def exercise_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    popularity = results['popularity']
    audio_features_result = sp.audio_features(track)     
    acousticness = audio_features_result[0]['acousticness']
    energy = audio_features_result[0]['energy']
    loudness = audio_features_result[0]['loudness']
    tempo = audio_features_result[0]['tempo']
    danceability = audio_features_result[0]['danceability']
    exercise_score = 2.5 * (popularity / 100) \
        + 1.5 * (-1 * acousticness) \
        + 2 * energy \
        + 1.5 * (loudness / 100) \
        + 1.5 * (tempo / 100) \
        + 1 * danceability
    # print_track_details(sp, track, exercise_score)
    return exercise_score

def pregame_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    popularity = results['popularity']
    audio_features_result = sp.audio_features(track)     
    valence = audio_features_result[0]['valence']
    energy = audio_features_result[0]['energy']
    loudness = audio_features_result[0]['loudness']
    tempo = audio_features_result[0]['tempo']
    danceability = audio_features_result[0]['danceability']
    pregame_score = 2.5 * (popularity / 100) \
        + 1 * energy \
        + 2 * valence \
        + 1.5 * (loudness / 100) \
        + 1 * (tempo / 100) \
        + 2 * danceability
    # print_track_details(sp, track, pregame_score)
    return pregame_score

def live_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    popularity = results['popularity']
    audio_features_result = sp.audio_features(track)  
    liveness = audio_features_result[0]['liveness']
    energy = audio_features_result[0]['energy']
    loudness = audio_features_result[0]['loudness']
    danceability = audio_features_result[0]['danceability']
    instrumentalness = audio_features_result[0]['instrumentalness']
    live_score = 1.5 * (popularity / 100) \
        + 3.5 * liveness \
        + 1 * energy \
        + 1 * (loudness / 100) \
        + 1.5 * danceability \
        + 1.5 * instrumentalness
    # print_track_details(sp, track, live_score)
    return live_score
    
def main(user_id, saved_bool, playlist_bool, setting):
    start = time()
    global token
    scope = 'playlist-read-private user-library-read user-top-read playlist-modify-public'
    token = spotipy_token(scope, user_id)    
    sp = spotipy.Spotify(auth=token)

    total_tracks_list = []

    if saved_bool == True:
        saved_tracks_results = sp.current_user_saved_tracks(limit=10)
        total_tracks_list = populate_total_track_list(saved_tracks_results, total_tracks_list)
        while saved_tracks_results['next']:
            saved_tracks_results = sp.next(saved_tracks_results)
            total_tracks_list = populate_total_track_list(saved_tracks_results, total_tracks_list)

    if playlist_bool == True:
        playlists = sp.user_playlists(user_id)
        while playlists:
            for playlist in playlists['items']:
                playlist_results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = playlist_results['tracks']
                total_tracks_list = populate_total_track_list(tracks, total_tracks_list)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    total_tracks_list = populate_total_track_list(tracks, total_tracks_list)
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None

    total_tracks_list = set(total_tracks_list)
    total_tracks_list = list(total_tracks_list)

    setting_tracks_list = []

    total_tracks_list_length = len(total_tracks_list)
    if total_tracks_list_length > 0:
        split_range = int(total_tracks_list_length / 100) + 1
        for i in range(0, split_range):
            split = split_set(total_tracks_list, i, 100)
            audio_features_results = sp.audio_features(split)
            for track in audio_features_results:
                if setting == "morning":
                    if track['acousticness'] > 0.6 \
                        and track['energy'] < 0.3 \
                        and track['loudness'] < -10 \
                        and track['tempo'] < 100:
                        setting_tracks_list.append(track['uri'])
                elif setting == "exercise":
                    if track['acousticness'] < 0.2 \
                        and track['energy'] > 0.8 \
                        and track['loudness'] > -10 \
                        and track['tempo'] > 130 \
                        and track['danceability'] > 0.5:
                        setting_tracks_list.append(track['uri'])
                elif setting == "pregame":
                    if track['energy'] > 0.4 \
                        and track['loudness'] > -10 \
                        and track['tempo'] > 110 \
                        and track['valence'] > 0.5 \
                        and track['danceability'] > 0.7:
                        setting_tracks_list.append(track['uri'])
                elif setting == "live":
                    if track['liveness'] > 0.6 \
                        and track['instrumentalness'] > 0.05:
                        setting_tracks_list.append(track['uri'])

    # for track_uri in setting_tracks_list:
    #     track = sp.track(track_uri)
    #     print(track['name'] + " ----- " + track['album']['name'] + " ----- " + track['artists'][0]['name'])
    
    if setting == "morning":
        setting_tracks_list.sort(reverse=True, key=morning_sort)
    elif setting == "exercise":
        setting_tracks_list.sort(reverse=True, key=exercise_sort)
    elif setting == "pregame":
        setting_tracks_list.sort(reverse=True, key=pregame_sort)
    elif setting == "live":
        setting_tracks_list.sort(reverse=True, key=live_sort)

    playlist_name = "Audio Analysis Playlist: " + str.title(setting)

    playlist_id = get_playlist_id(sp, playlist_name, user_id)

    already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id)
    
    if len(already_on_tracks_list) > 0:
        split_range = int(len(already_on_tracks_list) / 100) + 1
        for i in range(0, split_range):
            split = split_set(already_on_tracks_list, i, 100)
            sp.user_playlist_remove_all_occurrences_of_tracks(user_id, playlist_id, split)

    add_playlist_desc(sp, user_id, playlist_id, setting)

    setting_tracks_list_length = len(setting_tracks_list)
    if setting_tracks_list_length > 200:
        split_range = 2
        for i in range(0, split_range):
            split = split_set(setting_tracks_list, i, 100)
            sp.user_playlist_add_tracks(user_id, playlist_id, split)
    else:
        split_range = int(setting_tracks_list_length / 100) + 1
        for i in range(0, split_range):
            split = split_set(setting_tracks_list, i, 100)
            sp.user_playlist_add_tracks(user_id, playlist_id, split)
    
    print(time() - start)

if __name__ == "__main__":
    # pass
    main("jwilso29", True, False, setting="morning")
    # main("jwilso29", True, False, setting="exercise")
    # main("jwilso29", True, False, setting="pregame")
    # main("jwilso29", True, False, setting="live")