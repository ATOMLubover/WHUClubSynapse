# vLLM 代理服务器

这是一个基于FastAPI的代理服务器，用于接收prompt请求并转发给vLLM服务器。

## 功能特性

- 🚀 基于FastAPI的高性能异步服务器
- 🔄 自动转发请求到vLLM服务器
- 📝 支持多种聊天接口（完整接口和简化接口）
- 🏥 健康检查功能
- 📊 模型列表查询
- 🔧 JSON配置文件，易于管理
- 🌐 CORS支持
- 📋 详细的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.json` 文件来自定义服务器设置：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "vllm": {
    "api_url": "http://localhost:8000/v1/chat/completions",
    "default_model": "Qwen/Qwen3-8B-AWQ"
  },
  "request": {
    "default_max_tokens": 30000,
    "default_temperature": 0.7,
    "default_top_p": 0.8,
    "timeout": 120
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "security": {
    "enable_cors": true,
    "allowed_origins": [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "*"
    ]
  },
  "rate_limit": {
    "enabled": false,
    "requests_per_minute": 100,
    "window_seconds": 60
  }
}
```

### 配置说明

- **server**: 服务器配置
  - `host`: 监听地址（0.0.0.0表示监听所有网络接口）
  - `port`: 监听端口

- **vllm**: vLLM服务器配置
  - `api_url`: vLLM服务器地址
  - `default_model`: 默认模型名称

- **request**: 请求配置
  - `default_max_tokens`: 默认最大生成token数
  - `default_temperature`: 默认温度参数
  - `default_top_p`: 默认top_p参数
  - `timeout`: 请求超时时间（秒）

- **logging**: 日志配置
  - `level`: 日志级别（DEBUG, INFO, WARNING, ERROR）
  - `format`: 日志格式

- **security**: 安全配置
  - `enable_cors`: 是否启用CORS
  - `allowed_origins`: 允许的跨域来源

- **rate_limit**: 限流配置
  - `enabled`: 是否启用请求限流
  - `requests_per_minute`: 每分钟最大请求数
  - `window_seconds`: 限流时间窗口（秒）

## 启动服务器

### 方式一：使用启动脚本（推荐）

```bash
python start_server.py
```

### 方式二：直接运行服务器

```bash
python vllm_proxy_server.py
```

服务器启动后，您将看到类似以下的输出：

```
启动vLLM代理服务器...
服务器地址: http://0.0.0.0:8080
vLLM API地址: http://localhost:8000/v1/chat/completions
默认模型: Qwen/Qwen3-8B-AWQ
健康检查: http://0.0.0.0:8080/health
聊天接口: http://0.0.0.0:8080/chat
简化接口: http://0.0.0.0:8080/simple_chat
模型列表: http://0.0.0.0:8080/models
配置信息: http://0.0.0.0:8080/config
```

## vLLM 代理服务器 API 文档

**基础URL**: `http://localhost:8080` (端口可能根据 `config.json` 配置而异)

### 1. 服务器状态

*   **GET** `/`
    *   **描述**: 健康检查接口，返回服务器基本状态。
    *   **响应示例**:
        ```json
        {
          "message": "vLLM代理服务器已启动",
          "status": "running",
          "vllm_api_url": "http://localhost:8000/v1/chat/completions",
          "default_model": "Qwen/Qwen3-8B-AWQ"
        }
        ```

### 2. 健康检查

*   **GET** `/health`
    *   **描述**: 详细的健康检查，包括 vLLM 服务器连接状态。
    *   **响应示例**:
        ```json
        {
          "proxy_server": "running",
          "vllm_server": "connected",
          "vllm_api_url": "http://localhost:8000/v1/chat/completions",
          "server_config": {
            "host": "0.0.0.0",
            "port": 8080,
            "default_model": "Qwen/Qwen3-8B-AWQ"
          }
        }
        ```

### 3. 完整聊天接口

