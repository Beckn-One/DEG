# Energy Registries

## Overview

Authoritative, machine-readable repositories holding critical information that serves as the root of trust in the energy ecosystem. Registries provide standardized, cryptographically verifiable access to foundational data that credentials and transactions depend upon. Registries can be public or private. 

## Why Registries Matter

Much of the information needed to establish trust in energy transactions is held by institutions—certification bodies, utilities, regulators, financial institutions—often in siloed databases or paper records. For decentralized energy markets to function efficiently, this information must be accessible in a machine-readable, cryptographically verifiable manner through standardized APIs.

## Types of Registry Information

### Certification and Compliance
- **Certified manufacturers**: Lists of approved solar panel vendors, inverter manufacturers, battery suppliers
- **Accredited certification bodies**: Entities authorized to issue green energy certificates
- **Standards compliance**: Equipment meeting IEC, UL, or BIS standards
- **Revoked licenses**: Operators whose certifications have been withdrawn

### Network Participants
- **Registered ERAs**: Global directory of Energy Resource Addresses
- **Public keys**: Cryptographic keys of all participating entities for signature verification
- **Participant profiles**: BAP/BPP network participant information
- **Service endpoints**: URLs for API discovery and communication

### Authorizations and Approvals
- **Grid interconnection approvals**: Approved DER installations with export limits
- **Operating licenses**: Valid CPO licenses, ESCO registrations
- **Subsidy program eligibility**: Lists of participants eligible for government schemes
- **Payment gateway approvals**: Authorized payment processors

### Regulatory and Tariff Information
- **Tariff schedules**: Official electricity tariffs by region and consumer category
- **Renewable Purchase Obligations (RPO)**: State-wise renewable energy mandates
- **Wheeling charges**: Transmission and distribution network usage fees
- **Policy documents**: Machine-readable versions of regulatory frameworks

## Examples

### Certified Solar Panel Manufacturer Registry
**Maintained by**: Bureau of Indian Standards (BIS)
**Purpose**: List of approved solar panel vendors meeting quality standards
**Access**: Public API

```json
{
  "registryId": "bis-solar-manufacturers-2024",
  "entries": [
    {
      "manufacturerId": "MNFR-2024-001",
      "name": "ABC Solar Industries",
      "certificationNumber": "BIS-R-12345",
      "validFrom": "2024-01-01",
      "validUntil": "2026-12-31",
      "products": ["Monocrystalline 550W", "Bifacial 600W"],
      "certificationStatus": "valid"
    }
  ]
}
```

### Grid Interconnection Approval Registry
**Maintained by**: State utilities
**Purpose**: Record of approved DER installations with export limits
**Access**: Authenticated API

```json
{
  "registryId": "uppcl-interconnection-approvals",
  "entries": [
    {
      "approvalId": "IC-2024-UPPCL-5678",
      "era": "household-solar-001.uppcl.prosumer",
      "installedCapacity": "5kW",
      "exportLimit": "5kW",
      "meterType": "Bidirectional Smart Meter",
      "netMeteringEnabled": true,
      "approvalDate": "2024-03-15",
      "validUntil": "2049-03-15"
    }
  ]
}
```

### Public Key Registry
**Maintained by**: DeDi.global or network registry
**Purpose**: Public keys of network participants for signature verification
**Access**: Public API

```json
{
  "registryId": "deg-participant-keys",
  "entries": [
    {
      "participantId": "ecopower-charging.bpp.example.com",
      "publicKey": {
        "type": "Ed25519VerificationKey2020",
        "publicKeyMultibase": "z6MkpT..."
      },
      "registeredDate": "2024-01-10",
      "status": "active"
    }
  ]
}
```
## Summary

Energy Registries provide the authoritative, machine-readable foundation upon which trust, credentials, and transactions are built in the India Energy Stack. By making critical information—certified manufacturers, approved installations, participant keys, tariff schedules, subsidy eligibility—accessible through standardized, cryptographically verifiable APIs, registries enable decentralized energy markets to operate with the same level of trust as centralized systems, but without centralized control.
