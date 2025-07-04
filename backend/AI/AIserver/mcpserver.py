from fastapi import FastAPI
from fastapi_mcp import add_mcp_server, MCPTool  # 引入MCP支持
app = FastAPI()  # 创建一个FastAPI应用
# 3. 定义一个工具：查数据库 (假装我们连了数据库)
@MCPTool(name="query_db")  # 给工具起个名，大模型就靠这个名字调用它
async def query_database(sql: str) -> list:  # 定义工具：输入是SQL字符串，输出是列表
    """
    执行SQL查询并返回结果 (给大模型看的说明书)
    参数:
        sql: 合法的SQL查询语句 (比如 'SELECT name FROM products WHERE id=1')
    返回:
        查询结果列表, 比如 [{'name': '超强吸尘器'}]
    """
    # 这里应该是真实连接数据库的代码，为了演示，我们模拟一下
    if "product" in sql.lower():
        return [{"id": 1, "name": "AI开发板"}, {"id": 2, "name": "智能水杯"}]
    else:
        return [{"error": "模拟结果：请检查SQL语句"}]
# 4. 把MCP服务“挂”到我们的FastAPI应用上
add_mcp_server(
    app,  # 我们的FastAPI应用
    mount_path="/mcp",  # MCP服务的访问路径，比如 http://你的地址/mcp
    name="我的第一个MCP服务器",  # 起个名
    version="0.1",  # 版本号
    tools=[query_database]  # 把我们刚定义的工具注册进去！
)
# 5. 启动服务器！
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)  # 在本地8082端口跑起来