import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.config import settings
from sentence_transformers import SentenceTransformer

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

def init_vector_db(pdf_dir: str, collection_name: str):
    vector_db = Chroma(
        persist_directory=settings.VECTOR_DB_PATH,
        collection_name=collection_name
    )
    # 初始化SentenceTransformer
    st_model = SentenceTransformer(settings.EMBEDDING_MODEL_DIR)

    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            loader = PyMuPDFLoader(file_path)
            chunks = loader.load_and_split(text_splitter=text_splitter)

            # 提取文本并生成向量
            texts = [doc.page_content for doc in chunks]
            embeddings = st_model.encode(texts, normalize_embeddings=True)

            # 添加文档和预计算向量
            vector_db.add_documents(
                documents=chunks,
                embeddings=embeddings
            )

    vector_db.persist()

if __name__ == "__main__":
    init_vector_db(settings.STATIC_DOC_PATH, settings.VECTRO_DB_COLLECTION)