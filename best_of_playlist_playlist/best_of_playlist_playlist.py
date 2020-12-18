import spotipy
from dotenv import load_dotenv
import os
import json
import random
import datetime

def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI_2')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


def split_set(total_tracks_set, i, x):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:x]
    elif len(tracks_list) > x:
        split = tracks_list[x*i:x+x*i]
    else:
        split = tracks_list[x*i:len(tracks_list)]
    return split

def popularity_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    return results['popularity']

def show_album_tracks(album, sp):
    tracks_list = list()
    tracks = list()
    results = sp.album(album)
    tracks.extend(results['tracks']['items'])
    print(tracks)
    for track in tracks:
        tracks_list.append(track['id'])
    tracks_list.sort(reverse=True, key=popularity_sort)
    top_two_list = list()
    top_two_list.append(tracks_list[0])
    if len(tracks_list) > 1:
        top_two_list.append(tracks_list[1])
    return top_two_list

def main(source_playlist, best_of_playlist, add_since_date):
    global my_user_id
    global token
    my_user_id = 'jwilso29'
    scope = 'playlist-read-private playlist-modify-public'
    token_temp = spotipy_token(scope, my_user_id)
    token = token_temp
    sp = spotipy.Spotify(auth=token)

    album_set = set()
    album_list = list()
    track_tup = tuple()
    tracks_set = set()

    results = sp.playlist(source_playlist, fields="tracks.items.track.album.id,tracks.next,tracks.items.track.popularity,tracks.items.track.id,tracks.items.added_at")
    tracks = results['tracks']
    for item in tracks['items']:
        if item['added_at'] < add_since_date:
            continue
        track = item['track']
        album_id = track['album']['id']
        track_id = track['id']
        popularity = track['popularity']
        track_tup = (track_id, popularity)
        album_list.append([album_id, track_tup])
        album_set.add(album_id)
    for album_1 in album_set:
        track_list = list()
        for album_2 in album_list:
            if album_1 == album_2[0]:
                track_list.append(album_2[1])
        track_list.sort(key = lambda x: x[1])
        if len(track_list) > 4:
            for i in range(0,2):
                tracks_set.add(track_list[i][0])
        else:
            tracks_set.add(track_list[0][0])
    while results:
        tracks = sp.next(tracks)
        for item in tracks['items']:
            if item['added_at'] < add_since_date:
                continue
            track = item['track']
            album_id = track['album']['id']
            track_id = track['id']
            popularity = track['popularity']
            track_tup = (track_id, popularity)
            album_list.append([album_id, track_tup])
            album_set.add(album_id)
        for album_1 in album_set:
            track_list = list()
            for album_2 in album_list:
                if album_1 == album_2[0]:
                    track_list.append(album_2[1])
            track_list.sort(key = lambda x: x[1])
            if len(track_list) > 4:
                for i in range(-2,0):
                    tracks_set.add(track_list[i][0])
            else:
                tracks_set.add(track_list[-1][0])
        if tracks['next']:
            results = sp.next(tracks)
        else:
            results = None

    split_range = int(len(tracks_set) / 100) + 1
    for i in range(0, split_range):
        split = split_set(tracks_set, i, 100)
        sp.user_playlist_add_tracks(my_user_id, best_of_playlist, split)


if __name__ == "__main__":
    #pass
    main("spotify:playlist:7FX7Xi04nCe3kZ2cFVR9im", "spotify:playlist:7xEw6E9gNWNBHDdkiTbcG7","2020-11-24")