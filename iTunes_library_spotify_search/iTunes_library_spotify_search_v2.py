import os
from itunesLibrary import library
from dotenv import load_dotenv
import os
import spotipy
import difflib
import time



def spotipy_token(scope, username):
    project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI_2')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


def spotify_search(playlist_item, year, sp):
    search_string = "track:" + playlist_item.title + " " + "album:" + playlist_item.album + " " + "artist:" + playlist_item.artist + " " + "year:" + year
    result = sp.search(search_string, limit=50, type='track', market='US')
    items = result['tracks']['items']
    temp_list_of_tracks = []
    temp_list_of_albums = []
    temp_list_of_artists = []
    for item in items:
        found_bool = False
        if playlist_item.album.upper() == item['album']['name'].upper() and \
            playlist_item.artist.upper() == item['artists'][0]['name'].upper() and \
            year in item['album']['release_date']:
            found_bool = True
            #print("found ", playlist_item.title, playlist_item.album, playlist_item.artist, sep='\t')#########################
        else:
            temp_list_of_tracks.append(item['name'])
            temp_list_of_albums.append(item['album']['name'])
            temp_list_of_artists.append(item['artists'][0]['name'])
        if not found_bool:
            if len(temp_list_of_tracks) > 0 and \
                len(temp_list_of_albums) > 0 and \
                len(temp_list_of_artists) > 0:
                #print(playlist_item.title, playlist_item.album, playlist_item.artist, temp_list_of_tracks, temp_list_of_albums, temp_list_of_artists, sep='\t') ################################
                closest_track = difflib.get_close_matches(playlist_item.title, temp_list_of_tracks, n=1, cutoff=0)[0]
                closest_album = difflib.get_close_matches(playlist_item.album, temp_list_of_albums, n=1, cutoff=0)[0]
                closest_artist = difflib.get_close_matches(playlist_item.artist, temp_list_of_artists, n=1, cutoff=0)[0]
                #print("closest ", closest_track, closest_album, closest_artist, sep='\t') ###################################
                search_string_2 = "track:" + closest_track + " " + "album:" + closest_album + " " + "artist:" + closest_artist + " " + "year:" + year
                result = sp.search(search_string_2, limit=50, type='track', market='US')
                items = result['tracks']['items']
                found_bool = False
                for item in items:
                    if closest_album.upper() == item['album']['name'].upper() \
                        and closest_artist.upper() == item['artists'][0]['name'].upper() \
                        and year in item['album']['release_date']:
                        #print("found2 ", playlist_item.title, playlist_item.album, playlist_item.artist, sep='\t')#########################
                        found_bool = True
                        break
                if not found_bool:
                    print("not found ", playlist_item.title, playlist_item.album, playlist_item.artist, sep='\t')#########################
                    print("not found data: ", search_string, search_string_2, playlist_item.album.upper() == item['album']['name'].upper(), playlist_item.artist.upper() == item['artists'][0]['name'].upper(), item['album']['name'], item['artists'][0]['name'], result, sep='\t')#########################


def main(user_id, xml_path, playlist_name, year):
    scope = 'user-top-read'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    lib = library.parse(xml_path)

    playlist = lib.getPlaylist(playlist_name)

    for item in playlist.items:
        time.sleep(.2)
        spotify_search(item, year, sp)

if __name__ == "__main__":
    #pass
    xml_path = r'D:\Documents\iTunesLibraryFiles\Altos_08.31.2020.xml'
    main("jwilso29", xml_path, "Altos", "2019")

    # only use with year playlists