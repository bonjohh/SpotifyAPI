import os 
import spotipy
import json
import datetime
import itertools
import boto3
import botocore
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
    
def get_albums_released_today(data):
    EST = pytz.timezone('America/New_York')
    today = datetime.datetime.now(EST)
    today = today.strftime("%m-%d")
    
    response = []
    header = "%3s %20s %50s %50s" % ("id", "release date", "album", "artist")
    response.append(header)
    i = 1
    
    for line in data:
        if today in line[0]:
            response.append("%3d %20s %50s %50s" % (i, line[0], line[1], line[2]))
            i += 1
        
    return response
    
def invoke_function(event):
    client = boto3.client('lambda')
    function_name = 'albums_released_today_write'
    function_invoke_response = client.invoke(FunctionName=function_name, 
                                            InvocationType='Event', 
                                            Payload=json.dumps(event))
    
def lambda_handler(event, context):
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    user_id = try_sp(sp)
    
    client = boto3.client("s3")
    
    file_name = "saved-albums-" + user_id + ".json"
    bucket_name = "bonjohh-saved-albums"

    try:
        fileObj = client.get_object(Bucket=bucket_name, Key=file_name)
        file_content = fileObj["Body"].read().decode('utf-8')
        
        data = json.loads(file_content)
        
        response = get_albums_released_today(data)
        
        invoke_function(event)
        
        if len(response) > 1:
            response = {
                "response": response
            }
            return response
        else:
            return "None of your liked tracks or albums were released on this day"
    except botocore.exceptions.ClientError as e:
        invoke_function(event)
        
        response = {
            "response": '''Please try running this function again to see your results. 
                        As this was your first time running the function, your results have not been cached.'''
        }
        return response
            
            
