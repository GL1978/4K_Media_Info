import os
import sqlite3
import faiss
import json
import numpy as np
from transformers import BertTokenizer, BertModel

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
cache_dir = 'D:/MakeMKV/media_info'


def extract_data_from_sqlite(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT full_json FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    return data


def convert_to_embeddings(texts):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', cache_dir=cache_dir)
    model = BertModel.from_pretrained('bert-base-uncased', cache_dir=cache_dir)

    embeddings = []
    for text in texts:
        if isinstance(text, str):
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
            embeddings.append(embedding)
        else:
            print(f"Skipping non-string input: {text}")

    return embeddings


def create_faiss_index(embeddings):
    dimension = embeddings[0].shape[1]  # Assuming all embeddings have the same dimensionality
    index = faiss.IndexFlatL2(dimension)

    embeddings_np = np.vstack(embeddings)
    index.add(embeddings_np)

    return index


def save_faiss_index(index, index_file):
    faiss.write_index(index, index_file)


def load_faiss_index(index_file):
    return faiss.read_index(index_file)


def retrieve_texts(indices, texts):
    return [texts[idx] for idx in indices]


def search_faiss_index(faiss_index, query_embedding, texts, k=5):
    # Perform semantic search
    D, I = faiss_index.search(query_embedding.reshape(1, -1).astype(np.float32), k)

    # Retrieve corresponding texts
    retrieved_texts = [texts[i] for i in I[0]]

    return retrieved_texts, D[0]


if __name__ == '__main__':
    db_path = 'D:/MakeMKV/media_info/media_info.db'
    table_name = 'media_info'
    index_file = 'D:/MakeMKV/media_info/media_info_faiss_index.bin'

    # Step 1: Extract data from SQLite database
    json_data = extract_data_from_sqlite(db_path, table_name)

    # Extract texts from JSON data
    texts = [json.loads(row[0]) for row in json_data]

    # Ensure all texts are strings
    texts = [json.dumps(text) if not isinstance(text, str) else text for text in texts]

    if not os.path.exists(index_file):
        # Step 2: Convert texts to embeddings
        embeddings = convert_to_embeddings(texts)

        # Step 3: Create FAISS index and save it
        faiss_index = create_faiss_index(embeddings)
        save_faiss_index(faiss_index, index_file)

        print("FAISS index created and saved.")
    else:
        # Load existing FAISS index
        faiss_index = load_faiss_index(index_file)
        print("FAISS index loaded.")

    # Example query
    query_text = "99528040927093357896556819182693091232"
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', cache_dir=cache_dir)
    model = BertModel.from_pretrained('bert-base-uncased', cache_dir=cache_dir)

    inputs = tokenizer(query_text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    query_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()

    retrieved_texts, distances = search_faiss_index(faiss_index, query_embedding, texts)

    # Display results
    for idx, (text, distance) in enumerate(zip(retrieved_texts, distances), 1):
        print(f"Result {idx}:")
        print(f"Text: {text}")
        print(f"Distance: {distance}")
        print()
