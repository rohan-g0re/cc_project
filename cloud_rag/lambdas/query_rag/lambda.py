import json
import boto3
import os

bedrock = boto3.client("bedrock-runtime")
s3v = boto3.client("s3vectors")

VECTOR_BUCKET = os.environ["VECTOR_BUCKET"]
VECTOR_INDEX = os.environ["VECTOR_INDEX"]
BEDROCK_MODEL_ID = "amazon.titan-embed-text-v2:0"
TOP_K = 5


def embed_text(text):
    body = {
        "inputText": text,
        "dimensions": 256,
        "normalize": True
    }

    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    out = json.loads(resp["body"].read())
    return out.get("embedding") or out.get("vector") or out.get("embeddings")


def lambda_handler(event, context):
    question = event["question"]
    user_id = event["user_id"]
    paper_ids = event.get("paper_ids", None)

    # 1. Embed question
    q_emb = embed_text(question)

    # 2. Build filter
    filter_obj = {"user_id": {"equals": user_id}}
    if paper_ids:
        filter_obj["paper_id"] = {"in": paper_ids}

    # 3. Query Vectors
    resp = s3v.query_vectors(
        vectorBucketName=VECTOR_BUCKET,
        indexName=VECTOR_INDEX,
        queryVector={"float32": q_emb},
        topK=TOP_K,
        # filter=filter_obj, --> we are not using this for now as we are not filtering by paper_ids, just metadata -- i guess so
        returnMetadata=True,
        returnDistance=True
    )

    hits = resp.get("vectors", [])
    out_chunks = []
    rank = 1
    for v in hits:
        md = v.get("metadata", {})
        text = md.get("source_text", "")
        dist = v.get("distance", 0)
        sim = 1 - dist
        out_chunks.append({
            "rank": rank,
            "similarity": sim,
            "text": text
        })
        rank += 1

    return {"top_k_chunks": out_chunks}