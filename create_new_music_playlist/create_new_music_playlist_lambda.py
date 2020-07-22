import os 
import spotipy
import json
import calendar
import datetime
import pytz

class LambdaException(Exception):
    pass

def try_sp(sp):
    try:
        user_id = sp.me()
        return user_id['id']
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        how_to_fix = 'please get a fresh new spotify authorization token' 
        exception_str = {
            "isError": True,
            "type": exception_type,
            "HOW TO FIX": str.upper(how_to_fix),
            "message": exception_message
        }
        raise LambdaException(exception_str)

def spotipy_token(event):
    token = event['SPOTIFY_TOKEN']
    return token

def show_tracks(results, sp, playlist_name, total_tracks_list, playlist_id):
    tracks_list = []
    for item in results['items']:
        track = item['track']
        album = sp.album(show_tracks_album_uri(track))
        if album['album_type'] == "album" or str.upper(album['name']).find(' EP') > 0:
            tracks_list.append(track['uri']) # to add only featured tracks to the playlist
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

NEW_MUSIC_PLAYLISTS_LIST = []
    # 'spotify:playlist:37i9dQZF1DX4JAvHpjipBk', 'spotify:playlist:6y4wz0Gmh2nMlBMjxduLCi', 
                            # 'spotify:playlist:5X8lN5fZSrLnXzFtDEUwb9']

def get_release_radar(sp):
    searches = sp.search(q='Release Radar', limit=1, offset=0, type="playlist", market=None)
    search_owner_id = searches['playlists']['items'][0]['owner']['id']
    search_playlist_name = searches['playlists']['items'][0]['name']
    search_playlist_uri = searches['playlists']['items'][0]['uri']
    if search_owner_id == 'spotify' and search_playlist_name == 'Release Radar':
        NEW_MUSIC_PLAYLISTS_LIST.append(search_playlist_uri)

def get_new_music_playlist_id(sp, new_playlist_name, user_id):
    top_playlist_details = sp.current_user_playlists(limit=1) # must keep the new music playlist at the top if you're going to run it again
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

def add_new_music_playlist_details(sp, user_id, playlist_uri, event):
    playlist_id = playlist_uri[17:]
    playlist_number = len(NEW_MUSIC_PLAYLISTS_LIST)
    playlist_desc1 = "This is a new music playlist created from code by John Wilson (bonjohh on spotify). It was created "
    playlist_desc2 = "by taking the featured album or EP tracks (excluding singles tracks) from these " + str(playlist_number) + " playlists: "
    playlist_SPOTIFY_NM = "New Music Friday by Spotify"
    playlist_GETALTERNATIVE_NM = "The Alternative New Music Friday by getalternative"
    playlist_NPRMUSIC_NM = "NPR Music's New Music Friday by NPR Music"
    playlist_SPOTIFY_RR = "Release Radar by Spotify"
    playlist_desc = playlist_desc1 + playlist_desc2
    count = 0
    while count < playlist_number:
        if event['SPOTIFY_NM'] and playlist_SPOTIFY_NM not in playlist_desc:
            playlist_desc += playlist_SPOTIFY_NM
            count += 1
            if count < playlist_number:
                playlist_desc += ", "
            continue
        if event['GETALTERNATIVE_NM'] and playlist_GETALTERNATIVE_NM not in playlist_desc:
            playlist_desc += playlist_GETALTERNATIVE_NM
            count += 1
            if count < playlist_number:
                playlist_desc += ", "
            continue
        if event['NPRMUSIC_NM'] and playlist_NPRMUSIC_NM not in playlist_desc:
            playlist_desc += playlist_NPRMUSIC_NM
            count += 1
            if count < playlist_number:
                playlist_desc += ", "
            continue
        if event['SPOTIFY_RR']:
            playlist_desc += playlist_SPOTIFY_RR
            count += 1
            break
    print(playlist_desc)
    sp.user_playlist_change_details(user_id, playlist_id, description=playlist_desc)
    
def decide_what_playlists_to_pull_from(sp, event):
    if event['SPOTIFY_NM']:
        NEW_MUSIC_PLAYLISTS_LIST.append('spotify:playlist:37i9dQZF1DX4JAvHpjipBk')
    if event['GETALTERNATIVE_NM']:
        NEW_MUSIC_PLAYLISTS_LIST.append('spotify:playlist:6y4wz0Gmh2nMlBMjxduLCi')
    if event['NPRMUSIC_NM']:
        NEW_MUSIC_PLAYLISTS_LIST.append('spotify:playlist:5X8lN5fZSrLnXzFtDEUwb9')
    if event['SPOTIFY_RR']:
        get_release_radar(sp)
    
def main(event, context):
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    user_id = try_sp(sp)
    
    new_playlist_name = playlist_name()

    playlist_id = get_new_music_playlist_id(sp, new_playlist_name, user_id) 
    
    if len(event) > 1:
        decide_what_playlists_to_pull_from(sp, event)
    else:
        response = {
                    "Status": "Please check at least one playlist from which to build your new music playlist"
                }
        return response
    
    add_new_music_playlist_details(sp, user_id, playlist_id, event) # add new music playlist description

    total_tracks_list = []

    already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id)

    for playlist_uri in NEW_MUSIC_PLAYLISTS_LIST:
        fields = get_fields()
        new_music_playlist = sp.playlist(playlist_uri, fields=fields)
        new_playlist_tracks = new_music_playlist['tracks']
        total_tracks_list = show_tracks(new_playlist_tracks, sp, new_playlist_name, total_tracks_list, playlist_id)
    total_tracks_set = set(total_tracks_list)
    total_tracks_set = remove_already_on_tracks(total_tracks_set, already_on_tracks_list)
    total_tracks_set_length = len(total_tracks_set)
    if total_tracks_set_length > 0:
        sp.user_playlist_add_tracks(user_id, playlist_id, total_tracks_set)
        
    create_status = str(total_tracks_set_length) + " songs added to playlist: [" + new_playlist_name + "]"
    
    response = {
                    "Status": create_status
                }
    return response
    
    #handle exceptions like the SpotifyException when token has expired
