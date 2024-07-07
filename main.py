import requests
from os import cpu_count
from concurrent.futures import ThreadPoolExecutor
from ytmusicapi import YTMusic,setup_oauth
import create_secrets
import secrets
ytmusic = YTMusic("oauth.json")
def getAccessToken():
    url = "https://accounts.spotify.com/api/token"
    payload = {
            'grant_type': 'client_credentials',
            'client_id': secrets.CLIENT_ID,
            'client_secret': secrets.CLIENT_SECRET
            }
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
            }
    response = requests.post(url, headers=headers, data=payload)
    access_token = response.json().get('access_token')
    if access_token == None:
        print("Invalid secrets, recreating secrets...")
        create_secrets.main(bad_secrets=True)
    return access_token
def getPlaylistID(url):
    return url.split('/')[4].split('?')[0]

def getTracks(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()

def isValidTrackInfo(new_track):
    return new_track['album'] != "" and new_track['track'] != "" and new_track['artist'] != ""

def filterTrackInfo(track_info):
    track_list = []
    for item in track_info['items']:
        track = item['track']
        album_name = track['album']['name']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        new_track = {'album': album_name, 'track': track_name, 'artist': artist_name}
        if isValidTrackInfo(new_track):
            track_list.append(new_track)
    return track_list

def getYTMusicLinks(track):
    query = track["track"]
    filter = "songs"
    limit = 3  # Limit not working 
    ignore_spelling = True
    data = ytmusic.search(query=query, filter=filter, limit=limit, ignore_spelling=ignore_spelling)
    track_info = [{'videoId': item['videoId'], 'title': item['title']} for item in data]
    return track_info

def process_track(track):
    return getYTMusicLinks(track)[0]  # will change when limit gets fixed

def main():
    create_secrets.main()
    access_token = getAccessToken()
    spotify_playlist_id = getPlaylistID(input("Enter link to spotify playlist"))
    new_playlist_name = input("Enter the name of the new playlist: ")
    new_playlist_description = input("Enter the description of the new playlist: ")
    str1 = r"https://api.spotify.com/v1/playlists/"
    str2 = r"/tracks" 
    url = f"{str1}{spotify_playlist_id}{str2}"
    headers = {
            'Authorization': 'Bearer ' + access_token,
            }

    all_tracks = []

# Fetch tracks from Spotify
    while url:
        track_info = getTracks(url, headers)
        filtered_tracks = filterTrackInfo(track_info)
        all_tracks.extend(filtered_tracks)
        url = track_info.get('next')  

    YTMusicLinks = []
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        futures = [executor.submit(process_track, track) for track in all_tracks]
        for future in futures:
            result = future.result()
            YTMusicLinks.append(result)

    video_ids = [item['videoId'] for item in YTMusicLinks]
    
    print(ytmusic.create_playlist(title=new_playlist_name,description=new_playlist_description,video_ids = video_ids))

if __name__ == "__main__":
    main()
