import spotipy
from dotenv import load_dotenv
import os
import json
import random
import datetime

class Track:
    __slots__ = ['track_id', 'liked']

    def __init__(self, track_id, liked):
        self.track_id = track_id
        self.liked = liked
    
    def __eq__(self, other):
        return self.track_id == other.track_id

    def __hash__(self):
        return hash(str(self))

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


def read_text_file(filepath):
    f = open(filepath, 'r', encoding='utf-8')
    playlist_list = list()
    for x in f:
        playlist_uri = x.split('|')[0]
        playlist_list.append(playlist_uri)
    f.close()
    return playlist_list


def read_playlist(playlist_uri, songs_list, sp):
    results = sp.playlist(playlist_uri, fields="tracks.next,tracks.items.track.id,tracks.items.track.album.release_date,tracks.total", market='US')
    tracks = results['tracks']
    for item in tracks['items']:
        if item['track']['album']['release_date'] >= '2020-01-01':
            songs_list.add(Track(item['track']['id'], False))
    while results and tracks['total'] > 100:
        tracks = sp.next(tracks)
        for item in tracks['items']:
            if item['track']['album']['release_date'] >= '2020-01-01':
                songs_list.add(Track(item['track']['id'], False))
        if tracks['next']:
            results = sp.next(tracks)
        else:
            results = None
    return songs_list


def remove_liked_songs(sp, songs_list):
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        if item['track']['album']['release_date'] >= '2020-01-01':
            temp = Track(item['track']['id'], False)
            songs_list_len = len(songs_list) - 1
            for i in range(0, songs_list_len):
                track = songs_list[i]
                if track.track_id == temp.track_id:
                    songs_list.remove(track)
                    songs_list_len = songs_list_len - 1
                    break
    while results['next']:
        results = sp.next(results)
        for item in results['items']:
            if item['track']['album']['release_date'] >= '2020-01-01':
                temp = Track(item['track']['id'], False)
                songs_list_len = len(songs_list) - 1
                for i in range(0, songs_list_len):
                    track = songs_list[i]
                    if track.track_id == temp.track_id:
                        songs_list.remove(track)
                        songs_list_len = songs_list_len - 1
                        break
    return songs_list


def remove_all_playlist_songs(sp, songs_list, all_playlist):
    results = sp.playlist(all_playlist, fields="tracks.next,tracks.items.track.id,tracks.items.track.album.release_date,tracks.total", market='US')
    tracks = results['tracks']
    for item in tracks['items']:
        if item['track']['album']['release_date'] >= '2020-01-01':
            temp = Track(item['track']['id'], False)
            songs_list_len = len(songs_list) - 1
            for i in range(0, songs_list_len):
                track = songs_list[i]
                if track.track_id == temp.track_id:
                    songs_list.remove(track)
                    songs_list_len = songs_list_len - 1
                    break
    while results and tracks['total'] > 100:
        tracks = sp.next(tracks)
        for item in tracks['items']:
            if item['track']['album']['release_date'] >= '2020-01-01':
                temp = Track(item['track']['id'], False)
                songs_list_len = len(songs_list) - 1
                for i in range(0, songs_list_len):
                    track = songs_list[i]
                    if track.track_id == temp.track_id:
                        songs_list.remove(track)
                        songs_list_len = songs_list_len - 1
                        break
        if tracks['next']:
            results = sp.next(tracks)
        else:
            results = None
    return songs_list


def main(user_id, text_path, aggregate_playlist_id, all_playlist):
    scope = 'user-library-read playlist-modify-public playlist-read-private'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    playlist_list = read_text_file(text_path)

    songs_list = set()
    for playlist in playlist_list:
        songs_list = read_playlist(playlist, songs_list, sp)

    songs_list = list(songs_list)
    songs_list = remove_liked_songs(sp, songs_list)
    songs_list = remove_all_playlist_songs(sp, songs_list, all_playlist)

    songs_list_2 = set()
    for track in songs_list:
        if track.liked != True:
            songs_list_2.add(track.track_id)
    
    split_range = int(len(songs_list_2) / 100) + 1
    for i in range(0, split_range):
        split = split_set(songs_list_2, i, 100)
        sp.user_playlist_add_tracks(user_id, aggregate_playlist_id, split)


if __name__ == "__main__":
    #pass
    text_path = r'D:\Documents\Music Stuff\best_of_2020_playlists.txt'
    aggregate_playlist_id = 'spotify:playlist:2c5yrR3NSCDcP9UE4eSvsq'
    all_playlist = 'spotify:playlist:3qGW530jk1N1grN6ALyWvz'
    main("jwilso29", text_path, aggregate_playlist_id, all_playlist)