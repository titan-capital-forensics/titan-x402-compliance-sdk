/**
 * Titan x402 Compliance SDK - Node.js/TypeScript Client
 * Zero-dependency client for TITAN Capital Forensics x402 Base USDC gateways.
 */

import { createHash } from 'crypto';
import { URL } from 'url';

export interface X402PaymentChallenge {
  x402_version: number;
  accepts: Array<{
    asset: string;
    network: string;
    payTo: string;
    maxAmountRequired: string;
    description?: string;
  }>;
  error?: string;
}

export interface X402PaymentHeader {
  x402_version: number;
  scheme: string;
  network: string;
  payload: {
    to: string;
    value: string;
    asset: string;
    network: string;
    nonce: string;
    payload: Record<string, any>;
    signature: string;
  };
}

export interface EinvoiceValidationRequest {
  invoice_xml: string;
  standard: 'ubl-peppol' | 'uae-pint-ae' | 'de-xrechnung' | 'ksa-zatca-phase2' | 'iso20022-pain001';
  country: string;
}

export interface OfacScreeningRequest {
  entity_name?: string;
  wallet_address?: string;
  transaction_hash?: string;
}

export interface ValidationResult {
  valid: boolean;
  standard: string;
  country: string;
  errors?: Array<{ code: string; message: string; path?: string }>;
  warnings?: Array<{ code: string; message: string }>;
  attestation?: {
    sha256: string;
    timestamp: string;
    validator_version: string;
  };
}

export interface ScreeningResult {
  screened: boolean;
  entity_name?: string;
  wallet_address?: string;
  matches: Array<{
    sdn_entry: string;
    match_type: 'exact' | 'fuzzy' | 'wallet';
    confidence: number;
    source: 'OFAC_SDN' | 'CRYPTO_WALLET';
  }>;
  kyt_analysis?: {
    transaction_hash: string;
    risk_score: number;
    flags: string[];
  };
  attestation?: {
    sha256: string;
    timestamp: string;
    screener_version: string;
  };
}

export class TitanX402Client {
  private readonly EINVOICE_BASE_URL = 'https://x402.titancapitalforensics.com';
  private readonly OFAC_BASE_URL = 'https://ofac-x402.titancapitalforensics.com';
  private readonly MCP_BASE_URL = 'https://mcp.titancapitalforensics.com/mcp';
  
  private readonly walletAddress: string;
  private readonly privateKey: string;
  private readonly timeout: number;

  constructor(walletAddress: string, privateKey: string, timeout: number = 30000) {
    this.walletAddress = walletAddress;
    this.privateKey = privateKey;
    this.timeout = timeout;
  }

  private async makeRequest<T>(
    url: string,
    method: string = 'GET',
    headers: Record<string, string> = {},
    body?: string
  ): Promise<{ status: number; data: T; headers: Record<string, string> }> {
    const requestHeaders = {
      'User-Agent': 'titan-x402-compliance-sdk/1.0.0',
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...headers,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: requestHeaders,
        body,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseHeaders: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      const responseText = await response.text();
      const data = responseText ? JSON.parse(responseText) : {};

      return { status: response.status, data, headers: responseHeaders };
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  private signPayment(payload: Record<string, any>): string {
    // In production, use proper ethereum signing (e.g., ethers.js or viem)
    // This is a placeholder for the signing logic
    const message = JSON.stringify(payload, Object.keys(payload).sort());
    const hash = createHash('sha256');
    hash.update(this.privateKey + message);
    return '0x' + hash.digest('hex');
  }

  async getX402Config(gateway: 'einvoice' | 'ofac' = 'einvoice'): Promise<any> {
    const baseUrl = gateway === 'einvoice' ? this.EINVOICE_BASE_URL : this.OFAC_BASE_URL;
    const url = `${baseUrl}/.well-known/x402.json`;
    const { status, data } = await this.makeRequest(url);
    if (status === 200) {
      return data;
    }
    throw new Error(`Failed to get x402 config: ${JSON.stringify(data)}`);
  }

  async validateEinvoice(request: EinvoiceValidationRequest): Promise<ValidationResult> {
    const url = `${this.EINVOICE_BASE_URL}/v1/validate/einvoice`;
    const body = JSON.stringify(request);

    let { status, data, headers } = await this.makeRequest(url, 'POST', {}, body);

    if (status === 402) {
      const challenge = data as X402PaymentChallenge;
      const paymentHeader = this.createPaymentHeader(challenge, request);
      const newHeaders = { ...headers, 'X-Payment': paymentHeader };
      const retry = await this.makeRequest<ValidationResult>(url, 'POST', newHeaders, body);
      return retry.data;
    }

    return data as ValidationResult;
  }

  async screenOfacKyt(request: OfacScreeningRequest): Promise<ScreeningResult> {
    if (!request.entity_name && !request.wallet_address && !request.transaction_hash) {
      throw new Error('At least one of entity_name, wallet_address, or transaction_hash required');
    }

    const url = `${this.OFAC_BASE_URL}/v1/screen/ofac-kyt`;
    const body = JSON.stringify(request);

    let { status, data, headers } = await this.makeRequest(url, 'POST', {}, body);

    if (status === 402) {
      const challenge = data as X402PaymentChallenge;
      const paymentHeader = this.createPaymentHeader(challenge, request);
      const newHeaders = { ...headers, 'X-Payment': paymentHeader };
      const retry = await this.makeRequest<ScreeningResult>(url, 'POST', newHeaders, body);
      return retry.data;
    }

    return data as ScreeningResult;
  }

  private createPaymentHeader(challenge: X402PaymentChallenge, payload: Record<string, any>): string {
    const usdcAccept = challenge.accepts.find(
      (a) => a.asset === 'USDC' && a.network === 'base'
    );

    if (!usdcAccept) {
      throw new Error('No USDC on Base acceptance found in challenge');
    }

    const paymentPayload = {
      to: usdcAccept.payTo,
      value: usdcAccept.maxAmountRequired,
      asset: 'USDC',
      network: 'base',
      nonce: String(Date.now()),
      payload,
    };

    const signature = this.signPayment(paymentPayload);

    const paymentHeader: X402PaymentHeader = {
      x402_version: 1,
      scheme: 'exact',
      network: 'base',
      payload: {
        ...paymentPayload,
        signature,
      },
    };

    return JSON.stringify(paymentHeader);
  }

  async callMcp(method: string, params: Record<string, any>): Promise<any> {
    const url = this.MCP_BASE_URL;
    const body = JSON.stringify({
      jsonrpc: '2.0',
      method,
      params,
      id: Date.now(),
    });

    const { data } = await this.makeRequest(url, 'POST', {}, body);
    return data;
  }
}

// Convenience functions for simple usage
export async function validateEinvoiceSimple(
  invoiceXml: string,
  standard: EinvoiceValidationRequest['standard'] = 'ubl-peppol',
  country: string = 'SA'
): Promise<{ note: string }> {
  return { note: 'Use TitanX402Client with wallet credentials for actual validation' };
}

export async function screenOfacSimple(entityName: string): Promise<{ note: string }> {
  return { note: 'Use TitanX402Client with wallet credentials for actual screening' };
}

export default TitanX402Client;