# RAGtest - LightRAG MCP Server

将LightRAG知识图谱系统集成到Claude Code的MCP服务器。

## 快速开始

### 前置要求

- Python 3.11+
- 已安装 `uv` 工具
- Claude Code（CLI/桌面版/Web版）

### 第一步：启动LightRAG服务器

LightRAG服务器提供知识库的API接口，必须先启动。

**Windows（推荐使用批处理脚本）：**

双击运行 `start_lightrag.bat`，或在命令行执行：

```cmd
cd /d D:\GKXTwork\agent_dev\RAGtest\LightRAG
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8
lightrag-server --host 127.0.0.1 --port 9621
```

**Linux/Mac：**

```bash
cd LightRAG
export PATH="$HOME/.local/bin:$PATH"
export PYTHONIOENCODING=utf-8
lightrag-server --host 127.0.0.1 --port 9621
```

**验证服务器运行：**

```bash
curl http://127.0.0.1:9621/health
# 应返回：{"status":"healthy",...}
```

访问Web UI：http://127.0.0.1:9621

### 第二步：配置MCP服务器

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "lightrag": {
      "command": "python",
      "args": ["-u", "lightrag_mcp_server_fixed.py"]
    }
  }
}
```

**配置说明：**
- 文件位置：项目根目录（与 `lightrag_mcp_server_fixed.py` 同级）
- `command`: Python命令（确保在PATH中）
- `args`: 使用相对路径即可，Claude Code会自动解析

### 第三步：连接MCP

在Claude Code中：
1. 进入项目目录
2. 输入 `/mcp` 命令
3. 选择 `lightrag` 并连接

连接成功后会显示 "Connected to lightrag"。

### 第四步：测试

询问calibre相关问题，Claude会自动调用知识库：
```
什么是calibre？
```

或手动插入文档：
```
请将这段文本插入知识库：Calibre是Siemens的EDA工具...
```

## 项目结构

```
RAGtest/
├── LightRAG/                           # LightRAG源码和数据
│   ├── .env                            # LLM/Embedding配置
│   └── rag_storage/                    # 知识库存储
├── lightrag_mcp_server_fixed.py        # MCP服务器（修复中文编码）
├── .mcp.json                           # MCP配置文件
├── start_lightrag.bat                  # Windows启动脚本
```

## MCP工具说明

连接成功后，Claude Code获得两个工具：

### 1. lightrag_query - 查询知识库

**自动触发：** 当询问calibre相关问题时自动调用

**参数：**
- `query` (必需): 查询文本
- `mode` (可选): 查询模式，默认 `hybrid`
  - `hybrid`: 混合检索（推荐）
  - `local`: 实体聚焦检索
  - `global`: 社区摘要检索
  - `naive`: 纯向量检索

### 2. lightrag_insert - 插入文档

**用途：** 向知识库添加新文档或文本

**参数：**
- `text` (必需): 要插入的文本内容

## 配置说明

### LLM配置

编辑 `LightRAG/.env` 文件修改LLM和Embedding配置：

```env
# LLM配置（当前使用SiliconFlow）
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.siliconflow.cn/v1
LLM_BINDING_API_KEY=your-api-key
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct

# Embedding配置
EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=https://api.siliconflow.cn/v1
EMBEDDING_BINDING_API_KEY=your-api-key
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
```

修改后重启LightRAG服务器生效。

## 故障排除

### 1. LightRAG服务器无法启动

**问题：找不到 lightrag-server 命令**

```cmd
# 检查安装位置
where lightrag-server

# 添加到PATH
set PATH=%USERPROFILE%\.local\bin;%PATH%
```

**问题：tiktoken下载失败**

```bash
cd LightRAG
```

### 2. MCP连接问题

**MCP服务器无法启动：**

```cmd
# 检查Python是否在PATH中
where python

# 如果需要，使用完整路径修改 .mcp.json
{
  "mcpServers": {
    "lightrag": {
      "command": "C:\\Python311\\python.exe",
      "args": ["-u", "lightrag_mcp_server_fixed.py"]
    }
  }
}
```

**修改配置后重新连接：**

在Claude Code中输入 `/mcp` 重新连接。

**中文查询乱码：**

确保使用 `lightrag_mcp_server_fixed.py`（已修复编码问题）。

### 3. 查看调试日志

```bash
# MCP服务器日志
cat mcp_debug.log

# LightRAG服务器日志
cat LightRAG/lightrag.log
```

### 4. 端口被占用

```cmd
# 查看端口占用
netstat -ano | findstr :9621

# 杀死进程
taskkill /F /PID <进程ID>

# 或修改端口（编辑 LightRAG/.env）
PORT=9622
```

## 常见问题

**Q: 如何重新连接MCP？**  
A: 在Claude Code中输入 `/mcp` 命令。

**Q: 可以使用相对路径吗？**  
A: 可以，`.mcp.json` 中的路径相对于项目根目录。

**Q: 如何更新知识库？**  
A: 通过Web UI上传文档，或使用 `lightrag_insert` 工具。

**Q: 如何清空知识库？**  
A: 删除 `LightRAG/rag_storage` 目录，重启服务器。

**Q: 支持哪些文档格式？**  
A: TXT, PDF, DOCX, PPTX, XLSX等。

## 相关资源

- [LightRAG官方文档](https://github.com/HKUDS/LightRAG)
- [API文档](http://127.0.0.1:9621/docs)（需先启动服务器）
- Web UI: http://127.0.0.1:9621

## 许可证

本项目基于LightRAG构建，遵循其开源许可证。
