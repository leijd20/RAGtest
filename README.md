# RAGtest - LightRAG知识库系统

将LightRAG知识图谱RAG系统集成到Claude Code的完整解决方案。

## 快速开始

### 前置要求

- Python 3.11+
- 已安装 `uv` 工具
- 网络连接（用于下载tiktoken缓存）

### 本地启动LightRAG服务器

#### Windows环境（推荐方法）

**方法1：使用批处理脚本（最简单）**

1. 创建启动脚本 `start_lightrag.bat`：

```batch
@echo off
echo ========================================
echo Starting LightRAG Server
echo ========================================

cd /d D:\GKXTwork\agent_dev\RAGtest\LightRAG
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8

echo.
echo Server will start at: http://127.0.0.1:9621
echo Web UI: http://127.0.0.1:9621
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

lightrag-server --host 127.0.0.1 --port 9621

pause
```

2. 双击 `start_lightrag.bat` 运行

**方法2：CMD命令行**

```cmd
:: 1. 进入LightRAG目录
cd /d D:\GKXTwork\agent_dev\RAGtest\LightRAG

:: 2. 设置环境变量
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8

:: 3. 启动服务器
lightrag-server --host 127.0.0.1 --port 9621
```

**方法3：PowerShell**

```powershell
# 1. 进入LightRAG目录
cd D:\GKXTwork\agent_dev\RAGtest\LightRAG

# 2. 设置环境变量
$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
$env:PYTHONIOENCODING = "utf-8"

# 3. 启动服务器
lightrag-server --host 127.0.0.1 --port 9621
```

**方法4：后台运行（使用start命令）**

```cmd
:: 在新窗口后台运行
cd /d D:\GKXTwork\agent_dev\RAGtest\LightRAG
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8
start "LightRAG Server" lightrag-server --host 127.0.0.1 --port 9621

:: 查看运行状态
tasklist | findstr lightrag

:: 停止服务（找到PID后）
taskkill /F /IM lightrag-server.exe
```

#### Linux/Mac环境

**方法1：直接启动**

```bash
# 1. 进入LightRAG目录
cd LightRAG

# 2. 设置环境变量
export PATH="$HOME/.local/bin:$PATH"
export PYTHONIOENCODING=utf-8

# 3. 启动服务器
lightrag-server --host 127.0.0.1 --port 9621
```

**方法2：后台运行**

```bash
# 使用nohup后台运行
cd LightRAG
export PATH="$HOME/.local/bin:$PATH"
export PYTHONIOENCODING=utf-8
nohup lightrag-server --host 127.0.0.1 --port 9621 > lightrag.log 2>&1 &

# 查看进程
ps aux | grep lightrag-server

# 停止服务
pkill -f lightrag-server
```

### 验证服务器运行

```bash
# 检查健康状态
curl http://127.0.0.1:9621/health

# 应该返回：
# {"status":"healthy","webui_available":true,...}
```

### 访问Web UI

浏览器打开：http://127.0.0.1:9621

## 项目结构

```
RAGtest/
├── LightRAG/                           # LightRAG源码
│   ├── .env                            # 配置文件（LLM、Embedding等）
│   ├── rag_storage/                    # 知识库存储目录
│   ├── tiktoken_cache/                 # Tiktoken缓存
│   └── lightrag.log                    # 服务器日志
├── lightrag_mcp_server.py              # MCP服务器（基础版）
├── lightrag_mcp_server_with_log.py     # MCP服务器（带日志）
├── .claude/
│   └── mcp_config.json                 # MCP配置
├── CLAUDE.md                           # 项目文档
└── README.md                           # 本文件
```

## 配置说明

### LLM配置（LightRAG/.env）

当前使用SiliconFlow API：

```env
# LLM配置
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.siliconflow.cn/v1
LLM_BINDING_API_KEY=sk-kkijpciadappjfsofzshqmylfpqliixhnptzthptdbcihwze
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct

# Embedding配置
EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=https://api.siliconflow.cn/v1
EMBEDDING_BINDING_API_KEY=sk-kkijpciadappjfsofzshqmylfpqliixhnptzthptdbcihwze
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
```

