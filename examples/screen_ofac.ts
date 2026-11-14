/**
 * Example: OFAC SDN & KYT Screening with Titan x402 SDK (TypeScript)
 */

import { TitanX402Client, OfacScreeningRequest } from '../node/titan-x402-client';

async function main() {
  // Initialize client with your wallet credentials
  const client = new TitanX402Client(
    '0xYourWalletAddress',
    '0xYourPrivateKey'
  );

  console.log('=== Titan x402 OFAC SDN & KYT Screening Example ===\n');

  // Get x402 configuration
  console.log('1. Fetching x402 configuration...');
  const config = await client.getX402Config('ofac');
  console.log(`   Gateway: ${config.description || 'OFAC SDN & KYT Screener'}`);
  console.log(`   Price: $${config.price || '0.003'}/call`);
  console.log(`   Network: ${config.network || 'base'}\n`);

  // Screen entity name
  console.log('2. Screening entity name...');
  try {
    const request: OfacScreeningRequest = {
      entity_name: 'Example Entity LLC',
    };

    const result = await client.screenOfacKyt(request);

    console.log(`   Screened: ${result.screened}`);
    console.log(`   Entity: ${result.entity_name || 'N/A'}`);

    if (result.matches && result.matches.length > 0) {
      console.log(`   Matches found: ${result.matches.length}`);
      for (const match of result.matches) {
        console.log(`     - ${match.match_type.toUpperCase()}: ${match.sdn_entry} (confidence: ${match.confidence.toFixed(2)})`);
      }
    } else {
      console.log('   No matches found - clean screening');
    }

    if (result.attestation) {
      console.log(`   Attestation: ${result.attestation.sha256.substring(0, 16)}...`);
    }
  } catch (error) {
    console.log(`   Error: ${error}`);
  }

  console.log('\n3. Screening crypto wallet address...');
  try {
    const request: OfacScreeningRequest = {
      wallet_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    };

    const result = await client.screenOfacKyt(request);

    console.log(`   Screened: ${result.screened}`);
    console.log(`   Wallet: ${result.wallet_address || 'N/A'}`);

    if (result.matches && result.matches.length > 0) {
      console.log(`   Matches found: ${result.matches.length}`);
      for (const match of result.matches) {
        console.log(`     - ${match.match_type.toUpperCase()}: ${match.sdn_entry} (confidence: ${match.confidence.toFixed(2)})`);
      }
    } else {
      console.log('   No matches found - clean screening');
    }
  } catch (error) {
    console.log(`   Error: ${error}`);
  }

  console.log('\n=== Example Complete ===');
}

main().catch(console.error);