*   **POST** `/chat`
    *   **描述**: 接收聊天请求并转发给 vLLM 服务器。支持多轮对话和各种生成参数。
    *   **请求体 (JSON)**: `ChatRequest`
        *   `messages` (List[Message]): 消息列表，每个消息包含 `role` (str) 和 `content` (str)。
            *   示例: `[{"role": "user", "content": "你好"}]`
        *   `model` (Optional[str], default: `config.default_model`): 要使用的模型名称。
        *   `max_tokens` (Optional[int], default: `config.default_max_tokens`): 生成的最大 token 数量。
        *   `temperature` (Optional[float], default: `config.default_temperature`): 采样温度，用于控制输出的随机性。
        *   `top_p` (Optional[float], default: `config.default_top_p`): top_p 参数。
        *   `stream` (Optional[bool], default: `False`): 是否流式输出。
        *   `system_prompt` (Optional[str], default: `"You are a helpful assistant."`): 系统提示。
    *   **响应体 (JSON)**: `ChatResponse`
        *   `response` (str): 模型生成的回复文本。
        *   `model` (str): 使用的模型名称。
        *   `usage` (Optional[Dict]): Token 使用情况 (如果 vLLM 响应中包含)。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/chat \
          -H "Content-Type: application/json" \
          -d '{
            "messages": [
              {"role": "user", "content": "请用中文回答：什么是人工智能？"}
            ],
            "model": "Qwen/Qwen3-8B-AWQ",
            "max_tokens": 1500,
            "temperature": 0.7
          }'
        ```

### 4. 简化聊天接口

*   **POST** `/simple_chat`
    *   **描述**: 简化的聊天接口，只需要提供 prompt 字符串。
    *   **查询参数**:
        *   `prompt` (str): 用户输入的提示。
        *   `model` (Optional[str], default: `config.default_model`): 模型名称。
        *   `max_tokens` (Optional[int], default: `config.default_max_tokens`): 最大生成 token 数。
    *   **响应体 (JSON)**:
        *   `response` (str): 模型生成的回复文本。
        *   `model` (str): 使用的模型名称。
    *   **`curl` 示例**:
        ```bash
        curl -X POST "http://localhost:8080/simple_chat?prompt=你好，请简单介绍一下自己&model=Qwen/Qwen3-8B-AWQ&max_tokens=1000"
        ```

### 5. 通义千问总结接口

*   **POST** `/summarize_tongyi`
    *   **描述**: 使用嵌入的通义千问模型总结文本。
    *   **请求体 (JSON)**: `TongyiSummaryRequest`
        *   `text` (str): 要总结的文本内容。
        *   `temperature` (Optional[float], default: `0.7`): 采样温度。
        *   `max_tokens` (Optional[int], default: `1024`): 最大生成 token 数。
        *   `presence_penalty` (Optional[float], default: `0.0`): 存在惩罚。
        *   `top_p` (Optional[float], default: `1.0`): top_p 参数。
    *   **响应体 (JSON)**:
        *   `summary` (str): 总结后的文本。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/summarize_tongyi \
          -H "Content-Type: application/json" \
          -d '{
            "text": "您的帖子"寻求转行人工智能的职业建议"收到了 2 条新评论。\n\n用户：@TechSavvySarah 回复道："很棒的话题！您考虑过在线机器学习课程吗？"\n\n用户：@DataDudeDave 回复道："我也有过类似的经历。如果您愿意，我很乐意分享。"\n\n您的帖子"新加坡远程工作最佳咖啡馆"收到了 1 条新评论。\n\n用户：@LatteLoverLily 回复道："您一定要去中峇鲁的'The Daily Grind'看看——氛围超棒！"\n\n社团新帖\n\n【摄影俱乐部】 @ShutterbugSteve 发布了一个新讨论："即将举行的摄影漫步——滨海湾花园（6 月 29 日）"\n\n【烹饪爱好者】 @GourmetGabby 分享了一个新食谱："简单的工作日晚餐：烤蔬菜意面"\n\n【书虫匿名会】 @LiteraryLiz 创建了一个新投票："下一次读书会：科幻还是奇幻？"\n\n社团管理员通知\n\n【游戏公会】 @GuildMasterMax (管理员) 发布了一条新通知："服务器维护计划于 6 月 28 日晚上 10 点（新加坡时间）进行"\n\n【健身狂热者】 @FitFamFred (管理员) 发布了一条新通知："新健身挑战：30 天平板支撑挑战将于 7 月 1 日开始！""
          }'
        ```

### 6. AI内容生成接口

