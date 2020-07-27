import spotipy
import json
import boto3
import botocore

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
    
def popularity_sort(track):
    sp = spotipy.Spotify(auth=token)
    results = sp.track(track)
    return results['popularity']
    
def split_set(total_tracks_set, i, x):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:x]
    elif len(tracks_list) > x:
        split = tracks_list[x*i:x+x*i]
    else:
        split = tracks_list[x*i:len(tracks_list)]
    return split
    
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
    
def add_playlist_desc(sp, my_user_id, this_user, other_user, playlist_id):
    playlist_id = playlist_id[17:]
    playlist_desc1 = "This is a playlist created from code by John Wilson (bonjohh on spotify). It was created "
    playlist_desc2 = "based on top songs of artists, where the artists are similar to those that both users have "
    playlist_desc3 = "similar interest in. Users are " + this_user + " and " + other_user + "."
    playlist_desc = playlist_desc1 + playlist_desc2 + playlist_desc3
    sp.user_playlist_change_details(my_user_id, playlist_id, description=playlist_desc)

def main(event, context):
    global my_user_id
    global token
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    my_user_id = try_sp(sp)
    other_user_id = event['other_user_id']
    
    client = boto3.client("s3")
    
    file_name = "similar-artists-" + my_user_id + "-" + other_user_id + ".json"
    bucket_name = "bonjohh-compatibility-playlist"

    try:
        fileObj = client.get_object(Bucket=bucket_name, Key=file_name)
        file_content = fileObj["Body"].read().decode('utf-8')
        data = json.loads(file_content)
    except botocore.exceptions.ClientError as e:
        return "Could Not Find your file in the S3 bucket."
        
    similar_artists = data['similar_artists']
    similar_artists = list(similar_artists)
    similar_artists_names = data['similar_artists_names']
    similar_artists_names = list(similar_artists_names)
    compatible_artists_id_list = data['compatible_artists_id_list'] 
    compatible_artists_id_list = list(compatible_artists_id_list)

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
    
    m = -1
    while True:
        popularity = popularity_sort(similar_artists_tracks[m])
        if popularity < 30:
            similar_artists_tracks.remove(similar_artists_tracks[m])
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

    similar_artists_tracks_length = len(similar_artists_tracks)
    if similar_artists_tracks_length > 0:
        split_range = int(similar_artists_tracks_length / 100) + 1
        for i in range(0, split_range):
            split = split_set(similar_artists_tracks, i, 100)
            sp.user_playlist_add_tracks(my_user_id, playlist_id, split)