import requests
import json
import os
from datetime import datetime
from tqdm import tqdm
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_training_data(
    server_url: str = "http://localhost:8080",
    batch_size: int = 100,
    total_count: int = 1000,
    output_dir: str = "generated_data",
    data_type: str = "general",
):
    """
    生成训练数据并保存到文件
    
    Args:
        server_url: vLLM代理服务器地址
        batch_size: 每批生成的数量
        total_count: 总共需要生成的数量
        output_dir: 输出目录
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"training_data_{timestamp}.jsonl")
        
        # 准备请求
        url = f"{server_url}/generate_training_data"
        payload = {
            "batch_size": batch_size,
            "total_count": total_count,
            "save_file": output_file,
            "data_type": data_type
        }
        
        logger.info(f"开始生成训练数据，目标数量: {total_count}")
        logger.info(f"输出文件: {output_file}")
        
        # 发送请求
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        logger.info(f"生成完成！实际生成数量: {result['generated_count']}")
        logger.info(f"消息: {result['message']}")
        
        # 显示样例数据
        logger.info("\n示例数据:")
        for i, sample in enumerate(result['sample_data'], 1):
            logger.info(f"\n样例 {i}:")
            logger.info(f"Instruction: {sample['instruction']}")
            logger.info(f"Input: {sample['input']}")
            logger.info(f"Output: {sample['output']}")
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"错误详情: {e.response.text}")
    except Exception as e:
        logger.error(f"发生错误: {e}")

def validate_generated_data(file_path: str):
    """
    验证生成的数据文件
    
    Args:
        file_path: JSONL文件路径
    """
    try:
        logger.info(f"开始验证数据文件: {file_path}")
        
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        valid_count = 0
        error_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(tqdm(f, total=total_lines, desc="验证进度")):
                try:
                    data = json.loads(line)
                    # 验证必要字段
                    if not all(key in data for key in ["instruction", "input", "output"]):
                        logger.warning(f"行 {i+1}: 缺少必要字段")
                        error_count += 1
                        continue
                    # 验证字段类型
                    if not all(isinstance(data[key], str) for key in ["instruction", "input", "output"]):
                        logger.warning(f"行 {i+1}: 字段类型错误")
                        error_count += 1
                        continue
                    valid_count += 1
                except json.JSONDecodeError:
                    logger.warning(f"行 {i+1}: JSON解析错误")
                    error_count += 1
        
        logger.info(f"\n验证完成:")
        logger.info(f"总行数: {total_lines}")
        logger.info(f"有效数据: {valid_count}")
        logger.info(f"错误数据: {error_count}")
        logger.info(f"有效率: {(valid_count/total_lines)*100:.2f}%")
        
    except Exception as e:
        logger.error(f"验证过程发生错误: {e}")

def main():
    """
    主函数
    """
    # 配置参数
    server_url = "http://localhost:8080"  # 根据实际情况修改
    batch_size = 20
    total_count = 500
    output_dir = "generated_data"
    
    try:
        # 生成数据
        output_file = generate_training_data(
            server_url=server_url,
            batch_size=batch_size,
            total_count=total_count,
            output_dir=output_dir,
            data_type="faq"
        )
        
        if output_file and os.path.exists(output_file):
            # 验证生成的数据
            validate_generated_data(output_file)
        else:
            logger.error("数据生成失败或文件不存在")
            
    except Exception as e:
        logger.error(f"程序执行出错: {e}")

if __name__ == "__main__":
    main() 