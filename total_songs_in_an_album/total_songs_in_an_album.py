import spotipy
import os
from dotenv import load_dotenv
import time

def spotipy_token(scope, username):
    env_path = r'D:\Documents\Python_Git_SpotifyAPI_2'
    project_folder = os.path.expanduser(env_path)
    load_dotenv(os.path.join(project_folder, '.env'))
    token = spotipy.util.prompt_for_user_token(username, scope)
    return token

def main(filepath, filepath2):
    user_id = 'jwilso29'
    scope = 'user-library-read'
    token = spotipy_token(scope, user_id)
    sp = spotipy.Spotify(auth=token)

    f = open(filepath, 'r', encoding='utf-8')
    album_list = list()
    line = f.readline()
    album_list = line.split('||')
    f.close()

    total_songs_list = list()
    for album in album_list:
        split = album.split('|')
        result = sp.search('artist:' + split[0] + ' ' + 'album:' + split[1] , limit=1, type='album')
        if len(result['albums']['items']) < 1:
            print(album)
            total_songs_list.append('1000')
            continue
        elif result['albums']['items'][0]['release_date'] > '2020-01-01':
            total_songs_list.append(result['albums']['items'][0]['total_tracks'])
            time.sleep(.5)

    if len(total_songs_list) != len(album_list):
        print(len(total_songs_list))
        print(len(album_list))


    f = open(filepath2, 'w', encoding='utf-8')
    for length in total_songs_list:
        f.write(str(length) + '\n')
    f.close()

if __name__ == "__main__":
    #pass
    main(r'D:\Documents\Music Stuff\2020_albums.txt', r'D:\Documents\Music Stuff\2020_albums_total_songs.txt')