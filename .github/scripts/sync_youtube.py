# import requests
# import os
# import time
# from googleapiclient.discovery import build

# # Constants
# API_URL = 'https://api.getport.io/v1'

# # Get configuration from environment variables
# CLIENT_ID = os.environ.get('PORT_CLIENT_ID')
# CLIENT_SECRET = os.environ.get('PORT_CLIENT_SECRET')
# YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
# PLAYLIST_ID = 'PLpceAx4bWoTMmBJ-TL2g0futt0CSja6Jc'

# # First, let's add a function to get all available blueprints to debug
# def get_blueprints(access_token):
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     response = requests.get(f'{API_URL}/blueprints', headers=headers)
#     response.raise_for_status()
#     return response.json()

# def get_access_token(client_id, client_secret):
#     credentials = {'clientId': client_id, 'clientSecret': client_secret}
#     token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
#     token_response.raise_for_status()
#     return token_response.json()['accessToken']

# def get_entity(api_url, blueprint_id, identifier, access_token):
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     response = requests.get(f'{api_url}/blueprints/{blueprint_id}/entities/{identifier}', headers=headers)
#     if response.status_code == 404:
#         return None
#     response.raise_for_status()
#     return response.json()

# def create_or_update_entity(api_url, blueprint_id, entity_data, access_token):
#     existing_entity = get_entity(api_url, blueprint_id, entity_data["identifier"], access_token)
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
    
#     print(f"Creating/updating entity for blueprint: {blueprint_id}")  # Debug print
    
#     if existing_entity:
#         print(f"Updating existing entity: {entity_data['identifier']}")  # Debug print
#         response = requests.put(
#             f'{api_url}/blueprints/{blueprint_id}/entities/{entity_data["identifier"]}', 
#             json=entity_data, 
#             headers=headers
#         )
#     else:
#         print(f"Creating new entity: {entity_data['identifier']}")  # Debug print
#         response = requests.post(
#             f'{api_url}/blueprints/{blueprint_id}/entities', 
#             json=entity_data, 
#             headers=headers
#         )
    
#     if response.status_code != 200 and response.status_code != 201:
#         print(f"Error response: {response.status_code}")  # Debug print
#         print(f"Response content: {response.text}")  # Debug print
    
#     response.raise_for_status()
#     return response.json()

# def fetch_playlist_details(youtube_api_key, playlist_id):
#     youtube = build('youtube', 'v3', developerKey=youtube_api_key)
#     request = youtube.playlists().list(part="snippet,contentDetails", id=playlist_id)
#     response = request.execute()
#     return response['items'][0]

# def fetch_playlist_items(youtube_api_key, playlist_id):
#     youtube = build('youtube', 'v3', developerKey=youtube_api_key)
#     items = []
#     request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=playlist_id, maxResults=50)

#     while request:
#         response = request.execute()
#         items.extend(response['items'])
#         request = youtube.playlistItems().list_next(request, response)
#         time.sleep(0.1)
    
#     return items

# def get_video_duration(youtube_api_key, video_id):
#     youtube = build('youtube', 'v3', developerKey=youtube_api_key)
#     request = youtube.videos().list(part="contentDetails", id=video_id)
#     response = request.execute()
#     duration = response['items'][0]['contentDetails']['duration']
#     return duration

# def main():
#     access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
#     # First, let's get and print all available blueprints
#     blueprints = get_blueprints(access_token)
#     print("Available blueprints:")
#     for blueprint in blueprints['blueprints']:
#         print(f"- {blueprint['identifier']}")
    
#     # Now proceed with the sync
#     playlist = fetch_playlist_details(YOUTUBE_API_KEY, PLAYLIST_ID)
#     playlist_entity = {
#         "identifier": PLAYLIST_ID,
#         "title": playlist['snippet']['title'],
#         "properties": {
#             "playlistId": PLAYLIST_ID,
#             "title": playlist['snippet']['title'],
#             "description": playlist['snippet'].get('description', ''),
#             "videoCount": playlist['contentDetails']['itemCount']
#         },
#         "relations": {
#             "has_videos": []
#         }
#     }
    
#     videos = fetch_playlist_items(YOUTUBE_API_KEY, PLAYLIST_ID)
#     video_ids = []
    
#     # First create/update the playlist
#     create_or_update_entity(API_URL, "youtubePlaylist", playlist_entity, access_token)
    
#     for video in videos:
#         video_id = video['contentDetails']['videoId']
#         video_ids.append(video_id)
        
#         duration = get_video_duration(YOUTUBE_API_KEY, video_id)
        
#         video_entity = {
#             "identifier": video_id,
#             "title": video['snippet']['title'],
#             "properties": {
#                 "title": video['snippet']['title'],
#                 "videoId": video_id,
#                 "description": video['snippet'].get('description', ''),
#                 "thumbnailUrl": video['snippet']['thumbnails']['default']['url'],
#                 "duration": duration
#             },
#             "relations": {
#                 "belongs_to_playlist": [PLAYLIST_ID]
#             }
#         }
#         create_or_update_entity(API_URL, "youtubeVideo", video_entity, access_token)
    
