import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.core.readers import SimpleDirectoryReader  # correct import

load_dotenv()
Settings.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from llama_index.embeddings.openai import OpenAIEmbedding
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",  # or "text-embedding-ada-002"
    api_key=os.getenv("OPENAI_API_KEY")
)

# Use explicit connection URI (bypass env var issues)
pgvector_store = PGVectorStore.from_params(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="ragpass",
    table_name="law_chunks",
    embed_dim=1536
)

index = VectorStoreIndex.from_vector_store(pgvector_store)

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

def check_compliance(query: str, law_category: str, law_name: str) -> str:
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,
        filters={"category": law_category}  # filter by law!
    )

    query_engine = RetrieverQueryEngine(retriever=retriever)

    # Structured prompt template
    full_prompt = f"""
You are a U.S. cosmetics regulatory expert. Review the law chunks and client data below, and return your response in structured JSON format.

--- LAW: {law_name} ---
(You are using real excerpts from the law database)

--- CLIENT DATA ---
    {query}

--- REQUIRED OUTPUT FORMAT (JSON) ---
    {{
  "law": "{law_name}",
  "compliant": true or false,
  "issues": ["list specific issues if any"],
  "fixes": ["list concrete fixes if any"],
  "confidence": float between 0 and 1
    }}
"""

    response = query_engine.query(full_prompt)
    return str(response)


# following is an example of a function we could run to check compliance of 1 specific law/regulation
# repeat for each one --> then find aggregate score for dashboard

if __name__ == "__main__":
    client_input = "Ingredients: water, benzene, fragrance"
    print(check_compliance(
        client_input,
        law_category="prop65",
        law_name="California Prop 65"
    ))