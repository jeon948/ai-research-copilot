from dotenv import load_dotenv
from langchain_groq import ChatGroq

from vector_store import search_documents
from multi_pdf_store import get_all_documents

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)


def ask_groq(question):
    try:
        response = llm.invoke(question)
        return response.content
    except Exception as e:
        return f"Groq API Error: {str(e)}"


def get_context(query):
    docs = search_documents(query)

    if not docs:
        return None

    return "\n\n".join([doc.page_content for doc in docs])


def chatgpt_style_prompt(task, context, user_question=None):
    question_part = f"\nUser Question:\n{user_question}\n" if user_question else ""

    return f"""
You are a helpful AI Study and Research Copilot, similar to ChatGPT.

Your job:
- Understand the uploaded PDF.
- Answer clearly and naturally.
- Explain like a friendly tutor.
- Use headings, bullet points, and simple language.
- Give direct answers first.
- Then explain details.
- If the user asks for study help, make it student-friendly.
- If the PDF is a resume, answer like a career mentor.
- If the PDF is a research paper, answer like a research assistant.
- If the exact answer is not found, say: "I could not find this exact information in the uploaded PDF."
- After saying that, you may give a helpful explanation based on related content from the PDF.
- Do not hallucinate fake page numbers, fake units, or fake facts.

Task:
{task}

Document Context:
{context}
{question_part}

Answer style:
- Start with a direct answer.
- Use clear headings.
- Use bullet points when useful.
- Explain concepts in simple words.
- Make the answer useful and complete.
"""


def ask_document(question):
    try:
        context = get_context(question)

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="Answer the user's question based on the uploaded PDF.",
            context=context,
            user_question=question
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Document QA Error: {str(e)}"


def summarize_document():
    try:
        context = get_context("summary overview main topics key concepts important points")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Create a high-quality summary of the uploaded PDF.

Format:
1. Quick Overview
2. Main Topics
3. Key Concepts
4. Important Points
5. Why This Document Matters
6. Final Takeaway
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Summary Error: {str(e)}"


def generate_flashcards():
    try:
        context = get_context("important definitions key terms concepts facts explanations")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Generate 15 useful flashcards from the uploaded PDF.

Format exactly:

Flashcard 1
Q: ...
A: ...

Rules:
- Make questions exam-friendly.
- Keep answers clear and short.
- Use only the uploaded PDF content.
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Flashcard Error: {str(e)}"


def generate_quiz():
    try:
        context = get_context("important concepts exam questions quiz practice answers")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Create a student-friendly quiz from the uploaded PDF.

Include:
1. 10 Multiple Choice Questions
2. 5 Short Answer Questions
3. Answer Key
4. Simple Explanations

Format neatly.
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Quiz Error: {str(e)}"


def generate_notes():
    try:
        context = get_context("study notes concepts definitions explanations examples important details")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Convert the uploaded PDF into clean ChatGPT-style study notes.

Format:
1. Topic Overview
2. Important Concepts
3. Definitions
4. Detailed Explanation
5. Examples / Applications
6. Quick Revision Points

Make it easy to study before exams.
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Notes Error: {str(e)}"


def generate_important_questions():
    try:
        context = get_context("important questions exam questions definitions concepts answers")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Generate important exam questions from the uploaded PDF.

Include:
1. 2-Mark Questions
2. 5-Mark Questions
3. 10-Mark Questions
4. Most Expected Questions
5. Short Answer Hints

Make it useful for students.
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Important Questions Error: {str(e)}"


def generate_revision_sheet():
    try:
        context = get_context("revision important points definitions formulas concepts summary")

        if not context:
            return "No document uploaded yet. Please upload a PDF first."

        prompt = chatgpt_style_prompt(
            task="""
Create a one-page style revision sheet from the uploaded PDF.

Format:
1. Quick Overview
2. Must-Know Concepts
3. Important Terms
4. Key Definitions
5. Formulas / Processes if available
6. Common Exam Points
7. Last-Minute Revision Notes

Keep it concise but useful.
""",
            context=context
        )

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Revision Sheet Error: {str(e)}"


def compare_documents():
    try:
        documents = get_all_documents()

        if len(documents) < 2:
            return "Please upload at least two PDFs to compare."

        context = ""

        for filename, text in documents.items():
            context += f"\n\n--- Document: {filename} ---\n{text[:7000]}"

        prompt = f"""
You are a helpful AI Research Copilot, similar to ChatGPT.

Compare the uploaded documents clearly and professionally.

Documents:
{context}

Format:
1. Overview of Each Document
2. Similarities
3. Differences
4. Strengths of Each Document
5. Limitations of Each Document
6. Final Comparison Summary

Use simple, clear language.
"""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Comparison Error: {str(e)}"