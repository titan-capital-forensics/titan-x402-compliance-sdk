"""
Example: OFAC SDN & KYT Screening with Titan x402 SDK
"""

from titan_x402_client import TitanX402Client


def main():
    # Initialize client with your wallet credentials
    client = TitanX402Client(
        wallet_address="0xYourWalletAddress",
        private_key="0xYourPrivateKey"
    )
    
    print("=== Titan x402 OFAC SDN & KYT Screening Example ===\n")
    
    # Get x402 configuration
    print("1. Fetching x402 configuration...")
    config = client.get_x402_config("ofac")
    print(f"   Gateway: {config.get('description', 'OFAC SDN & KYT Screener')}")
    print(f"   Price: ${config.get('price', '0.003')}/call")
    print(f"   Network: {config.get('network', 'base')}\n")
    
    # Screen entity name
    print("2. Screening entity name...")
    try:
        result = client.screen_ofac_kyt(entity_name="Example Entity LLC")
        
        print(f"   Screened: {result.get('screened', False)}")
        print(f"   Entity: {result.get('entity_name', 'N/A')}")
        
        matches = result.get('matches', [])
        if matches:
            print(f"   Matches found: {len(matches)}")
            for match in matches:
                print(f"     - {match['match_type'].upper()}: {match['sdn_entry']} (confidence: {match['confidence']:.2f})")
        else:
            print("   No matches found - clean screening")
        
        if result.get('attestation'):
            print(f"   Attestation: {result['attestation']['sha256'][:16]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Screening crypto wallet address...")
    try:
        result = client.screen_ofac_kyt(wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
        
        print(f"   Screened: {result.get('screened', False)}")
        print(f"   Wallet: {result.get('wallet_address', 'N/A')}")
        
        matches = result.get('matches', [])
        if matches:
            print(f"   Matches found: {len(matches)}")
            for match in matches:
                print(f"     - {match['match_type'].upper()}: {match['sdn_entry']} (confidence: {match['confidence']:.2f})")
        else:
            print("   No matches found - clean screening")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()