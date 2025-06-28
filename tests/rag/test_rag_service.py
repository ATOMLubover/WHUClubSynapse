from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch

from app.rag_service import (
    retrieve,
    format_context,
    generate_response,
    rag_pipeline
)


# ---- Fixtures ----
@pytest.fixture
def mock_tokenizer():
    tokenizer = MagicMock()
    tokenizer.return_value = {"input_ids": torch.tensor([[1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1]])}
    return tokenizer


@pytest.fixture
def mock_model():
    model = MagicMock()
    mock_output = MagicMock()
    mock_output.last_hidden_state = torch.rand(1, 3, 768)  # [batch_size, seq_len, hidden_size]
    model.return_value = mock_output
    return model


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.query.return_value = {
        "documents": [["doc1 content", "doc2 content"]],
        "metadatas": [[{"source": "test1"}, {"source": "test2"}]]
    }
    return collection


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.invoke.return_value = "Mocked LLM response"
    return llm


"""
# def test_tokenize_inputs(mock_tokenizer):
#     with patch('app.rag_service.tokenizer', mock_tokenizer):
#         inputs = ["test text"]
#         result = tokenize_inputs(inputs)
#         assert "input_ids" in result
#         assert "attention_mask" in result
#         mock_tokenizer.assert_called_with(inputs, return_tensors='pt', padding=True, truncation=True)

# def test_get_embeddings_cpu(mock_model, mock_tokenizer):
#     with patch.multiple('app.rag_service',
#                        model=mock_model,
#                        tokenizer=mock_tokenizer):
#         texts = ["test text"]
#         embeddings = get_embeddings(texts)
#         assert isinstance(embeddings, np.ndarray)
#         assert embeddings.shape == (1, 768)  # [batch_size, hidden_size]
# 
# @patch('torch.cuda.is_available', return_value=True)
# def test_get_embeddings_gpu(mock_cuda, mock_model, mock_tokenizer):
#     with patch.multiple('app.rag_service',
#                        model=mock_model,
#                        tokenizer=mock_tokenizer):
#         texts = ["test text"]
#         get_embeddings(texts)
#         mock_model.to.assert_called_with(torch.device('cuda'))
# 
# def test_get_embeddings_empty_input():
#     with pytest.raises(ValueError):
#         get_embeddings([])
"""


# ---- Test Cases ----
def test_retrieve(mock_collection):
    with patch('app.rag_service.collection', mock_collection), \
            patch('app.rag_service.get_embeddings', return_value=np.random.rand(768)):
        results = retrieve("test query", 2)
        assert len(results) == 2
        assert "content" in results[0]
        assert "metadata" in results[0]
        mock_collection.query.assert_called_once()


def test_retrieve_empty_results(mock_collection):
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
    with patch('app.rag_service.collection', mock_collection):
        results = retrieve("test query")
        assert results == []


def test_format_context():
    test_docs = [
        {"content": "doc1", "metadata": {"source": "s1"}},
        {"content": "doc2", "metadata": {"source": "s2"}}
    ]
    context = format_context(test_docs)
    assert "doc1" in context
    assert "doc2" in context
    assert "文档 1" in context
    assert "文档 2" in context


def test_format_context_empty_input():
    assert format_context([]) == ""


def test_generate_response(mock_llm):
    with patch('app.rag_service.ChatPromptTemplate') as mock_prompt, \
            patch('app.rag_service.StrOutputParser') as mock_parser:
        # Setup mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "test response"

        # Simulate correct chain construction: llm | parser
        mock_llm.__or__.return_value = mock_chain

        # Setup prompt template
        mock_template = MagicMock()
        mock_prompt.from_template.return_value = mock_template
        mock_template.format.return_value = "formatted_prompt"

        response = generate_response("test query", "test context", mock_llm)

        assert response == "test response"
        mock_prompt.from_template.assert_called_once()
        mock_template.format.assert_called_once_with(
            context="test context",
            question="test query"
        )
        mock_chain.invoke.assert_called_once_with("formatted_prompt")


def test_rag_pipeline(mock_collection, mock_llm):
    with patch('app.rag_service.collection', mock_collection), \
            patch('app.rag_service.get_embeddings', return_value=np.random.rand(768)):
        result = rag_pipeline("test query", mock_llm)
        assert "answer" in result
        assert "source_documents" in result
        assert "context" in result
        assert len(result["source_documents"]) == 2


def test_rag_pipeline_empty_retrieval(mock_collection, mock_llm):
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
    with patch('app.rag_service.collection', mock_collection):
        result = rag_pipeline("test query", mock_llm)
        assert result["answer"]  # Should still get response even with no docs
        assert len(result["source_documents"]) == 0
