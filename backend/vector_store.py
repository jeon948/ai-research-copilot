from langchain_text_splitters import RecursiveCharacterTextSplitter

stored_chunks = []


def create_vector_store(text):
    global stored_chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )

    stored_chunks = splitter.split_text(text)

    return len(stored_chunks)


def search_documents(query, k=8):
    global stored_chunks

    if not stored_chunks:
        return []

    query_words = set(query.lower().split())
    scored_chunks = []

    for chunk in stored_chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower)

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda item: item[0])

    class SimpleDocument:
        def __init__(self, page_content):
            self.page_content = page_content

    if scored_chunks:
        return [
            SimpleDocument(chunk)
            for _, chunk in scored_chunks[:k]
        ]

    return [
        SimpleDocument(chunk)
        for chunk in stored_chunks[:k]
    ]