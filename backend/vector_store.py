from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = None


def create_vector_store(text):
    global vector_db

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    vector_db = FAISS.from_texts(
        texts=chunks,
        embedding=embedding_model
    )

    return len(chunks)


def search_documents(query):
    global vector_db

    if vector_db is None:
        return []

    docs = vector_db.similarity_search(
        query,
        k=3
    )

    return docs