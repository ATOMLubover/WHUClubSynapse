import requests
data = {
    "messages": [{"role": "user", "content": "你好，能给我讲个故事吗？"}]
}
r = requests.post("http://localhost:8000/chat", json=data)
print(r.json())
