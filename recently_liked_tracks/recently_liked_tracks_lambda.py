import spotipy
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
    for item in results['items']:
        track = item['track']
        total_tracks_list.append(track['uri'])
    return total_tracks_list 

def get_playlist_date():
    EST = pytz.timezone('America/New_York')
    two_weeks_ago = datetime.datetime.now(EST)
    two_weeks = datetime.timedelta(days=14)
    two_weeks_ago -= two_weeks
    two_weeks_ago = two_weeks_ago.strftime("%m/%d/%Y")
    return two_weeks_ago

def create_recently_liked_playlist(sp, user_id, new_playlist_name):
    return_string = sp.user_playlist_create(user_id, new_playlist_name, public=True)    
    return return_string['uri']

def get_recently_liked_playlist_id(sp, new_playlist_name, user_id):
    playlists = sp.current_user_playlists(limit=10) # must keep the new music playlist at the top if you're going to run it again
    playlist_id = ''
    for playlist in playlists['items']:
        if playlist['name'] == new_playlist_name:
            playlist_id = playlist['uri']
            break
    if playlist_id == '':
        playlist_id = create_recently_liked_playlist(sp, user_id, new_playlist_name)
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

def add_new_music_playlist_details(sp, user_id, playlist_uri):
    playlist_id = playlist_uri[17:]
    playlist_date = get_playlist_date()
    playlist_desc1 = "This is a playlist created from code by John Wilson (bonjohh on spotify). It was created "
    playlist_desc2 = "from songs liked in the past two weeks (since " + str(playlist_date) + ")."
    playlist_desc = playlist_desc1 + playlist_desc2
    sp.user_playlist_change_details(user_id, playlist_id, description=playlist_desc)
    return playlist_date
    
def split_set(total_tracks_set, i):
    tracks_list = list(total_tracks_set)
    if i == 0:
        split = tracks_list[:100]
    elif len(tracks_list) > 100:
        split = tracks_list[100*i:100+100*i]
    else:
        split = tracks_list[100*i:len(tracks_list)]
    return split
    
def get_last_date_added(results):
    last_added_date = results['items'][-1]['added_at']
    last_added_date = last_added_date[:10]
    last_added_date = last_added_date.replace('-', '/')
    last_added_date = datetime.datetime.strptime(last_added_date, "%Y/%m/%d")
    last_added_date = last_added_date.strftime("%m/%d/%Y")
    return last_added_date
    
def main(event, context):
    token = spotipy_token(event)

    sp = spotipy.Spotify(auth=token)
    
    user_id = try_sp(sp)
    
    new_playlist_name = "Recently Liked"

    playlist_id = get_recently_liked_playlist_id(sp, new_playlist_name, user_id) 
    
    playlist_date = add_new_music_playlist_details(sp, user_id, playlist_id)

    total_tracks_list = []

    already_on_tracks_list = add_tracks_already_on_playlist(sp, playlist_id)
    
    split_range = int(len(already_on_tracks_list) / 100) + 1
    for i in range(0, split_range):
        split = split_set(already_on_tracks_list, i)
        sp.user_playlist_remove_all_occurrences_of_tracks(user_id, playlist_id, split)

    results = sp.current_user_saved_tracks()
    total_tracks_list = show_tracks(results, sp, new_playlist_name, total_tracks_list, playlist_id)
    
    stop_after_next = False
    while True:
        results = sp.next(results)
        total_tracks_list = show_tracks(results, sp, new_playlist_name, total_tracks_list, playlist_id)
        last_added_date = get_last_date_added(results)
        if last_added_date < playlist_date:
            if stop_after_next:
                break
            stop_after_next = True

    total_tracks_set = set(total_tracks_list)
    
    total_tracks_set_length = len(total_tracks_set)
    if total_tracks_set_length > 0:
        split_range = int(total_tracks_set_length / 100) + 1
        for i in range(0, split_range):
            split = split_set(total_tracks_set, i)
            sp.user_playlist_add_tracks(user_id, playlist_id, split)
        
    create_status = str(total_tracks_set_length) + " songs added to playlist: [" + new_playlist_name + "]"
    
    response = {
        "Status": create_status
    }
    return response