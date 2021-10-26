import os
from itunesLibrary import library
from dotenv import load_dotenv
import spotipy
import difflib
import time
import similar


def spotipy_token(scope, username):
    # project_folder = os.path.expanduser('D:/Documents/Python_Git_SpotifyAPI_2')
    project_folder = os.path.expanduser('/Users/john/Documents/python_files')
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token


def spotify_search(playlist_item, year, sp):
    if str(playlist_item.artist).__contains__(","):
        commaInt = str(playlist_item.artist).find(",")
        playlist_artist = str(playlist_item.artist)[:commaInt]
    playlist_artist = playlist_item.artist
    if str(playlist_item.artist).__contains__("\'"):
        playlist_artist = str(playlist_item.artist).replace("\'","")
    playlist_album = playlist_item.album
    if str(playlist_item.album).__contains__("\'"):
        playlist_album = str(playlist_item.album).replace("\'","")
    playlist_title = playlist_item.title
    if str(playlist_item.title).__contains__("["):
        bracketInt = str(playlist_item.title).find("[")
        playlist_title = str(playlist_item.title)[:bracketInt]
    if str(playlist_item.title).__contains__("(Feat"):
        parenInt = str(playlist_item.title).find("(Feat")
        playlist_title = str(playlist_item.title)[:parenInt]
    elif str(playlist_item.title).__contains__("(feat"):
        parenInt = str(playlist_item.title).find("(feat")
        playlist_title = str(playlist_item.title)[:parenInt]
    elif str(playlist_item.title).__contains__("(ft"):
        parenInt = str(playlist_item.title).find("(ft")
        playlist_title = str(playlist_item.title)[:parenInt]
    elif str(playlist_item.title).__contains__("(Ft"):
        parenInt = str(playlist_item.title).find("(Ft")
        playlist_title = str(playlist_item.title)[:parenInt]
    else:
        if str(playlist_item.title).__contains__("Feat"):
            featInt = str(playlist_item.title).find("Feat")
            playlist_title = str(playlist_item.title)[:featInt]
        elif str(playlist_item.title).__contains__("feat"):
            featInt = str(playlist_item.title).find("feat")
            playlist_title = str(playlist_item.title)[:featInt]
        elif str(playlist_item.title).__contains__("ft"):
            ftInt = str(playlist_item.title).find("ft")
            playlist_title = str(playlist_item.title)[:ftInt]
        elif str(playlist_item.title).__contains__("Ft"):
            ftInt = str(playlist_item.title).find("Ft")
            playlist_title = str(playlist_item.title)[:ftInt]
    if str(playlist_title).__contains__("(Prod"):
        prodInt = str(playlist_title).find("(Prod")
        playlist_title = str(playlist_title)[:prodInt]
    elif str(playlist_title).__contains__("(prod"):
        prodInt = str(playlist_title).find("(prod")
        playlist_title = str(playlist_title)[:prodInt]
    if str(playlist_item.title).__contains__("\'"):
        playlist_title = str(playlist_item.title).replace("\'","")
    if playlist_album != None:
        search_string = "track:" + playlist_title + " " + "album:" + playlist_album + " " + "artist:" + playlist_artist + " " + "year:" + year
        result = sp.search(search_string, limit=50, type='track', market='US')
        items = result['tracks']['items']
        temp_list_of_tracks = []
        temp_list_of_albums = []
        temp_list_of_artists = []
        if len(items) == 0:
            print("not found ", playlist_title, playlist_album, playlist_artist, sep='\t')#########################
            print("not found data: ", search_string, result, sep='\t')#########################
        for item in items:
            found_bool = False
            if str(playlist_album).upper() == str(item['album']['name']).replace("\'", "").upper() and \
                str(item['artists'][0]['name']).replace("\'", "").upper() in str(playlist_artist).upper() and \
                year in item['album']['release_date']:
                found_bool = True
                #print("found ", playlist_title, playlist_album, playlist_artist, sep='\t')#########################
            else:
                temp_list_of_tracks.append(item['name'])
                temp_list_of_albums.append(item['album']['name'])
                temp_list_of_artists.append(item['artists'][0]['name'])
                tempYear = item['album']['release_date']
            if not found_bool:
                if len(temp_list_of_tracks) > 0 and \
                    len(temp_list_of_albums) > 0 and \
                    len(temp_list_of_artists) > 0:
                    #print(playlist_title, playlist_album, playlist_artist, temp_list_of_tracks, temp_list_of_albums, temp_list_of_artists, sep='\t') ################################
                    yearBool = True
                    if year not in tempYear:
                        print("wrong year ", playlist_title, playlist_album, playlist_artist, tempYear, sep='\t')#########################
                        yearBool = False
                    if yearBool:
                        closest_track_list = difflib.get_close_matches(playlist_title, temp_list_of_tracks, n=10, cutoff=0)
                        closest_album_list = difflib.get_close_matches(playlist_album, temp_list_of_albums, n=10, cutoff=0)
                        closest_artist_list = difflib.get_close_matches(playlist_artist, temp_list_of_artists, n=10, cutoff=0)
                        closest_track = similar.best_match(playlist_title, closest_track_list)
                        closest_album = similar.best_match(playlist_album, closest_album_list)
                        closest_artist = similar.best_match(playlist_artist, closest_artist_list)
                        #print("closest ", closest_track, closest_album, closest_artist, sep='\t') ###################################
                        search_string_2 = "track:" + closest_track + " " + "album:" + closest_album + " " + "artist:" + closest_artist + " " + "year:" + year
                        result = sp.search(search_string_2, limit=50, type='track', market='US')
                        items = result['tracks']['items']
                        found_bool = False
                        for item in items:
                            if str(closest_album).upper() == str(item['album']['name']).replace("\'", "").upper() \
                                and str(item['artists'][0]['name']).replace("\'", "").upper() in str(closest_artist).upper() \
                                and year in item['album']['release_date']:
                                print("found2 ", playlist_title, playlist_album, playlist_artist, sep='\t')#########################
                                found_bool = True
                                break
                        if not found_bool:
                            print("not found2 ", playlist_title, playlist_album, playlist_artist, sep='\t')#########################
                            print("not found2 data: ", search_string, search_string_2, playlist_album.upper() == item['album']['name'].upper(), playlist_artist.upper() == item['artists'][0]['name'].upper(), item['album']['name'], item['artists'][0]['name'], result, sep='\t')#########################


def main(user_id, xml_path, playlist_name, year):
    scope = 'user-top-read'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    lib = library.parse(xml_path, ignoreRemoteSongs=False)

    playlist = lib.getPlaylist(playlist_name)

    for item in playlist.items:
        time.sleep(.1)
        spotify_search(item, year, sp)
    
    print("done")


if __name__ == "__main__":
    #pass
    xml_path = r'D:\Downloads\2001_Loved.xml'
    main("jwilso29", xml_path, "2001", "2001")

    # only use with year playlists