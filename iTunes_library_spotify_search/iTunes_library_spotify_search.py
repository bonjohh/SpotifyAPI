import os
import spotipy
from dotenv import load_dotenv
import pprint
import difflib


class Track:
# Name	Artist	Album   Track Number	Year
    __slots__ = ['track_name', 'artist_name', \
        'album_name', 'track_id', 'year']

    def __init__(self, track_name, artist_name, \
                 album_name, track_id, year):
        self.track_name = track_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.track_id = track_id
        self.year = year

    def __eq__(self, other):
        return self.track_name == other.track_name and \
            self.artist_name == other.artist_name and \
            self.album_name == other.album_name and \
            self.year == other.year


def spotipy_token(scope, username):
    env_path = r'D:\Documents\Python_Git_SpotifyAPI_2'
    project_folder = os.path.expanduser(env_path)
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


def read_text_file(text_path):
    text_file = open(text_path, 'r', encoding='utf-8') 
    text_file_lines = text_file.readlines()

    count = 0
    tracks_list = []

    for line in text_file_lines:
        if count != 0:
            track_attributes = read_track_line(line)
            temp_track = Track(track_attributes[0], track_attributes[1], \
                               track_attributes[2], track_attributes[3], \
                               track_attributes[4])
            tracks_list.append(temp_track)
        if count == 0:
            count += 1
    return tracks_list


def read_track_line(line):
    temp_list = line.split('\t')

    attribute_list = []
    attribute_list.append(temp_list[0])
    attribute_list.append(temp_list[1])
    attribute_list.append(temp_list[3])
    attribute_list.append(temp_list[14])
    attribute_list.append(temp_list[16])

    return attribute_list


def spotify_search(track, sp):
    search_string = "track:" + track.track_name + " " + "album:" + track.album_name + " " + "artist:" + track.artist_name
    result = sp.search(search_string, limit=50, type='track', market='US')
    items = result['tracks']['items']
    temp_list_of_tracks = []
    temp_list_of_albums = []
    temp_list_of_artists = []
    for item in items:
        found_bool = False
        if track.album_name == item['album']['name'] and \
            track.artist_name == item['artists'][0]['name'] and \
            track.year in item['album']['release_date']:
            found_bool = True
            #print("found", track.track_name, track.album_name, track.artist_name, sep='\t')#########################
        else:
            temp_list_of_tracks.append(item['name'])
            temp_list_of_albums.append(item['album']['name'])
            temp_list_of_artists.append(item['artists'][0]['name'])
        if not found_bool:
            if len(temp_list_of_tracks) > 0 and \
                len(temp_list_of_albums) > 0 and \
                len(temp_list_of_artists) > 0:
                print(track.track_name, track.album_name, track.artist_name, temp_list_of_tracks, temp_list_of_albums, temp_list_of_artists, sep='\t') ################################
                closest_track = difflib.get_close_matches(track.track_name, \
                    temp_list_of_tracks, n=1)[0]
                closest_album = difflib.get_close_matches(track.album_name, \
                    temp_list_of_albums, n=1)[0]
                closest_artist = difflib.get_close_matches(track.artist_name, \
                    temp_list_of_artists, n=1)[0]
                #print(closest_track, closest_album, closest_artist, sep='\t') ###################################
                search_string_2 = "track:" + closest_track + " " + "album:" + closest_album + " " + "artist:" + closest_artist
                result = sp.search(search_string_2, limit=50, type='track', market='US')
                items = result['tracks']['items']
                found_bool = False
                for item in items:
                    if track.album_name == item['album']['name'] \
                        and track.artist_name == item['artists'][0]['name'] \
                        and track.year in item['album']['release_date']:
                        #print("found", track.track_name, track.album_name, track.artist_name, sep='\t')#########################
                        found_bool = True
                        break
                if not found_bool:
                    print("not found", track.track_name, track.album_name, track.artist_name, sep='\t')#########################


def main(user_id, text_path):
    scope = 'user-top-read' ##################
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    tracks_list = read_text_file(text_path)
    
    for track in tracks_list:
        spotify_search(track, sp)


if __name__ == "__main__":
    #pass
    text_path = r'D:\Documents\iTunesLibraryFiles\Altos_08.31.2020.txt'
    main("jwilso29", text_path)