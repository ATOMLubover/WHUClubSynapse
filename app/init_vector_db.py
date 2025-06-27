import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.config import settings
from transformers import AutoModel

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
embedding_model = AutoModel.from_pretrained(settings.EMBEDDING_MODEL_DIR)

def init_vector_db(pdf_dir: str, collection_name: str):
    vector_db = Chroma(
        embedding_function=embedding_model,
        persist_directory=settings.VECTOR_DB_PATH,
        collection_name=collection_name
    )
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            loader = PyMuPDFLoader(file_path)
            chunks = loader.load_and_split(text_splitter=text_splitter)
            vector_db.add_documents(chunks)
    vector_db.persist()

if __name__ == "__main__":
    init_vector_db(settings.STATIC_DOC_PATH, settings.VECTRO_DB_COLLECTION)