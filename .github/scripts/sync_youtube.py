from googleapiclient.discovery import build
from port.client import PortClient
import os

# Initialize clients
youtube = build('youtube', 'v3', developerKey=os.environ['YOUTUBE_API_KEY'])
port_client = PortClient()

PLAYLIST_ID = 'PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy'

def fetch_playlist_details():
    try:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            id=PLAYLIST_ID
        )
        response = request.execute()
        return response['items'][0]
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        raise

def fetch_playlist_items():
    items = []
    try:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=PLAYLIST_ID,
            maxResults=50
        )
        
        while request:
            response = request.execute()
            items.extend(response['items'])
            request = youtube.playlistItems().list_next(request, response)
        
        return items
    except Exception as e:
        print(f"Error fetching playlist items: {e}")
        raise

def sync_to_port():
    try:
        # Fetch and sync playlist
        playlist = fetch_playlist_details()
        playlist_entity = {
            "identifier": PLAYLIST_ID,
            "title": playlist['snippet']['title'],
            "properties": {
                "playlistId": PLAYLIST_ID,
                "description": playlist['snippet']['description'],
                "videoCount": playlist['contentDetails']['itemCount']
            }
        }
        
        port_client.create_entity("youtube-playlist", playlist_entity)
        
        # Fetch and sync videos
        videos = fetch_playlist_items()
        for video in videos:
            video_entity = {
                "identifier": video['contentDetails']['videoId'],
                "title": video['snippet']['title'],
                "properties": {
                    "videoId": video['contentDetails']['videoId'],
                    "description": video['snippet']['description'],
                    "thumbnailUrl": video['snippet']['thumbnails']['default']['url']
                },
                "relations": {
                    "playlist": PLAYLIST_ID
                }
            }
            
            port_client.create_entity("youtube-video", video_entity)
            
    except Exception as e:
        print(f"Error syncing to Port: {e}")
        raise

if _name_ == "_main_":
    sync_to_port()
