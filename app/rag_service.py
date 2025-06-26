from transformers import AutoModel, AutoTokenizer
import torch
from app.config import settings
import chromadb
from functools import reduce
from typing import List

# 加载模型和分词器
model_dir = settings.EMBEDDING_MODEL_DIR
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModel.from_pretrained(model_dir)

'''
从输入获取嵌入向量
'''
def tokenize_inputs(texts: List[str]):
    return tokenizer(texts, return_tensors='pt', padding=True, truncation=True)

def move_to_device(inputs, device):
        return {key: value.to(device) for key, value in inputs.items()}

def get_model_outputs(inputs):
    with torch.no_grad():
        return model(**inputs)

def compute_embeddings(outputs: torch.tensor) -> torch.tensor:  # [batch_size, hidden_size]
    return outputs.last_hidden_state.mean(dim=1)

def get_embeddings(texts: List[str]):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # 定义流水线步骤
    pipeline = [
        lambda x: tokenize_inputs(x),
        lambda x: move_to_device(x, device),
        lambda x: get_model_outputs(x),
        lambda x: compute_embeddings(x)
    ]
    # 使用流水线。参数的含义分别是：累计值，每个步骤如何处理累计值，处理步骤列表，初始值
    embeddings = reduce(lambda acc, f: f(acc), pipeline, texts)

    return embeddings.cpu().numpy() if isinstance(embeddings, torch.Tensor) else np.array(embeddings)


