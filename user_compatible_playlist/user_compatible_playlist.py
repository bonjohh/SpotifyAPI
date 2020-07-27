import spotipy
from dotenv import load_dotenv
import os
import json
import random

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/SpotifyAPI')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def get_artist_id(sp, name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]['id']
    else:
        return None

def create_playlist(sp, user_id, new_playlist_name):
    return_string = sp.user_playlist_create(user_id, new_playlist_name, public=True)    
    return return_string['uri']

def get_recently_liked_playlist_id(sp, new_playlist_name, user_id):
    playlists = sp.current_user_playlists(limit=10) # must keep the new music playlist at the top if you're going to run it again
    playlist_id = ''
    for playlist in playlists['items']:
        if playlist['name'] == new_playlist_name:
            playlist_id = playlist['uri']
            break
    if playlist_id == '':
        playlist_id = create_playlist(sp, user_id, new_playlist_name)
    return playlist_id

def add_playlist_desc(sp, my_user_id, this_user, other_user, playlist_id):
    playlist_id = playlist_id[17:]
    playlist_desc1 = "This is a playlist created from code by John Wilson (bonjohh on spotify). It was created "
    playlist_desc2 = "based on top songs of artists, where the artists are similar to those that both users have "
    playlist_desc3 = "similar interest in. Users are " + this_user + " and " + other_user + "."
    playlist_desc = playlist_desc1 + playlist_desc2 + playlist_desc3
    sp.user_playlist_change_details(my_user_id, playlist_id, description=playlist_desc)

def split_set(total_tracks_set, i, x):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:x]
    elif len(tracks_list) > x:
        split = tracks_list[x*i:x+x*i]
    else:
        split = tracks_list[x*i:len(tracks_list)]
    return split

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

def popularity_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    return results['popularity']

def main(my_user_id_temp, other_user_id):
    global my_user_id
    global token
    my_user_id = my_user_id_temp
    scope = 'playlist-read-private playlist-modify-public user-top-read'
    token_temp = spotipy_token(scope, my_user_id)
    token = token_temp
    sp = spotipy.Spotify(auth=token)

    playlists = sp.user_playlists(other_user_id) # , fields="")

    artist_list = []

    while playlists:
        for playlist in playlists['items']:
            pl_id = playlist['id']
            playlist_tracks = sp.playlist(pl_id) #, fields='items.track.id,total')
            for track in playlist_tracks['tracks']['items']:
                if track['track'] == None:
                    continue
                artists = ''
                artist_num = len(track['track']['artists'])
                if artist_num > 1:
                    artists = track['track']['artists'][0]['name']
                    for j in range(1, artist_num):
                        artists = artists + " " + track['track']['artists'][j]['name']
                else:
                    artists = track['track']['artists'][0]['name']
                if artists in artist_list:
                    for i in range(0, len(artist_list)):
                        if artist_list[i] == artists:
                            artist_list[i+1] += 1
                else:
                    artist_list.append(artists)
                    artist_list.append(1)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    
    ranges = ['short_term', 'medium_term', 'long_term']

    top_artist_list = []

    for sp_range in ranges:
        results = sp.current_user_top_artists(time_range=sp_range, limit=50)
        for item in results['items']:
            artist = item['name']
            if artist in top_artist_list:
                for i in range(0, len(top_artist_list)):
                    if top_artist_list[i] == artist:
                        top_artist_list[i+1] += 1
            else:
                top_artist_list.append(artist)
                top_artist_list.append(1)
        
    compatible_artists_list = []
    compatible_artists_id_list = []

    for k in range(0, len(artist_list) - 1, 2):
        if artist_list[k] in top_artist_list and artist_list[k + 1] > 2:
            compatible_artists_list.append(artist_list[k])
            compatible_artists_list.append(artist_list[k + 1])

    similar_artists = []
    similar_artists_names = []

    for l in range(0, len(compatible_artists_list) - 1, 2):
        artist_id = get_artist_id(sp, compatible_artists_list[l])
        results = sp.artist_related_artists(artist_id)
        compatible_artists_id_list.append(artist_id)
        a = 0
        for artist in results['artists']:
            if artist['popularity'] >= 40 and a < 4:
                similar_artists.append(artist['id'])
                similar_artists_names.append(artist['name'])
                a += 1

    for m in range(0, len(compatible_artists_list) - 1, 2):
        artist_id = get_artist_id(sp, compatible_artists_list[m])
        for artist in results['artists']:
            similar_artists.append(artist_id)
            similar_artists_names.append(compatible_artists_list[m])

    similar_artists = set(similar_artists)
    similar_artists_names = set(similar_artists_names)
    similar_artists_names = list(similar_artists_names)
    random.shuffle(similar_artists_names)

    similar_artists_tracks = []

    for id in similar_artists:
        results = sp.artist_top_tracks(id)
        if id in compatible_artists_id_list:
            for n in range(0, 9):
                similar_artists_tracks.append(results['tracks'][n]['id'])
        else:
            for n in range(0, 4):
                similar_artists_tracks.append(results['tracks'][n]['id'])

    similar_artists_tracks.sort(reverse=True, key=popularity_sort)

    for track in similar_artists_tracks:
        popularity = popularity_sort(track)
        if popularity < 40:
            similar_artists_tracks.remove(track)

    other_user = sp.user(other_user_id)
    other_user = other_user['display_name']
    this_user = sp.user(my_user_id)
    this_user = this_user['display_name']

    playlist_name = "Compatibility Playlist: " + this_user + " + " + other_user

    playlist_id = get_recently_liked_playlist_id(sp, playlist_name, my_user_id)

    already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id)
    
    split_range = int(len(already_on_tracks_list) / 100) + 1
    for i in range(0, split_range):
        split = split_set(already_on_tracks_list, i, 100)
        sp.user_playlist_remove_all_occurrences_of_tracks(my_user_id, playlist_id, split)

    add_playlist_desc(sp, my_user_id, this_user, other_user, playlist_id)

    similar_artists_tracks_length = len(similar_artists_tracks)
    if similar_artists_tracks_length > 0:
        split_range = int(similar_artists_tracks_length / 100) + 1
        for i in range(0, split_range):
            split = split_set(similar_artists_tracks, i, 100)
            sp.user_playlist_add_tracks(my_user_id, playlist_id, split)

    create_status = str(similar_artists_tracks_length) + " songs added to playlist: [" + playlist_name + "]"
    
    response = {
        "Status": create_status,
        "Compatible Artists": similar_artists_names
    }
    return response

if __name__ == "__main__":
    # print(main("jwilso29", "1251692081"))
    print(main("jwilso29", "calamityclaire14"))
    # print(main("jwilso29", "1210157395"))