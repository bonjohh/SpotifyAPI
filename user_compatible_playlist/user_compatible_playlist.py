import spotipy
from dotenv import load_dotenv
import os
import json
import random
import time
 
def spotipy_token(scope, username):
    #project_folder = os.path.expanduser('D:/Documents/Python_Course/SpotifyAPI')
    project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def create_playlist(sp, user_id, new_playlist_name):
    return_string = sp.user_playlist_create(user_id, new_playlist_name, public=True)    
    return return_string['uri']

def get_compatible_playlist_id(sp, new_playlist_name, user_id):
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

def populate_combined_liked_list(results, combined_liked_list):
    for track in results['items']:
        if track['track'] == None:
            continue
        artists = ''
        artist_num = len(track['track']['artists'])
        if artist_num > 1:
            artists = track['track']['artists'][0]['name']
            artists_id = track['track']['artists'][0]['id']
            for j in range(1, artist_num):
                artists = artists + "|||" + track['track']['artists'][j]['name']
                artists_id = artists_id + "|||" + track['track']['artists'][j]['id']
        else:
            artists = track['track']['artists'][0]['name'] + "|||"
            artists_id = track['track']['artists'][0]['id'] + "|||"
        artists_split = artists.split("|||")
        artists_id_split = artists_id.split("|||")
        for artist in artists_split:
            for artist_id in artists_id_split:
                if artist in combined_liked_list:
                    artists_index = combined_liked_list.index(artist)
                    combined_liked_list[artists_index + 1] += 1
                else:
                    combined_liked_list.append(artist)
                    combined_liked_list.append(1)
                    combined_liked_list.append(artist_id)
    return combined_liked_list

