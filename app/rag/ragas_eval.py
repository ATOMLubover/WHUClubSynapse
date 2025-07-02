import os
import sys
import asyncio
import json
import httpx
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_openai import ChatOpenAI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.configs.config import settings

# 1. 定义评估用的 LLM
# RAGAS 评估需要一个 LLM 来判断 Faithfulness, Answer Relevancy 等。
# 引入先进的 deepseek-v3
llm = ChatOpenAI(
    openai_api_base=settings.DEEPSEEK_API_URL,
    openai_api_key=settings.DEEPSEEK_API_KEY,
    model_name=settings.DEEPSEEK_MODEL,
    temperature=0.6,
    max_tokens=4096,
    top_p=0.9,
    stop=["<|eot_id|>", "<|end_of_text|>", "<|im_end|>"],
)

# 2. 定义一组测试问题
# 这些问题应该与您的社团管理系统文档相关
questions = [
    "如何成为社团的认证成员？",
    "社团管理员有什么权限？",
    "如何查看社团的最新活动？",
    "忘记密码了怎么办？",
    "如何创建新的社团？",
    "如何申请创建新的社团？",
    "社团成员如何进行年度注册？",
    "社团活动如何申请场地？",
    "如何查看我的社团的财务状况？",
    "社团如何发布招新公告？",
    "普通成员可以发起活动吗？",
    "社团的认证流程是怎样的？",
    "如何修改社团的基本信息？",
    "社团的年审需要提交哪些材料？",
    "如何加入一个已经存在的社团？",
]

# 3. 准备评估数据集
async def generate_evaluation_data():
    data = {
        "question": [],
        "contexts": [],
        "answer": [],
        "ground_truth": [] # 在这个场景下，我们将检索到的文档作为 ground_truth
    }
    
    headers = {
        "X-API-Key": "super_plus_api_key" 
    }

    for question in questions:
        print(f"正在处理问题: {question}")
        search_query = {"query": question}
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", f"http://127.0.0.1:{settings.FASTAPI_PORT}/smart-search", json=search_query, headers=headers, timeout=120) as response:
                    if response.status_code != 200:
                        print(f"请求失败，状态码: {response.status_code}")
                        # 如果请求失败，我们仍然添加一个空的数据点以保持数据集的完整性
                        data["question"].append(question)
                        data["contexts"].append([])
                        data["answer"].append("")
                        data["ground_truth"].append("")
                        continue

                    source_received = False
                    answer_tokens = []
                    contexts = []
                    ground_truth_str = ""

                    async for line in response.aiter_lines():
                        if line.startswith("event: "):
                            event_type = line[len("event: "):]
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[len("data: "):]
                            if event_type == "source":
                                source_data = json.loads(data_str)
                                contexts = [doc['content'] for doc in source_data]
                                ground_truth_docs = [f"内容: {doc['content']}" for doc in source_data]
                                ground_truth_str = "\n\n".join(ground_truth_docs)
                                source_received = True
                            
                            elif event_type == "token":
                                token_data = json.loads(data_str)
                                answer_tokens.append(token_data.get("token", ""))

                            elif event_type == "end":
                                break
                
                full_answer = "".join(answer_tokens)
                
                data["question"].append(question)
                data["contexts"].append(contexts)
                data["answer"].append(full_answer)
                data["ground_truth"].append(ground_truth_str)

        except httpx.RequestError as e:
            print(f"请求 '{question}' 时发生错误: {e}")
            # 发生请求错误时，也添加空数据点
            data["question"].append(question)
            data["contexts"].append([])
            data["answer"].append("")
            data["ground_truth"].append("")

    return data

async def main():
    print("正在生成评估数据集...")
    eval_data = await generate_evaluation_data()
    dataset = Dataset.from_dict(eval_data)

    print("数据集生成完毕，开始使用 RAGAS 进行评估...")
    # 4. 运行 RAGAS 评估
    result = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,
        raise_exceptions=False # 避免因单个评估点失败而中断
    )

    print("评估完成！")
    print(result)

    # 5. 将结果保存到文件
    df = result.to_pandas()
    df.to_csv("ragas_evaluation_results.csv", index=False)
    print("评估结果已保存到 ragas_evaluation_results.csv")

if __name__ == "__main__":
    # 在 uvicorn 等异步环境中，可能需要不同的方式运行
    # 这里我们使用 asyncio.run()
    # 如果您在 Jupyter Notebook 中运行，直接 await main() 即可
    asyncio.run(main())
