import os
from dotenv import load_dotenv
import spotipy


def spotipy_token(scope, username):
    # project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI_2')
    project_folder = os.path.expanduser('/Users/john/Documents/python_files')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


def spotify_search(artist_name, sp):
    artist_name = str(artist_name).upper()
    search_string = "artist:" + artist_name
    results = sp.search(search_string, limit=50, type='artist', market='US')
    artists = results['artists']['items']
    found_bool = False
    for artist in artists:
        if str(artist['name']).upper() == artist_name:
            found_bool = True
            search_artist_uri = artist['uri']
            search_artist_name = artist['name']
            break
    if not found_bool and len(results['artists']['items']) > 0:
        search_artist_uri = results['artists']['items'][0]['uri']
        search_artist_name = results['artists']['items'][0]['name']
        print("could not find artist, running instead for this artsist: [" + results['artists']['items'][0]['name'] + "]")
    if not found_bool and len(results['artists']['items']) == 0:
        print("no search results returned for the artist entered")
        search_artist_uri = ""
        search_artist_name = ""
    return (found_bool, search_artist_uri, search_artist_name)


def get_liked_songs(sp):
    liked_songs = list()
    saved_results = sp.current_user_saved_tracks(limit=50)
    for item in saved_results['items']:
        track = item['track']
        liked_songs.append(track['uri'])
    while saved_results['next']:
        saved_results = sp.next(saved_results)
        for item in saved_results['items']:
            track = item['track']
            liked_songs.append(track['uri'])
    return liked_songs


def main(user_id, artist_name):
    scope = 'user-library-read'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    search_tuple = spotify_search(artist_name, sp)
    found_bool = search_tuple[0]
    found_artist_uri = search_tuple[1]
    found_artist_name = search_tuple[2]
    
    artists_top_tracks_list = list()

    if found_artist_uri != "":
        results = sp.artist_top_tracks(found_artist_uri, country = 'US')
        for track in results['tracks']:
            track_uri = track['uri']
            track_name = track['name']
            track_album = track['album']['name']
            track_year = track['album']['release_date'][:4]
            artists_top_tracks_list.append((track_uri, track_name, track_album, track_year))

        liked_songs = get_liked_songs(sp)
        for t in artists_top_tracks_list:
            if t[0] in liked_songs:
                print(t[1], t[2], t[3], found_artist_name, "-------- LIKED", sep='\t\t')
            else:
                print(t[1], t[2], t[3], found_artist_name, sep='\t\t')


if __name__ == "__main__":
    #pass
    user_id = "jwilso29"
    artist_name = "The Hotelier"
    main(user_id, artist_name)