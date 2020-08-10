import spotipy
import json
import random
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

def split_set(total_tracks_set, i, x):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:x]
    elif len(tracks_list) > x:
        split = tracks_list[x*i:x+x*i]
    else:
        split = tracks_list[x*i:len(tracks_list)]
    return split

def invoke_function(event):
    client = boto3.client('lambda')
    function_name = 'compatibility_playlist_child'
    function_invoke_response = client.invoke(FunctionName=function_name, 
                                            InvocationType='Event', 
                                            Payload=json.dumps(event))

def main(event, context):
    global my_user_id
    global token
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    my_user_id = try_sp(sp)
    other_user_id = event['other_user_id']

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
                            artists = artists + " " + track['track']['artists'][j]['name']
                            artists_id = artists_id + " " + track['track']['artists'][j]['id']
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
        
        json_str = {
            "similar_of_similar_artists": similar_of_similar_artists,
            "similar_of_similar_artists_names": similar_of_similar_artists_names,
            "similar_artists": similar_artists,
            "similar_artists_names": similar_artists_names,
            "compatible_artists_list": compatible_artists_list,
            "compatible_artists_id_list": compatible_artists_id_list
            }
        json_str = json.dumps(json_str)
        
        client = boto3.client('s3')
        resource = boto3.resource('s3')
        
        file_name = "similar-artists-" + my_user_id + "-" + other_user_id + ".json"
        bucket_name = "bonjohh-compatibility-playlist"
    
        try:
            resource.Object(bucket_name, file_name).load()
            print("file already exists!!!!!!!!!!!!!!!!!!!!!")
            json_str = str(json_str).encode("utf-8")
            s3_path = file_name
            client.put_object(Body=json_str, Bucket=bucket_name, Key=s3_path)
            print("file overwritten!!!!!!!!!!!")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                json_str = str(json_str).encode("utf-8")
                s3_path = file_name
                client.put_object(Body=json_str, Bucket=bucket_name, Key=s3_path)
                print("file created!!!!!!!!!!!!!!!!!!!!")
                
        invoke_function(event)

        create_status = "Playlist has been successfully created and songs have been added."
        response = {
            "Status": create_status,
            "Compatible Artists": compatible_artists_list,
            "Similar Artists": similar_artists_names,
            "Similar of Similar Artists": similar_of_similar_artists_names
        }
        return response
        
    if continue_bool == False:
        response = "You and the user input have no compatible artists in common."
        return response