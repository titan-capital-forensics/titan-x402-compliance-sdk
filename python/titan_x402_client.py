"""
Titan x402 Compliance SDK - Python Client
Zero-dependency client for TITAN Capital Forensics x402 Base USDC gateways.
"""

import json
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List
from urllib import request, parse, error
from dataclasses import dataclass, asdict


@dataclass
class X402PaymentChallenge:
    """x402 payment challenge response."""
    x402_version: int
    accepts: List[Dict[str, Any]]
    error: Optional[str] = None


@dataclass
class X402PaymentHeader:
    """x402 payment header for authenticated requests."""
    x402_version: int
    scheme: str
    network: str
    payload: Dict[str, Any]


class TitanX402Client:
    """
    Zero-dependency Python client for TITAN x402 gateways.
    
    Gateways:
    - E-Invoice & ISO 20022 Validator: https://x402.titancapitalforensics.com ($0.005/call)
    - OFAC SDN & KYT Screener: https://ofac-x402.titancapitalforensics.com ($0.003/call)
    - MCP Server: https://mcp.titancapitalforensics.com/mcp
    """
    
    EINVOICE_BASE_URL = "https://x402.titancapitalforensics.com"
    OFAC_BASE_URL = "https://ofac-x402.titancapitalforensics.com"
    MCP_BASE_URL = "https://mcp.titancapitalforensics.com/mcp"
    
    def __init__(
        self,
        wallet_address: str,
        private_key: str,
        timeout: int = 30
    ):
        """
        Initialize client with wallet credentials.
        
        Args:
            wallet_address: Ethereum/Base wallet address (0x...)
            private_key: Private key for signing payments (0x...)
            timeout: Request timeout in seconds
        """
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.timeout = timeout
    
    def _make_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None
    ) -> tuple[int, Dict[str, Any], Optional[Dict[str, str]]]:
        """Make HTTP request and return status, response, and response headers."""
        req_headers = {
            "User-Agent": "titan-x402-compliance-sdk/1.0.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if headers:
            req_headers.update(headers)
        
        req = request.Request(url, data=body, headers=req_headers, method=method)
        
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                resp_headers = dict(resp.headers)
                resp_body = resp.read().decode("utf-8")
                return resp.status, json.loads(resp_body) if resp_body else {}, resp_headers
        except error.HTTPError as e:
            resp_headers = dict(e.headers)
            resp_body = e.read().decode("utf-8")
            return e.code, json.loads(resp_body) if resp_body else {}, resp_headers
        except Exception as e:
            return 0, {"error": str(e)}, None
    
    def _sign_payment(self, payload: Dict[str, Any]) -> str:
        """Sign payment payload with private key (simplified - use proper eth_account in production)."""
        # In production, use eth_account.Account.sign_message
        # This is a placeholder for the signing logic
        message = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        # Actual implementation would use: eth_account.Account.from_key(self.private_key).sign_message(message)
        return "0x" + hashlib.sha256((self.private_key + message).encode()).hexdigest()
    
    def get_x402_config(self, gateway: str = "einvoice") -> Dict[str, Any]:
        """Get x402 configuration from gateway."""
        base_url = self.EINVOICE_BASE_URL if gateway == "einvoice" else self.OFAC_BASE_URL
        url = f"{base_url}/.well-known/x402.json"
        status, resp, _ = self._make_request(url)
        if status == 200:
            return resp
        raise Exception(f"Failed to get x402 config: {resp}")
    
    def validate_einvoice(
        self,
        invoice_xml: str,
        standard: str = "ubl-peppol",
        country: str = "SA"
    ) -> Dict[str, Any]:
        """
        Validate e-invoice against ISO 20022 / UBL / ZATCA / Peppol standards.
        
        Args:
            invoice_xml: Invoice XML content
            standard: Validation standard (ubl-peppol, uae-pint-ae, de-xrechnung, ksa-zatca-phase2, iso20022-pain001)
            country: Country code for jurisdiction-specific rules
            
        Returns:
            Validation result with compliance status
        """
        url = f"{self.EINVOICE_BASE_URL}/v1/validate/einvoice"
        payload = {
            "invoice_xml": invoice_xml,
            "standard": standard,
            "country": country
        }
        
        # First request - may return 402
        status, resp, headers = self._make_request(url, "POST", body=json.dumps(payload).encode())
        
        if status == 402:
            # Handle payment challenge
            challenge = X402PaymentChallenge(**resp)
            payment_header = self._create_payment_header(challenge, payload)
            headers_with_payment = {"X-Payment": payment_header}
            status, resp, _ = self._make_request(url, "POST", headers=headers_with_payment, body=json.dumps(payload).encode())
        
        return resp
    
    def screen_ofac_kyt(
        self,
        entity_name: Optional[str] = None,
        wallet_address: Optional[str] = None,
        transaction_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Screen entity or wallet against US Treasury OFAC SDN list and KYT.
        
        Args:
            entity_name: Entity name to screen
            wallet_address: Crypto wallet address to screen
            transaction_hash: Transaction hash for KYT analysis
            
        Returns:
            Screening result with match details
        """
        url = f"{self.OFAC_BASE_URL}/v1/screen/ofac-kyt"
        payload = {}
        if entity_name:
            payload["entity_name"] = entity_name
        if wallet_address:
            payload["wallet_address"] = wallet_address
        if transaction_hash:
            payload["transaction_hash"] = transaction_hash
        
        if not payload:
            raise ValueError("At least one of entity_name, wallet_address, or transaction_hash required")
        
        status, resp, headers = self._make_request(url, "POST", body=json.dumps(payload).encode())
        
        if status == 402:
            challenge = X402PaymentChallenge(**resp)
            payment_header = self._create_payment_header(challenge, payload)
            headers_with_payment = {"X-Payment": payment_header}
            status, resp, _ = self._make_request(url, "POST", headers=headers_with_payment, body=json.dumps(payload).encode())
        
        return resp
    
    def _create_payment_header(self, challenge: X402PaymentChallenge, payload: Dict[str, Any]) -> str:
        """Create x402 payment header from challenge."""
        # Find USDC on Base acceptance
        usdc_accept = None
        for accept in challenge.accepts:
            if accept.get("asset") == "USDC" and accept.get("network") == "base":
                usdc_accept = accept
                break
        
        if not usdc_accept:
            raise Exception("No USDC on Base acceptance found in challenge")
        
        payment_payload = {
            "to": usdc_accept["payTo"],
            "value": str(usdc_accept["maxAmountRequired"]),
            "asset": "USDC",
            "network": "base",
            "nonce": str(int(time.time() * 1000)),
            "payload": payload
        }
        
        signature = self._sign_payment(payment_payload)
        
        payment_header = X402PaymentHeader(
            x402_version=1,
            scheme="exact",
            network="base",
            payload={
                **payment_payload,
                "signature": signature
            }
        )
        
        return json.dumps(asdict(payment_header), separators=(",", ":"))
    
    def call_mcp(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server method."""
        url = f"{self.MCP_BASE_URL}"
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": int(time.time() * 1000)
        }
        status, resp, _ = self._make_request(url, "POST", body=json.dumps(payload).encode())
        return resp


# Convenience functions for simple usage
def validate_einvoice_simple(invoice_xml: str, standard: str = "ubl-peppol", country: str = "SA") -> Dict[str, Any]:
    """Simple e-invoice validation (requires payment setup)."""
    # This would need wallet credentials in real usage
    return {"note": "Use TitanX402Client with wallet credentials for actual validation"}


def screen_ofac_simple(entity_name: str) -> Dict[str, Any]:
    """Simple OFAC screening (requires payment setup)."""
    return {"note": "Use TitanX402Client with wallet credentials for actual screening"}