import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is initialized in app/main.py

client = TestClient(app)

def test_smart_search():
    # Define a sample search query
    search_query = {
        "query": "如何创建一个社团？"
    }
    
    headers = {
        "X-API-Key": "super_plus_api_key"
    }

    # Send a POST request to the /smart-search endpoint
    response = client.post("/smart-search", json=search_query, headers=headers)

    # Assert the response status code is 200
    assert response.status_code == 200

    # Assert the response contains the expected keys
    response_data = response.json()
    assert "answer" in response_data
    assert "source" in response_data

    # Optionally, assert the content of the response
    assert isinstance(response_data["answer"], str)
    assert isinstance(response_data["source"], list)

    # Print the response for manual verification
    print(response_data)