*   **POST** `/generate/content`
    *   **描述**: 根据关键词和内容类型，使用AI生成活动宣传或新闻稿。
    *   **请求体 (JSON)**: `ContentGenerationRequest`
        *   `content` (Optional[str]): 原始文案草稿。
        *   `style` (Optional[str]): 文体风格 (如 "enthusiastic", "formal")。
        *   `expection` (Optional[str]): 预期效果。
    *   **响应体 (JSON)**: `ContentGenerationResponse`
        *   `generated_text` (str): 生成的文本。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/generate/content \
          -H "Content-Type: application/json" \
          -d '{
            "content": "本周五晚7点，A栋101教室，举办Python入门讲座，面向全校师生",
            "style": "enthusiastic",
            "expection": "吸引更多人参与活动，激发读者热情"
          }'
        ```

### 7. AI社团介绍生成接口

*   **POST** `/generate/introduction`
    *   **描述**: 根据关键词和内容类型，使用AI生成社团介绍。
    *   **请求体 (JSON)**: `ContentGenerationRequest`
        *   `content` (Optional[str]): 原始文案草稿。
        *   `style` (Optional[str]): 文体风格 (如 "humorous", "formal")。
        *   `target_people` (Optional[str]): 目标人群 (如 "新生", "对编程感兴趣的同学")。
    *   **响应体 (JSON)**: `ContentGenerationResponse`
        *   `generated_text` (str): 生成的社团介绍文本。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/generate/introduction \
          -H "Content-Type: application/json" \
          -d '{
            "content": "这是一个关于我们社团的草稿：我们是一个热爱编程的社团，经常组织编程比赛和技术分享。",
            "style": "humorous",
            "target_people": "新生，对编程感兴趣的同学"
          }'
        ```

### 8. AI社团口号生成接口

*   **POST** `/generate/Slogan`
    *   **描述**: 根据关键词使用AI生成社团口号。
    *   **请求体 (JSON)**: `SloganGenerationRequest`
        *   `theme` (str): 口号主题。
    *   **响应体 (JSON)**: `ContentGenerationResponse`
        *   `generated_text` (str): 生成的社团口号文本。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/generate/Slogan \
          -H "Content-Type: application/json" \
          -d '{
            "theme": "编程社，创新，活力"
          }'
        ```

### 9. 配置信息

*   **GET** `/config`
    *   **描述**: 获取当前服务器配置（不包含敏感信息）。
    *   **响应示例**:
        ```json
        {
          "server": {
            "host": "0.0.0.0",
            "port": 8080
          },
          "vllm": {
            "api_url": "http://localhost:8000/v1/chat/completions",
            "default_model": "Qwen/Qwen3-8B-AWQ"
          },
          "request": {
            "default_max_tokens": 30000,
            "default_temperature": 0.7,
            "default_top_p": 0.8,
            "timeout": 120
          },
          "logging": {
            "level": "INFO"
          },
          "security": {
            "enable_cors": true
          }
        }
        ```

### 10. 配置重载接口

*   **GET** `/reload_config`
    *   **描述**: 重新加载服务器配置，使`config.json`中的更改生效而无需重启服务器。
    *   **响应示例**:
        ```json
        {
          "message": "配置文件已成功重载",
          "status": "success"
        }
        ```

### 11. 智能申请筛选助手接口

*   **POST** `/screen_application`
    *   **描述**: 智能申请筛选助手，自动分析申请理由和个人资料，生成摘要和建议。
    *   **请求体 (JSON)**:
        *   `applicant_data` (Dict[str, Any]): 申请者个人资料，例如：
            ```json
            {
              "name": "李华",
              "major": "计算机科学与技术",
              "skills": ["Python编程", "数据结构"],
              "experience": "曾参与校内编程竞赛并获得二等奖"
            }
            ```
        *   `application_reason` (str): 申请理由的文本内容。
        *   `required_conditions` (List[str]): 社团所需条件列表，例如：`["有编程基础", "对算法有兴趣"]`。
    *   **响应体 (JSON)**:
        *   `summary` (str): AI生成的申请摘要。
        *   `suggestion` (str): AI生成的建议。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/screen_application \
          -H "Content-Type: application/json" \
          -d '{
            "applicant_data": {
                "name": "李华",
                "major": "计算机科学与技术",
                "skills": ["Python编程", "数据结构", "Web开发"],
                "experience": "曾参与校内编程竞赛并获得二等奖"
            },
            "application_reason": "我对贵社团的编程氛围和技术挑战非常感兴趣，希望能在社团中提升自己的编程能力并结识志同道合的朋友。我熟悉Python语言，并有Web开发经验。",
            "required_conditions": ["有编程基础", "对算法有兴趣", "积极参与团队项目"]
          }'
        ```

### 12. 社团"氛围"透视镜接口