#     # Update playlist with video IDs
#     playlist_entity["relations"]["has_videos"] = video_ids
#     create_or_update_entity(API_URL, "youtubePlaylist", playlist_entity, access_token)

# if __name__ == "__main__":
#     main()







import requests
import os
from googleapiclient.discovery import build
import time
import isodate

CLIENT_ID = os.environ.get('PORT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PORT_CLIENT_SECRET')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = 'PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy'

API_URL = 'https://api.getport.io/v1'

def format_duration(youtube_duration):
    # Convert ISO 8601 duration to readable format
    duration_obj = isodate.parse_duration(youtube_duration)
    minutes = int(duration_obj.total_seconds() // 60)
    seconds = int(duration_obj.total_seconds() % 60)
    return f"{minutes}:{seconds:02d}"

# Step 1: Get Port.io access token
credentials = {
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
}
token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
access_token = token_response.json()['accessToken']

headers = {
    'Authorization': f'Bearer {access_token}'
}

# Step 2: Set up YouTube API
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Step 3: Get playlist information with full details
playlist_request = youtube.playlists().list(
    part="snippet,contentDetails,status",
    id=PLAYLIST_ID
)
playlist_response = playlist_request.execute()
playlist = playlist_response['items'][0]

# Step 4: Create playlist entity for Port with additional properties
playlist_entity = {
    "identifier": PLAYLIST_ID,
    "title": playlist['snippet']['title'],
    "properties": {
        "playlistId": PLAYLIST_ID,
        "title": playlist['snippet']['title'],
        "description": playlist['snippet'].get('description', 'No description available'),
        "videoCount": playlist['contentDetails']['itemCount'],
        "thumbnailUrl": playlist['snippet']['thumbnails']['default']['url'],  # New property
        "createdAt": playlist['snippet']['publishedAt'],  # New property
        "updatedAt": playlist['status']['updatedAt']  # New property
    },
    "relations": {
        "has_videos": []
    }
}

# Step 5: Send playlist data to Port
playlist_response = requests.post(
    f'{API_URL}/blueprints/youtubePlaylist/entities?upsert=true',
    json=playlist_entity,
    headers=headers
)
print(f"Playlist sync status: {playlist_response.status_code}")

# Step 6: Get all videos in playlist
video_ids = []
next_page_token = None

while True:
    # Get batch of playlist items
    playlist_items_request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=PLAYLIST_ID,
        maxResults=50,
        pageToken=next_page_token
    )
    playlist_items = playlist_items_request.execute()
    
    # Process each video in the batch
    for item in playlist_items['items']:
        video_id = item['contentDetails']['videoId']
        video_ids.append(video_id)
        
        # Get video duration, view count, and other details
        video_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            id=video_id
        )
        video_response = video_request.execute()
        video_details = video_response['items'][0]
        
        # Format the duration to be readable
        youtube_duration = video_details['contentDetails']['duration']
        duration_str = format_duration(youtube_duration)
        
        # Create video entity with additional properties
        video_entity = {
            "identifier": video_id,
            "title": item['snippet']['title'],
            "properties": {
                "title": item['snippet']['title'],
                "videoId": video_id,
                "description": item['snippet'].get('description', 'No description available'),
                "thumbnailUrl": item['snippet']['thumbnails']['default']['url'],
                "duration": duration_str,
                "viewCount": video_details['statistics']['viewCount'],  # New property
                "likeCount": video_details['statistics']['likeCount'],  # New property
                "commentCount": video_details['statistics']['commentCount']  # New property
            },
            "relations": {
                "belongs_to_playlist": [PLAYLIST_ID]
            }
        }
        
        # Send video data to Port
        video_response = requests.post(
            f'{API_URL}/blueprints/youtubeVideo/entities?upsert=true',
            json=video_entity,
            headers=headers
        )
        print(f"Video sync status for {video_id}: {video_response.status_code}")
        
        # Small delay to respect API rate limits
        time.sleep(0.1)
    
    # Check if there are more videos to process
    next_page_token = playlist_items.get('nextPageToken')
    if not next_page_token:
        break

# Step 7: Update playlist with all video IDs
playlist_entity["relations"]["has_videos"] = video_ids
final_playlist_response = requests.post(
    f'{API_URL}/blueprints/youtubePlaylist/entities?upsert=true',
    json=playlist_entity,
    headers=headers
)
print("Sync complete!")













# # Dependencies to install:
# # $ python -m pip install requests google-api-python-client

# import requests
# import os
# from googleapiclient.discovery import build
# import time
# import isodate

