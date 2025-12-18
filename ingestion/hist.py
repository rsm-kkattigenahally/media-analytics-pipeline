import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

auth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope=os.getenv("SPOTIFY_SCOPE"),
    cache_path=".cache-spotify"
)

sp = spotipy.Spotify(auth_manager=auth)
print("Authenticated as:", sp.current_user()["display_name"])
