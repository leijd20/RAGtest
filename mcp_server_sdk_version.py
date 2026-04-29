#!/usr/bin/env python3
"""LightRAG MCP Server - 使用官方SDK版本"""
import asyncio
import httpx
import re
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

LIGHTRAG_API = "http://127.0.0.1:9621"

# 创建MCP服务器实例
app = Server("lightrag-mcp")

# HTTP客户端
client = httpx.AsyncClient(timeout=300.0)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """注册工具"""
    return [
        Tool(
            name="lightrag_query",
            description="Query LightRAG knowledge base. Use this tool when encountering calibre-related questions, issues, or when you need information about calibre (EDA tool by Siemens).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query text"},
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid", "naive"],
                        "default": "hybrid"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="lightrag_insert",
            description="Insert text into LightRAG knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to insert"}
                },
                "required": ["text"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    if name == "lightrag_query":
        query = arguments.get("query", "")
        mode = arguments.get("mode", "hybrid")
        result = await query_kb(query, mode)
        return [TextContent(type="text", text=result)]

    elif name == "lightrag_insert":
        text = arguments.get("text", "")
        result = await insert_text(text)
        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def query_kb(query: str, mode: str = "hybrid") -> str:
    """查询知识库"""
    try:
        # 编码修复
        if isinstance(query, str):
            query = query.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')

        response = await client.post(
            f"{LIGHTRAG_API}/query",
            json={"query": query, "mode": mode}
        )
        response.raise_for_status()

        # 清理代理字符
        raw_text = response.text
        cleaned_text = re.sub(r'[\udc80-\udcff]', '', raw_text)

        import json
        data = json.loads(cleaned_text)
        return data.get("response", "No response")
    except Exception as e:
        return f"Error: {str(e)}"

async def insert_text(text: str) -> str:
    """插入文本"""
    try:
        response = await client.post(
            f"{LIGHTRAG_API}/documents/text",
            json={"text": text}
        )
        response.raise_for_status()
        return f"Inserted {len(text)} characters"
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    """运行服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
