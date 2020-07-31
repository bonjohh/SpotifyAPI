import os 
import spotipy
import json
import datetime
import itertools
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

def show_saved_tracks(saved_results, album_list):
    for item in saved_results['items']:
        track = item['track']
        temp_list = []
        temp_list.append(track['album']['release_date'])
        temp_list.append(track['album']['name'])
        temp_list.append(track['artists'][0]['name'])
        album_list.append(temp_list)
    return album_list

def main(event, context):
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    user_id = try_sp(sp)

    album_list = []
    
    saved_results = sp.current_user_saved_tracks(limit=50)
    album_list = show_saved_tracks(saved_results, album_list)

    while saved_results['next']:
        saved_results = sp.next(saved_results)
        album_list = show_saved_tracks(saved_results, album_list)

    album_list = [tuple(album) for album in album_list]
    album_list = set(album_list)
    album_list = [list(album) for album in album_list]

    json_str = album_list
    json_str = json.dumps(json_str)

    client = boto3.client('s3')
    resource = boto3.resource('s3')
    
    file_name = "saved-albums-" + user_id + ".json"
    bucket_name = "bonjohh-saved-albums"

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