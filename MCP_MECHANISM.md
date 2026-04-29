# MCP服务器运行流程

## 阶段1：配置加载
Claude Code启动时读取 `.claude/mcp_config.json`
- 记录MCP服务器的启动命令
- 但此时**不启动**服务器

## 阶段2：按需启动（当对话中可能需要工具时）
1. Claude Code执行配置中的命令：
   ```
   python D:\GKXTwork\agent_dev\RAGtest\lightrag_mcp_server.py
   ```

2. MCP服务器进程启动，等待stdin输入

## 阶段3：初始化握手
Claude Code → MCP服务器：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

MCP服务器 → Claude Code：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "lightrag-mcp-server", "version": "1.0.0"}
  }
}
```

## 阶段4：工具发现（关键！）
Claude Code → MCP服务器：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

MCP服务器 → Claude Code：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "lightrag_query",
        "description": "Query the LightRAG knowledge base. Use this tool when encountering calibre-related questions...",
        "inputSchema": {...}
      }
    ]
  }
}
```

**此时工具描述被加载到Claude的上下文中！**

## 阶段5：工具调用（如果需要）
当Claude决定使用工具时：

Claude Code → MCP服务器：
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "lightrag_query",
    "arguments": {"query": "calibre如何导入电子书？"}
  }
}
```

MCP服务器 → Claude Code：
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [{"type": "text", "text": "查询结果..."}]
  }
}
```

## 阶段6：会话结束
- MCP服务器进程可能保持运行（等待下次调用）
- 或在一段时间后被Claude Code关闭

## 关键点

### 描述何时生效？
✅ **每次MCP服务器启动时**
- 修改描述后，下次启动MCP服务器时生效
- 不需要重启Claude Code
- 但需要等待当前MCP服务器进程结束（或手动重启）

### Claude如何决定调用工具？
基于：
1. **工具描述** - "Use this tool when encountering calibre-related questions"
2. **对话内容** - 用户提到了calibre
3. **Claude的判断** - 综合评估是否需要查询知识库

### 通信方式
- **stdio** (标准输入输出)
- JSON-RPC 2.0协议
- 同步请求-响应模式
