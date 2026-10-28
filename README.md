# TLDR

Cloud Function for ingesting QnA knowledge stored in a .csv into a Pinecone Vector DB

## How to run this project locally

### Install dependencies

**Using UV (recommended, consistent with other Kalygo projects):**

```sh
# Install UV if you haven't already: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

**Using pip (alternative):**

```sh
pip install -r requirements.txt
```

Note: `requirements.txt` is maintained for Google Cloud Functions deployment compatibility, but `pyproject.toml` is the source of truth for development.

### Run locally with Functions Framework

The function automatically detects HTTP vs Pub/Sub triggers (matching the Node.js implementation).

Configuration is read from environment variables (see [Required Secrets](#required-secrets)). Copy `.env.example` to `.env` and fill it in.

**Using UV:**

```sh
uv run --env-file .env functions-framework --target=process_qna_ingest_topic_message --source=main.py
```

**Using pip:**

```sh
set -a && source .env && set +a
functions-framework --target=process_qna_ingest_topic_message --source=main.py
```

The function will automatically handle both HTTP requests (for local testing) and Pub/Sub events (in production).

## Set up a topic

Create a Pub/Sub topic named `qna-ingest-topic` in your GCP project.

## How to deploy to GCF

```sh
# Of course make sure the Cloud Functions API is enabled in your project
# gcloud services enable cloudfunctions.googleapis.com

# Then deploy the function
gcloud functions deploy process-qna-ingest-topic-message-python \
--project=command-labs \
--gen2 \
--runtime=python312 \
--region=us-east1 \
--source=. \
--entry-point=process_qna_ingest_topic_message \
--trigger-topic=qna-ingest-topic \
--memory=1GB \
--timeout=540s \
--max-instances=10 \
--set-secrets=EMBEDDINGS_API_URL=EMBEDDINGS_API_URL:latest,PINECONE_API_KEY=PINECONE_API_KEY:latest,PINECONE_ALL_MINILM_L6_V2_INDEX=PINECONE_ALL_MINILM_L6_V2_INDEX:latest,KB_INGEST_SA=KB_INGEST_SA:latest,POSTGRES_URL=POSTGRES_URL:latest,CREDENTIALS_ENCRYPTION_KEY=CREDENTIALS_ENCRYPTION_KEY:latest
```

## cURL for testing the Cloud Function locally (that will eventually act as the subscriber of a Pub/Sub topic)

```sh
curl -X POST http://localhost:8080/ \
-H "Content-Type: application/json" \
-d '{ "data": "'$(echo -n '{"action":"process","key":"value"}' | base64)'", "attributes": { "exampleAttribute": "exampleValue" } }'
```

## Publishing a test message onto the Pub/Sub topic to confirm the Cloud Function gets triggered

```sh
gcloud pubsub topics publish qna-ingest-topic \
--message='{"action":"process","key":"value"}' \
--attribute=test=true
```

## Watch logs in real-time

```sh
gcloud functions logs tail process-qna-ingest-topic-message --region=us-east1
```

## Or view recent logs

```sh
gcloud functions logs read process-qna-ingest-topic-message --region=us-east1 --limit=50
```

## Required Secrets

Configuration is read from environment variables. In production they're injected from Google Secret Manager at deploy time by the `--set-secrets` flag above, so each one must exist as a secret in the function's project:

- `EMBEDDINGS_API_URL` - URL of the embeddings API service
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ALL_MINILM_L6_V2_INDEX` - Default Pinecone index name
- `KB_INGEST_SA` - Service account JSON (base64 encoded or raw JSON) for the default GCS client
- `POSTGRES_URL` - PostgreSQL connection URL (for ingestion logging and per-account credentials)
- `CREDENTIALS_ENCRYPTION_KEY` - Fernet key for decrypting per-account credentials
- `CREDENTIALS_ENCRYPTION_KEY_OLD` - *(optional)* comma-separated previous keys during key rotation; add `CREDENTIALS_ENCRYPTION_KEY_OLD=CREDENTIALS_ENCRYPTION_KEY_OLD:latest` to `--set-secrets` when needed

The function's runtime service account needs `roles/secretmanager.secretAccessor`. Secrets are read when an instance starts, so after rotating a secret, redeploy (or wait for new instances) to pick it up.

## Project Structure

```
.
├── main.py                 # Entry point (handles both HTTP and Pub/Sub triggers)
├── requirements.txt       # Python dependencies
├── helpers/               # Helper modules
│   ├── csv_processor.py   # CSV parsing and processing
│   ├── embedding.py       # Embedding API client
│   ├── gcs.py             # Google Cloud Storage helpers
│   └── pinecone.py        # Pinecone client helpers
├── clients/               # Client factories
│   └── gcs_client_factory.py
└── singletons/            # Singleton modules
    └── environment_variables.py  # All config, read from env vars
```
