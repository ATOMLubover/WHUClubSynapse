import unittest
from unittest.mock import patch, MagicMock
import torch
import numpy as np
from app.rag_service import get_embeddings, tokenize_inputs, move_to_device, get_model_outputs, compute_embeddings
from app.config import settings

class TestGetEmbeddings(unittest.TestCase):

    @patch('app.rag_service.tokenize_inputs')
    @patch('app.rag_service.move_to_device')
    @patch('app.rag_service.get_model_outputs')
    @patch('app.rag_service.compute_embeddings')
    def test_get_embeddings_normal(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device, mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!", "This is a test."]
        mock_tokenized_inputs = MagicMock()
        mock_device_inputs = MagicMock()
        mock_model_outputs = MagicMock()
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        mock_tokenize_inputs.return_value = mock_tokenized_inputs
        mock_move_to_device.return_value = mock_device_inputs
        mock_get_model_outputs.return_value = mock_model_outputs
        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        mock_tokenize_inputs.assert_called_once_with(texts)
        mock_move_to_device.assert_called_once_with(mock_tokenized_inputs, torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        mock_get_model_outputs.assert_called_once_with(mock_device_inputs)
        mock_compute_embeddings.assert_called_once_with(mock_model_outputs)
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())

    @patch('app.rag_service.tokenize_inputs')
    @patch('app.rag_service.move_to_device')
    @patch('app.rag_service.get_model_outputs')
    @patch('app.rag_service.compute_embeddings')
    def test_get_embeddings_empty_texts(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device, mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = []
        mock_tokenized_inputs = MagicMock()
        mock_device_inputs = MagicMock()
        mock_model_outputs = MagicMock()
        mock_embeddings = torch.tensor([])

        mock_tokenize_inputs.return_value = mock_tokenized_inputs
        mock_move_to_device.return_value = mock_device_inputs
        mock_get_model_outputs.return_value = mock_model_outputs
        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        mock_tokenize_inputs.assert_called_once_with(texts)
        mock_move_to_device.assert_called_once_with(mock_tokenized_inputs, torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        mock_get_model_outputs.assert_called_once_with(mock_device_inputs)
        mock_compute_embeddings.assert_called_once_with(mock_model_outputs)
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())

    @patch('app.rag_service.tokenize_inputs')
    @patch('app.rag_service.move_to_device')
    @patch('app.rag_service.get_model_outputs')
    @patch('app.rag_service.compute_embeddings')
    def test_get_embeddings_single_text(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device, mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!"]
        mock_tokenized_inputs = MagicMock()
        mock_device_inputs = MagicMock()
        mock_model_outputs = MagicMock()
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3]])

        mock_tokenize_inputs.return_value = mock_tokenized_inputs
        mock_move_to_device.return_value = mock_device_inputs
        mock_get_model_outputs.return_value = mock_model_outputs
        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        mock_tokenize_inputs.assert_called_once_with(texts)
        mock_move_to_device.assert_called_once_with(mock_tokenized_inputs, torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        mock_get_model_outputs.assert_called_once_with(mock_device_inputs)
        mock_compute_embeddings.assert_called_once_with(mock_model_outputs)
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())

    @patch('app.rag_service.tokenize_inputs')
    @patch('app.rag_service.move_to_device')
    @patch('app.rag_service.get_model_outputs')
    @patch('app.rag_service.compute_embeddings')
    def test_get_embeddings_large_texts(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device, mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!"] * 1000
        mock_tokenized_inputs = MagicMock()
        mock_device_inputs = MagicMock()
        mock_model_outputs = MagicMock()
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3]] * 1000)

        mock_tokenize_inputs.return_value = mock_tokenized_inputs
        mock_move_to_device.return_value = mock_device_inputs
        mock_get_model_outputs.return_value = mock_model_outputs
        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        mock_tokenize_inputs.assert_called_once_with(texts)
        mock_move_to_device.assert_called_once_with(mock_tokenized_inputs, torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        mock_get_model_outputs.assert_called_once_with(mock_device_inputs)
        mock_compute_embeddings.assert_called_once_with(mock_model_outputs)
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())

    @patch('app.rag_service.tokenize_inputs')
    @patch('app.rag_service.move_to_device')
    @patch('app.rag_service.get_model_outputs')
    @patch('app.rag_service.compute_embeddings')
    def test_get_embeddings_device_error(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device, mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!"]
        mock_tokenized_inputs = MagicMock()
        mock_device_inputs = MagicMock()
        mock_model_outputs = MagicMock()
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3]])

        mock_tokenize_inputs.return_value = mock_tokenized_inputs
        mock_move_to_device.side_effect = RuntimeError("Device error")
        mock_get_model_outputs.return_value = mock_model_outputs
        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function and assert it raises an error
        with self.assertRaises(RuntimeError):
            get_embeddings(texts)

        # Assertions
        mock_tokenize_inputs.assert_called_once_with(texts)
        mock_move_to_device.assert_called_once_with(mock_tokenized_inputs, torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        mock_get_model_outputs.assert_not_called()
        mock_compute_embeddings.assert_not_called()

if __name__ == '__main__':
    unittest.main()