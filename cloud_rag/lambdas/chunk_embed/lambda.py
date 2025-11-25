import boto3
import json
import os

s3 = boto3.client("s3")

VECTOR_BUCKET = os.environ.get("VECTOR_BUCKET")
VECTOR_INDEX = os.environ.get("VECTOR_INDEX")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")


def lambda_handler(event, context):
    """
    CURRENT BEHAVIOUR:
      - Read the text file from S3 (created by IndexPdfLambda)
      - Log its size and a preview of the content

    NEXT PHASE:
      - Chunk the text
      - Call Bedrock Titan for embeddings
      - Store vectors in S3 Vectors
    """

    print("[ChunkAndEmbedLambda] Event received:")
    print(json.dumps(event))

    # 1. Parse payload from IndexPdfLambda
    try:
        user_id = event["user_id"]
        paper_id = event["paper_id"]
        text_bucket = event["text_s3_bucket"]
        text_key = event["text_s3_key"]
    except KeyError as e:
        print(f"[ChunkAndEmbedLambda] ERROR: Missing expected key in event: {e}")
        raise

    print(f"[ChunkAndEmbedLambda] user_id={user_id}, paper_id={paper_id}")
    print(f"[ChunkAndEmbedLambda] Reading text from s3://{text_bucket}/{text_key}")

    # 2. Download the extracted text from S3
    obj = s3.get_object(Bucket=text_bucket, Key=text_key)
    text_bytes = obj["Body"].read()
    text = text_bytes.decode("utf-8", errors="replace")

    text_length = len(text)
    preview = text[:500]   # first 500 characters for logging

    print(f"[ChunkAndEmbedLambda] Text length: {text_length} characters")
    print(f"[ChunkAndEmbedLambda] Text preview (first 500 chars):")
    print(preview)

    # 3. Return basic info (for testing via console)
    return {
        "statusCode": 200,
        "message": "Text loaded successfully",
        "user_id": user_id,
        "paper_id": paper_id,
        "text_length": text_length
    }
