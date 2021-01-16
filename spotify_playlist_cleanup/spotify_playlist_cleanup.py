import os
from itunesLibrary import library
from dotenv import load_dotenv
import os
import spotipy
import difflib
import time
import similar
import re


def spotipy_token(scope, username):
    # project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI_2')
    project_folder = os.path.expanduser('/Users/john/Documents/python_files')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


class Album:
    __slots__ = ['album_uri', 'album_name', 'artist_name', 'album_type', 'artist_uri', 'year']

    def __init__(self, album_uri, album_name, artist_name, album_type, artist_uri, year):
        self.album_uri = album_uri
        self.album_name = album_name
        self.artist_name = artist_name
        self.album_type = album_type
        self.artist_uri = artist_uri
        self.year = year

    def __eq__(self, other):
        return self.album_uri == other.album_uri

    def __hash__(self):
        return hash(self.album_uri)


def album_set_add(results, tuple_):
    album_set = tuple_[0]
    track_set = tuple_[1]
    for track in results['items']:
        temp_album_uri = track['track']['album']['uri']
        temp_album_name = track['track']['album']['name']
        temp_artist_name = track['track']['album']['artists'][0]['name']
        temp_album_type = 'temp'
        temp_artist_uri = track['track']['album']['artists'][0]['uri']
        temp_year = 100000
        if track['track']['uri'] not in track_set:
            track_set.add(track['track']['uri'])
        else:
            print("duplicate found: ", track['track']['name'], temp_album_name, temp_artist_name, sep='\t\t')#########################
        temp_album = Album(temp_album_uri, temp_album_name, temp_artist_name, temp_album_type, temp_artist_uri, temp_year)
        if temp_album not in album_set:
            album_set.add(temp_album)
    return (album_set, track_set)


def album_search(album, sp):
    search_string = "album:" + album.album_name + " " + "artist:" + album.artist_name + " " + "year:" + album.year
    result = sp.search(search_string, limit=1, type='album', market='US')
    items = result['albums']['items']
    if len(items) == 0:
        search_string = "album:" + album.album_name + " " + "artist:" + album.artist_name
        result = sp.search(search_string, limit=1, type='album', market='US')
        items = result['albums']['items']
        if len(items) == 0:
            print("not found: ", album.album_name, album.artist_name, album.year, sep='\t\t')#########################
    else:
        for item in items:
            if item['uri'] != album.album_uri:
                album_results = sp.artist_albums(album.artist_uri, album.album_type, country='US', limit=50)
                counter = 1
                for album_iter in album_results['items']:
                    if album.album_name == album_iter['name'] and album.year == album_iter['release_date'][:4] and album.album_type == album_iter['album_type']:
                        counter = counter + 1
                        break
                    elif counter == len(album_results['items']):
                        print("not found2: ", album.album_name, album.artist_name, album.year, sep='\t\t')#########################


def like_songs(sp, results, liked_songs):
    temp_unliked = list()
    for track in results['items']:
        temp_track_uri = track['track']['uri']
        if temp_track_uri not in liked_songs:
            temp_unliked.append(temp_track_uri)
            print("liked: ", track['track']['name'], track['track']['album']['name'], track['track']['album']['artists'][0]['name'], sep='\t\t')#########################
    if len(temp_unliked) > 0:
        sp.current_user_saved_tracks_add(temp_unliked)


def get_liked_songs(sp):
    liked_songs = list()
    saved_results = sp.current_user_saved_tracks(limit=50)
    for item in saved_results['items']:
        track = item['track']
        liked_songs.append(track['uri'])
    while saved_results['next']:
        saved_results = sp.next(saved_results)
        for item in saved_results['items']:
            track = item['track']
            liked_songs.append(track['uri'])
    return liked_songs


