import os
import random

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader

from app.configs.config import settings
from app.rag.rag_service import get_embeddings
from app.utils.singleton import chroma_collection
from app.utils.singleton import logger

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", "，", "、", " "],
    length_function=len
)

def init_vector_db(pdf_dir: str):
    """
    从PDF目录初始化向量数据库，通过HTTP客户端连接。
    """
    logger.info(f"Starting to process PDF files from directory: {pdf_dir}")
    # 定义批处理大小，避免一次性向量化上万个条目，提高稳健性
    batch_size = 64

    for filename in os.listdir(pdf_dir):
        if not filename.endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_dir, filename)
        logger.info(f"Processing file: {file_path}")

        try:
            # 准备 pdf loader 和 文本块
            loader = PyMuPDFLoader(file_path)
            chunks = loader.load_and_split(text_splitter=text_splitter)

            if not chunks:
                logger.warning(f"No text chunks extracted from {filename}. Skipping.")
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
                logger.info(f"Generating embeddings for batch {i // batch_size + 1} of file {filename}...")
                batch_embeddings = get_embeddings(batch_texts)

                # d. 通过HTTP客户端批量上传数据
                chroma_collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )
                logger.info(f"Successfully upserted batch of {len(batch_chunks)} chunks for {filename}.")

        except Exception as e:
            logger.error(f"Failed to process file {filename}. Error: {e}", exc_info=True)

    logger.info("Finished processing all PDF files.")


def check_collection_data(collection):
    """
    检查集合中是否有数据。
    """
    # 查询集合中的所有数据
    results = collection.query(
        query_embeddings=[random.random() for _ in range(len(get_embeddings([""])[0]))],
        n_results=10  # 返回前10条数据
    )
    # 输出文档
    if results and results.get("documents"):
        logger.info(f"Collection contains {len(results['documents'])} documents.")
        for i, doc in enumerate(results["documents"]):
            logger.info(f"Document {i + 1}: {doc}")
    else:
        logger.warning("No documents found in the collection.")


if __name__ == "__main__":
    init_vector_db(settings.STATIC_DOC_PATH)
    # check_collection_data(chroma_collection)  # 测试向量数据库初始化是否正常的函数，生产环境请注释
