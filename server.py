from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Do numbers add karta hai"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Do numbers multiply karta hai"""
    return a * b

@mcp.tool()
def greet(name: str) -> str:
    """Name se greet karta hai"""
    return f"Hello {name}! Kaise ho?"

if __name__ == "__main__":
    mcp.run(transport="stdio")   # ya "streamable-http"
