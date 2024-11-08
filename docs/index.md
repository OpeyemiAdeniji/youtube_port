
---
sidebar_position: 4
displayed_sidebar: null
description: Learn how to ingest and visualize YouTube playlist and video data in Port to optimize content strategies and gain insights.
---

import Tabs from "@theme/Tabs"
import TabItem from "@theme/TabItem"
import PortTooltip from "/src/components/tooltip/tooltip.jsx"
import PortApiRegionTip from "/docs/generalTemplates/_port_region_parameter_explanation_template.md"

# Ingest and Visualize YouTube Playlist Data in Port

This guide takes approximately 30 minutes to complete and aims to demonstrate the value of Port's integration with external data sources like YouTube.

:::info Prerequisites

- This guide assumes you have a Port account and that you have completed the [onboarding process](/quickstart). 
- Access to a GitHub repository for workflow integration.
- API keys and credentials: Port Client ID, Client Secret, and YouTube API Key.

:::

<br/>

### The goal of this guide

In this guide, we will model and visualize YouTube playlist and video data in Port.

By completing this guide, you will understand:

- How to create and configure blueprints in Port for YouTube data.
- How to set up a GitHub workflow to automate data ingestion from YouTube.
- How to visualize and analyze the ingested data in Port.

<br/>

### Step 1: Create Blueprints in Port

Create blueprints for both `YouTube Video` and `YouTube Playlist`:

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

**Example JSON**:
```json showLineNumbers
{
  "identifier": "youtubeVideo",
  "title": "YouTube Video",
  "schema": {
    "properties": {
      "videoId": {"type": "string", "title": "Video ID"},
      "title": {"type": "string", "title": "Title"},
      "description": {"type": "string", "title": "Description"},
      "thumbnailUrl": {"type": "string", "title": "Thumbnail URL"},
      "duration": {"type": "string", "title": "Duration"},
      "viewCount": {"type": "number", "title": "View Count"},
      "likeCount": {"type": "number", "title": "Like Count"},
      "commentCount": {"type": "number", "title": "Comment Count"}
    },
    "required": ["videoId", "title"]
  }
}
```

#### Blueprint for YouTube Playlist

- **Properties**:
  - `playlistId`: string (required)
  - `title`: string (required)
  - `description`: string
  - `videoCount`: number
  - `thumbnailUrl`: string
  - `created_at`: string

**Example JSON**:
```json showLineNumbers
{
  "identifier": "youtubePlaylist",
  "title": "YouTube Playlist",
  "schema": {
    "properties": {
      "playlistId": {"type": "string", "title": "Playlist ID"},
      "title": {"type": "string", "title": "Title"},
      "description": {"type": "string", "title": "Description"},
      "videoCount": {"type": "number", "title": "Video Count"},
      "thumbnailUrl": {"type": "string", "title": "Thumbnail URL"},
      "created_at": {"type": "string", "title": "CreatedAt"}
    },
    "required": ["playlistId", "title"]
  }
}
```

<br/>

### Step 2: Set Up the GitHub Workflow

Create a GitHub workflow file (`.github/workflows/sync_youtube_data.yml`):

```yaml showLineNumbers
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

<br/>

### Step 3: Implement the YouTube Data Sync Script

Create a script (`.github/scripts/sync_youtube.py`):

```python showLineNumbers
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

<PortApiRegionTip/>

<br/>

### Step 4: Run and Verify Workflow

1. Trigger the GitHub action manually or wait for the scheduled run.
2. Verify the ingestion status in the workflow logs.
3. Check the data in your Port account.

<br/>

### Step 5: Visualize Data in Port

Create custom visualizations in Port for better insights:

- **Playlist metrics**: Visualize video count and total views.
- **Engagement analysis**: Use dashboards to analyze likes and comments.

<br/>

### Conclusion

Following this guide, you can ingest YouTube playlist data into Port and visualize it effectively, enabling data-driven decisions and optimizing your content strategy.

---

