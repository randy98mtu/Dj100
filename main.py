
import os
import requests
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_USER = os.getenv("LASTFM_USER")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public"))

def get_lastfm_top(period):
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={LASTFM_USER}&api_key={LASTFM_API_KEY}&format=json&period={period}&limit=50"
    data = requests.get(url).json()
    return [(t['artist']['name'], t['name']) for t in data['toptracks']['track']]

# Collect feeder sets
feeders = {
    'Last 30 Days': get_lastfm_top('1month')[:10],
    'Last 90 Days': get_lastfm_top('3month')[:10],
    'All Time': get_lastfm_top('overall')[:10],
}

# Flatten and shuffle
dj100_tracks = sum(feeders.values(), [])
random.shuffle(dj100_tracks)

# Search and collect Spotify URIs
track_uris = []
for artist, track in dj100_tracks:
    results = sp.search(q=f"track:{track} artist:{artist}", type="track", limit=1)
    items = results.get('tracks', {}).get('items', [])
    if items:
        track_uris.append(items[0]['uri'])

# Create playlist
user_id = sp.current_user()["id"]
playlist = sp.user_playlist_create(user=user_id, name="DJ100 – Autoplaylist", public=True)
sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_uris)

print(f"✅ DJ100 playlist created with {len(track_uris)} tracks.")
