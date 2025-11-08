<<<<<<< HEAD
# AI-Powered Regulatory Compliance Assistant

**Developed by:** Sahit Reddy, Rex Tabachnick, and Avi Raj  
**Tech Stack:** FastAPI • PostgreSQL + pgvector • LlamaIndex • OpenAI GPT-4o • Streamlit • Docker  

---

## Overview
**goosePool** is an AI-driven compliance intelligence system designed to automatically evaluate product data against complex legal frameworks such as FDA cosmetic regulations, Prop 65, and MoCRA.  

The platform enables regulatory, R&D, and product teams to quickly assess whether product formulations, ingredient lists, and claims meet regional compliance standards — turning what used to take hours of manual legal cross-checking into an automated, explainable workflow.

---

## Core Architecture

### **Backend (FastAPI + PostgreSQL + pgvector)**
- Ingests product specification files and regulatory PDFs.  
- Extracts, chunks, and embeds text data using OpenAI embeddings.  
- Stores vectors efficiently in PostgreSQL using the  extension.  
- Runs retrieval-augmented generation (RAG) queries through LlamaIndex to locate relevant legal sections.  
- Synthesizes AI-generated compliance summaries citing the original legal text.

### **Frontend (Streamlit Interface)**
- Allows users to upload documents and view structured compliance reports.  
- Displays relevant legal text, highlights potential issues, and summarizes findings.

### **Data Layer (law_docs + summary folders)**
- Contains raw legal documents and AI-generated summaries linked for context.  
- Provides a modular ingestion pipeline via  for maintaining law datasets.

---

## My Role (Rex Tabachnick)
I co-developed the **backend retrieval system** and **data ingestion pipeline**, focusing on:

- Implementing the FastAPI backend for structured RAG queries.  
- Designing the pgvector-based embedding database schema.  
- Writing the document extraction and embedding script ().  
- Creating the linkage between regulatory PDFs and summary text files.  
- Troubleshooting and optimizing database connections, Docker configs, and vector search logic.

---

## Example Flow
1. User uploads a product data file.  
2. System parses product attributes and matches ingredients/claims to relevant laws.  
3. LlamaIndex retrieves and ranks relevant text passages.  
4. GPT-4o generates a concise compliance report citing the exact legal sources.  
5. Results are displayed interactively in the Streamlit UI.

---

## Project Context
Built as part of the **OpenAI x UW–Madison SAIL Program**, this project demonstrates practical RAG deployment for real-world compliance automation.  
Our focus was scalability, transparency, and the ability to integrate with enterprise CRMs or R&D systems via API.

---

## Repository Structure (Demo Version)
=======
# Precompliance-Auditor
This project loads California cosmetic law/regulation data into a RAG vector database, then semantically retrieves it based on an interactive localhosted frontend UI to grade cosmetic brand ingredients and marketing based on compliance.
>>>>>>> d07cc3d72f35f8077dce347b0a2f00549b8cfff6
