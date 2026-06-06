uploaded_documents = {}


def store_pdf_text(filename, text):
    uploaded_documents[filename] = text


def get_all_documents():
    return uploaded_documents


def get_document_names():
    return list(uploaded_documents.keys())


def delete_document(filename):
    if filename in uploaded_documents:
        del uploaded_documents[filename]
        return True

    return False


def clear_all_documents():
    uploaded_documents.clear()
    return True