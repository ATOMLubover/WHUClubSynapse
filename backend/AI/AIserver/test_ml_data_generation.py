import requests
import json
import pandas as pd
import os

# 服务器地址和端口（请根据您的实际配置修改）
# 确保 vllm_proxy_server.py 正在运行
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
API_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/generate_ml_data"

def call_generate_ml_data(num_communities: int = 5, num_users: int = 5, num_interactions: int = 8):
    """
    调用 /generate_ml_data 接口并打印响应。
    """
    payload = {
        "num_communities": num_communities,
        "num_users": num_users,
        "num_interactions": num_interactions
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"正在向 {API_URL} 发送请求，请求体: {payload}")

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=None)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()
        print("\n--- 接收到的原始 JSON 响应 ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 将 JSON 数据转换为 Pandas DataFrame 并保存为 CSV
        output_dir = "generated_ml_data"
        os.makedirs(output_dir, exist_ok=True)

        if "communities" in data:
            communities_df = pd.DataFrame(data["communities"])
            communities_file = os.path.join(output_dir, "communities.csv")
            communities_df.to_csv(communities_file, index=False, encoding='utf-8')
            print(f"\n社团数据已保存到: {communities_file}")
            print("部分社团数据预览:\n", communities_df.head())

        if "users" in data:
            users_df = pd.DataFrame(data["users"])
            users_file = os.path.join(output_dir, "users.csv")
            users_df.to_csv(users_file, index=False, encoding='utf-8')
            print(f"\n用户数据已保存到: {users_file}")
            print("部分用户数据预览:\n", users_df.head())

        if "interactions" in data:
            interactions_df = pd.DataFrame(data["interactions"])
            interactions_file = os.path.join(output_dir, "interactions.csv")
            interactions_df.to_csv(interactions_file, index=False, encoding='utf-8')
            print(f"\n互动数据已保存到: {interactions_file}")
            print("部分互动数据预览:\n", interactions_df.head())

    except requests.exceptions.ConnectionError as e:
        print(f"错误: 无法连接到服务器。请确保 vllm_proxy_server.py 正在运行，并且地址 {SERVER_HOST}:{SERVER_PORT} 正确。详细错误: {e}")
    except requests.exceptions.Timeout:
        print("错误: 请求超时。服务器可能响应缓慢或网络问题。")
    except requests.exceptions.HTTPError as e:
        print(f"错误: HTTP 请求失败，状态码: {e.response.status_code}, 响应: {e.response.text}")
    except json.JSONDecodeError as e:
        print(f"错误: 服务器返回的响应不是有效的 JSON。详细错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    # 您可以根据需要修改要生成的数据量
    call_generate_ml_data(num_communities=50, num_users=480, num_interactions=2000) 