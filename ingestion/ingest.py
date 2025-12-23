import os
import json
from pathlib import Path
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import boto3
import io
from dotenv import load_dotenv
load_dotenv()
s3_client = boto3.client('s3')


#DIR = Path("/data/raw/spotify")

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),   
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=os.getenv("SPOTIFY_SCOPE", "user-read-recently-played"),
        cache_path="/opt/airflow/spotify_cache/.cache-spotify",
        #cache_path="../spotify_cache/.cache-spotify",
        #open_browser=True
    ))

def main():
    # create the path DIR, if it doesn't exist else do nothing
    # DIR.mkdir(parents=True, exist_ok=True)
    
    # spotify client
    sp = get_spotify_client()
    
    
    results = sp.current_user_recently_played()
    #local_path = LOCAL_DIR / filename
    filename = f"spotify_recently_played_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    #out_path = DIR / filename
    
    json_bytes = json.dumps(results, indent=2).encode("utf-8")
    fileobj = io.BytesIO(json_bytes)
    
    #upload to s3
    s3_client.upload_fileobj(
        Fileobj=fileobj,
        Bucket=os.getenv("S3_BUCKET_NAME"),
        Key=f"data/raw/spotify/{filename}"
    )
    return filename  


if __name__ == "__main__":
    main()