def has_numbers(sp, album_uri, year_range, album):
    is_in_range = False
    album_tracks = sp.album_tracks(album_uri, market='US')
    tracks = album_tracks['items']
    for track in tracks:
        has_number = bool(re.search(r'\d\d\d\d', track['name']))
        if has_number:
            numbers = [int(s) for s in track['name'].split() if s.isdigit()]
            if len(numbers) > 0:
                for number in numbers:
                    if year_range.__contains__(int(number)):
                        print('remaster or live: ', album.album_name, album.artist_name, album.year, sep='\t\t')#########################))
                        is_in_range = True
    return is_in_range


def main(user_id, playlist_album_uri, year, liked):
    scope = 'user-library-read playlist-modify-public playlist-read-private user-library-modify'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    album_set = set()
    track_set = set()
    tuple_ = (album_set, track_set)

    if liked:
        liked_songs = get_liked_songs(sp)

    results = sp.playlist_tracks(playlist_album_uri, fields='items.track.uri,items.track.album.uri,items.track.album.artists.uri,items.track.album.artists.name,items.track.album.name,items.track.name,total,next')
    if liked:
        like_songs(sp, results, liked_songs)
    tuple_ = album_set_add(results, tuple_)
    while results['next']:
        if liked:
            like_songs(sp, results, liked_songs)
        results = sp.next(results)
        tuple_ = album_set_add(results, tuple_)

    if year != '' and year.__contains__('-'):
        dash_int = year.find('-')
        year_range = range(int(year[:dash_int]),int(year[dash_int+1:]))
    else:
        year_range = range(int(year), int(year))

    for album in album_set:
        time.sleep(.1)
        results = sp.album(album.album_uri)
        album.year = results['release_date'][:4]
        if year != '' and not year.__contains__('-') and int(album.year) != int(year):
            print('wrong year: ', album.album_name, album.artist_name, album.year, sep='\t\t')#########################))
        elif year_range.__len__() > 0:
            if year != '' and year.__contains__('-') and not year_range.__contains__(int(album.year)):
                if not has_numbers(sp, album.album_uri, year_range, album):
                    print('wrong year: ', album.album_name, album.artist_name, album.year, sep='\t\t')#########################))
        album.album_type = results['album_type']
        if album.album_type != 'album':
            print('not an album: ', album.album_name, album.artist_name, album.year, sep='\t\t')#########################)
        album_search(album, sp)
    
    print("done")


if __name__ == "__main__":
    #pass
    #playlist_album_uri = 'spotify:playlist:7FX7Xi04nCe3kZ2cFVR9im' #2020
    #playlist_album_uri = 'spotify:playlist:3qGW530jk1N1grN6ALyWvz' # 2020 - All
    #playlist_album_uri = 'spotify:playlist:5AZJlZbLvj1n1imbDoYDk6' # 2019 - iTunes
    #playlist_album_uri = 'spotify:playlist:3biiXSq79NsTGMYU4plMfc' # 2019 - Missed
    #playlist_album_uri = 'spotify:playlist:3wIBckGyFc4Y54ALUZBtsz' # 2018 - iTunes
    #playlist_album_uri = 'spotify:playlist:3eE07mckCcmB57gApAvRO1' # 2018 - Missed
    #playlist_album_uri = 'spotify:playlist:0gP5Gb87W5oMoDqMKdsD2X' # Pre 2018 - Missed
    #playlist_album_uri = 'spotify:playlist:1JFZtmaSwKZlU2e0nRYopx' # 2017 - iTunes
    #playlist_album_uri = 'spotify:playlist:5Q4Uq6hNzY1v987SMoB7xR' # 2016 - iTunes
    #playlist_album_uri = 'spotify:playlist:6BT939wVcwH9IrAMKY9FOP' # 2015 - iTunes
    #playlist_album_uri = 'spotify:playlist:3wsIo8Os9nb6riCznGRWxf' # 2014 - iTunes
    #playlist_album_uri = 'spotify:playlist:2SsPNWZpOZQ5mzYDVf2MSL' # 1970's
    year = ''
    liked = True
    main("jwilso29", playlist_album_uri, year, liked)