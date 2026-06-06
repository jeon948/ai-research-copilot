from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from pdf_loader import extract_text_from_pdf
from rag import (
    ask_groq,
    ask_document,
    summarize_document,
    compare_documents,
    generate_flashcards,
    generate_quiz,
    generate_notes,
    generate_important_questions,
    generate_revision_sheet,
)

from vector_store import create_vector_store
from multi_pdf_store import (
    store_pdf_text,
    get_document_names,
    delete_document,
)

app = FastAPI(
    title="AI Research Copilot API",
    description="Backend API for AI Study Assistant / AI Research Copilot",
    version="1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "AI Research Copilot backend is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = extract_text_from_pdf(file_path)

        if not extracted_text or len(extracted_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from this PDF",
            )

        store_pdf_text(safe_filename, extracted_text)
        chunks_count = create_vector_store(extracted_text)

        return {
            "success": True,
            "filename": safe_filename,
            "message": "PDF uploaded successfully",
            "chunks_created": chunks_count,
            "uploaded_documents": get_document_names(),
            "text_preview": extracted_text[:500],
        }

    except HTTPException:
        raise

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}",
        )


@app.get("/ask")
def ask(question: str):
    try:
        answer = ask_groq(question)
        return {
            "success": True,
            "question": question,
            "answer": answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask-document")
def ask_pdf(question: str):
    try:
        answer = ask_document(question)
        return {
            "success": True,
            "question": question,
            "answer": answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary")
def summary():
    try:
        result = summarize_document()
        return {
            "success": True,
            "summary": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flashcards")
def flashcards():
    try:
        result = generate_flashcards()
        return {
            "success": True,
            "flashcards": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quiz")
def quiz():
    try:
        result = generate_quiz()
        return {
            "success": True,
            "quiz": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes")
def notes():
    try:
        result = generate_notes()
        return {
            "success": True,
            "notes": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/important-questions")
def important_questions():
    try:
        result = generate_important_questions()
        return {
            "success": True,
            "important_questions": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/revision-sheet")
def revision_sheet():
    try:
        result = generate_revision_sheet()
        return {
            "success": True,
            "revision_sheet": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare")
def compare():
    try:
        result = compare_documents()
        return {
            "success": True,
            "comparison": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def documents():
    try:
        return {
            "success": True,
            "uploaded_documents": get_document_names(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-document/{filename}")
def remove_document(filename: str):
    try:
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        delete_document(safe_filename)

        return {
            "success": True,
            "message": f"{safe_filename} deleted successfully",
            "uploaded_documents": get_document_names(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )