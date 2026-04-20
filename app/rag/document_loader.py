import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader

DOCS_PATH = "data/documents"


def load_documents():
    documents = []

    for file in os.listdir(DOCS_PATH):
        path = os.path.join(DOCS_PATH, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

        elif file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
            documents.extend(loader.load())

    return documents