# CLIENT_ID = os.environ.get('PORT_CLIENT_ID')
# CLIENT_SECRET = os.environ.get('PORT_CLIENT_SECRET')
# YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
# PLAYLIST_ID = 'PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy'

# # Port.io configuration
# # CLIENT_ID = 'YOUR_PORT_CLIENT_ID'
# # CLIENT_SECRET = 'YOUR_PORT_SECRET'
# API_URL = 'https://api.getport.io/v1'

# # YouTube configuration
# # YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'
# # PLAYLIST_ID = 'YOUR_PLAYLIST_ID'


# # def format_duration(youtube_duration):
# #     # Convert ISO 8601 duration to readable format
# #     duration_obj = isodate.parse_duration(youtube_duration)
# #     minutes = int(duration_obj.total_seconds() // 60)
# #     seconds = int(duration_obj.total_seconds() % 60)
# #     return f"{minutes}:{seconds:02d}"

# # Step 1: Get Port.io access token
# credentials = {
#     'clientId': CLIENT_ID,
#     'clientSecret': CLIENT_SECRET
# }
# token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
# access_token = token_response.json()['accessToken']

# headers = {
#     'Authorization': f'Bearer {access_token}'
# }

# # Step 2: Set up YouTube API
# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# # Step 3: Get playlist information with full details
# playlist_request = youtube.playlists().list(
#     part="snippet,contentDetails,status",  # Added more parts to get full details
#     id=PLAYLIST_ID
# )
# playlist_response = playlist_request.execute()
# playlist = playlist_response['items'][0]

# # Step 4: Create playlist entity for Port with description
# playlist_entity = {
#     "identifier": PLAYLIST_ID,
#     "title": playlist['snippet']['title'],
#     "properties": {
#         "playlistId": PLAYLIST_ID,
#         "title": playlist['snippet']['title'],
#         "description": playlist['snippet'].get('description', 'No description available'),  # Default value if empty
#         "videoCount": playlist['contentDetails']['itemCount']
#     },
#     "relations": {
#         "has_videos": []
#     }
# }

# # Step 5: Send playlist data to Port
# playlist_response = requests.post(
#     f'{API_URL}/blueprints/youtubePlaylist/entities?upsert=true',
#     json=playlist_entity,
#     headers=headers
# )
# print(f"Playlist sync status: {playlist_response.status_code}")

# # Step 6: Get all videos in playlist
# video_ids = []
# next_page_token = None

# while True:
#     # Get batch of playlist items
#     playlist_items_request = youtube.playlistItems().list(
#         part="snippet,contentDetails",
#         playlistId=PLAYLIST_ID,
#         maxResults=50,
#         pageToken=next_page_token
#     )
#     playlist_items = playlist_items_request.execute()
    
#     # Process each video in the batch
#     for item in playlist_items['items']:
#         video_id = item['contentDetails']['videoId']
#         video_ids.append(video_id)
        
#         # Get video duration and other details
#         video_request = youtube.videos().list(
#             part="contentDetails,snippet",  # Added snippet to get full details
#             id=video_id
#         )
#         video_response = video_request.execute()
#         video_details = video_response['items'][0]
        
#         # Format the duration to be readable
#         youtube_duration = video_details['contentDetails']['duration']
#         duration_obj = isodate.parse_duration(youtube_duration)
#         minutes = int(duration_obj.total_seconds() // 60)
#         seconds = int(duration_obj.total_seconds() % 60)
#         duration_str = f"{minutes}:{seconds:02d}"
        
#         # Create video entity with formatted duration
#         video_entity = {
#             "identifier": video_id,
#             "title": item['snippet']['title'],
#             "properties": {
#                 "title": item['snippet']['title'],
#                 "videoId": video_id,
#                 "description": item['snippet'].get('description', 'No description available'),  # Default value if empty
#                 "thumbnailUrl": item['snippet']['thumbnails']['default']['url'],
#                 "duration": duration_str  # Now using formatted duration
#             },
#             "relations": {
#                 "belongs_to_playlist": [PLAYLIST_ID]
#             }
#         }
        
#         # Send video data to Port
#         video_response = requests.post(
#             f'{API_URL}/blueprints/youtubeVideo/entities?upsert=true',
#             json=video_entity,
#             headers=headers
#         )
#         print(f"Video sync status for {video_id}: {video_response.status_code}")
        
#         # Small delay to respect API rate limits
#         time.sleep(0.1)
    
#     # Check if there are more videos to process
#     next_page_token = playlist_items.get('nextPageToken')
#     if not next_page_token:
#         break

# # Step 7: Update playlist with all video IDs
# playlist_entity["relations"]["has_videos"] = video_ids
# final_playlist_response = requests.post(
#     f'{API_URL}/blueprints/youtubePlaylist/entities?upsert=true',
#     json=playlist_entity,
#     headers=headers
# )
# print("Sync complete!")