### 修改配置

编辑 `LightRAG/.env` 文件，修改后重启服务器生效。

## MCP服务器部署

### 完整部署流程

#### 步骤1：准备MCP服务器脚本

确保项目根目录有 `lightrag_mcp_server_fixed.py` 文件，这是修复了中文编码问题的版本。

**关键特性：**
- ✅ 支持中文查询和响应
- ✅ 处理Windows下的编码问题
- ✅ 包含详细的调试日志
- ✅ 自动触发机制（通过工具描述）

#### 步骤2：配置MCP服务器

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "lightrag": {
      "command": "python",
      "args": [
        "-u",
        "D:\\GKXTwork\\agent_dev\\RAGtest\\lightrag_mcp_server_fixed.py"
      ]
    }
  }
}
```

**配置说明：**
- `command`: Python解释器路径（可以是`python`或完整路径如`D:\miniconda3\python.exe`）
- `args`: 
  - `-u`: 无缓冲模式，确保日志实时输出
  - 第二个参数：MCP服务器脚本的**绝对路径**

#### 步骤3：启动LightRAG服务器

MCP服务器依赖LightRAG API，必须先启动：

```bash
# Windows
cd LightRAG
set PATH=%USERPROFILE%\.local\bin;%PATH%
lightrag-server --host 127.0.0.1 --port 9621

# Linux/Mac
cd LightRAG
export PATH="$HOME/.local/bin:$PATH"
lightrag-server --host 127.0.0.1 --port 9621
```

验证服务器运行：
```bash
curl http://127.0.0.1:9621/health
```

#### 步骤4：在Claude Code中连接MCP

1. 打开Claude Code
2. 进入项目目录：`D:\GKXTwork\agent_dev\RAGtest`
3. 执行命令：`/mcp`
4. 选择 `lightrag` 服务器并连接

**验证连接成功：**
- 连接后会显示 "Connected to lightrag" 或 "Reconnected to lightrag"
- 可以在对话中询问calibre相关问题测试

#### 步骤5：测试MCP工具

**测试查询功能：**
```
你：什么是calibre？
```

Claude应该自动调用 `lightrag_query` 工具查询知识库。

**测试插入功能：**
```
你：请将这段文本插入知识库：[你的文本内容]
```

### MCP工具说明

部署成功后，Claude Code会获得两个工具：

#### 1. lightrag_query - 查询知识库

**自动触发条件：**
- 用户询问calibre相关问题
- 需要查询知识库中的信息

**参数：**
- `query` (必需): 查询文本
- `mode` (可选): 查询模式
  - `hybrid` (默认): 混合检索，推荐使用
  - `local`: 实体聚焦检索
  - `global`: 社区摘要检索
  - `naive`: 纯向量检索

**示例：**
```python
lightrag_query(query="什么是calibre？", mode="hybrid")
```

#### 2. lightrag_insert - 插入文档

**用途：**
向知识库添加新文档或文本内容

**参数：**
- `text` (必需): 要插入的文本内容

**示例：**
```python
lightrag_insert(text="Calibre是一个EDA工具...")
```

### 调试MCP连接

#### 查看MCP日志

```bash
# 查看调试日志
cat mcp_debug.log

# 实时监控日志
tail -f mcp_debug.log
```

#### 常见MCP问题

**问题1：MCP服务器无法启动**

检查Python路径：
```bash
# Windows
where python

