from openai import OpenAI
api_key="sk-354859a6d3ae438fb8ab9b98194f5266"
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
def tongyi_chat(messages=None,temperature=0.7,max_tokens=1024,presence_penalty=0.0,top_p=1.0):
    try:        
        client = OpenAI(
            api_key="sk-354859a6d3ae438fb8ab9b98194f5266",
            base_url=base_url,
        )
        messages=[
            {"role": "system", "content": "你是一个专业的通知总结专家，请根据通知内容总结，基于通知像人一样总结，更像朋友之间的聊天。"},
            {"role": "user", "content": messages}
        ]
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            top_p=top_p
        )
        for chunk in completion:
            yield{"type": "content", "content": chunk.choices[0].delta.content}
    except Exception as e:
        print(f"错误信息：{e}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")