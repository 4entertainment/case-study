from sentence_transformers import SentenceTransformer
from weaviate import Client

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
client = Client("http://localhost:8181")


def retrieve(query, top_k=5):
    query_vector = embedding_model.encode(query, normalize_embeddings=True).tolist()
    result = (
        client.query.get("Document", ["content", "source"])
        .with_near_vector({"vector": query_vector})
        .with_limit(top_k)
        .do()
    )
    return result["data"]["Get"]["Document"]


if __name__ == "__main__":
    while True:
        print("Arama yapmak için bir sorgu girin (çıkmak için 'exit' yazın):")
        user_input = input()
        if user_input.lower() == "exit":
            break

        results = retrieve(user_input)
        if results:
            for i, doc in enumerate(results, 1):
                print(
                    f"\n--- [{i}] Kaynak: {doc['source']} ---\n{doc['content'][:1000]}"
                )
        else:
            print(
                "🔍 Arama kriterlerinize uygun sonuç bulunamadı. Farklı anahtar kelimeler deneyin."
            )
