import requests
from concurrent.futures import ThreadPoolExecutor
from ytmusicapi import YTMusic

ytmusic = YTMusic()

def getAccessToken():
    url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': 'c81471798011498a8d1c572988452e75',
        'client_secret': 'ade595ff2e97449a8eb499ec0a6638cc'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json().get('access_token')

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

access_token = getAccessToken()

url = "https://api.spotify.com/v1/playlists/06YhinCx7gKywjtJupZXyt/tracks"
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
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_track, track) for track in all_tracks]
    for future in futures:
        result = future.result()
        YTMusicLinks.append(result)

print(YTMusicLinks)

