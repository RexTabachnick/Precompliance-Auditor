#!/usr/bin/env python3
"""
Simple compliance checker that works directly with the database,
bypassing LlamaIndex vector store issues.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import re
from typing import List, Dict, Tuple

# allow imports from project root  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
import psycopg2
from openai import OpenAI

# ───────────────────────────  SETUP  ────────────────────────────

def get_db_connection():
    """Get database connection."""
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT", 5432)),
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        sslmode="require"
    )

def get_openai_client():
    """Get OpenAI client."""
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(client: OpenAI, query: str) -> List[float]:
    """Create embedding for query."""
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    return resp.data[0].embedding

def cosine_similarity_sql(embedding: List[float]) -> str:
    """Generate SQL for cosine similarity."""
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return f"1 - (embedding <=> '{embedding_str}')"

# ────────────────────────  DIRECT RETRIEVAL  ─────────────────────

def retrieve_relevant_chunks(
    conn, 
    client: OpenAI, 
    query: str, 
    category: str = None, 
    limit: int = 10
) -> List[Tuple]:
    """
    Retrieve relevant chunks using direct database query with cosine similarity.
    """
    print(f"    Query: '{query}' (category: {category})")
    
    try:
        # Create query embedding
        query_embedding = embed_query(client, query)
        
        # Build SQL query
        similarity_expr = cosine_similarity_sql(query_embedding)
        
        base_query = f"""
            SELECT 
                text,
                metadata,
                document_id,
                {similarity_expr} as similarity
            FROM law_chunks 
            WHERE embedding IS NOT NULL
        """
        
        params = []
        
        # Add category filter if specified
        if category:
            base_query += " AND metadata->>'category' = %s"
            params.append(category)
        
        # Add similarity threshold and ordering
        base_query += f"""
            AND {similarity_expr} > 0.3
            ORDER BY similarity DESC
            LIMIT %s
        """
        params.append(limit)
        
        with conn.cursor() as cur:
            cur.execute(base_query, params)
            results = cur.fetchall()
            
            print(f"    Found {len(results)} chunks")
            
            # Show top result if any
            if results:
                top_result = results[0]
                text_preview = top_result[0][:100].replace('\n', ' ')
                similarity = top_result[3]
                print(f"    Best match (similarity: {similarity:.3f}): {text_preview}...")
            
            return results
            
    except Exception as e:
        print(f"    Retrieval failed: {e}")
        return []

def extract_json_from_response(text: str) -> Dict:
    """Extract JSON from LLM response."""
    if not text:
        raise ValueError("No response text to parse.")
    
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON block
        print("❌ JSON parsing failed.")
        print("Offending response:\n", text)
        raise  # So you catch it in dev

        # match = re.search(r'\{.*\}', text, re.DOTALL)
        # if match:
        #     try:
        #         return json.loads(match.group(0))
        #     except json.JSONDecodeError:
        #         pass
        
        # # Return default structure
        # return {
        #     "law": "Unknown",
        #     "compliant": True,
        #     "issues": [],
        #     "fixes": [],
        #     "confidence": 0.0,
        #     "compliance_score": 50
        # }

#Hallucinating Fix
def is_likely_ingredient_issue(text: str) -> bool:
    ingredient_keywords = ["ingredient", "listed in", "concentration", "formulation", "chemical", "compound"]
    chemical_pattern = r"\b([A-Z][a-z]?[a-z]?\s?[A-Za-z0-9()\-,]*)\b"

    return any(kw in text.lower() for kw in ingredient_keywords) or re.search(chemical_pattern, text)

# ────────────────────────  COMPLIANCE CHECK  ─────────────────────

def check_single_law_direct(
    conn,
    client: OpenAI,
    ingredients: List[str],
    claims: List[str],
    law_category: str,
    law_name: str,
) -> Dict:
    """
    Check compliance against a single law using direct database queries.
    """
    print(f"\n Checking {law_name} (category: {law_category})")
    
    claim_queries = []
    if claims:
        claims_text = "; ".join(claims)
        claim_queries = [
            f"{law_category} claims: {claims_text}",
            f"{law_category} marketing language: {claims_text}",
            f"{law_category} prohibitied claims",
        ]

    # Create targeted queries
    if not ingredients:
        queries = [
            f"{law_category} prohibited claims",
            f"{law_category} false advertising",
            f"{law_category} labeling violations",
            *claim_queries
        ]
    else:
        queries = [
            f"{law_category} " + " ".join(ingredients),
            f"{law_category} prohibited substances",
            f"{law_category} banned ingredients",
            # Test specific dangerous ingredients
            *[f"{law_category} {ingredient}" for ingredient in ingredients 
            if ingredient.lower() in ['benzene', 'formaldehyde', 'lead', 'mercury', 'arsenic', 'toluene']],
            *claim_queries
        ]
    
    # Collect all relevant chunks
    all_chunks = []
    seen_doc_ids = set()
    
    for query in queries[:4]:  # Limit queries to avoid rate limits
        chunks = retrieve_relevant_chunks(conn, client, query, law_category, limit=5)
        
        for chunk_data in chunks:
            doc_id = chunk_data[2]  # document_id
            if doc_id not in seen_doc_ids:
                all_chunks.append(chunk_data)
                seen_doc_ids.add(doc_id)
                
                if len(all_chunks) >= 8:  # Limit total chunks
                    break
        
        if len(all_chunks) >= 8:
            break
    
    print(f"    Total unique chunks: {len(all_chunks)}")
    
    if not all_chunks:
        print(f"     No relevant chunks found for {law_name}")
        return {
            "law": law_name,
            "compliant": True,
            "issues": [],
            "fixes": [],
            "confidence": 0.1,
            "compliance_score": 50,
            "note": "No relevant regulatory content found"
        }
    
    # Build context from chunks
    context_parts = []
    for i, (text, metadata, doc_id, similarity) in enumerate(all_chunks):
        context_parts.append(f"--- REGULATORY EXCERPT {i+1} (similarity: {similarity:.3f}) ---\n{text}\n")
    
    context = "\n".join(context_parts)
    ingredient_list = ", ".join(ingredients)
    claims_text = "; ".join(claims)

    if not ingredients:
        prompt = f"""You are a regulatory compliance expert analyzing **marketing claims** against {law_name}.

    REGULATORY CONTEXT:
    {context}

    CLAIMS TO ANALYZE:
    {claims_text}

    INSTRUCTIONS:
    1. Identify marketing claims that violate {law_name}
    2. Look for misleading language, unsubstantiated effects, or restricted phrasing
    3. Flag any health-related claims that imply physiological changes without FDA approval
    4. Only report actual violations backed by excerpts
    5. Ignore ingredients entirely

    Return ONLY a JSON object:
    {{
    "law": "{law_name}",
    "compliant": true or false,
    "issues": ["specific issue 1", "specific issue 2"],
    "fixes": ["specific fix 1", "specific fix 2"],
    "confidence": 0.0 to 1.0,
    "compliance_score": 0 to 100
    }}

    Be specific and reference actual regulatory requirements when possible.
    """
    
    else:
    # Create prompt for LLM analysis
        prompt = f"""You are a regulatory compliance expert analyzing cosmetic ingredients against {law_name}.

    REGULATORY CONTEXT:
    {context}

    INGREDIENTS TO ANALYZE:
    {ingredient_list}

    INSTRUCTIONS:
    1. Review each ingredient against the regulatory excerpts above
    2. Look for explicit prohibitions, restrictions, concentration limits, or labeling requirements  
    3. Consider chemical synonyms and alternate names
    4. Only flag violations where there's clear regulatory support
    5. If no relevant restrictions are found, assume compliance

    Return ONLY a JSON object:
    {{
    "law": "{law_name}",
    "compliant": true or false,
    "issues": ["specific issue 1", "specific issue 2"],
    "fixes": ["specific fix 1", "specific fix 2"],
    "confidence": 0.0 to 1.0,
    "compliance_score": 0 to 100
    }}

    Be specific and reference actual regulatory requirements when possible.
    """
    
    # Get LLM analysis
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )

        print("\nFull LLM response text:\n", response.choices[0].message.content)
        
        response_text = response.choices[0].message.content
        print(f"    LLM Response: {response_text[:150]}...")
        if not response_text:
            raise ValueError("LLM response content is None")
        
        result = extract_json_from_response(response_text)

        original_issues = result.get("issues", [])

        if not ingredients and original_issues:
            # Only remove ingredient-related hallucinations *if* they actually appear
            filtered_issues = [
                issue for issue in original_issues
                if not is_likely_ingredient_issue(issue)
            ]
            if filtered_issues:
                result["issues"] = filtered_issues
            else:
                # If everything gets filtered out, restore the originals to be safe
                result["issues"] = original_issues
            
            print(f"    Filtered out {len(original_issues) - len(result['issues'])} issues as likely ingredient hallucinations")

            return result
        

        
        if result["issues"]:
            result["compliant"] = False
        else:
            result["compliant"] = True

        return result
        
    except Exception as e:
        print(f"    LLM analysis failed: {e}")
        return {
            "law": law_name,
            "compliant": True,
            "issues": [],
            "fixes": [],
            "confidence": 0.0,
            "compliance_score": 0,
            "error": str(e)
        }

def evaluate_product_direct(ingredients: List[str], claims: List[str] = None) -> Dict:
    """
    Run compliance checks using direct database access.
    """
    print(f" EVALUATING INGREDIENTS: {', '.join(ingredients)}")
    
    try:
        conn = get_db_connection()
        client = get_openai_client()
        print(" Connected to database and OpenAI")
    except Exception as e:
        print(f" Setup failed: {e}")
        return {"non_compliant": [{"law": "System Error", "reason": f"Setup failed: {e}"}]}
    
    # Define law frameworks
    law_frameworks = [
        {"category": "prop65", "name": "California Prop 65"},
        {"category": "mocra", "name": "MoCRA 2022"},
        {"category": "cosmetics", "name": "Federal Cosmetics Act"},
        {"category": "color_additives", "name": "FDA Color Additive Regulations"},
        {"category": "ftc_health", "name": "FTC Health Product Guidelines"},
    ]
    
    non_compliant_results = []
    
    for law in law_frameworks:
        try:
            result = check_single_law_direct(
                conn, client, ingredients, claims or [],
                law["category"], law["name"]
            )
            
            if not result.get("compliant", True):
                issues = result.get("issues", [])
                print(f"  ⚠️ Issues detected for {law['name']}: {issues}")
                reason = "; ".join(issues) if issues else "Regulatory violation detected"
                
                non_compliant_results.append({
                    "law": law["name"],
                    "reason": reason,
                    "confidence": result.get("confidence", 0.0)
                })
                
        except Exception as e:
            print(f" Error checking {law['name']}: {e}")
            non_compliant_results.append({
                "law": law["name"],
                "reason": f"Analysis error: {e}"
            })
    
    conn.close()
    
    # Summary
    print(f"\n COMPLIANCE SUMMARY:")
    print(f"   Non-compliant: {len(non_compliant_results)}")
    print(f"   Compliant: {len(law_frameworks) - len(non_compliant_results)}")
    
    return {"non_compliant": non_compliant_results}

# ───────────────────────────  CLI ENTRY  ─────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 simple_compliance.py '{\"ingredients\": [\"benzene\"]}'", file=sys.stderr)
        sys.exit(1)
    
    arg = sys.argv[1]

    if arg.endswith(".json") and os.path.isfile(arg):
        with open(arg, "r") as f:
            payload = json.load(f)
    
    else:
        try:
            payload = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print("Input must be valid JSON or path to JSON file", file=sys.stderr)
            sys.exit(1)

    if isinstance(payload, dict):
        ingredients = payload.get("ingredients", [])
        claims = payload.get("claims", [])
        
        if not ingredients and not claims:
            print("Must provide at least 'ingredients' or 'claims' for compliance checking.", file=sys.stderr)
            sys.exit(1)
    else:
        print("JSON must be a dictionary with optional 'ingredients' and/or 'claims' keys", file=sys.stderr)
        sys.exit(1)

    result = evaluate_product_direct(ingredients, claims)
    # print(f"\n FINAL RESULT:")
    print(json.dumps(result))

if __name__ == "__main__":
    main()