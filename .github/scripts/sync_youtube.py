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

# Ensure all required environment variables are present
if not all([CLIENT_ID, CLIENT_SECRET, YOUTUBE_API_KEY, PLAYLIST_ID]):
    raise ValueError("Missing required environment variables")

# Step 1: Get access token from Port API
def get_access_token(client_id, client_secret):
    credentials = {'clientId': client_id, 'clientSecret': client_secret}
    token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
    token_response.raise_for_status()  # Raise an error for bad responses
    return token_response.json()['accessToken']

# Step 2: Fetch playlist details from YouTube
def fetch_playlist_details(youtube_api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.playlists().list(part="snippet,contentDetails", id=playlist_id)
    response = request.execute()
    return response['items'][0]

# Step 3: Fetch all videos in the playlist
def fetch_playlist_items(youtube_api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    items = []
    request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=playlist_id, maxResults=50)

    while request:
        response = request.execute()
        items.extend(response['items'])
        request = youtube.playlistItems().list_next(request, response)
        time.sleep(0.1)  # Respect YouTube API quota

    return items

# Step 4: Create an entity in Port
def create_entity(api_url, blueprint_id, entity_data, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(f'{api_url}/blueprints/{blueprint_id}/entities', json=entity_data, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

# Main execution flow
def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    # Fetch and sync playlist
    playlist = fetch_playlist_details(YOUTUBE_API_KEY, PLAYLIST_ID)
    playlist_entity = {
        "identifier": PLAYLIST_ID,
        "title": playlist['snippet']['title'],
        "properties": {
            "playlistId": PLAYLIST_ID,
            "description": playlist['snippet'].get('description', ''),
            "videoCount": playlist['contentDetails']['itemCount']
        }
    }
    create_entity(API_URL, "youtube-playlist", playlist_entity, access_token)
    
    # Fetch and sync videos
    videos = fetch_playlist_items(YOUTUBE_API_KEY, PLAYLIST_ID)
    for video in videos:
        video_entity = {
            "identifier": video['contentDetails']['videoId'],
            "title": video['snippet']['title'],
            "properties": {
                "videoId": video['contentDetails']['videoId'],
                "description": video['snippet'].get('description', ''),
                "thumbnailUrl": video['snippet']['thumbnails']['default']['url']
            },
            "relations": {
                "playlist": PLAYLIST_ID
            }
        }
        create_entity(API_URL, "youtube-video", video_entity, access_token)

if __name__ == "__main__":
    main()
