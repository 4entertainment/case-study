"""
import os
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from weaviate import Client
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 512
CHUNK_OVERLAP = 0.1
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
DATA_PATH = "data/"

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
client = Client("http://localhost:8181")


def create_schema():
    class_obj = {
        "class": "Document",
        "vectorizer": "none",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "source", "dataType": ["text"]},
        ],
    }
    client.schema.delete_all()
    client.schema.create_class(class_obj)


def ingest_documents(data_folder):
    for file_name in os.listdir(data_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(data_folder, file_name)
            # elements = partition(filename=file_path, languages=["tur"])
            elements = partition(
                filename=file_path,
                languages=["tur"],
                strategy="fast",  # NLP analizlerini minimal tutar, POS'a girmez
            )
            chunks = chunk_by_title(
                elements, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )

            for chunk in chunks:
                content = chunk.text.strip()
                if not content:
                    continue
                vector = embedding_model.encode(
                    content, normalize_embeddings=True
                ).tolist()
                client.data_object.create(
                    {"content": content, "source": file_name},
                    class_name="Document",
                    vector=vector,
                )


if __name__ == "__main__":
    create_schema()
    ingest_documents(data_folder=DATA_PATH)


"""

import os
import PyPDF2
from weaviate import Client
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 512
CHUNK_OVERLAP = 0.1
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
DATA_PATH = "data/"

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
client = Client("http://localhost:8181")


def create_schema():
    class_obj = {
        "class": "Document",
        "vectorizer": "none",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "source", "dataType": ["text"]},
        ],
    }
    client.schema.delete_all()
    client.schema.create_class(class_obj)


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def chunk_text(text, chunk_size=512, overlap=0.1):
    chunks = []
    step = int(chunk_size * (1 - overlap))
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def ingest_documents(data_folder):
    for file_name in os.listdir(data_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(data_folder, file_name)
            text = extract_text_from_pdf(file_path)
            chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

            for chunk in chunks:
                vector = embedding_model.encode(
                    chunk, normalize_embeddings=True
                ).tolist()
                client.data_object.create(
                    {"content": chunk, "source": file_name},
                    class_name="Document",
                    vector=vector,
                )


if __name__ == "__main__":
    create_schema()
    ingest_documents(data_folder=DATA_PATH)
