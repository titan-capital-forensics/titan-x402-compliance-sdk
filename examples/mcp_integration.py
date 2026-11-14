"""
Example: MCP Server Integration with Titan x402 SDK
"""

from titan_x402_client import TitanX402Client


def main():
    # Initialize client with your wallet credentials
    client = TitanX402Client(
        wallet_address="0xYourWalletAddress",
        private_key="0xYourPrivateKey"
    )
    
    print("=== Titan x402 MCP Server Integration Example ===\n")
    
    # Call MCP server - list available tools
    print("1. Listing MCP tools...")
    try:
        result = client.call_mcp("tools/list", {})
        print(f"   Tools available: {len(result.get('result', {}).get('tools', []))}")
        for tool in result.get('result', {}).get('tools', []):
            print(f"     - {tool.get('name')}: {tool.get('description')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Call MCP server - call a specific tool (statutory gate)
    print("\n2. Calling statutory gate tool...")
    try:
        result = client.call_mcp("tools/call", {
            "name": "statutory_gate_validate",
            "arguments": {
                "portal": "cbam",
                "data": {
                    "cn_code": "72081000",
                    "country_of_origin": "CN",
                    "quantity_tonnes": 100,
                    "embedded_emissions": 1.85
                }
            }
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()