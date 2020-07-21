import spotipy


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

def show_all_playlists(event, context):
    sp = spotipy.Spotify(auth=event['SPOTIFY_TOKEN'])
    user_id = try_sp(sp)
    if event['user_id'] != '':
        user_id = event['user_id']
    playlists = sp.user_playlists(user_id)
    playlist_list = []
    header = "%3s %35s %25.20s %35s %15s" % ("id", "playlist name", "playlist uri", "playlist owner", "total tracks")
    playlist_list.append(header)
    i = 1
    while playlists:
        for playlist in playlists['items']:
            playlist_name =  "%s" % (playlist['name'])
            playlist_uri = "%s" % (playlist['uri'])
            playlist_owner = "%s" % (playlist['owner']['id'])
            total_tracks = "%d" % (playlist['tracks']['total'])
            playlist_output = "%3d %35.35s %45.45s %15.15s %15.15s" % (i, playlist_name, playlist_uri, playlist_owner, total_tracks)
            playlist_list.append(playlist_output)
            i += 1
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    response = {
                    "playlist_list": playlist_list
                }
    return response
