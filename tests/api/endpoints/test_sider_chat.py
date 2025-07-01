import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_sider_chat_streaming():
    """
    Tests the sider-chat endpoint with a follow-up question,
    ensuring it correctly handles streaming responses.
    """
    # Define a sample chat query with history
    chat_query = {
        "query": "审核一般需要多久？",
        "history": [
            {
                "role": "user",
                "content": "如何创建一个新的社团？"
            },
            {
                "role": "assistant",
                "content": "要创建一个新的社团，您需要先提交一份包含社团基本信息的申请表..."
            }
        ]
    }

    headers = {
        "X-API-Key": "super_plus_api_key"
    }

    # Send a POST request to the /sider-chat endpoint
    response = client.post("/sider-chat", json=chat_query, headers=headers)

    # Assert the response status code is 200
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Process the event stream
    source_received = False
    answer_tokens = []
    end_received = False
    event_type = None

    for line in response.iter_lines():
        if line.startswith("event: "):
            event_type = line[len("event: "):]
            continue

        if line.startswith("data: "):
            data_str = line[len("data: "):]
            if not data_str:
                continue

            if event_type == "source":
                source_data = json.loads(data_str)
                assert isinstance(source_data, list)
                source_received = True

            elif event_type == "token":
                token_data = json.loads(data_str)
                assert "token" in token_data
                answer_tokens.append(token_data["token"])

            elif event_type == "end":
                end_received = True
                break

    # Final assertions after processing the stream
    assert source_received, "Source event was not received"
    assert end_received, "End event was not received"
    assert len(answer_tokens) > 0, "No tokens were received"

    full_answer = "".join(answer_tokens)
    assert isinstance(full_answer, str)
    assert len(full_answer) > 0

    # Print the reconstructed answer for manual verification
    print("\n--- Reconstructed Answer ---")
    print(full_answer)
    print("\n--- Source Documents ---")
    print(source_data)