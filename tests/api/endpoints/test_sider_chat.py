import pytest
from fastapi.testclient import TestClient
from app.main import app

# 使用 TestClient 初始化，它允许我们向 FastAPI 应用发送模拟请求
client = TestClient(app)


def test_chat_initial_message():
    """
    测试场景 1: 首次发起对话，历史记录为空。
    """
    print("\n--- Running Test: Initial Chat Message ---")

    # 模拟用户第一次提问，此时 history 列表为空
    chat_request_body = {
        "query": "如何创建一个社团？",
        "history": []
    }

    response = client.post("/chat", json=chat_request_body)

    assert response.status_code == 200

    response_data = response.json()

    # a. 检查核心键是否存在
    assert "answer" in response_data
    assert "source" in response_data

    # b. 检查值的类型是否正确
    assert isinstance(response_data["answer"], str)
    assert isinstance(response_data["source"], list)

    # c. 检查内容是否非空
    assert response_data["answer"] != ""
    # RAG 检索可能会返回空列表，但这本身是有效的结果，所以我们只检查类型

    # 打印响应内容，便于手动验证 (运行时需加 -s 参数)
    print("Response for initial message:")
    print(response_data)


def test_chat_follow_up_message():
    """
    测试场景 2: 进行跟进提问，提供历史对话记录。
    """
    print("\n--- Running Test: Follow-up Chat Message ---")

    # 模拟用户在得到第一次回答后，提出一个相关的跟进问题
    chat_request_body = {
        "query": "那需要多少人才能发起呢？",
        "history": [
            {
                "role": "user",
                "content": "如何创建一个社团？"
            },
            {
                "role": "assistant",
                "content": "创建社团需要明确目标、组建团队、提交申请并完成审批流程..."
            }
        ]
    }

    response = client.post("/api/v1/chat", json=chat_request_body)

    assert response.status_code == 200

    response_data = response.json()

    # a. 检查核心键是否存在
    assert "answer" in response_data
    assert "source" in response_data

    # b. 检查值的类型是否正确
    assert isinstance(response_data["answer"], str)
    assert isinstance(response_data["source"], list)

    # c. 检查回答是否非空
    assert response_data["answer"] != ""

    print("Response for follow-up message:")
    print(response_data)