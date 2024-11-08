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
PLAYLIST_ID = 'PLpceAx4bWoTMmBJ-TL2g0futt0CSja6Jc'

# First, let's add a function to get all available blueprints to debug
def get_blueprints(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{API_URL}/blueprints', headers=headers)
    response.raise_for_status()
    return response.json()

def get_access_token(client_id, client_secret):
    credentials = {'clientId': client_id, 'clientSecret': client_secret}
    token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
    token_response.raise_for_status()
    return token_response.json()['accessToken']

def get_entity(api_url, blueprint_id, identifier, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{api_url}/blueprints/{blueprint_id}/entities/{identifier}', headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def create_or_update_entity(api_url, blueprint_id, entity_data, access_token):
    existing_entity = get_entity(api_url, blueprint_id, entity_data["identifier"], access_token)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    print(f"Creating/updating entity for blueprint: {blueprint_id}")  # Debug print
    
    if existing_entity:
        print(f"Updating existing entity: {entity_data['identifier']}")  # Debug print
        response = requests.put(
            f'{api_url}/blueprints/{blueprint_id}/entities/{entity_data["identifier"]}', 
            json=entity_data, 
            headers=headers
        )
    else:
        print(f"Creating new entity: {entity_data['identifier']}")  # Debug print
        response = requests.post(
            f'{api_url}/blueprints/{blueprint_id}/entities', 
            json=entity_data, 
            headers=headers
        )
    
    if response.status_code != 200 and response.status_code != 201:
        print(f"Error response: {response.status_code}")  # Debug print
        print(f"Response content: {response.text}")  # Debug print
    
    response.raise_for_status()
    return response.json()

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
    duration = response['items'][0]['contentDetails']['duration']
    return duration

def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    # First, let's get and print all available blueprints
    blueprints = get_blueprints(access_token)
    print("Available blueprints:")
    for blueprint in blueprints['blueprints']:
        print(f"- {blueprint['identifier']}")
    
    # Now proceed with the sync
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
            "has_videos": []
        }
    }
    
    videos = fetch_playlist_items(YOUTUBE_API_KEY, PLAYLIST_ID)
    video_ids = []
    
    # First create/update the playlist
    create_or_update_entity(API_URL, "youtubePlaylist", playlist_entity, access_token)
    
    for video in videos:
        video_id = video['contentDetails']['videoId']
        video_ids.append(video_id)
        
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
                "belongs_to_playlist": [PLAYLIST_ID]
            }
        }
        create_or_update_entity(API_URL, "youtubeVideo", video_entity, access_token)
    
    # Update playlist with video IDs
    playlist_entity["relations"]["has_videos"] = video_ids
    create_or_update_entity(API_URL, "youtubePlaylist", playlist_entity, access_token)

if __name__ == "__main__":
    main()
