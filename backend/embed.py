import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
from backend.config import get_connection
from backend.extract import extract_text_from_pdf
from backend.chunk import chunk_text


# 1. Load API Key
load_dotenv
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 


# 2. Define function to embed text chunks
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 3. Create DB table to store embeddings
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding VECTOR(1536)
            );
        """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Table 'chunks' created or already exists.")


# 4. Embed and store all chunks
def embed_and_store(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)

    conn = get_connection()
    cur = conn.cursor()

    for chunk in chunks:
        embedding = get_embedding(chunk)
        cur.execute(
            "INSERT INTO chunks (content, embedding) VALUES (%s, %s);",
            (chunk, embedding)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Stored {len(chunks)} chunks in the database.")

if __name__ == "__main__":
    create_table()
    embed_and_store("data/sample.pdf")