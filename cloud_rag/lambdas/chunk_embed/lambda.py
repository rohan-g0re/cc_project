import boto3
import json
import os

s3 = boto3.client("s3")

VECTOR_BUCKET = os.environ.get("VECTOR_BUCKET")
VECTOR_INDEX = os.environ.get("VECTOR_INDEX")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")


def chunk_text(text: str, max_chars: int = 1000):
    """
    Split text into chunks of ~max_chars characters, without breaking words.

    Strategy:
      - Split text into words.
      - Greedily pack words into the current chunk until adding the next word
        would exceed max_chars.
      - Start a new chunk when needed.
    """
    words = text.split()
    chunks = []
    current_words = []
    current_len = 0

    for word in words:
        # +1 for the space if there are already words in the chunk
        extra_len = len(word) if current_len == 0 else len(word) + 1

        if current_len + extra_len > max_chars and current_words:
            # close current chunk
            chunks.append(" ".join(current_words))
            # start new chunk
            current_words = [word]
            current_len = len(word)
        else:
            # add word to current chunk
            if current_len == 0:
                current_words.append(word)
                current_len = len(word)
            else:
                current_words.append(word)
                current_len += len(word) + 1  # +1 space

    # flush last chunk
    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def lambda_handler(event, context):
    """
    CURRENT BEHAVIOUR:
      - Read the text file from S3 (created by IndexPdfLambda)
      - Chunk it into ~1000-character segments
      - Log chunk statistics and previews

    NEXT PHASE:
      - For each chunk, call Bedrock Titan embeddings
      - Store vectors (with source_text) in S3 Vectors
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
    print(f"[ChunkAndEmbedLambda] Full text length: {text_length} characters")

    # 3. Chunk the text
    chunks = chunk_text(text, max_chars=1000)
    num_chunks = len(chunks)
    print(f"[ChunkAndEmbedLambda] Number of chunks: {num_chunks}")

    if num_chunks > 0:
        first_chunk = chunks[0]
        last_chunk = chunks[-1]
        print(f"[ChunkAndEmbedLambda] First chunk length: {len(first_chunk)}")
        print(f"[ChunkAndEmbedLambda] First chunk preview (first 300 chars):")
        print(first_chunk[:300])

        if num_chunks > 1:
            print(f"[ChunkAndEmbedLambda] Last chunk length: {len(last_chunk)}")
            print(f"[ChunkAndEmbedLambda] Last chunk preview (first 300 chars):")
            print(last_chunk[:300])

    # 4. Return basic info for testing
    return {
        "statusCode": 200,
        "message": "Text loaded and chunked successfully",
        "user_id": user_id,
        "paper_id": paper_id,
        "text_length": text_length,
        "num_chunks": num_chunks,
        "chunk_size_target": 1000
    }