*   **POST** `/club_atmosphere`
    *   **描述**: 对社团内部交流内容进行情感分析和主题建模，生成"氛围标签"和"文化摘要"。
    *   **请求体 (JSON)**:
        *   `communication_content` (str): 社团内部的交流内容，如论坛帖子、聊天记录摘要等。
    *   **响应体 (JSON)**:
        *   `atmosphere_tags` (List[str]): AI生成的氛围标签列表。
        *   `culture_summary` (str): AI生成的文化摘要。
    *   **`curl` 示例**:
        ```bash
        curl -X POST http://localhost:8080/club_atmosphere \
          -H "Content-Type: application/json" \
          -d '{
            "communication_content": "社团成员A: 今天的编程挑战太难了，我卡住了！\n社团成员B: 别灰心，我来帮你看看！我们可以一起调试。\n社团成员C: 对，大家多交流，互相帮助才能进步！\n社团成员D: 最近有个新算法很有意思，有空我给大家分享一下。\n社团成员E: 期待！正好最近在研究这方面的东西。\n社团管理员: 下周五有一次线下技术交流会，欢迎大家积极参加！"
          }'
        ```

### 13. 模型列表

*   **GET** `/models`
    *   **描述**: 获取 vLLM 服务器可用的模型列表。
    *   **响应示例**: (实际响应取决于 vLLM 服务器)
        ```json
        {
          "data": [
            {
              "id": "Qwen/Qwen3-8B-AWQ",
              "object": "model",
              "created": 0,
              "owned_by": "vllm"
            }
          ]
        }
        ```

## 测试

### 测试配置导入

```bash
python test_import.py
```

### 运行完整测试

```bash
python test_client.py
```

测试包括：
- 健康检查
- 简化聊天接口
- 完整聊天接口
- 模型列表查询
- 配置信息查询
- 多轮对话

## 使用示例

### Python客户端示例

```python
import requests

# 简化聊天
response = requests.post(
    "http://localhost:8080/simple_chat",
    params={"prompt": "你好，请介绍一下人工智能"}
)
print(response.json())

# 完整聊天
payload = {
    "messages": [
        {"role": "user", "content": "请用中文解释什么是机器学习"}
    ],
    "max_tokens": 1000,
    "temperature": 0.7
}

response = requests.post(
    "http://localhost:8080/chat",
    headers={"Content-Type": "application/json"},
    json=payload
)
print(response.json())
```

### JavaScript客户端示例

```javascript
// 简化聊天
const response = await fetch('http://localhost:8080/simple_chat?prompt=你好', {
    method: 'POST'
});
const result = await response.json();
console.log(result);

// 完整聊天
const payload = {
    messages: [
        {role: "user", content: "请介绍一下深度学习"}
    ],
    max_tokens: 1000
};

const response = await fetch('http://localhost:8080/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
});
const result = await response.json();
console.log(result);
```

## 配置文件管理

### 动态重载配置

如果需要在不重启服务器的情况下更新配置，可以修改`config.json`文件，然后调用配置重载接口（如果实现的话）。

### 环境变量支持

您可以通过环境变量覆盖配置文件中的设置：

```bash
export VLLM_API_URL="http://your-vllm-server:8000/v1/chat/completions"
export DEFAULT_MODEL="your-model-name"
python vllm_proxy_server.py
```

## 注意事项

1. **vLLM服务器**: 确保vLLM服务器正在运行并监听正确的地址和端口
2. **模型名称**: 确保请求中使用的模型名称与vLLM服务器中加载的模型匹配
3. **网络连接**: 确保代理服务器能够访问vLLM服务器
4. **资源限制**: 根据您的硬件配置调整 `max_tokens` 和超时设置
5. **配置文件**: 确保`config.json`文件格式正确，可以使用JSON验证工具检查

## 故障排除

### 常见问题

1. **配置文件错误**
   - 检查`config.json`文件格式是否正确
   - 使用JSON验证工具验证配置文件
   - 确保所有必要的配置项都存在

2. **连接vLLM服务器失败**
   - 检查vLLM服务器是否正在运行
   - 验证`vllm.api_url`配置是否正确
   - 检查网络连接

3. **模型不存在错误**
   - 确认模型名称拼写正确
   - 检查vLLM服务器是否加载了指定的模型

4. **请求超时**
   - 增加`request.timeout`配置值
   - 检查vLLM服务器的响应时间

5. **CORS错误**
   - 在`config.json`