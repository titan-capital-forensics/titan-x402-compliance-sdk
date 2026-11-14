/**
 * Example: MCP Server Integration with Titan x402 SDK (TypeScript)
 */

import { TitanX402Client } from '../node/titan-x402-client';

async function main() {
  // Initialize client with your wallet credentials
  const client = new TitanX402Client(
    '0xYourWalletAddress',
    '0xYourPrivateKey'
  );

  console.log('=== Titan x402 MCP Server Integration Example ===\n');

  // Call MCP server - list available tools
  console.log('1. Listing MCP tools...');
  try {
    const result = await client.callMcp('tools/list', {});
    const tools = result?.result?.tools || [];
    console.log(`   Tools available: ${tools.length}`);
    for (const tool of tools) {
      console.log(`     - ${tool.name}: ${tool.description}`);
    }
  } catch (error) {
    console.log(`   Error: ${error}`);
  }

  // Call MCP server - call a specific tool (statutory gate)
  console.log('\n2. Calling statutory gate tool...');
  try {
    const result = await client.callMcp('tools/call', {
      name: 'statutory_gate_validate',
      arguments: {
        portal: 'cbam',
        data: {
          cn_code: '72081000',
          country_of_origin: 'CN',
          quantity_tonnes: 100,
          embedded_emissions: 1.85,
        },
      },
    });
    console.log(`   Result: ${JSON.stringify(result, null, 2)}`);
  } catch (error) {
    console.log(`   Error: ${error}`);
  }

  console.log('\n=== Example Complete ===');
}

main().catch(console.error);