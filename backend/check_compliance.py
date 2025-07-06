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

def check_compliance(query: str) -> str:
    return str(
        index.as_query_engine(similarity_top_k=3).query(query)
    )

if __name__ == "__main__":
    print(check_compliance("Is lead acetate compliant with Prop 65?"))