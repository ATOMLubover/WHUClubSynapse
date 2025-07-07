# MCP 服务器测试指南

这个目录下 test_mcp 系列文件，是用于测试 MCP (Model Context Protocol) 服务器的测试文件和工具。

## 文件说明

### 测试文件

1. **`test_mcp_server.py`** - 完整的 MCP 服务器测试套件

   - 包含 MCP 接口的全面测试
   - 测试工具列表、工具调用、错误处理等
   - 需要 ChromaDB 和嵌入模型

2. **`test_mcp_core.py`** - 核心功能的简化测试
   - 专注于基础 MCP 功能
   - 使用模拟数据，减少外部依赖
   - 适合快速验证

### 工具脚本

3. **`quick_test_mcp.py`** - 快速测试脚本

   - 一键测试 MCP 服务器基础功能
   - 不需要真实的数据库连接
   - 适合开发环境快速验证

4. **`run_mcp_tests.py`** - 完整测试运行器
   - 运行所有 MCP 测试
   - 检查依赖和环境
   - 提供详细的测试报告

## 使用方法

### 1. 快速验证（推荐）

```bash
# 快速测试基础功能
python quick_test_mcp.py
```

这个脚本会测试：

- MCP 模块导入
- 工具定义
- 基础工具调用（使用模拟数据）

### 2. 核心功能测试

```bash
# 使用 pytest 运行核心测试
python -m pytest tests/rag/test_mcp_core.py -v

# 或者直接运行
python tests/rag/test_mcp_core.py
```

### 3. 完整测试（需要真实环境）

```bash
# 运行完整的 MCP 测试套件
python -m pytest tests/rag/test_mcp_server.py -v

# 或使用测试运行器
python run_mcp_tests.py
```

**注意**：完整测试需要：

- ChromaDB 服务正在运行
- 嵌入模型已下载并配置
- 测试数据集

### 4. 特定测试

```bash
# 只测试工具列表功能
python -m pytest tests/rag/test_mcp_server.py::test_list_tools -v

# 只测试异步功能
python -m pytest tests/rag/test_mcp_server.py -k "asyncio" -v

# 只测试错误处理
python -m pytest tests/rag/test_mcp_server.py -k "error" -v
```

## 测试环境要求

### 最小要求（快速测试）

```bash
pip install pytest pytest-asyncio mcp
```

### 完整要求（所有测试）

```bash
pip install pytest pytest-asyncio mcp chromadb sentence-transformers langchain langchain-community
```

### 服务依赖（完整测试）

- ChromaDB 服务运行在配置的端口
- 嵌入模型文件存在于指定目录
- 测试数据集

## 测试结果解释

### 成功输出示例

```
✅ MCP 组件导入成功
✅ 找到 1 个工具: ['retrieve']
✅ 工具调用基础功能正常
✅ 错误处理功能正常
🎉 所有测试都通过了！MCP 服务器基础功能正常
```

### 常见错误

1. **导入错误**

   ```
   ❌ 导入失败: No module named 'mcp'
   ```

   解决：`pip install mcp`

2. **模型加载错误**

   ```
   ⚠️ KnowledgeRetrieverMCP 初始化失败（可能因为模型或数据库不可用）
   ```

   解决：检查模型路径和 ChromaDB 服务

3. **配置错误**
   ```
   ❌ 数据库连接失败
   ```
   解决：检查 `config.py` 中的配置

## 测试架构

### MCP 工具测试流程

1. **导入测试** - 验证所有必要模块能够正确导入
2. **工具列表测试** - 验证 MCP 服务器能够返回可用工具列表
3. **工具调用测试** - 验证工具能够正确处理输入并返回结果
4. **错误处理测试** - 验证各种错误情况的处理
5. **集成测试** - 端到端的完整流程测试

### 模拟与真实测试

- **模拟测试**：使用 `unittest.mock` 模拟外部依赖，专注于 MCP 协议本身
- **真实测试**：使用真实的数据库和模型，测试完整功能

## 扩展测试

如果需要添加新的测试：

1. **简单功能测试** → 添加到 `test_mcp_core.py`
2. **复杂集成测试** → 添加到 `test_mcp_server.py`
3. **新的工具测试** → 在两个文件中都添加相应测试

## 故障排除

### 1. 测试运行慢

使用核心测试或快速测试脚本：

```bash
python quick_test_mcp.py
```

### 2. 依赖缺失

运行依赖检查：

```bash
python run_mcp_tests.py  # 会先检查依赖
```

### 3. 服务连接问题

检查配置文件 `app/configs/config.py` 中的设置：

- `CHROMA_SERVER_HOST`
- `CHROMA_SERVER_PORT`
- `EMBEDDING_MODEL_DIR`

### 4. 异步测试问题

确保安装了 `pytest-asyncio`：

```bash
pip install pytest-asyncio
```

## 持续集成

这些测试可以集成到 CI/CD 流水线中：

```yaml
# 示例 GitHub Actions 配置
- name: Test MCP Server
  run: |
    python quick_test_mcp.py
    python -m pytest tests/rag/test_mcp_core.py -v
```
