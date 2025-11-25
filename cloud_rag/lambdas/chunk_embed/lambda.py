import boto3
import json
import os

s3 = boto3.client("s3")

VECTOR_BUCKET = os.environ.get("VECTOR_BUCKET")
VECTOR_INDEX = os.environ.get("VECTOR_INDEX")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")

# Bedrock runtime client for embeddings
bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def chunk_text(text: str, max_chars: int = 1000):
    """
    Split text into chunks of ~max_chars characters, without breaking words.
    """
    words = text.split()
    chunks = []
    current_words = []
    current_len = 0

    for word in words:
        extra_len = len(word) if current_len == 0 else len(word) + 1

        if current_len + extra_len > max_chars and current_words:
            chunks.append(" ".join(current_words))
            current_words = [word]
            current_len = len(word)
        else:
            if current_len == 0:
                current_words.append(word)
                current_len = len(word)
            else:
                current_words.append(word)
                current_len += len(word) + 1

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def embed_text(text: str, dims: int = 256) -> list[float]:
    """
    Call Amazon Titan Embeddings (v2) on a single text chunk and return the vector.
    """
    body = {
        "inputText": text,
        "dimensions": dims,
        "normalize": True
    }

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    payload = json.loads(response["body"].read())
    embedding = payload.get("embedding") or payload.get("embeddings") or payload.get("vector")
    # exact key name may differ slightly by SDK version; adjust if needed

    if embedding is None:
        raise RuntimeError(f"Unexpected embedding response format: {payload}")

    return embedding


def lambda_handler(event, context):
    """
    Behaviour now:
      - Read text file from S3
      - Chunk into ~1000-char segments
      - For each chunk, call Titan embeddings
      - Log embedding sizes (no S3 Vectors yet)
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

    if num_chunks == 0:
        print("[ChunkAndEmbedLambda] WARNING: No chunks produced; nothing to embed.")
        return {
            "statusCode": 200,
            "message": "No text to embed",
            "user_id": user_id,
            "paper_id": paper_id,
            "text_length": text_length,
            "num_chunks": 0
        }

    # 4. Embed each chunk with Titan
    embeddings = []
    for idx, chunk in enumerate(chunks):
        print(f"[ChunkAndEmbedLambda] Embedding chunk {idx+1}/{num_chunks} (length={len(chunk)})")
        embedding = embed_text(chunk)
        emb_len = len(embedding)
        print(f"[ChunkAndEmbedLambda] Got embedding of length {emb_len} for chunk {idx+1}")
        embeddings.append(embedding)

    # (Next task: use `embeddings` + `chunks` to write into S3 Vectors)

    # 5. Return basic info for testing
    return {
        "statusCode": 200,
        "message": "Text loaded, chunked, and embedded successfully",
        "user_id": user_id,
        "paper_id": paper_id,
        "text_length": text_length,
        "num_chunks": num_chunks,
        "embedding_dim": len(embeddings[0]) if embeddings else 0
    }