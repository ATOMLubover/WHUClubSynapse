import unittest

import numpy as np
import torch

from app.rag_service import get_embeddings


class TestGetEmbeddings(unittest.TestCase):

    def test_get_embeddings_normal(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device,
                                   mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!", "This is a test."]
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array(mock_embeddings))

    def test_get_embeddings_empty_texts(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device,
                                        mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = []
        mock_embeddings = torch.tensor([])

        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array(mock_embeddings))

    def test_get_embeddings_single_text(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device,
                                        mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!"]
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3]])

        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())

    def test_get_embeddings_large_texts(self, mock_compute_embeddings, mock_get_model_outputs, mock_move_to_device,
                                        mock_tokenize_inputs):
        # Mock inputs and outputs
        texts = ["Hello, world!"] * 1000
        mock_embeddings = torch.tensor([[0.1, 0.2, 0.3]] * 1000)

        mock_compute_embeddings.return_value = mock_embeddings

        # Call the function
        result = get_embeddings(texts)

        # Assertions
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_array_equal(result, mock_embeddings.cpu().numpy())


if __name__ == '__main__':
    unittest.main()
