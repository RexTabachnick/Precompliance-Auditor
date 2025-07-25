from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
client = OpenAI(
    organization="org-1JHpjwLgFDXERtl0rSNTwS1l"
)
model = SentenceTransformer("all-MiniLM-L6-v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/demo-compliance")
def get_compliance():

    law_chunks = [
    "Products containing parabens must disclose this on the label clearly.",
    "Ingredient lists must use INCI names and be ordered by concentration.",
    "Cosmetic products must not claim therapeutic or medical benefits.",
    "Fragrance allergens like linalool must be declared if over threshold amounts."
    ]

    client_chunks = [
        "Our new face cream contains water, glycerin, parabens, and lavender extract.",
        "Label: Heals acne fast and reduces inflammation.",
        "Ingredients: Aqua, Glycerin, Parabens, Lavandula Oil.",
        "No mention of fragrance allergens."
    ]

    law_embeddings = model.encode(law_chunks)
    client_embeddings = model.encode(client_chunks)

    d  = law_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(law_embeddings))
    
    results = []

    for i, c_chunk in enumerate(client_chunks):
        c_vector = np.array([client_embeddings[i]])
        D, I = index.search(c_vector, k=1)
        matched_law = law_chunks[I[0][0]]

        prompt = (
            "You are a cosmetics compliance expert.\n\n"
            "Given a piece of client documentation and a related regulation, determine whether the client is in compliance. "
            "Explain your reasoning in simple language.\n\n"
            f"Client Text:\n{c_chunk}\n\n"
            f"Regulation:\n{matched_law}\n\n"
            "Answer in this format:\n"
            "- Verdict: [Compliant / Non-Compliant]\n"
            "- Reason: [One-sentence explanation]\n"
            "- Recommendation: [Optional advice]"
        )

        response = client.chat.completions.create(
            model = "gpt-4.1",
            messages = [
                {"role": "system", "content": "You are a cosmetics compliance expert."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.3,
            max_tokens = 200
        )

        results.append({
            "client_chunk": c_chunk,
            "matched_law": matched_law,
            "verdict": response.choices[0].message.content.strip()
        })

    return {"results": results}