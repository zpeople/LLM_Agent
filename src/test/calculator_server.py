from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

@mcp.tool()
def calculator_tool(base: float, exponent: float) -> float:
    """Raise base to the power of exponent (floats ok)"""
    logger.info("calc success")
    return base ** exponent

# 启动 MCP 服务器并注册工具
if __name__ == "__main__":
    mcp.run(transport="stdio")
    