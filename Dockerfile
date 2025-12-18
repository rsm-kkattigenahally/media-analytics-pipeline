FROM apache/airflow:2.8.0

WORKDIR /tmp

COPY transform/requirements.txt tmp/requirements.txt
RUN pip install --no-cache-dir -r tmp/requirements.txt

COPY ingestion/requirements.txt tmp/requirements.txt
RUN pip install --no-cache-dir -r tmp/requirements.txt

