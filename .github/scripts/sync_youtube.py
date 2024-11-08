import requests
import os
import time
from googleapiclient.discovery import build

# Constants
API_URL = 'https://api.getport.io/v1'

# Get configuration from environment variables
CLIENT_ID = os.environ.get('PORT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PORT_CLIENT_SECRET')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = 'PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy'

if not all([CLIENT_ID, CLIENT_SECRET, YOUTUBE_API_KEY, PLAYLIST_ID]):
    raise ValueError("Missing required environment variables")

def get_access_token(client_id, client_secret):
    credentials = {'clientId': client_id, 'clientSecret': client_secret}
    token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
    token_response.raise_for_status()
    return token_response.json()['accessToken']

def fetch_playlist_details(youtube_api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.playlists().list(part="snippet,contentDetails", id=playlist_id)
    response = request.execute()
    return response['items'][0]

def fetch_playlist_items(youtube_api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    items = []
    request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=playlist_id, maxResults=50)

    while request:
        response = request.execute()
        items.extend(response['items'])
        request = youtube.playlistItems().list_next(request, response)
        time.sleep(0.1)

    return items

def get_video_duration(youtube_api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(part="contentDetails", id=video_id)
    response = request.execute()
    return response['items'][0]['contentDetails']['duration']

def create_entity(api_url, blueprint_id, entity_data, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(f'{api_url}/blueprints/{blueprint_id}/entities', json=entity_data, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    # Create or update playlist entity
    playlist = fetch_playlist_details(YOUTUBE_API_KEY, PLAYLIST_ID)
    playlist_entity = {
        "identifier": PLAYLIST_ID,
        "title": playlist['snippet']['title'],
        "properties": {
            "playlistId": PLAYLIST_ID,
            "title": playlist['snippet']['title'],
            "description": playlist['snippet'].get('description', ''),
            "videoCount": playlist['contentDetails']['itemCount']
        }
    }
    create_entity(API_URL, "youtube-playlist", playlist_entity, access_token)
    
    # Create or update video entities with relations
    videos = fetch_playlist_items(YOUTUBE_API_KEY, PLAYLIST_ID)
    for video in videos:
        video_id = video['contentDetails']['videoId']
        duration = get_video_duration(YOUTUBE_API_KEY, video_id)
        
        video_entity = {
            "identifier": video_id,
            "title": video['snippet']['title'],
            "properties": {
                "title": video['snippet']['title'],
                "videoId": video_id,
                "description": video['snippet'].get('description', ''),
                "thumbnailUrl": video['snippet']['thumbnails']['default']['url'],
                "duration": duration
            },
            "relations": {
                "playlist_video_relationship": PLAYLIST_ID
            }
        }
        create_entity(API_URL, "youtube-video", video_entity, access_token)

if __name__ == "__main__":
    main()
