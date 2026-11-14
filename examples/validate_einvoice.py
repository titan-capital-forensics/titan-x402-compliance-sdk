"""
Example: E-Invoice Validation with Titan x402 SDK
"""

from titan_x402_client import TitanX402Client

# Sample UBL 2.1 invoice XML (simplified)
SAMPLE_INVOICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0</cbc:CustomizationID>
  <cbc:ID>INV-2024-001</cbc:ID>
  <cbc:IssueDate>2024-01-15</cbc:IssueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PartyIdentification>
        <cbc:ID schemeID="CRN">1234567890</cbc:ID>
      </cac:PartyIdentification>
      <cac:PartyName>
        <cbc:Name>Supplier Company Ltd</cbc:Name>
      </cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>King Fahd Road</cbc:StreetName>
        <cbc:CityName>Riyadh</cbc:CityName>
        <cbc:PostalZone>12211</cbc:PostalZone>
        <cac:Country>
          <cbc:IdentificationCode>SA</cbc:IdentificationCode>
        </cac:Country>
      </cac:PostalAddress>
      <cac:PartyTaxScheme>
        <cbc:CompanyID>300000000000003</cbc:CompanyID>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyIdentification>
        <cbc:ID schemeID="CRN">0987654321</cbc:ID>
      </cac:PartyIdentification>
      <cac:PartyName>
        <cbc:Name>Customer Company Ltd</cbc:Name>
      </cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>Olaya Street</cbc:StreetName>
        <cbc:CityName>Riyadh</cbc:CityName>
        <cbc:PostalZone>12212</cbc:PostalZone>
        <cac:Country>
          <cbc:IdentificationCode>SA</cbc:IdentificationCode>
        </cac:Country>
      </cac:PostalAddress>
      <cac:PartyTaxScheme>
        <cbc:CompanyID>300000000000004</cbc:CompanyID>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingCustomerParty>
  <cac:TaxTotal>
    <cbc:TaxAmount currencyID="SAR">150.00</cbc:TaxAmount>
    <cac:TaxSubtotal>
      <cbc:TaxableAmount currencyID="SAR">1000.00</cbc:TaxableAmount>
      <cbc:TaxAmount currencyID="SAR">150.00</cbc:TaxAmount>
      <cac:TaxCategory>
        <cbc:ID>S</cbc:ID>
        <cbc:Percent>15.0</cbc:Percent>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:TaxCategory>
    </cac:TaxSubtotal>
  </cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="SAR">1000.00</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="SAR">1000.00</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="SAR">1150.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="SAR">1150.00</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:ID>1</cbc:ID>
    <cbc:InvoicedQuantity unitCode="EA">10</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="SAR">1000.00</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Name>Professional Services</cbc:Name>
      <cac:ClassifiedTaxCategory>
        <cbc:ID>S</cbc:ID>
        <cbc:Percent>15.0</cbc:Percent>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="SAR">100.00</cbc:PriceAmount>
    </cac:Price>
  </cac:InvoiceLine>
</Invoice>"""


def main():
    # Initialize client with your wallet credentials
    # In production, load these from environment variables or secure storage
    client = TitanX402Client(
        wallet_address="0xYourWalletAddress",
        private_key="0xYourPrivateKey"
    )
    
    print("=== Titan x402 E-Invoice Validation Example ===\n")
    
    # Get x402 configuration
    print("1. Fetching x402 configuration...")
    config = client.get_x402_config("einvoice")
    print(f"   Gateway: {config.get('description', 'E-Invoice Validator')}")
    print(f"   Price: ${config.get('price', '0.005')}/call")
    print(f"   Network: {config.get('network', 'base')}\n")
    
    # Validate invoice
    print("2. Validating e-invoice (UBL-Peppol, Saudi Arabia)...")
    try:
        result = client.validate_einvoice(
            invoice_xml=SAMPLE_INVOICE_XML,
            standard="ubl-peppol",
            country="SA"
        )
        
        print(f"   Valid: {result.get('valid', False)}")
        print(f"   Standard: {result.get('standard', 'N/A')}")
        print(f"   Country: {result.get('country', 'N/A')}")
        
        if result.get('errors'):
            print("   Errors:")
            for err in result['errors']:
                print(f"     - [{err['code']}] {err['message']}")
        
        if result.get('warnings'):
            print("   Warnings:")
            for warn in result['warnings']:
                print(f"     - [{warn['code']}] {warn['message']}")
        
        if result.get('attestation'):
            print(f"   Attestation: {result['attestation']['sha256'][:16]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()