# Linux/Mac  
which python
```

修改 `.mcp.json` 中的 `command` 为完整路径。

**问题2：工具调用卡死**

原因：编码问题（已在 `lightrag_mcp_server_fixed.py` 中修复）

检查日志：
```bash
cat mcp_debug.log | grep "Error"
```

**问题3：Claude不自动调用工具**

检查工具描述是否包含触发关键词：
```python
# 在 lightrag_mcp_server_fixed.py 中
"description": "Query LightRAG knowledge base. Use this tool when encountering calibre-related questions..."
```

**问题4：中文查询乱码**

确保使用 `lightrag_mcp_server_fixed.py`，该版本已修复：
- stdin/stdout使用 `errors='surrogateescape'`
- 查询字符串自动清理代理字符
- 响应结果正确编码

### 配置文件对比

| 文件 | 用途 | 状态 |
|------|------|------|
| `.mcp.json` | 项目级MCP配置 | ✅ 推荐使用 |
| `.claude/mcp_config.json` | 旧版配置 | ❌ 已废弃 |
| `~/.claude.json` | 全局Claude配置 | ⚠️ 自动生成 |
| `mcp_debug.log` | MCP调试日志 | 📝 用于排查问题 |

### 注意事项

1. **路径必须使用绝对路径**
   - ❌ 错误：`"./lightrag_mcp_server_fixed.py"`
   - ✅ 正确：`"D:\\GKXTwork\\agent_dev\\RAGtest\\lightrag_mcp_server_fixed.py"`

2. **Windows路径使用双反斜杠**
   - JSON中需要转义：`\\` 而不是 `\`

3. **LightRAG服务器必须先启动**
   - MCP服务器只是客户端，需要连接到LightRAG API

4. **修改配置后需要重新连��**
   - 修改 `.mcp.json` 后执行 `/mcp` 重新连接

5. **Python环境一致性**
   - MCP服务器使用的Python环境需要安装 `httpx`
   - 建议使用与LightRAG相同的Python环境

## 使用方法

### 1. 在Claude Code中使用（推荐）

MCP服务器注册后，Claude会自动获得两个工具：

**插入文档：**
```
请帮我插入这篇文档到知识库：[文档内容]
```

**查询知识库：**
```
请查询知识库：calibre如何导入电子书？
```

Claude Code会自动调用相应的工具。

### 2. 通过Web UI使用

1. 打开 http://127.0.0.1:9621
2. 上传文档或输入文本
3. 等待处理完成
4. 在查询界面输入问题

### 3. 通过API使用

**上传文档：**
```bash
curl -X POST http://127.0.0.1:9621/documents/upload \
  -F "file=@your_document.txt"
```

**查询：**
```bash
curl -X POST http://127.0.0.1:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query":"你的问题","mode":"hybrid"}'
```

**查询模式：**
- `local`: 实体聚焦检索
- `global`: 社区摘要检索
- `hybrid`: 混合模式（推荐）
- `naive`: 纯向量检索

## 故障排除

### Windows环境特有问题

**问题1：找不到lightrag-server命令**

```cmd
:: 检查安装位置
where lightrag-server

:: 如果找不到，手动添加到PATH
set PATH=%USERPROFILE%\.local\bin;%PATH%

:: 或者使用完整路径
%USERPROFILE%\.local\bin\lightrag-server.exe --host 127.0.0.1 --port 9621
```

**问题2：中文乱码/编码错误**

```cmd
:: 方法1：设置环境变量
set PYTHONIOENCODING=utf-8

:: 方法2：修改CMD代码页
chcp 65001

:: 方法3：在批处理脚本开头添加
@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
```

**问题3：权限问题**

```cmd
:: 以管理员身份运行CMD
:: 右键点击CMD -> "以管理员身份运行"

:: 或者检查防火墙设置
:: Windows Defender防火墙 -> 允许应用通过防火墙
```

**问题4：Python环境冲突**

```cmd
:: 检查Python版本
python --version

:: 如果有多个Python，指定完整路径
C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\python.exe -m pip list
```

**问题5：端口被占用**

```cmd
:: 查看端口占用
netstat -ano | findstr :9621

:: 找到PID后杀死进程
taskkill /F /PID <进程ID>

