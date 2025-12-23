# Media Analytics Pipeline

An end-to-end data pipeline for collecting and transforming media listening data (e.g. Spotify recently played tracks). The project uses Docker + Airflow to orchestrate ingestion from external APIs and cleaning/transform steps, with credentials and configuration managed via a `.env` file.

## Project Structure

- `docker-compose.yml` – Defines the Airflow stack (Postgres, webserver, scheduler) and mounts local code into the containers.
- `Dockerfile` – Custom Airflow image used by `webserver` and `scheduler`.
- `airflow/` – Airflow DAGs and plugins.
- `ingestion/` – Spotify ingestion code.
  - `ingest.py` – Fetches "recently played" data from the Spotify API and writes raw JSON.
  - `requirements.txt` – Python dependencies for the ingestion component.
- `transform/` – Data cleaning and transformation code.
  - `clean_spotify.py` – Reads raw Spotify data (e.g. from S3) and cleans/transforms it using pandas.
  - `requirements.txt` – Python dependencies for the transform component.
- `spotify_cache/` – Local cache directory used by the Spotify client/auth flow.
- `.env` – Environment variables for Spotify, AWS/S3, and Airflow (not committed).

## Environment Variables

Create a `.env` file in the project root with (at minimum) values like:

```env
# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_SCOPE=user-read-recently-played

# AWS / S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Airflow (override as needed)
AIRFLOW_UID=50000
```

Never commit real secrets to version control.

## Running with Docker Compose

From the project root:

```bash
docker-compose up --build
```

Once the containers are up:

- Access the Airflow web UI at: http://localhost:8080
- Enable the media analytics DAG (once you have a DAG defined in `airflow/dags`).

The `ingestion/` and `transform/` folders are mounted into the Airflow containers so that PythonOperators in your DAGs can import:

```python
from ingestion.ingest import main as ingest_spotify
from transform.clean_spotify import main as clean_spotify
```

## Local Development (Optional)

You can also run the ingestion or transform scripts directly on your host machine (outside Docker) for quick testing.

Example (from project root):

```bash
# WSL / Linux
python ingestion/ingest.py
python transform/clean_spotify.py
```

Make sure you have the required dependencies installed:

```bash
pip install -r ingestion/requirements.txt
pip install -r transform/requirements.txt
```

## Final Steps

- Add one or more DAGs under `airflow/dags/` to orchestrate:
  - Spotify ingestion (raw JSON to S3 or local storage).
  - Cleaning and transformation of the raw data.
  - Loading into your analytics destination (e.g. Snowflake, Postgres, files).
- Build dashboards or analyses on top of the cleaned media data.
