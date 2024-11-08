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
PLAYLIST_ID = 'PLTwEf67PTkOs3KkKClKbddX2ckHaGDV3Z'

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

# Fetch video duration using YouTube API
def get_video_duration(youtube_api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(part="contentDetails", id=video_id)
    response = request.execute()
    duration = response['items'][0]['contentDetails']['duration']
    return duration

# Check if entity exists
def get_entity(api_url, blueprint_id, identifier, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{api_url}/blueprints/{blueprint_id}/entities/{identifier}', headers=headers)
    if response.status_code == 404:
        return None  # Entity does not exist
    response.raise_for_status()  # Raise an error for other bad responses
    return response.json()

# Create or update an entity
def create_or_update_entity(api_url, blueprint_id, entity_data, access_token):
    existing_entity = get_entity(api_url, blueprint_id, entity_data["identifier"], access_token)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    if existing_entity:
        # Update the existing entity
        response = requests.put(f'{api_url}/blueprints/{blueprint_id}/entities/{entity_data["identifier"]}', json=entity_data, headers=headers)
    else:
        # Create a new entity
        response = requests.post(f'{api_url}/blueprints/{blueprint_id}/entities', json=entity_data, headers=headers)
    
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    # Fetch and sync playlist
    playlist = fetch_playlist_details(YOUTUBE_API_KEY, PLAYLIST_ID)
    playlist_entity = {
        "identifier": PLAYLIST_ID,
        "title": playlist['snippet']['title'],
        "properties": {
            "playlistId": PLAYLIST_ID,
            "title": playlist['snippet']['title'],
            "description": playlist['snippet'].get('description', ''),
            "videoCount": playlist['contentDetails']['itemCount']
        },
        "relations": {
            "has_videos": []  # Will be populated with video IDs
        }
    }
    
    # Fetch and sync videos
    videos = fetch_playlist_items(YOUTUBE_API_KEY, PLAYLIST_ID)
    video_ids = []  # Store video IDs to update playlist relations
    
    for video in videos:
        video_id = video['contentDetails']['videoId']
        video_ids.append(video_id)
        
        # Fetch video duration
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
                "belongs_to_playlist": [PLAYLIST_ID]  # Make it an array even though it's a single value
            }
        }
        create_or_update_entity(API_URL, "youtube-video", video_entity, access_token)
    
    # Update playlist with all video IDs
    playlist_entity["relations"]["has_videos"] = video_ids
    create_or_update_entity(API_URL, "youtube-playlist", playlist_entity, access_token)

if __name__ == "__main__":
    main()
