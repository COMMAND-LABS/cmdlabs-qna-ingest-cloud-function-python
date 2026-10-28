# TLDR

# 

- `https://console.cloud.google.com/cloudpubsub/topic/create?project=command-labs`
- called `qna-ingest-topic`

#

enable GCP API [cloudfunctions.googleapis.com] on project
enable GCP API [eventarc.googleapis.com] on project

#

```sh
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