import spotipy

class LambdaException(Exception):
    pass

def try_sp(sp):
    try:
        user_id = sp.me()

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

def top_tracks_for_user(event, context):
    sp = spotipy.Spotify(auth=event['SPOTIFY_TOKEN'])
    try_sp(sp)
    choice = event['choice']
    
    ranges = ['short_term', 'medium_term', 'long_term']
    
    if choice == 'tracks':
        for sp_range in ranges:
            printed_thing = []
            header = "%4s %35.35s %35.35s %35.35s" % ("id", "track name", "album name", "track artist")
            printed_thing.append(header)
            results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
            for i, item in enumerate(results['items']):
                row_id = i + 1
                track_name = item['name']
                track_album = item['album']['name']
                track_artist = item['artists'][0]['name']
                printed = "%4d %35.35s %35.35s %35.35s" % (row_id, track_name, track_album, track_artist)
                printed_thing.append(printed)
            if sp_range == "short_term":
                short_term_results = printed_thing
            if sp_range == "medium_term":
                medium_term_results = printed_thing
            if sp_range == "long_term":
                long_term_reults = printed_thing
                
    if choice == 'artists':
        for sp_range in ranges:
            printed_thing = []
            header = "%4s %50s %20s" % ("id", "artist", "popularity score")
            printed_thing.append(header)
            results = sp.current_user_top_artists(time_range=sp_range, limit=50)
            for i, item in enumerate(results['items']):
                row_id = i + 1
                artist = item['name']
                popularity = item['popularity']
                printed = "%4d %50s %20d" % (row_id, artist, popularity)
                printed_thing.append(printed)
            if sp_range == "short_term":
                short_term_results = printed_thing
            if sp_range == "medium_term":
                medium_term_results = printed_thing
            if sp_range == "long_term":
                long_term_reults = printed_thing

    return {
        "body": {
            "short term": short_term_results,
            "medium term": medium_term_results,
            "long term": long_term_reults
        }
    }