:: 或者修改端口
:: 编辑 LightRAG\.env 文件，修改 PORT=9621 为其他端口
```

### 通用问题

### 1. 服务器无法启动

**问题：tiktoken下载失败**

Windows CMD:
```cmd
cd LightRAG
set PATH=%USERPROFILE%\.local\bin;%PATH%
set PYTHONIOENCODING=utf-8
lightrag-download-cache --cache-dir ./tiktoken_cache
```

Linux/Mac:
```bash
cd LightRAG
export PATH="$HOME/.local/bin:$PATH"
export PYTHONIOENCODING=utf-8
lightrag-download-cache --cache-dir ./tiktoken_cache
```

**问题：SSL证书错误**

```cmd
:: Windows - 临时禁用SSL验证（不推荐用于生产）
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=

:: 或者更新证书
pip install --upgrade certifi
```

### 2. MCP服务器问题

**注册MCP服务器：**
```bash
# 使用claude mcp add命令注册
claude mcp add --transport stdio lightrag -- python D:\GKXTwork\agent_dev\RAGtest\lightrag_mcp_server_with_log.py

# 重启Claude Code
```

**检查MCP配置：**
```bash
# 配置位置：~/.claude.json
# Windows: C:\Users\你的用户名\.claude.json
# Linux/Mac: ~/.claude.json

# 查看项目MCP配置
cat ~/.claude.json | grep -A 10 "mcpServers"
```

**查看MCP日志：**
```bash
cat mcp_server.log
```

**测试MCP服务器：**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python lightrag_mcp_server.py
```

### 3. 查询无结果

**原因：知识库为空**
- 先上传文档到知识库
- 等待文档处理完成（查看Web UI状态）

**原因：查询模式不合适**
- 尝试不同的查询模式（hybrid/local/global）

### 4. 查看日志

```bash
# LightRAG服务器日志
tail -f LightRAG/lightrag.log

# MCP服务器日志
tail -f mcp_server.log
```

## 高级配置

### 修改服务器端口

编辑 `LightRAG/.env`:
```env
PORT=9621  # 改为其他端口
```

### 使用其他LLM

编辑 `LightRAG/.env`，参考 `LightRAG/env.example` 中的配置示例：

**使用Ollama（本地）：**
```env
LLM_BINDING=ollama
LLM_BINDING_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:32b
OLLAMA_LLM_NUM_CTX=32768
```

**使用OpenAI：**
```env
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini
```

### 性能优化

编辑 `LightRAG/.env`:
```env
# 并发配置
MAX_ASYNC=8                # LLM并发数
MAX_PARALLEL_INSERT=4      # 文档处理并发数

# 检索配置
TOP_K=60                   # 检索实体/关系数量
CHUNK_TOP_K=20            # 检索文本块数量
```

## 开发相关

### 修改MCP工具描述

编辑 `lightrag_mcp_server.py` 中的工具描述，修改后下次MCP服务器启动时生效。

### 添加新的MCP工具

在 `lightrag_mcp_server.py` 的 `tools/list` 部分添加新工具定义。

### 调试MCP通信

使用带日志的版本：
```bash
# 修改 .claude/mcp_config.json 指向：
# lightrag_mcp_server_with_log.py

# 查看日志
tail -f mcp_server.log
```

## 相关文档

- [LightRAG官方文档](https://github.com/HKUDS/LightRAG)
- [项目配置说明](CLAUDE.md)
- [MCP运行机制](MCP_MECHANISM.md)
- [Claude决策机制](HOW_CLAUDE_DECIDES.md)
- [API文档](http://127.0.0.1:9621/docs)（需先启动服务器）

## 常见问题

**Q: 如何更新知识库？**
A: 直接上传新文档，LightRAG会自动更新知识图谱。

**Q: 如何清空知识库？**
A: 删除 `LightRAG/rag_storage` 目录，重启服务器。

**Q: 支持哪些文档格式？**
A: TXT, PDF, DOCX, PPTX, XLSX等（通过Web UI上传）。

**Q: 如何备份知识库？**
A: 备份 `LightRAG/rag_storage` 目录即可。

**Q: 可以同时运行多个知识库吗？**
A: 可以，使用不同的 `WORKING_DIR` 和端口。

## 许可证

本项目基于LightRAG构建，遵循其开源许可证。
