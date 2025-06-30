import json
import os
from typing import Dict, Any

class ConfigManager:
    """配置管理器，用于加载和管理JSON配置文件"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证必要的配置项
            self._validate_config(config)
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """验证配置文件的必要字段"""
        required_sections = ['server', 'vllm', 'request', 'logging', 'security']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"配置文件缺少必要的配置节: {section}")
        
        # 验证服务器配置
        if 'host' not in config['server'] or 'port' not in config['server']:
            raise ValueError("服务器配置缺少host或port")
        
        # 验证vLLM配置
        if 'api_url' not in config['vllm'] or 'default_model' not in config['vllm']:
            raise ValueError("vLLM配置缺少api_url或default_model")
    
    def get(self, key: str, default=None):
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self):
        """重新加载配置文件"""
        self.config = self._load_config()
    
    @property
    def server_host(self) -> str:
        return self.get('server.host', '0.0.0.0')
    
    @property
    def server_port(self) -> int:
        return self.get('server.port', 8080)
    
    @property
    def vllm_api_url(self) -> str:
        return self.get('vllm.api_url', 'http://localhost:8000/v1/chat/completions')
    
    @property
    def default_model(self) -> str:
        return self.get('vllm.default_model', 'Qwen/Qwen3-8B-AWQ')
    
    @property
    def default_max_tokens(self) -> int:
        return self.get('request.default_max_tokens', 30000)
    
    @property
    def default_temperature(self) -> float:
        return self.get('request.default_temperature', 0.7)
    
    @property
    def default_top_p(self) -> float:
        return self.get('request.default_top_p', 0.8)
    
    @property
    def request_timeout(self) -> int:
        return self.get('request.timeout', 120)
    
    @property
    def log_level(self) -> str:
        return self.get('logging.level', 'INFO')
    
    @property
    def log_format(self) -> str:
        return self.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    @property
    def enable_cors(self) -> bool:
        return self.get('security.enable_cors', True)
    
    @property
    def allowed_origins(self) -> list:
        return self.get('security.allowed_origins', ['*'])
    
    @property
    def rate_limit_enabled(self) -> bool:
        return self.get('rate_limit.enabled', False)
    
    @property
    def rate_limit_requests(self) -> int:
        return self.get('rate_limit.requests_per_minute', 100)
    
    @property
    def rate_limit_window(self) -> int:
        return self.get('rate_limit.window_seconds', 60)

    @property
    def financial_data_file(self) -> str:
        return self.get('financial_assistant.data_file', 'financial_data.json')

# 创建全局配置实例
config = ConfigManager() 