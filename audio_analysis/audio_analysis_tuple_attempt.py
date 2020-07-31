import spotipy
from dotenv import load_dotenv
import os
import json
import pprint
from time import time

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/SpotifyAPI')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def populate_audio_features(sp, total_tracks_tuple):
    temp_tracks_list = []
    num_type = len(total_tracks_tuple) / 100
    if isinstance(num_type, int):
        split_range = int(len(total_tracks_tuple) / 100)
    else:
        split_range = int(len(total_tracks_tuple) / 100) + 1
    for i in range(0, split_range):
        uri_list = []
        split = split_set(total_tracks_tuple, i, 100)
        for split_tuple in split:
            uri = split_tuple[0]
            uri_list.append(uri)
        track_audio_features = sp.audio_features(uri_list)
        for l in range(0, len(track_audio_features)):
            acousticness = track_audio_features[l]['acousticness']
            energy = track_audio_features[l]['energy']
            valence = track_audio_features[l]['valence']
            loudness = track_audio_features[l]['loudness']
            tempo = track_audio_features[l]['tempo']
            danceability = track_audio_features[l]['danceability']
            liveness = track_audio_features[l]['liveness']
            instrumentalness = track_audio_features[l]['instrumentalness']
            temp_list = [acousticness, energy, valence, loudness, tempo, \
                danceability, liveness, instrumentalness]
            temp_list = list(split[l]) + temp_list
            temp_tracks_list.append(temp_list)
        temp_total_tracks_tuple = ('first value', )
        for track in temp_tracks_list:
            temp_total_tracks_tuple = temp_total_tracks_tuple + (tuple(track), )
    temp_total_tracks_tuple = tuple(x for x in temp_total_tracks_tuple if 'first value' not in x)
    return temp_total_tracks_tuple

def populate_total_tracks(sp, results, total_tracks_tuple):
    for item in results['items']:
        track = item['track']
        uri = track['uri']
        track_name = track['name']
        album_name = track['album']['name']
        artist_name = track['artists'][0]['name']
        track_id = track['id']
        popularity = track['popularity']
        temp_track_tuple = ((uri, track_name, album_name, artist_name, track_id, popularity), )
        total_tracks_tuple = total_tracks_tuple + (temp_track_tuple)
    return total_tracks_tuple

def split_set(total_tracks_tuple, i, x):
    if i == 0:
        split = total_tracks_tuple[:x]
    elif len(total_tracks_tuple) > x:
        split = total_tracks_tuple[x*i:x+x*i]
    else:
        split = total_tracks_tuple[x*i:len(total_tracks_tuple)]
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

def print_track_details(track, score):
    print(track[1] + " ----- " + track[2] + " ------ " + track[3] + " ------ " + str(score))

def morning_sort(track):
    popularity = track[5]
    acousticness = track[6]
    energy = track[7]
    loudness = track[9]
    tempo = track[10]
    morning_score = 3 * (popularity / 100) \
        + 2 * acousticness \
        + 1.5 * energy \
        + 2 * (abs(loudness) / 100) \
        + 1.5 * (tempo / 100)
    # print_track_details(track, morning_score)
    return morning_score
    
def exercise_sort(track):
    popularity = track[5]
    acousticness = track[6]
    energy = track[7]
    loudness = track[9]
    tempo = track[10]
    danceability = track[11]
    exercise_score = 2.5 * (popularity / 100) \
        + 1.5 * (-1 * acousticness) \
        + 2 * energy \
        + 1.5 * (loudness / 100) \
        + 1.5 * (tempo / 100) \
        + 1 * danceability
    # print_track_details(track, exercise_score)
    return exercise_score

def pregame_sort(track):
    popularity = track[5]
    valence = track[8]
    energy = track[7]
    loudness = track[9]
    tempo = track[10]
    danceability = track[11]
    pregame_score = 2.5 * (popularity / 100) \
        + 1 * energy \
        + 2 * valence \
        + 1.5 * (loudness / 100) \
        + 1 * (tempo / 100) \
        + 2 * danceability
    # print_track_details(track, pregame_score)
    return pregame_score

def live_sort(track):
    popularity = track[5]
    liveness = track[12]
    instrumentalness = track[13]
    energy = track[7]    
    loudness = track[9]
    danceability = track[11]
    live_score = 1.5 * (popularity / 100) \
        + 3.5 * liveness \
        + 1 * energy \
        + 1 * (loudness / 100) \
        + 1.5 * danceability \
        + 1.5 * instrumentalness
    # print_track_details(track, live_score)
    return live_score
    
def main(user_id, saved_bool, playlist_bool, setting):
    start = time()
    global token
    scope = 'playlist-read-private user-library-read user-top-read playlist-modify-public'
    token = spotipy_token(scope, user_id)    
    sp = spotipy.Spotify(auth=token)

    total_tracks_tuple = ('first value', )

    if saved_bool == True:
        saved_tracks_results = sp.current_user_saved_tracks(limit=50)
        total_tracks_tuple = populate_total_tracks(sp, saved_tracks_results, total_tracks_tuple)
        while saved_tracks_results['next']:
            saved_tracks_results = sp.next(saved_tracks_results)
            total_tracks_tuple = populate_total_tracks(sp, saved_tracks_results, total_tracks_tuple)

    if playlist_bool == True:
        playlists = sp.user_playlists(user_id)
        while playlists:
            for playlist in playlists['items']:
                playlist_results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = playlist_results['tracks']
                total_tracks_tuple = populate_total_tracks(sp, tracks, total_tracks_tuple)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    total_tracks_tuple = populate_total_tracks(sp, tracks, total_tracks_tuple)
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None

    total_tracks_tuple = total_tracks_tuple[1:]

    total_tracks_tuple = populate_audio_features(sp, total_tracks_tuple)

    total_tracks_tuple = set(total_tracks_tuple)
    total_tracks_tuple = tuple(total_tracks_tuple)

    setting_tracks_list = []

    total_tracks_tuple_length = len(total_tracks_tuple)
    if total_tracks_tuple_length > 0:
        for track in total_tracks_tuple:
            acousticness = track[6]
            energy = track[7]
            valence = track[8]
            loudness = track[9]
            tempo = track[10]
            danceability = track[11]
            liveness = track[12]
            instrumentalness = track[13]
            if setting == "morning":
                if acousticness > 0.6 \
                    and energy < 0.3 \
                    and loudness < -10 \
                    and tempo < 100:
                    setting_tracks_list.append(track)
            elif setting == "exercise":
                if acousticness < 0.2 \
                    and energy > 0.8 \
                    and loudness > -10 \
                    and tempo > 130 \
                    and danceability > 0.5:
                    setting_tracks_list.append(track)
            elif setting == "pregame":
                if energy > 0.4 \
                    and loudness > -10 \
                    and tempo > 110 \
                    and valence > 0.5 \
                    and danceability > 0.7:
                    setting_tracks_list.append(track)
            elif setting == "live":
                if liveness > 0.6 \
                    and instrumentalness > 0.05:
                    setting_tracks_list.append(track)

    # for track in setting_tracks_list:
    #     print(track[1] + " ----- " + track[2] + " ----- " + track[3])
    
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
            uri_list = []
            for track in setting_tracks_list:
                uri_list.append(track[0])
            split = split_set(uri_list, i, 100)
            sp.user_playlist_add_tracks(user_id, playlist_id, split)
    
    print(time() - start)

if __name__ == "__main__":
    # pass
    main("jwilso29", True, False, setting="morning")
    # main("jwilso29", True, False, setting="exercise")
    # main("jwilso29", True, False, setting="pregame")
    # main("jwilso29", True, False, setting="live")