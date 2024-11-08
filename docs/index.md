
# Ingest and Visualize YouTube Playlist Data in Port

This guide takes approximately 30 minutes to complete and demonstrates the value of integrating Port with external data sources like YouTube.

## Prerequisites

- Ensure you have a Port account and have completed the [onboarding process](/quickstart).
- Access to a GitHub repository for workflow integration.
- API keys and credentials: Port Client ID, Client Secret, and YouTube API Key.

## Goal of This Guide

This guide will walk you through:

- Creating and configuring blueprints in Port for YouTube data.
- Setting up a GitHub workflow to automate data ingestion from YouTube.
- Visualizing and analyzing the ingested data in Port.

---

## Step 1: Create Blueprints in Port

### 1.1 Log in to Your Port Account
Access Port's web app and log in with your credentials.

### 1.2 Navigate to the Builder Section
Click on **"Builder"** in the left-hand navigation menu. This is where you create and manage blueprints.

### 1.3 Create a Blueprint for YouTube Video
1. Click on **"New Blueprint"** at the top right corner of the Builder page.
2. Configure the blueprint details:
   - **Identifier**: `youtubeVideo`
   - **Title**: `YouTube Video`
   - **Icon**: Choose an icon representing a video (optional).

### Define the Schema
Add properties to the YouTube Video blueprint with names, types, and whether they are required:

#### Blueprint for YouTube Video
- **Properties**:
  - `videoId`: string (required)
  - `title`: string (required)
  - `description`: string
  - `thumbnailUrl`: string
  - `duration`: string
  - `viewCount`: number
  - `likeCount`: number
  - `commentCount`: number
- **Relation**: `belongs_to_playlist` to `YouTube Playlist`.

**Example JSON**:
```json
{
  "identifier": "youtubeVideo",
  "description": "This blueprint represents a video in our software catalog",
  "title": "YouTube Video",
  "icon": "Widget",
  "schema": {
    "properties": {
      "videoId": { "type": "string", "title": "Video ID" },
      "title": { "type": "string", "title": "Title" },
      "description": { "type": "string", "title": "Description" },
      "thumbnailUrl": { "type": "string", "title": "Thumbnail URL" },
      "duration": { "type": "string", "title": "Duration" },
      "viewCount": { "type": "number", "title": "View Count" },
      "likeCount": { "type": "number", "title": "Like Count" },
      "commentCount": { "type": "number", "title": "Comment Count" }
    },
    "required": ["videoId", "title"]
  },
  "relations": {
    "belongs_to_playlist": {
      "title": "Belongs to Playlist",
      "target": "youtubePlaylist",
      "required": false,
      "many": false
    }
  }
}
```

### Blueprint for YouTube Playlist
- **Properties**:
  - `playlistId`: string (required)
  - `title`: string (required)
  - `description`: string
  - `videoCount`: number
  - `thumbnailUrl`: string
  - `created_at`: string
- **Relation**: `has_videos` to `YouTube Video`.

**Example JSON**:
```json
{
  "identifier": "youtubePlaylist",
  "title": "YouTube Playlist",
  "icon": "Widget",
  "schema": {
    "properties": {
      "playlistId": { "type": "string", "title": "Playlist ID" },
      "title": { "type": "string", "title": "Title" },
      "description": { "type": "string", "title": "Description" },
      "videoCount": { "type": "number", "title": "Video Count" },
      "thumbnailUrl": { "type": "string", "title": "Thumbnail URL" },
      "created_at": { "type": "string", "title": "CreatedAt" }
    },
    "required": ["playlistId", "title"]
  },
  "relations": {
    "has_videos": {
      "title": "Has Videos",
      "target": "youtubeVideo",
      "required": false,
      "many": true
    }
  }
}
```

---

## Step 2: Set Up the GitHub Workflow

Create a GitHub workflow file at `.github/workflows/sync_youtube_data.yml`:

```yaml
name: Sync YouTube Data to Port

on:
  schedule:
    - cron: '0 */12 * * *'  # Runs every 12 hours
  workflow_dispatch:  # Manual triggers
  push:
    branches: [ main ]

jobs:
  sync-youtube-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
          
      - name: Install dependencies
        run: |
          pip install google-api-python-client isodate

      - name: Sync YouTube data
        env:
          PORT_CLIENT_ID: ${{ secrets.PORT_CLIENT_ID }}
          PORT_CLIENT_SECRET: ${{ secrets.PORT_CLIENT_SECRET }}
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        run: |
          python .github/scripts/sync_youtube.py
```

### Add Secrets
Add the following secrets to your GitHub repository:

1. Go to **Settings** > **Secrets and Variables** > **Actions**.
2. Create secrets:
   - `PORT_CLIENT_ID`: Your Port Client ID
   - `PORT_CLIENT_SECRET`: Your Port Client Secret
   - `YOUTUBE_API_KEY`: Your YouTube API Key

---

## Step 3: Implement the YouTube Data Sync Script

Create a script (`.github/scripts/sync_youtube.py`):

```python
import requests
import os
from googleapiclient.discovery import build
import isodate
import time

CLIENT_ID = os.environ.get('PORT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PORT_CLIENT_SECRET')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
PLAYLIST_ID = 'YOUR_PLAYLIST_ID'

API_URL = 'https://api.getport.io/v1'

# Fetch Port access token
credentials = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET}
token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
access_token = token_response.json()['accessToken']

headers = {'Authorization': f'Bearer {access_token}'}
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Get playlist and video details, format, and send data to Port
# (Add your detailed data ingestion logic here)
```

---

## Step 4: Run and Verify the Workflow

1. **Trigger the Action**: Run the GitHub action manually or wait for the scheduled run.
2. **Check the Logs**: Review the workflow logs for the status of the ingestion process.
3. **Verify in Port**: Ensure the data appears in your Port account with proper relationships.

---

## Step 5: Visualize Data in Port

Leverage Port's visualization tools for insights:

- **Playlist Metrics**: Display video count and total views.
- **Engagement Analysis**: Use dashboards to monitor likes and comments.

---

## Conclusion

By following this guide, you can effectively ingest and visualize YouTube playlist data in Port, enabling data-driven decisions and enhancing your content strategy.

---

