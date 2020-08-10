import os 
import spotipy
import json
import calendar
import datetime
from dotenv import load_dotenv
import pytz


def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Course/create_new_music_playlist')  # adjust as appropriate
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def show_tracks(results, sp, playlist_name, total_tracks_list, playlist_id):
    tracks_list = []
    for item in results['items']:
        track = item['track']
        if track == None:
            continue
        else:
            album = sp.album(show_tracks_album_uri(track))
        if album['album_type'] == "album" or str.upper(album['name']).find(' EP') > 0:
            tracks_list.append(track['uri'])
    for track_uri in tracks_list:
        total_tracks_list.append(track_uri)
    return total_tracks_list 

def show_tracks_album_uri(track):
    album_uri = track['album']['uri']
    return album_uri

def playlist_name():
    EST = pytz.timezone('America/New_York')
    lastFriday = datetime.datetime.now(EST)
    oneday = datetime.timedelta(days=1)
    while lastFriday.weekday() != calendar.FRIDAY:
        lastFriday -= oneday
    d1 = lastFriday.strftime("%m/%d/%Y")
    name = "New Music Playlist " + d1
    return name

def create_new_songs_playlist(sp, user_id, new_playlist_name):
    return_string = sp.user_playlist_create(user_id, new_playlist_name, public=True)    
    return return_string['uri']

NEW_MUSIC_PLAYLISTS_LIST = ['spotify:playlist:37i9dQZF1DX4JAvHpjipBk', 'spotify:playlist:6y4wz0Gmh2nMlBMjxduLCi', 
                            'spotify:playlist:5X8lN5fZSrLnXzFtDEUwb9']

def get_release_radar(sp):
    searches = sp.search(q='Release Radar', limit=1, offset=0, type="playlist", market=None)
    search_owner_id = searches['playlists']['items'][0]['owner']['id']
    search_playlist_name = searches['playlists']['items'][0]['name']
    search_playlist_uri = searches['playlists']['items'][0]['uri']
    if search_owner_id == 'spotify' and search_playlist_name == 'Release Radar':
        NEW_MUSIC_PLAYLISTS_LIST.append(search_playlist_uri)

def get_new_music_playlist_id(sp, new_playlist_name, user_id):
    top_playlist_details = sp.current_user_playlists(limit=1) # must keep the new music playlist at the top 
                                                                # if you're going to run it again
    if top_playlist_details['items'][0]['name'] == new_playlist_name:
        playlist_id = top_playlist_details['items'][0]['uri']
    else:
        playlist_id = create_new_songs_playlist(sp, user_id, new_playlist_name)
    return playlist_id

def get_fields():
    field1 = "tracks.items.track.uri,"
    field2 = "tracks.items.track.album.type,"
    field3 = "tracks.items.track.album.uri,"
    field4 = "tracks.items.track.album.name,"
    field5 = "next"
    fields = field1 + field2 + field3 + field4 + field5
    return fields

def add_tracks_already_on_playlist(sp, playlist_id):
    already_on_list = []
    response = sp.playlist_tracks(playlist_id, fields='items.track.uri,total')
    if response['total'] > 0:
        for track in response['items']:
            already_on_list.append(track['track']['uri'])
        return already_on_list
    else:
        return already_on_list

def remove_already_on_tracks(total_tracks_set, already_on_tracks_list):
    for track_uri_a in already_on_tracks_list:
        if track_uri_a in total_tracks_set:
            total_tracks_set.remove(track_uri_a)
    return total_tracks_set

def add_new_music_playlist_details(sp, user_id, playlist_uri):
    playlist_id = playlist_uri[17:]
    playlist_desc1 = '''This is a new music playlist created from code by John Wilson (bonjohh on spotify). '''
    playlist_desc2 = '''It was created by taking the featured album or EP tracks (excluding singles tracks) '''
    playlist_desc3 = '''from these 4 playlists: New Music Friday by Spotify, The Alternative New Music Friday by getalternative, '''
    playlist_desc4 = '''NPR Music's New Music Friday by NPR Music, Release Radar by Spotify'''
    playlist_desc = playlist_desc1 + playlist_desc2 + playlist_desc3 + playlist_desc4
    sp.user_playlist_change_details(user_id, playlist_id, description=playlist_desc)

def main(user_id):
    scope = 'playlist-modify-public playlist-read-private'
    token = spotipy_token(scope, user_id) # get the spotify authorization token

    sp = spotipy.Spotify(auth=token) # get the spotify authorization object
    
    new_playlist_name = playlist_name() # get the dynamic new music playlist name

    playlist_id = get_new_music_playlist_id(sp, new_playlist_name, user_id) # get the new music playlist id if 
                                                                                # created or else create the new 
                                                                                # # music playlist and get the id

    get_release_radar(sp) # add personal spotify release radar to 
                            # the list of new music playlists to pull from

    add_new_music_playlist_details(sp, user_id, playlist_id) # add new music playlist description

    total_tracks_list = [] # initialize the total tracks list

    already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id) # add tracks already on the 
                                                                                # new music playlist

    for playlist_uri in NEW_MUSIC_PLAYLISTS_LIST: # loop through the uris in the new music playlists list
        fields = get_fields() #get the fields for the playlist search below
        new_music_playlist = sp.playlist(playlist_uri, fields=fields) # search for the new music playlist
        new_playlist_tracks = new_music_playlist['tracks'] # get the tracks from the new music playlist
        total_tracks_list = show_tracks(new_playlist_tracks, sp, new_playlist_name, total_tracks_list, playlist_id)
            # call the show tracks function on the looped uri and append the returned tracks to the total tracks list
    total_tracks_set = set(total_tracks_list) # convert the list to a set to remove duplicates
    total_tracks_set = remove_already_on_tracks(total_tracks_set, already_on_tracks_list) # remove tracks already
                                                                                            #on the new music playlist
    if len(total_tracks_set) > 0: # if there are any songs to add
        sp.user_playlist_add_tracks(user_id, playlist_id, total_tracks_set) # add the tracks from the total tracks
                                                                                 # list to the new music playlist

if __name__ == "__main__":
    pass
    #main("jwilso29")
