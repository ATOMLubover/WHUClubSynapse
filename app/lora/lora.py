import pandas as pd
import swanlab
import torch
from datasets import Dataset
from swanlab.integration.transformers import SwanLabCallback
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq

"""
预处理输入数据
"""
def preprocess(sample):
    MAX_LENGTH = 1024  # 最大序列长度
    input_ids, attention_mask, labels = [], [], []  # 返回值，分别是输入文本编码、注意力掩码、输出文本编码
    # 1. 构建指令
    instruction = tokenizer(
        f"<s><|im_start|>system\n现在你要作为一个全能的社团管理系统AI助手，扮演各种角色<im_end>\n"
        f"<|im_start|>user\n{sample['instruction'] + sample['input']}<|im_end|>\n"
        f"<|im_start|>assistant\n<think>\n\n</think>\n\n",
        add_special_tokens=False
    )
    # 2. 编码并拼接为输入序列
    response = tokenizer(f"{sample['output']}", add_special_tokens=False)
    # 拼接 instruction 和 response 的 input_ids, 并在末尾添加 eos token 作为标记结束的 token
    input_ids = instruction['input_ids'] + response['input_ids'] + [tokenizer.pad_token_id]
    # 注意力掩码，表示模型需要关注的部分
    attention_mask = instruction['attention_mask'] + response['attention_mask'] + [1]
    # 3. 构造标签用于计算损失, 对于 instruction，使用 -100 表示这些位置无需计算 loss (无需预测)
    labels = [-100] * len(instruction['input_ids']) + response['input_ids'] + [tokenizer.pad_token_id]

    if len(input_ids) > MAX_LENGTH:  # 超出最大长度截断
        input_ids = input_ids[:MAX_LENGTH]
        attention_mask = attention_mask[:MAX_LENGTH]
        labels = labels[:MAX_LENGTH]

    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'labels': labels
    }    

if __name__ == "__main__":
    # 加载模型和分词器
    model = AutoModelForCausalLM.from_pretrained('/root/autodl-tmp/Qwen/Qwen3-8B-AWQ', device_map='cuda')
    model.enable_input_require_grads()  # 开启梯度检查点时，要执行该方法
    tokenizer = AutoTokenizer.from_pretrained('/root/autodl-tmp/Qwen/Qwen3-8B-AWQ')
    tokenizer.pad_token = tokenizer.eos_token
    # 加载和处理数据
    csv_file_path = './app/data/lora_dataset.csv'
    df = pd.read_csv(csv_file_path)
    ds = Dataset.from_pandas(df)
    tokenized_id = ds.map(preprocess)
    # 配置 LORA
    config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,  # 模型类型，CAUSAL_LM 表示因果语言模型
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],  # 需要训练的模型层的名字
        inference_mode=False,
        r=8,  # LoRA 的秩，决定了低秩矩阵的维度
        lora_alpha=32,  # 缩放参数，与 r 一起 决定了 LoRA 更新的强度。实际缩放比例为 lora_alpha / r = 4 倍
        lora_dropout=0.2,  # 用于 LoRA 层的 Dropout 比例
    )
    # 应用 PEFT，将 LoRA 配置应用到原始模型
    model = get_peft_model(model, config)
    model.print_trainable_parameters()  # 打印总训练参数
    # 配置训练参数
    args = TrainingArguments(
        output_dir="/root/autodl-tmp/Qwen/Qwen3-8B-AWQ-LoRA",
        per_device_train_batch_size=4,  # 每张卡上的 batch_size
        gradient_accumulation_steps=4,  # 梯度累积
        logging_steps=10,
        num_train_epochs=3,  # epoch
        save_steps=100,
        learning_rate=1e-4,
        save_on_each_node=True,
        gradient_checkpointing=True,
    )
    # 设置回调，记录指标到 SwanLab
    swanlab_callback = SwanLabCallback(
        project="Qwen3-8B-AWQ-Lora",
        experiment_name="Qwen3-8B-AWQ-LoRA-experiment",
    )
    # 初始化训练器
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_id,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
        callbacks=[swanlab_callback],
    )
    # 开始训练
    trainer.train()