#!/usr/bin/env python3
"""
LightRAG MCP Server - Fixed version with proper handshake
"""
import sys
import json
import asyncio
import httpx
import io
from typing import Any, Dict

# Force UTF-8 encoding for stdin/stdout on Windows
if sys.platform == 'win32':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='surrogateescape')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='surrogateescape')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# LightRAG API endpoint
LIGHTRAG_API_BASE = "http://127.0.0.1:9621"

def log(msg):
    """Write to debug log"""
    try:
        # Handle surrogate characters and encoding errors
        if isinstance(msg, str):
            msg = msg.encode('utf-8', errors='replace').decode('utf-8')
        with open("mcp_debug.log", "a", encoding="utf-8", errors='replace') as f:
            f.write(f"{msg}\n")
        print(f"[DEBUG] {msg}", file=sys.stderr, flush=True)
    except Exception:
        # Silently ignore logging errors to not break the main flow
        pass


class LightRAGMCPServer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.initialized = False
        log("=== MCP Server Starting ===")
        log(f"Python: {sys.version}")
        log(f"Executable: {sys.executable}")

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        log(f"Received: method={method}, id={request_id}")

        try:
            if method == "initialize":
                self.initialized = True
                log("Handling initialize request")
                # Use the client's protocol version
                client_version = params.get("protocolVersion", "2024-11-05")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": client_version,
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "lightrag-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "initialized" or method == "notifications/initialized":
                # Client confirms initialization (notification - no response needed)
                log("Client confirmed initialization")
                return None  # No response needed for notification

            elif method == "tools/list":
                log("Handling tools/list request")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "lightrag_insert",
                                "description": "Insert text into LightRAG knowledge base",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string",
                                            "description": "Text to insert"
                                        }
                                    },
                                    "required": ["text"]
                                }
                            },
                            {
                                "name": "lightrag_query",
                                "description": "Query LightRAG knowledge base. Use this tool when encountering calibre-related questions, issues, or when you need information about calibre (EDA tool by Siemens). The knowledge base contains calibre documentation and troubleshooting information.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Query text"
                                        },
                                        "mode": {
                                            "type": "string",
                                            "enum": ["local", "global", "hybrid", "naive"],
                                            "description": "Query mode",
                                            "default": "hybrid"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        ]
                    }
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                log(f"Handling tools/call: tool={tool_name}")

                if tool_name == "lightrag_insert":
                    result = await self.insert_text(arguments.get("text", ""))
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }

                elif tool_name == "lightrag_query":
                    query = arguments.get("query", "")
                    mode = arguments.get("mode", "hybrid")
                    result = await self.query_kb(query, mode)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }

                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }

            else:
                log(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }

        except Exception as e:
            log(f"Error handling request: {e}")
            import traceback
            log(traceback.format_exc())
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def insert_text(self, text: str) -> str:
        """Insert text into LightRAG"""
        try:
            log(f"Inserting text: {len(text)} chars")
            response = await self.client.post(
                f"{LIGHTRAG_API_BASE}/documents/text",
                json={"text": text}
            )
            response.raise_for_status()
            return f"Successfully inserted {len(text)} characters"
        except Exception as e:
            log(f"Error inserting: {e}")
            return f"Error: {str(e)}"

    async def query_kb(self, query: str, mode: str = "hybrid") -> str:
        """Query LightRAG knowledge base"""
        try:
            # Fix surrogate characters in query
            if isinstance(query, str):
                query = query.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')

            log(f"Querying: query='{query}', mode={mode}")
            response = await self.client.post(
                f"{LIGHTRAG_API_BASE}/query",
                json={"query": query, "mode": mode}
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", "No response")

            # Ensure result is properly encoded
            if isinstance(result, str):
                result = result.encode('utf-8', errors='replace').decode('utf-8')

            return result
        except Exception as e:
            log(f"Error querying: {e}")
            return f"Error: {str(e)}"

    async def run(self):
        """Run MCP server on stdin/stdout"""
        log("Server ready, waiting for requests...")
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    log("EOF received, shutting down")
                    break

                log(f"Received line: {line.strip()}")
                request = json.loads(line)
                response = await self.handle_request(request)

                if response is not None:
                    output = json.dumps(response)
                    log(f"Sending: {output}")
                    print(output, flush=True)

            except json.JSONDecodeError as e:
                log(f"JSON decode error: {e}")
                continue
            except Exception as e:
                log(f"Unexpected error: {e}")
                import traceback
                log(traceback.format_exc())


async def main():
    server = LightRAGMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server interrupted")
    except Exception as e:
        log(f"Fatal error: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)

