import json
import numpy as np
from tqdm import tqdm
from weaviate import Client
from sentence_transformers import SentenceTransformer

# Parametreler
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TEST_FILE = "test.json"
TOP_K = 5
DEBUG = True  # 🔧 Debug çıktısı almak için True yap

# Model ve Weaviate istemcisi
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
client = Client("http://localhost:8181")


def retrieve(query, top_k=TOP_K):
    query_vector = embedding_model.encode(query, normalize_embeddings=True).tolist()
    response = (
        client.query.get("Document", ["content", "source"])
        .with_near_vector({"vector": query_vector})
        .with_limit(top_k)
        .do()
    )
    return response.get("data", {}).get("Get", {}).get("Document", [])


def compute_metrics(ranks, k=5):
    mrr = np.mean([1.0 / (r + 1) if r != -1 else 0 for r in ranks])
    hits = {f"Hit@{i}": np.mean([r != -1 and r < i for r in ranks]) for i in [1, 3, 5]}
    return mrr, hits


def evaluate(test_file):
    ranks = []
    with open(test_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    for sample in tqdm(test_data, desc="Evaluating queries"):
        query = sample["query"]
        relevant_passages = [r.strip() for r in sample["relevant_passages"]]

        results = retrieve(query, top_k=TOP_K)

        # 🔍 DEBUG: Sorgu ve dönen sonuçları yazdır
        if DEBUG:
            print(f"\n=====================")
            print(f"🔍 QUERY: {query}")
            print(f"🎯 RELEVANT PASSAGES:")
            for p in relevant_passages:
                print(f"    - {p}")
            print(f"📄 TOP-{TOP_K} RESULTS:")
            for idx, doc in enumerate(results):
                snippet = doc["content"].strip().replace("\n", " ")[:200]
                print(f"  [{idx}] {snippet}\n")

        # Eşleşme var mı kontrol et
        rank = -1
        for idx, doc in enumerate(results):
            content = doc["content"].strip()
            for rel in relevant_passages:
                if rel in content:
                    rank = idx
                    if DEBUG:
                        print(f"✅ MATCH FOUND at Rank {idx + 1}")
                    break
            if rank != -1:
                break

        if rank == -1 and DEBUG:
            print("❌ NO MATCH FOUND")

        ranks.append(rank)

    mrr, hits = compute_metrics(ranks, TOP_K)

    print("\nFINAL EVALUATION METRICS")
    print(f"MRR: {mrr:.4f}")
    for k, v in hits.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    evaluate(TEST_FILE)
