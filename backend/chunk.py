# backend/chunk.py

def chunk_text(text, chunk_size=300, overlap=50):
    """
    Splits text into chunks of `chunk_size` words with `overlap` between them.
    Returns a list of text chunks.
    """
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += chunk_size - overlap  # move forward with overlap

    return chunks


if __name__ == "__main__":
    # Demo usage
    sample_text = (
        "This is a long test string. " * 50 +
        "We want to see how it's chunked. " * 30
    )
    result = chunk_text(sample_text, chunk_size=40, overlap=10)
    for i, chunk in enumerate(result):
        print(f"\n--- Chunk {i+1} ---\n{chunk}")
