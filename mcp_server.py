#!/usr/bin/env python3
"""LightRAG MCP Server"""
import sys
import json
import asyncio
import httpx
import io

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='surrogateescape')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='surrogateescape')

LIGHTRAG_API = "http://127.0.0.1:9621"

def log(msg):
    """Debug logging"""
    try:
        with open("mcp_debug.log", "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except:
        pass

class MCPServer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        log("MCP Server started")

    async def handle_request(self, request):
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "lightrag-mcp", "version": "1.0.0"}
                    }
                }

            elif method == "initialized":
                return None  # Notification, no response

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "lightrag_query",
                                "description": "Query LightRAG knowledge base. Use this tool when encountering calibre-related questions, issues, or when you need information about calibre (EDA tool by Siemens). The knowledge base contains calibre documentation and troubleshooting information.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Query text"},
                                        "mode": {
                                            "type": "string",
                                            "enum": ["local", "global", "hybrid", "naive"],
                                            "description": "Query mode",
                                            "default": "hybrid"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "lightrag_insert",
                                "description": "Insert text into LightRAG knowledge base",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string", "description": "Text to insert"}
                                    },
                                    "required": ["text"]
                                }
                            }
                        ]
                    }
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "lightrag_query":
                    result = await self.query(args.get("query", ""), args.get("mode", "hybrid"))
                elif tool_name == "lightrag_insert":
                    result = await self.insert(args.get("text", ""))
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": result}]}
                }

            else:
                raise ValueError(f"Unknown method: {method}")

        except Exception as e:
            log(f"Error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }

    async def query(self, query, mode="hybrid"):
        """Query knowledge base"""
        try:
            # Fix encoding issues
            query = query.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')

            response = await self.client.post(
                f"{LIGHTRAG_API}/query",
                json={"query": query, "mode": mode}
            )
            response.raise_for_status()
            return response.json().get("response", "No response")
        except Exception as e:
            return f"Error: {str(e)}"

    async def insert(self, text):
        """Insert text into knowledge base"""
        try:
            response = await self.client.post(
                f"{LIGHTRAG_API}/documents/text",
                json={"text": text}
            )
            response.raise_for_status()
            return f"Inserted {len(text)} characters"
        except Exception as e:
            return f"Error: {str(e)}"

    async def run(self):
        """Run server on stdin/stdout"""
        log("Server ready")
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                log(f"Error: {e}")

async def main():
    server = MCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped")
    except Exception as e:
        log(f"Fatal: {e}")
        sys.exit(1)
