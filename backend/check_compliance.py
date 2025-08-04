#!/usr/bin/env python3

import sys
import os
import json
import re

# allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever


def setup_index() -> VectorStoreIndex:
    load_dotenv()
    Settings.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    pgvector_store = PGVectorStore.from_params(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", 5432)),
        database=os.getenv("PG_DB", "postgres"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "ragpass"),
        table_name="law_chunks",
        embed_dim=1536
    )
    return VectorStoreIndex.from_vector_store(pgvector_store)


def extract_json(text: str) -> dict:
    """
    Try to load the text as JSON; if that fails, pull out the first {...} block.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            raise ValueError("No JSON object found in LLM response")
        return json.loads(m.group(0))


def check_compliance(
    index: VectorStoreIndex,
    ingredients: list[str],
    law_category: str,
    law_name: str
) -> dict:
    client_data = "Ingredients: " + ", ".join(ingredients)

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5
    )
    query_engine = RetrieverQueryEngine(retriever=retriever)

    prompt = f"""
You are a U.S. cosmetics regulatory expert. Only consider law excerpts in the category "{law_category}". Review the law chunks and client data below, and return _only_ valid JSON:

--- LAW: {law_name} ---
(Using real excerpts from the database, filtered by category "{law_category}")

--- CLIENT DATA ---
    {client_data}

--- OUTPUT FORMAT (JSON) ---
{{
  "law": "{law_name}",
  "compliant": true or false,
  "issues": ["list specific issues if any"],
  "fixes": ["list concrete fixes if any"],
  "confidence": float between 0 and 1,
  "compliance_score": integer between 0 and 100
}}

DO NOT include any text outside the JSON block.
"""
    print("Prompt sent to LLM: ", prompt)

    nodes = retriever.retrieve(prompt)
    print(f"📊 Retrieved {len(nodes)} law chunks")
    for i, node in enumerate(nodes):
        print(f"📄 Chunk {i+1} preview:\n{node.text[:200]}...\n")

    raw = query_engine.query(prompt)
    # convert to string and pull out JSON
    cleaned = str(raw).strip()
    cleaned = cleaned.replace("```json", "").replace("```","").strip()
    print(f"Raw response cleaned:\n{cleaned[:300]}...\n")

    return extract_json(cleaned)


def main():
    index = setup_index()
    ingredients_list = ["water", "benzene", "fragrance"]
    law_sets = [
        {"category": "prop65",    "name": "California Prop 65"},
        {"category": "cosmetics", "name": "Federal Cosmetics Act"},
        # add more as needed...
    ]

    results = []
    for law in law_sets:
        print(f"\n=== Checking: {law['name']} ===")
        try:
            res = check_compliance(
                index=index,
                ingredients=ingredients_list,
                law_category=law["category"],
                law_name=law["name"]
            )
            print(json.dumps(res, indent=2))
            results.append(res)
        except Exception as e:
            print(f"Error parsing response for {law['name']}: {e}")

    if results:
        avg = sum(r.get("compliance_score", 0) for r in results) / len(results)
        print(f"\nOverall average compliance score: {avg:.1f}/100")


if __name__ == "__main__":
    main()