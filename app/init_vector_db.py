import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.config import settings
from app.rag_service import get_embeddings
import chromadb
import logging

# 日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - [MessageID: %(msg_id)s] - %(message)s'
)

log = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

client = chromadb.HttpClient(
    host=settings.CHROMA_SERVER_HOST,
    port=settings.CHROMA_SERVER_PORT
)
collection = client.get_or_create_collection(name=settings.CHROMA_RAG_COLLECTION_NAME)

def init_vector_db(pdf_dir: str, collection_name: str):
    """
    从PDF目录初始化向量数据库，通过HTTP客户端连接。
    """
    log.info(f"Starting to process PDF files from directory: {pdf_dir}")
    # 定义批处理大小，避免一次性向量化上万个条目，提高稳健性
    batch_size = 100

    for filename in os.listdir(pdf_dir):
        if not filename.endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_dir, filename)
        log.info(f"Processing file: {file_path}")

        try:
            # 准备 pdf loader 和 文本块
            loader = PyMuPDFLoader(file_path)
            chunks = loader.load_and_split(text_splitter=text_splitter)

            if not chunks:
                log.warning(f"No text chunks extracted from {filename}. Skipping.")
                continue

            # --- 3. 批量处理和上传 ---
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]

                # a. 准备 upsert 所需的四项数据
                batch_texts = [doc.page_content for doc in batch_chunks]
                batch_metadatas = [doc.metadata for doc in batch_chunks]

                # b. 为每个块生成一个唯一的、确定性的ID
                batch_ids = [f"static::{filename}_chunk_{i + j}" for j in range(len(batch_chunks))]

                # c. 批量生成向量
                log.info(f"Generating embeddings for batch {i // batch_size + 1} of file {filename}...")
                batch_embeddings = get_embeddings(batch_texts)

                # d. 核心步骤：通过HTTP客户端批量上传数据
                collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )
                log.info(f"Successfully upserted batch of {len(batch_chunks)} chunks for {filename}.")

        except Exception as e:
            log.error(f"Failed to process file {filename}. Error: {e}", exc_info=True)

    log.info("Finished processing all PDF files.")

if __name__ == "__main__":
    init_vector_db(settings.STATIC_DOC_PATH, settings.CHROMA_RAG_COLLECTION_NAME)