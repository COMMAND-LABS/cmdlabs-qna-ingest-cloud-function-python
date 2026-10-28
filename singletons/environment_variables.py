"""
Environment variables singleton

In production these are injected from Secret Manager at deploy time via
`gcloud functions deploy --set-secrets` (see README). Locally, load them from a .env file.
"""
import os


class EnvironmentVariables:
    EMBEDDINGS_API_URL: str = os.environ.get("EMBEDDINGS_API_URL", "")
    PINECONE_API_KEY: str = os.environ.get("PINECONE_API_KEY", "")
    PINECONE_ALL_MINILM_L6_V2_INDEX: str = os.environ.get("PINECONE_ALL_MINILM_L6_V2_INDEX", "")
    KB_INGEST_SA: str = os.environ.get("KB_INGEST_SA", "")
    POSTGRES_URL: str = os.environ.get("POSTGRES_URL", "")
    CREDENTIALS_ENCRYPTION_KEY: str = os.environ.get("CREDENTIALS_ENCRYPTION_KEY", "")
    # Optional: comma-separated previous keys, for key rotation
    CREDENTIALS_ENCRYPTION_KEY_OLD: str = os.environ.get("CREDENTIALS_ENCRYPTION_KEY_OLD", "")
