import boto3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO
import os

#list files from s3
s3_client = boto3.client('s3')
RAW_PREFIX = "data/raw/spotify/"
SILVER_PREFIX = "data/silver/spotify/"
BUCKET = os.getenv("S3_BUCKET_NAME")

def list_raw_files(bucket):
    bucket_f = s3_client.list_objects_v2(
        Bucket = bucket,
       
    )
    files_name = [object['Key'] for object in bucket_f.get('Contents', []) if object["Key"].endswith(".json")]
    return files_name

def load_json_file(bucket, key):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    file_content = object['Body'].read().decode('utf-8')
    #print(file_content)
    return json.loads(file_content)

def normalize_spotify_items(json_data: dict):
    """Flatten raw Spotify items."""
    rows = []

    items = json_data.get("items", [])
    if not items:
        print("WARNING: No items found in JSON.")
        return rows

    for item in items:
        track = item.get("track") or {}
        album = track.get("album") or {}
        artists = track.get("artists") or [{}]
        artist = artists[0] if artists else {}

        # Context may be NULL → safe-handling
        context_obj = item.get("context") or {}
        context_uri = context_obj.get("uri")

        rows.append({
            "played_at": item.get("played_at"),
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "artist_name": artist.get("name"),
            "artist_id": artist.get("id"),
            "album_name": album.get("name"),
            "album_release_date": album.get("release_date"),
            "duration_ms": track.get("duration_ms"),
            "popularity": track.get("popularity"),
            "context_uri": context_uri,
        })

    return rows

def save_parquet_to_s3(df, bucket, key):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    key = f"{SILVER_PREFIX}spotify_silver_{ts}.parquet"

    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    s3_client.upload_fileobj(buffer, bucket, key)
    print(f"Uploaded Silver layer to → s3://{bucket}/{key}")
    
def main(filename=None):
    if not filename:
        raise ValueError("No filename provided for transform step")

    key = f"{RAW_PREFIX}{filename}"
    json_data = load_json_file(BUCKET, key)

    rows = normalize_spotify_items(json_data)
    df = pd.DataFrame(rows)

    save_parquet_to_s3(df, BUCKET, SILVER_PREFIX)
    
if __name__ == "__main__":
    main()