def main(my_user_id_temp, other_user_id, choice):
    start_time = time.time()
    global my_user_id
    global token
    my_user_id = my_user_id_temp
    scope = 'playlist-read-private user-library-read playlist-modify-public user-top-read'
    token_temp = spotipy_token(scope, my_user_id)
    token = token_temp
    sp = spotipy.Spotify(auth=token)

    continue_bool = False
    while continue_bool != True:
        playlists = sp.user_playlists(other_user_id)

        artist_list = []
        artist_id_list = []

        while playlists:
            for playlist in playlists['items']:
                pl_id = playlist['id']
                playlist_tracks = sp.playlist(pl_id, fields='tracks.items.track.artists.name,tracks.items.track.artists.id')
                for track in playlist_tracks['tracks']['items']:
                    if track['track'] == None:
                        continue
                    artists = ''
                    artist_num = len(track['track']['artists'])
                    if artist_num > 1:
                        artists = track['track']['artists'][0]['name']
                        artists_id = track['track']['artists'][0]['id']
                        for j in range(1, artist_num):
                            artists = artists + "|||" + track['track']['artists'][j]['name']
                            artists_id = artists_id + "|||" + track['track']['artists'][j]['id']
                    else:
                        artists = track['track']['artists'][0]['name']
                        artist_id = track['track']['artists'][0]['id']
                    if artists in artist_list:
                        artists_index = artist_list.index(artists)
                        artist_list[artists_index + 1] += 1
                        artist_id_list[artists_index + 1] += 1
                    else:
                        artist_list.append(artists)
                        artist_list.append(1)
                        artist_id_list.append(artist_id)
                        artist_id_list.append(1)
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None
        
        if choice == "top":

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
                    compatible_artists_id_list.append(artist_id_list[k])
                    compatible_artists_id_list.append(artist_id_list[k + 1])

        elif choice == "liked":

            combined_liked_list = []

            saved_tracks_results = sp.current_user_saved_tracks(limit=50)
            combined_liked_list = populate_combined_liked_list(saved_tracks_results, combined_liked_list)
            while saved_tracks_results['next']:
                saved_tracks_results = sp.next(saved_tracks_results)
                combined_liked_list = populate_combined_liked_list(saved_tracks_results, combined_liked_list)

            compatible_artists_list = []
            compatible_artists_id_list = []

            for k in range(0, len(combined_liked_list) - 2, 3):
                if combined_liked_list[k] in artist_list:
                    c = artist_list.index(combined_liked_list[k])
                    if artist_list[c + 1] > 4 and combined_liked_list[k + 1] > 4:
                        compatible_artists_list.append(combined_liked_list[k])
                        compatible_artists_list.append(combined_liked_list[k + 1])
                        compatible_artists_id_list.append(combined_liked_list[k + 2])
                        compatible_artists_id_list.append(combined_liked_list[k + 1])

        if len(compatible_artists_list) == 0:
            break
        else:
            continue_bool = True

        similar_artists = []
        similar_artists_names = []

        for l in range(0, len(compatible_artists_list) - 1, 2):
            artist_id = compatible_artists_id_list[l]
            results = sp.artist_related_artists(artist_id)
            compatible_artists_id_list.append(artist_id)
            a = 0
            for artist in results['artists']:
                if artist['popularity'] >= 40 and a < 4:
                    similar_artists.append(artist['id'])
                    similar_artists_names.append(artist['name'])
                    a += 1
                elif a > 3:
                    break
            similar_artists.append(artist_id)
            similar_artists_names.append(compatible_artists_list[l])

        similar_of_similar_artists = []
        similar_of_similar_artists_names = []

        for k in range(0, len(similar_artists)):
            artist_id = similar_artists[k]
            results = sp.artist_related_artists(artist_id)
            a = 0
            for artist in results['artists']:
                if artist['popularity'] >= 40 and a < 4:
                    similar_of_similar_artists.append(artist['id'])
                    similar_of_similar_artists_names.append(artist['name'])
                    a += 1
                elif a > 3:
                    break
            similar_of_similar_artists.append(artist_id)
            similar_of_similar_artists_names.append(similar_artists_names[k])

        similar_of_similar_artists_count = []

        for j in range(0, len(similar_of_similar_artists)):
            artist_id = similar_of_similar_artists[j]
            if artist_id not in similar_of_similar_artists_count:
                similar_of_similar_artists_count.append(artist_id)
                similar_of_similar_artists_count.append(1)
                similar_of_similar_artists_count.append(similar_of_similar_artists_names[j])
            else:
                artist_id_index = similar_of_similar_artists_count.index(artist_id)
                similar_of_similar_artists_count[artist_id_index + 1] += 1

        similar_of_similar_artists = []
        similar_of_similar_artists_names = []

        for m in range(0, len(similar_of_similar_artists_count) - 2, 3):
            artist_id = similar_of_similar_artists_count[m]
            artist_name = similar_of_similar_artists_count[m + 2]
            if similar_of_similar_artists_count[m + 1] >= 2:
                similar_of_similar_artists.append(artist_id)
                similar_of_similar_artists_names.append(artist_name)
                
        if len(similar_of_similar_artists) == 0:
            break
        else:
            continue_bool = True

        random.shuffle(similar_of_similar_artists_names)

        similar_of_similar_artists_tracks = []

        for id in similar_of_similar_artists:
            results = sp.artist_top_tracks(id, country="US")
            if id in compatible_artists_id_list:
                for n in range(0, 9):
                    similar_of_similar_artists_tracks.append(results['tracks'][n]['id'])
            elif id in similar_artists:
                for n in range(0, 6):
                    similar_of_similar_artists_tracks.append(results['tracks'][n]['id'])
            else:
                for n in range(0, 4):
                    similar_of_similar_artists_tracks.append(results['tracks'][n]['id'])

        similar_of_similar_artists_tracks = set(similar_of_similar_artists_tracks)
        similar_of_similar_artists_tracks = list(similar_of_similar_artists_tracks)

        similar_of_similar_artists_tracks.sort(reverse=True, key=popularity_sort)
        
        m = -1
        while True:
            popularity = popularity_sort(similar_of_similar_artists_tracks[m])
            if popularity < 30:
                similar_of_similar_artists_tracks.remove(similar_of_similar_artists_tracks[m])
                m -= 1
            else:
                break

        other_user = sp.user(other_user_id)
        other_user = other_user['display_name']
        this_user = sp.user(my_user_id)
        this_user = this_user['display_name']

        playlist_name = "Compatibility Playlist: " + this_user + " + " + other_user

        playlist_id = get_compatible_playlist_id(sp, playlist_name, my_user_id)

        already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id)
        
        split_range = int(len(already_on_tracks_list) / 100) + 1
        for i in range(0, split_range):
            split = split_set(already_on_tracks_list, i, 100)
            sp.user_playlist_remove_all_occurrences_of_tracks(my_user_id, playlist_id, split)

        add_playlist_desc(sp, my_user_id, this_user, other_user, playlist_id)


        similar_of_similar_artists_tracks_length = len(similar_of_similar_artists_tracks)
        if similar_of_similar_artists_tracks_length > 300:
            split_range = 3
            for i in range(0, split_range):
                split = split_set(similar_of_similar_artists_tracks, i, 100)
                sp.user_playlist_add_tracks(my_user_id_temp, playlist_id, split)
        else:
            split_range = int(similar_of_similar_artists_tracks_length / 100) + 1
            for i in range(0, split_range):
                split = split_set(similar_of_similar_artists_tracks, i, 100)
                sp.user_playlist_add_tracks(my_user_id_temp, playlist_id, split)

        create_status = str(similar_of_similar_artists_tracks_length) + " songs added to playlist: [" + playlist_name + "]"
        
        response = {
            "Status": create_status,
            "Compatible Artists": compatible_artists_list,
            "Similar Artists": similar_artists_names,
            "Similar of Similar Artists": similar_of_similar_artists_names
        }

        print(time.time() - start_time)

        return response
    
    if continue_bool == False:
        response = "You and the user input have no compatible artists in common."
        return response

if __name__ == "__main__":
    pass
    #print(main("jwilso29", "1251692081", choice="top"))
    #print(main("jwilso29", "1251692081", choice="liked"))
    # print(main("jwilso29", "calamityclaire14"))
    #print(main("jwilso29", "1210157395"))
    #print(main("jwilso29", "sarahmw27", choice="liked"))
    #print(main("sarahmw27", "grettakr5", choice="liked"))
    #print(main("jwilso29", "grettakr5", choice="liked"))