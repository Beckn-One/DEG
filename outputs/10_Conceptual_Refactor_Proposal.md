# Conceptual Refactor Proposal: EnergyOffer & EnergyContract Architecture

**Version:** 2.0  
**Date:** December 2024  
**Status:** Conceptual Proposal (Revised)

---

## Executive Summary

This document proposes a bold architectural refactoring centered on **EnergyOffer** and **EnergyContract** with telescoping design (simple shells, growing optional complexity). The refactor enables:

1. **EnergyOffer as core Beckn primitive**: Goes in `offerAttributes` slot, represents willingness to assume roles in contracts
2. **EnergyContract as computational agreement**: Defines roles, revenue flows, and quality metrics as functions of external signals
3. **Role-based participation**: Contracts have open roles (buyer/seller/trader) that participants fill
4. **Contract confirmation**: When all roles filled and input connections established
5. **EnergyIntent as optional optimization tool**: Used by actors/algorithms to select contracts, but not part of Beckn schema
6. **Fraud-resistant contracts**: Integration with Decentralized Directory Protocol (DeDi) for integrity, validity, and authenticity verification

**Key Innovation**: 
- **EnergyOffer** is the core Beckn primitive—a bouquet of contract participation opportunities with open roles
- **EnergyContract** is a **computational agreement** that specifies roles, revenue flows, and quality metrics as functions of external signals (prices, frequency, AGC setpoints) and telemetry
- **EnergyIntent** is optional—an expression of actor objectives used to select contracts, but not necessarily in Beckn schema
- **Role-based model**: CPOs publish contracts assuming seller role; EV users downselect and assume buyer role; contracts confirmed when all roles filled

---

## 1. Design Principles

### 1.1 Telescoping Design

**Principle**: Start with minimal required properties, add optional nested structures for complexity.

**Example**:
```json
// Shell (minimal)
{
  "@type": "EnergyIntent",
  "intentType": "BID_CURVE",
  "participantEra": "ev-battery-001"
}

// With depth (optional)
{
  "@type": "EnergyIntent",
  "intentType": "BID_CURVE",
  "participantEra": "ev-battery-001",
  "bidCurve": { /* nested */ },
  "objectives": { /* nested */ },
  "constraints": { /* nested */ }
}
```

### 1.2 Multi-Tenant Pattern

**Principle**: Single schema pattern works across EV charging, P2P trading, VPP coordination, demand flexibility, etc.

**Example**: Same `EnergyIntent` structure used for:
- EV charging bid curve
- Solar generation offer curve
- Service request (kWh needed along route)
- Tariff structure

### 1.3 Contract as Computation

**Principle**: Contracts specify **how to compute** billing, not just **what to bill**.

**Example**: Instead of fixed prices, contracts contain:
- Input signal IDs (meter readings, prices, states)
- Transformation logic (formulas, rules)
- Output: net-zero billing flows

### 1.4 Intent as Policy

**Principle**: Intent represents the **policy** or **action** to be taken based on external factors, not the desired outcomes (objectives).

**Key Distinction**:
- **Intent**: Policy/action (e.g., "charge at 11 kW if price ≤ ₹0.08/kWh")
- **Objective**: Desired outcome (e.g., "charge 20 kWh by 6 PM, minimize cost")
- **Relationship**: Optimization engines derive intents from objectives/constraints

**Types**:
- `OFFER_CURVE`: Price/power pairs (positive = grid injection, negative = withdrawal from grid)
- `SERVICE_REQUEST`: kWh needed, location constraints, time windows
- `TARIFF`: Pricing structure (time-of-day, tiered, etc.)

---

## 2. Core Abstract Schemas

### 2.1 EnergyOffer (Core Beckn Primitive)

**Purpose**: Represents willingness to assume a role in an EnergyContract. This is the **core Beckn primitive** that goes in `offerAttributes` slot.

**Key Concept**: 
- **EnergyOffer** is a bouquet of contract participation opportunities
- Each offer references a contract and specifies an **open role** (buyer/seller/trader)
- Participants select offers to assume roles in contracts
- Offers are published by providers (e.g., CPOs assume seller role)

**Shell (Minimal)**:
```json
{
  "@context": "https://deg.energy/schema/EnergyOffer/v1/context.jsonld",
  "@type": "EnergyOffer",
  "offerId": "offer-ev-charging-001",
  "contractId": "contract-walk-in-001",
  "providerId": "bpp.cpo.example.com",
  "providerUri": "https://bpp.cpo.example.com",
  "openRole": "BUYER"
}
```

**Telescoping Structure**:
```yaml
EnergyOffer:
  type: object
  required: [offerId, contractId, providerId, providerUri, openRole]
  properties:
    # Core (always present)
    offerId: string
    contractId: string  # Reference to EnergyContract
    providerId: string  # BPP ID of contract provider
    providerUri: string  # BPP URI of contract provider
    openRole: enum [BUYER, SELLER, TRADER]  # Role available in contract
    
    # Optional extensions (telescoping)
    expectedInputs: array[InputSpec]  # Expected inputs from role (e.g., accept/reject, offer curve)
    contractSummary: ContractSummary  # Brief summary of contract terms
    credentials: EnergyCredentials  # Required credentials for role
```

**Where Used**:
- `offerAttributes` in Beckn `Offer` objects
- Published in catalogues by providers (CPOs, aggregators, etc.)
- Selected by participants (EV users, prosumers, etc.)

---

### 2.2 EnergyContract (Core Abstract Schema)

**Purpose**: Computational agreement that defines roles, revenue flows, and quality metrics as functions of external signals and telemetry.

**Key Concept**: 
- Contracts specify **roles** (buyer, seller, trader) that need to be filled
- Contracts define **revenue flows** and **quality metrics** as functions of:
  - External signals (prices, frequency, AGC setpoints)
  - Telemetry (meter readings, charge data records)
- Contracts are **confirmed** when all roles are filled and input connections established

**Shell (Minimal)**:
```json
{
  "@context": "https://deg.energy/schema/EnergyContract/v1/context.jsonld",
  "@type": "EnergyContract",
  "contractId": "contract-walk-in-001",
  "roles": [
    { "role": "SELLER", "filledBy": "bpp.cpo.example.com", "filled": true },
    { "role": "BUYER", "filledBy": null, "filled": false }
  ],
  "status": "PENDING",  // PENDING, ACTIVE, COMPLETED, TERMINATED
  "createdAt": "2024-12-15T14:00:00Z"
}
```

**Telescoping Structure**:
```yaml
EnergyContract:
  type: object
  required: [contractId, roles, status, createdAt]
  properties:
    # Core (always present)
    contractId: string
    roles: array[ContractRole]  # Roles in contract (buyer, seller, trader)
    status: enum [PENDING, ACTIVE, COMPLETED, TERMINATED]
    createdAt: date-time
    
    # Input parameters (telescoping)
    inputParameters: array[InputParameter]  # Parameters from each role (e.g., price, offer curve)
    
    # Input signals (telescoping)
    inputSignals: array[InputSignal]  # External signals (prices, frequency, AGC setpoints)
    
    # Telemetry sources (telescoping)
    telemetrySources: array[TelemetrySource]  # Sources for fulfillment data (CDR, meter readings)
    
    # Transformation logic (telescoping)
    revenueFlows: RevenueFlowLogic  # Revenue flows as function of inputs/telemetry
    qualityMetrics: QualityMetricLogic  # Quality metrics (if not in revenue flows)
    
    # Optional extensions (telescoping)
    credentials: EnergyCredentials  # Required credentials
    verification: ContractVerification  # DeDi protocol verification data
```

**Contract Confirmation**: Contract moves from `PENDING` to `ACTIVE` when:
1. All roles are filled
2. All required input parameters provided
3. All input signal connections established
4. All telemetry sources connected

---

### 2.3 EnergyIntent (Optional - Not in Beckn Schema)

**Purpose**: Expression of actor objectives used to select contracts. **Not part of Beckn schema**—used by actors/algorithms for optimization.

**Key Concept**: 
- **EnergyIntent** represents what an actor wants to achieve (objectives)
- Actors use intents to **select a set of contracts** to participate in
- Optimization algorithms match intents to available offers/contracts
- Intent is **optional**—actors can select contracts directly without explicit intent

**Example**:
```json
{
  "intentId": "intent-ev-001",
  "actorEra": "ev-battery-001",
  "objectives": {
    "targetChargeKWh": 20,
    "deadline": "2024-12-15T18:00:00Z",
    "maxPricePerKWh": 0.12,
    "preferredSource": "SOLAR"
  },
  "constraints": {
    "location": { "lat": 12.9716, "lon": 77.5946, "radiusMeters": 10000 },
    "timeWindow": { "start": "2024-12-15T14:00:00Z", "end": "2024-12-15T18:00:00Z" }
  }
}
```

**Usage**:
- Used by optimization engines to select contracts
- Not transmitted in Beckn messages
- Internal to actors/applications

---


**Contract Verification Structure**:
```yaml
ContractVerification:
  type: object
  description: DeDi protocol verification data for contract integrity, validity, and authenticity
  properties:
    integrity:
      type: object
      properties:
        hash: string  # Cryptographic hash of contract
        algorithm: enum [SHA256, SHA512, BLAKE2B]
        signedBy: string  # ERA of signer
        signature: string  # Digital signature
        publicKeyEndpoint: string  # DeDi endpoint for public key lookup
    validity:
      type: object
      properties:
        revocationCheckEndpoint: string  # DeDi endpoint for revocation list
        expirationTime: date-time  # Contract expiration
        lastVerifiedAt: date-time  # Last validity check timestamp
    authenticity:
      type: object
      properties:
        participantVerifications: array[ParticipantVerification]
        membershipCheckEndpoints: array[string]  # DeDi endpoints for membership verification

ParticipantVerification:
  type: object
  properties:
    era: string
    publicKeyId: string
    namespace: string  # DeDi namespace
    verificationEndpoint: string  # DeDi lookup endpoint
    verifiedAt: date-time
```

---

## 3. Contract Role and Input Definitions

### 3.1 ContractRole

**Purpose**: Define roles in a contract that need to be filled.

**Structure**:
```json
{
  "role": "BUYER",
  "filledBy": null,  // ERA or BPP ID when filled
  "filled": false,
  "requiredInputs": [
    {
      "inputName": "accept",
      "inputType": "BOOLEAN",
      "description": "Accept or reject the contract"
    }
  ]
}
```

**Role Types**:
- `BUYER`: Energy consumer (e.g., EV user)
- `SELLER`: Energy provider (e.g., CPO, prosumer)
- `TRADER`: Market intermediary (e.g., aggregator, market clearing agent)

---

### 3.2 InputParameter

**Purpose**: Parameters provided by each role when filling the contract.

**Structure**:
```json
{
  "role": "SELLER",
  "parameters": {
    "price": 0.12,
    "startTime": "2024-12-15T14:00:00Z",
    "gracePeriod": "PT15M",
    "powerRating": 50.0
  }
}
```

**Example for Buyer with Offer Curve**:
```json
{
  "role": "BUYER",
  "parameters": {
    "offerCurve": [
      { "price": 0.08, "powerKW": -11 },
      { "price": 0.10, "powerKW": -5 },
      { "price": 0.12, "powerKW": 0 }
    ]
  }
}
```

---

### 3.3 RevenueFlowLogic

**Purpose**: Define revenue flows as functions of inputs, signals, and telemetry.

**Structure**:
```json
{
  "revenueFlows": [
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * price",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.chargeDataRecords[].energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.seller.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * price - waitTimePenalty - curtailmentPenalty",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.chargeDataRecords[].energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.seller.price" },
        "waitTimePenalty": {
          "formula": "max(0, (arrivalTime - startTime - gracePeriod) * penaltyRate)",
          "variables": {
            "arrivalTime": { "source": "telemetry", "path": "$.arrivalTime" },
            "startTime": { "source": "inputParameters", "path": "$.seller.startTime" },
            "gracePeriod": { "source": "inputParameters", "path": "$.seller.gracePeriod" },
            "penaltyRate": { "constant": 0.01 }
          }
        },
        "curtailmentPenalty": {
          "formula": "max(0, (requestedPower - actualPower) * curtailmentRate)",
          "variables": {
            "requestedPower": { "source": "inputParameters", "path": "$.buyer.requestedPower" },
            "actualPower": { "source": "telemetry", "path": "$.chargeDataRecords[].power" },
            "curtailmentRate": { "constant": 0.02 }
          }
        }
      }
    }
  ]
}
```

---

### 3.4 QualityMetricLogic

**Purpose**: Define quality of service metrics (if not already in revenue flows as incentives/penalties).

**Structure**:
```json
{
  "qualityMetrics": [
    {
      "metricName": "waitTime",
      "formula": "arrivalTime - startTime",
      "target": "PT5M",
      "penalty": {
        "formula": "max(0, (waitTime - target) * penaltyRate)",
        "appliedTo": "BUYER"
      }
    },
    {
      "metricName": "powerCurtailment",
      "formula": "requestedPower - actualPower",
      "target": 0,
      "penalty": {
        "formula": "max(0, powerCurtailment * curtailmentRate)",
        "appliedTo": "SELLER"
      }
    }
  ]
}
```

---

## 4. Contract Computation Model

### 4.1 Input Signals

**Purpose**: Reference external data sources (meter readings, prices, states).

**Structure**:
```json
{
  "inputSignals": [
    {
      "signalId": "meter-reading-source-001",
      "signalType": "METER_READING",
      "source": {
        "era": "solar-panel-001",
        "meterId": "100200300",
        "endpoint": "https://meter-api.example.com/readings/100200300"
      },
      "format": "IEEE_2030_5",
      "refreshInterval": "PT15M"  // ISO 8601 duration
    },
    {
      "signalId": "clearing-price-001",
      "signalType": "PRICE",
      "source": {
        "era": "market-clearing-agent",
        "endpoint": "https://market.example.com/prices/clearing"
      },
      "format": "JSON",
      "refreshInterval": "PT1H"
    },
    {
      "signalId": "wait-time-001",
      "signalType": "STATE",
      "source": {
        "era": "ev-charging-station-001",
        "endpoint": "https://cpo.example.com/stations/001/wait-time"
      },
      "format": "JSON",
      "refreshInterval": "PT5M"
    }
  ]
}
```

**Signal Types**:
- `METER_READING`: Energy flow measurements
- `PRICE`: Market prices, clearing prices
- `STATE`: Wait times, availability, congestion
- `COMMAND`: Setpoints, offsets

---

### 4.2 Billing Logic

**Purpose**: Transform input signals into net-zero billing flows.

**Structure**:
```json
{
  "billingLogic": {
    "mode": "FORMULA",  // or "RULE_BASED", "SCRIPT"
    "formula": {
      "expression": "energyFlow * clearingPrice + wheelingCharges + platformFee + tax",
      "variables": {
        "energyFlow": {
          "source": "meter-reading-source-001",
          "path": "$.energyFlow",
          "unit": "KWH"
        },
        "clearingPrice": {
          "source": "clearing-price-001",
          "path": "$.price",
          "unit": "CURRENCY_PER_KWH"
        },
        "wheelingCharges": {
          "source": "meter-reading-source-001",
          "path": "$.energyFlow",
          "transform": "multiply",
          "constant": 0.02,
          "unit": "CURRENCY"
        },
        "platformFee": {
          "source": "meter-reading-source-001",
          "path": "$.energyFlow",
          "transform": "multiply",
          "constant": 0.01,
          "unit": "CURRENCY"
        },
        "tax": {
          "source": "meter-reading-source-001",
          "path": "$.energyFlow",
          "transform": "multiply",
          "constant": 0.01,
          "unit": "CURRENCY"
        }
      }
    },
    "revenueFlowRules": [
      {
        "party": { "era": "solar-panel-001", "role": "SELLER" },
        "formula": "energyFlow * clearingPrice",
        "description": "Energy sale"
      },
      {
        "party": { "era": "grid-operator-utility", "role": "GRID_OPERATOR" },
        "formula": "energyFlow * 0.02",
        "description": "Wheeling charges"
      },
      {
        "party": { "era": "aggregator-platform", "role": "AGGREGATOR" },
        "formula": "energyFlow * 0.01",
        "description": "Platform fee"
      },
      {
        "party": { "era": "government-tax", "role": "GOVERNMENT" },
        "formula": "energyFlow * 0.01",
        "description": "Tax (10%)"
      }
    ],
    "netZeroConstraint": true  // Sum of all revenue flows must equal total
  }
}
```

**Computation Modes**:
- `FORMULA`: Mathematical expressions with variables
- `RULE_BASED`: If-then rules
- `SCRIPT`: JavaScript/Python scripts (for complex logic)

**Net-Zero Constraint**: Sum of all revenue flows must equal total contract value (money conserved).

---

### 4.3 Revenue Flows (Computed)

**Purpose**: Output of billing logic computation.

**Structure**:
```json
{
  "revenueFlows": [
    {
      "party": { "era": "solar-panel-001", "role": "SELLER" },
      "amount": 60.0,
      "currency": "INR",
      "description": "Energy sale (10 kWh × ₹6/kWh)",
      "computedAt": "2024-12-15T18:30:00Z",
      "signalSnapshot": {
        "energyFlow": 10.0,
        "clearingPrice": 6.0
      }
    },
    {
      "party": { "era": "grid-operator-utility", "role": "GRID_OPERATOR" },
      "amount": 20.0,
      "currency": "INR",
      "description": "Wheeling charges (10 kWh × ₹2/kWh)",
      "computedAt": "2024-12-15T18:30:00Z",
      "signalSnapshot": {
        "energyFlow": 10.0,
        "wheelingRate": 2.0
      }
    },
    {
      "party": { "era": "aggregator-platform", "role": "AGGREGATOR" },
      "amount": 10.0,
      "currency": "INR",
      "description": "Platform fee (10%)",
      "computedAt": "2024-12-15T18:30:00Z",
      "signalSnapshot": {
        "energyFlow": 10.0,
        "platformFeeRate": 0.01
      }
    },
    {
      "party": { "era": "government-tax", "role": "GOVERNMENT" },
      "amount": 10.0,
      "currency": "INR",
      "description": "Tax (10%)",
      "computedAt": "2024-12-15T18:30:00Z",
      "signalSnapshot": {
        "energyFlow": 10.0,
        "taxRate": 0.01
      }
    }
  ],
  "totalAmount": 100.0,
  "currency": "INR",
  "netZeroVerified": true
}
```

**Computation**: Revenue flows are computed from input signals using billing logic, not stored statically.

---

## 5. Fulfillment Modes

### 5.1 Post-Fulfillment Billing

**Purpose**: Compute billing after fulfillment completes.

**Flow**:
1. Contract formed (with billing logic)
2. Fulfillment occurs (meter readings collected)
3. Billing logic computes revenue flows from final meter readings
4. Settlement occurs

**Example**: P2P energy trade where billing happens after energy delivery.

---

### 5.2 Incremental Billing

**Purpose**: Compute billing incrementally during fulfillment.

**Flow**:
1. Contract formed (with billing logic)
2. Fulfillment occurs (meter readings collected periodically)
3. Billing logic computes revenue flows at each interval
4. Settlement occurs incrementally

**Example**: EV charging session where billing updates every 15 minutes.

**Structure**:
```json
{
  "fulfillmentMode": "INCREMENTAL",
  "billingInterval": "PT15M",  // ISO 8601 duration
  "settlementCycles": [
    {
      "cycleId": "settle-001",
      "startTime": "2024-12-15T14:00:00Z",
      "endTime": "2024-12-15T14:15:00Z",
      "status": "SETTLED",
      "revenueFlows": [ /* computed */ ]
    },
    {
      "cycleId": "settle-002",
      "startTime": "2024-12-15T14:15:00Z",
      "endTime": "2024-12-15T14:30:00Z",
      "status": "PENDING",
      "revenueFlows": [ /* computed */ ]
    }
  ]
}
```

---

## 6. Contract Integrity, Validity, and Authenticity

### 6.1 Decentralized Directory Protocol (DeDi) Integration

**Purpose**: Ensure integrity, validity, and authenticity of contracts and participants using the [Decentralized Directory Protocol](https://github.com/LF-Decentralized-Trust-labs/decentralized-directory-protocol).

**DeDi Capabilities**:
- **Integrity**: Cryptographic tamper-resistance via digital signatures and hash functions
- **Validity**: Real-time revocation lists and expiration checking
- **Authenticity**: Public key directory for verifying participant identities

**Integration Points**:

1. **Participant Verification**:
   ```json
   {
     "participants": [
       {
         "era": "solar-panel-001",
         "role": "SELLER",
         "dediVerification": {
           "namespace": "energy.example.com",
           "publicKeyId": "solar-panel-001",
           "verificationEndpoint": "https://dedi.global/lookup/public_key/solar-panel-001"
         }
       }
     ]
   }
   ```

2. **Contract Integrity**:
   ```json
   {
     "contractId": "contract-001",
     "integrity": {
       "hash": "sha256:abc123...",
       "signature": "ed25519:def456...",
       "signedBy": "solar-panel-001",
       "verificationEndpoint": "https://dedi.global/lookup/public_key/solar-panel-001"
     }
   }
   ```

3. **Credential Validity**:
   ```json
   {
     "credentials": {
       "presentedCredentials": [...],
       "validityCheck": {
         "revocationListEndpoint": "https://dedi.global/lookup/revoke/credential-123",
         "membershipCheck": "https://dedi.global/lookup/membership/energy-provider-registry"
       }
     }
   }
   ```

**DeDi Schema References**:
- `public_key.json`: Public key directory for authenticity verification
- `membership.json`: Membership/affiliation verification
- `revoke.json`: Revocation lists for validity checking

---

### 6.2 Automated Contract Creation Best Practices

**Principles for Fraud-Resistant Contracts**:

1. **Ricardian Contracts**: Human-readable contract text with machine-readable logic
   - Contract terms expressed in natural language
   - Billing logic embedded as executable code
   - Cryptographic hash links text to code

2. **Event Sourcing**: Immutable event log of all contract state changes
   ```json
   {
     "contractId": "contract-001",
     "events": [
       {
         "eventId": "evt-001",
         "eventType": "CONTRACT_CREATED",
         "timestamp": "2024-12-15T14:00:00Z",
         "data": { /* contract creation data */ },
         "signature": "ed25519:..."
       },
       {
         "eventId": "evt-002",
         "eventType": "SETTLEMENT_COMPUTED",
         "timestamp": "2024-12-15T18:30:00Z",
         "data": { /* settlement data */ },
         "signature": "ed25519:..."
       }
     ]
   }
   ```

3. **Cryptographic Verification**:
   - All contract events signed by participants
   - Public keys verified via DeDi protocol
   - Hash chain ensures immutability

4. **State Machine Validation**:
   - Contracts follow defined state transitions
   - Invalid transitions rejected
   - State verified at each step

5. **Net-Zero Constraint Verification**:
   - Automated verification that sum of revenue flows equals total
   - Prevents billing errors and fraud
   - Computed at settlement time

---

### 6.3 Settlement Robustness Patterns

**Patterns for Automated Settlement**:

1. **Multi-Signature Settlement**:
   - All participants must sign settlement computation
   - Prevents unilateral changes
   - Enables dispute resolution

2. **Time-Locked Settlements**:
   - Settlements computed at fixed intervals
   - Participants have time to verify before finalization
   - Enables challenge period

3. **Audit Trail**:
   - Complete history of all computations
   - Input signals, formulas, and outputs recorded
   - Enables post-hoc verification

4. **Dispute Resolution**:
   - Challenge mechanism for incorrect settlements
   - Arbitration via trusted third parties
   - Automated rollback on successful challenge

---

## 7. Use Case Examples

### 7.1 EV Charging (Walk-In Flow)

**Contract Definition** (published by CPO):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-walk-in-001",
  "roles": [
    {
      "role": "SELLER",
      "filledBy": "bpp.cpo.example.com",
      "filled": true,
      "requiredInputs": [
        { "inputName": "price", "inputType": "NUMBER" },
        { "inputName": "startTime", "inputType": "DATE_TIME" },
        { "inputName": "gracePeriod", "inputType": "DURATION" },
        { "inputName": "powerRating", "inputType": "NUMBER" }
      ]
    },
    {
      "role": "BUYER",
      "filledBy": null,
      "filled": false,
      "requiredInputs": [
        { "inputName": "accept", "inputType": "BOOLEAN" }
      ]
    }
  ],
  "status": "PENDING",
  "telemetrySources": [
    {
      "sourceId": "cdr-source",
      "sourceType": "CHARGE_DATA_RECORD",
      "endpoint": "https://cpo.example.com/cdr/contract-walk-in-001",
      "fields": ["arrivalTime", "chargeStartTime", "chargeEndTime", "energyDelivered", "power"]
    }
  ],
  "revenueFlows": [
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * price",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.seller.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * price - waitTimePenalty - curtailmentPenalty",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.seller.price" },
        "waitTimePenalty": {
          "formula": "max(0, (arrivalTime - startTime - gracePeriod) * 0.01)"
        },
        "curtailmentPenalty": {
          "formula": "max(0, (requestedPower - actualPower) * 0.02)"
        }
      }
    }
  ]
}
```

**EnergyOffer** (published in catalogue):
```json
{
  "@type": "EnergyOffer",
  "offerId": "offer-ev-charging-001",
  "contractId": "contract-walk-in-001",
  "providerId": "bpp.cpo.example.com",
  "providerUri": "https://bpp.cpo.example.com",
  "openRole": "BUYER",
  "expectedInputs": [
    { "inputName": "accept", "inputType": "BOOLEAN" }
  ],
  "contractSummary": {
    "description": "Walk-in EV charging at ₹12/kWh",
    "powerRating": "50 kW",
    "gracePeriod": "15 minutes"
  }
}
```

**Contract Confirmation** (when buyer accepts):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-walk-in-001",
  "roles": [
    { "role": "SELLER", "filledBy": "bpp.cpo.example.com", "filled": true },
    { "role": "BUYER", "filledBy": "bap.ev-user-app.com", "filled": true }
  ],
  "inputParameters": {
    "seller": {
      "price": 0.12,
      "startTime": "2024-12-15T14:00:00Z",
      "gracePeriod": "PT15M",
      "powerRating": 50.0
    },
    "buyer": {
      "accept": true
    }
  },
  "status": "ACTIVE"
}
```

**Note**: EnergyIntent (e.g., "charge 20 kWh by 6 PM, minimize cost") is used by EV user's app to select this contract, but is not part of Beckn schema.

---

### 7.2 EV Charging (Demand Flexibility with Offer Curve)

**Contract Definition** (published by Market Clearing Agent):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-demand-flex-001",
  "roles": [
    {
      "role": "BUYER",
      "filledBy": null,
      "filled": false,
      "requiredInputs": [
        { "inputName": "offerCurve", "inputType": "OFFER_CURVE" }
      ]
    },
    {
      "role": "SELLER",
      "filledBy": null,
      "filled": false,
      "requiredInputs": [
        { "inputName": "offerCurve", "inputType": "OFFER_CURVE" }
      ]
    }
  ],
  "status": "PENDING",
  "inputSignals": [
    {
      "signalId": "clearing-price",
      "signalType": "PRICE",
      "source": { "era": "market-clearing-agent" }
    }
  ],
  "telemetrySources": [
    {
      "sourceId": "meter-readings",
      "sourceType": "METER_READING",
      "endpoint": "https://meter-api.example.com/readings"
    }
  ],
  "revenueFlows": [
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * clearingPrice",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "clearingPrice": { "source": "inputSignals", "path": "$.clearing-price.price" }
      }
    },
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * clearingPrice",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "clearingPrice": { "source": "inputSignals", "path": "$.clearing-price.price" }
      }
    }
  ]
}
```

**EnergyOffer** (for buyer role):
```json
{
  "@type": "EnergyOffer",
  "offerId": "offer-demand-flex-buyer-001",
  "contractId": "contract-demand-flex-001",
  "providerId": "bpp.market-clearing-agent.com",
  "providerUri": "https://bpp.market-clearing-agent.com",
  "openRole": "BUYER",
  "expectedInputs": [
    {
      "inputName": "offerCurve",
      "inputType": "OFFER_CURVE",
      "description": "Offer curve with negative powers (desire to charge)"
    }
  ]
}
```

**Contract Confirmation** (when buyer provides offer curve):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-demand-flex-001",
  "roles": [
    { "role": "BUYER", "filledBy": "bap.ev-user-app.com", "filled": true },
    { "role": "SELLER", "filledBy": "bap.solar-prosumer-app.com", "filled": true }
  ],
  "inputParameters": {
    "buyer": {
      "offerCurve": [
        { "price": 0.08, "powerKW": -11 },
        { "price": 0.10, "powerKW": -5 },
        { "price": 0.12, "powerKW": 0 }
      ]
    },
    "seller": {
      "offerCurve": [
        { "price": 0.05, "powerKW": 0 },
        { "price": 0.06, "powerKW": 5 },
        { "price": 0.08, "powerKW": 10 }
      ]
    }
  },
  "status": "ACTIVE"
}
```

**Contract** (after market clearing):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-ev-001",
  "participants": [
    { "era": "ev-battery-001", "role": "BUYER" },
    { "era": "market-clearing-agent", "role": "MARKET_CLEARING_AGENT" }
  ],
  "intentIds": ["intent-ev-001", "intent-solar-001"],
  "inputSignals": [
    {
      "signalId": "clearing-price-001",
      "signalType": "PRICE",
      "source": { "era": "market-clearing-agent" }
    },
    {
      "signalId": "meter-reading-ev-001",
      "signalType": "METER_READING",
      "source": { "era": "ev-battery-001", "meterId": "98765456" }
    }
  ],
  "billingLogic": {
    "mode": "FORMULA",
    "formula": {
      "expression": "energyFlow * clearingPrice",
      "variables": {
        "energyFlow": { "source": "meter-reading-ev-001" },
        "clearingPrice": { "source": "clearing-price-001" }
      }
    },
    "revenueFlowRules": [
      {
        "party": { "era": "market-clearing-agent", "role": "MARKET_CLEARING_AGENT" },
        "formula": "energyFlow * clearingPrice",
        "description": "Energy purchase"
      }
    ]
  },
  "fulfillmentMode": "INCREMENTAL",
  "billingInterval": "PT15M"
}
```

---

### 7.3 P2P Trading (Market-Based)

**Contract Definition** (published by Market Clearing Agent):

**Contract** (after market clearing):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-p2p-001",
  "participants": [
    { "era": "solar-panel-001", "role": "SELLER" },
    { "era": "ev-battery-001", "role": "BUYER" },
    { "era": "grid-operator-utility", "role": "GRID_OPERATOR" },
    { "era": "aggregator-platform", "role": "AGGREGATOR" },
    { "era": "government-tax", "role": "GOVERNMENT" }
  ],
  "intentIds": ["intent-solar-001", "intent-ev-001"],
  "inputSignals": [
    {
      "signalId": "meter-reading-source-001",
      "signalType": "METER_READING",
      "source": { "era": "solar-panel-001", "meterId": "100200300" }
    },
    {
      "signalId": "meter-reading-target-001",
      "signalType": "METER_READING",
      "source": { "era": "ev-battery-001", "meterId": "98765456" }
    },
    {
      "signalId": "clearing-price-001",
      "signalType": "PRICE",
      "source": { "era": "market-clearing-agent" }
    }
  ],
  "billingLogic": {
    "mode": "FORMULA",
    "formula": {
      "expression": "energyFlow * clearingPrice + wheelingCharges + platformFee + tax",
      "variables": {
        "energyFlow": { "source": "meter-reading-source-001", "path": "$.energyFlow" },
        "clearingPrice": { "source": "clearing-price-001", "path": "$.price" },
        "wheelingCharges": { "source": "meter-reading-source-001", "transform": "multiply", "constant": 0.02 },
        "platformFee": { "source": "meter-reading-source-001", "transform": "multiply", "constant": 0.01 },
        "tax": { "source": "meter-reading-source-001", "transform": "multiply", "constant": 0.01 }
      }
    },
    "revenueFlowRules": [
      {
        "party": { "era": "solar-panel-001", "role": "SELLER" },
        "formula": "energyFlow * clearingPrice",
        "description": "Energy sale"
      },
      {
        "party": { "era": "grid-operator-utility", "role": "GRID_OPERATOR" },
        "formula": "energyFlow * 0.02",
        "description": "Wheeling charges"
      },
      {
        "party": { "era": "aggregator-platform", "role": "AGGREGATOR" },
        "formula": "energyFlow * 0.01",
        "description": "Platform fee"
      },
      {
        "party": { "era": "government-tax", "role": "GOVERNMENT" },
        "formula": "energyFlow * 0.01",
        "description": "Tax (10%)"
      }
    ],
    "netZeroConstraint": true
  },
  "fulfillmentMode": "POST_FULFILLMENT"
}
```

---

### 7.4 Service Request (EV Charging Along Route)

**Contract Definition** (published by CPO):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-route-001",
  "participants": [
    { "era": "ev-battery-001", "role": "BUYER" },
    { "era": "cpo-station-001", "role": "SELLER" }
  ],
  "intentIds": ["intent-route-001"],
  "inputSignals": [
    {
      "signalId": "wait-time-001",
      "signalType": "STATE",
      "source": { "era": "cpo-station-001" }
    },
    {
      "signalId": "meter-reading-001",
      "signalType": "METER_READING",
      "source": { "era": "cpo-station-001" }
    }
  ],
  "billingLogic": {
    "mode": "FORMULA",
    "formula": {
      "expression": "energyFlow * pricePerKWh",
      "variables": {
        "energyFlow": { "source": "meter-reading-001" },
        "pricePerKWh": { "constant": 0.12 }
      }
    },
    "revenueFlowRules": [
      {
        "party": { "era": "cpo-station-001", "role": "SELLER" },
        "formula": "energyFlow * 0.12",
        "description": "Charging service"
      }
    ]
  },
  "fulfillmentMode": "POST_FULFILLMENT"
}
```

---

## 8. Benefits of Refactor

### 8.1 Alignment with Beckn Architecture

**Before**: Intent scattered across different slots, unclear primitives

**After**: Clear Beckn alignment
- **EnergyOffer** goes in `offerAttributes` slot (core Beckn primitive)
- **EnergyContract** defines computational agreements
- **EnergyIntent** is optional optimization tool (not in Beckn schema)

---

### 8.2 Role-Based Participation

**Before**: Unclear how participants join contracts

**After**: Clear role-based model
- Contracts define **open roles** (buyer/seller/trader)
- Participants select **offers** to assume roles
- Contracts confirmed when **all roles filled** and inputs connected

---

### 8.3 Expressivity

**Before**: Static prices and fixed revenue flows
```json
{
  "clearingPrice": 0.075,
  "revenueFlows": [
    { "party": {...}, "amount": 60.0 }
  ]
}
```

**After**: Computational contracts with dynamic billing
```json
{
  "revenueFlows": [
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * price",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.seller.price" }
      }
    }
  ]
}
```

---

### 8.4 Multi-Tenant

**Before**: Different schemas for different use cases
- `EnergyTradeContract` for P2P trading
- `EnergyCoordination` for coordination
- Separate structures for EV charging

**After**: Single schema pattern works across all use cases
- **EnergyOffer** for all offer types
- **EnergyContract** for all contract types
- Works for walk-in charging, demand flexibility, P2P trading, etc.

---

### 8.5 Separation of Concerns

**Before**: Intent, objectives, and contracts mixed together

**After**: Clear separation
- **EnergyIntent**: Optional optimization tool (not in Beckn schema)
- **EnergyOffer**: Core Beckn primitive (in `offerAttributes`)
- **EnergyContract**: Computational agreement with roles
- Actors use intents to select contracts, but intents don't need to be in Beckn messages

---

## 9. Implementation Considerations

### 9.1 Signal Source Reliability

**Challenge**: Input signals must be reliable and accessible.

**Solutions**:
- Signal source endpoints must be authenticated
- Signal refresh intervals must be reasonable
- Fallback values for missing signals
- Signal validation and verification

---

### 9.2 Billing Logic Complexity

**Challenge**: Complex billing logic may be difficult to express in formulas.

**Solutions**:
- Support multiple computation modes (formula, rule-based, script)
- Provide common formula templates
- Allow external computation services
- Validate net-zero constraint

---

### 9.3 DeDi Protocol Integration

**Challenge**: Integrating DeDi protocol for verification without adding complexity.

**Solutions**:
- Optional verification fields (telescoping design)
- Standard DeDi API endpoints for lookups
- Caching verification results
- Fallback mechanisms for offline scenarios

---

### 9.4 Performance

**Challenge**: Computing billing flows from signals may be slower than static prices.

**Solutions**:
- Cache computed results
- Incremental computation
- Batch processing
- Optimize formula evaluation

---

## 10. Next Steps

1. **Review & Refine**: Gather feedback on this proposal
2. **Prototype**: Create prototype schemas and examples
3. **Validate**: Test with real use cases
4. **Migrate**: Plan migration path from current schemas
5. **Document**: Create implementation guides

---

## Appendix: Schema Comparison

### Current vs. Proposed

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Core Primitive** | Scattered in `intent`, `itemAttributes`, `offerAttributes` | **EnergyOffer** in `offerAttributes` slot (core Beckn primitive) |
| **Contract Model** | `EnergyTradeContract` with many optional properties | **EnergyContract** with role-based participation model |
| **Intent** | Mixed with contracts and offers | **Optional** (not in Beckn schema, used for optimization) |
| **Role-Based Participation** | Unclear how participants join | Contracts have **open roles** (buyer/seller/trader) that participants fill |
| **Contract Confirmation** | Unclear when contract is active | When **all roles filled** and input connections established |
| **Billing** | Static revenue flows | Computed from input parameters, signals, and telemetry |
| **Offer Curve Terminology** | "Bid curve" and "offer curve" | Unified "offer curve" (positive = injection, negative = withdrawal) |
| **Multi-Tenant** | Different schemas for different use cases | Single schema pattern for all use cases |
| **Complexity** | Many optional properties at root | Telescoping nested structures |
| **Fraud Prevention** | Limited | DeDi protocol integration for integrity, validity, authenticity |
| **Contract Verification** | Manual | Automated via DeDi public key directory, revocation lists, membership checks |

---

---

## 11. Key Refinements from Initial Proposal

### 11.1 EnergyOffer as Core Beckn Primitive

**Change**: Shifted from `EnergyIntent` as core schema to `EnergyOffer` as core Beckn primitive.

**Rationale**:
- **EnergyOffer** goes in `offerAttributes` slot (aligns with Beckn architecture)
- Offers represent willingness to assume roles in contracts
- CPOs publish contracts and assume seller role; EV users downselect and assume buyer role

**Impact**: 
- `EnergyOffer` is now the core Beckn primitive
- `EnergyIntent` is optional (not in Beckn schema, used for optimization)

---

### 11.2 Role-Based Contract Model

**Change**: Contracts now have **open roles** that need to be filled.

**Rationale**:
- Contracts specify roles (buyer/seller/trader)
- Participants fill roles by selecting offers
- Contracts confirmed when all roles filled and inputs connected

**Impact**: Clear participation model aligned with real-world energy transactions.

---

### 11.3 Contract as Computational Agreement

**Change**: Contracts define revenue flows and quality metrics as functions of inputs, signals, and telemetry.

**Rationale**:
- Revenue flows computed from input parameters (e.g., seller specifies price)
- Telemetry sources provide fulfillment data (e.g., CDR, meter readings)
- External signals provide dynamic pricing (e.g., clearing price, frequency)

**Impact**: Dynamic, signal-driven billing instead of static prices.

---

### 11.4 EnergyIntent as Optional Optimization Tool

**Change**: `EnergyIntent` is now optional and not part of Beckn schema.

**Rationale**:
- Intent represents actor objectives (e.g., "charge 20 kWh by 6 PM")
- Actors/algorithms use intents to select contracts
- Intent is internal to actors, not transmitted in Beckn messages

**Impact**: Cleaner separation between optimization (intent) and transaction (offer/contract).

---

### 11.5 Unified Offer Curve Terminology

**Change**: Eliminated "bid curve" term, unified under "offer curve" with signed power values.

**Rationale**:
- Positive power = grid injection (generation, discharge)
- Negative power = withdrawal from grid (consumption, charging)
- Single term reduces confusion

**Impact**: Simplified terminology and schema.

---

### 11.6 DeDi Protocol Integration

**Change**: Added integration with Decentralized Directory Protocol for contract verification.

**Rationale**:
- **Integrity**: Cryptographic tamper-resistance via digital signatures
- **Validity**: Real-time revocation lists and expiration checking
- **Authenticity**: Public key directory for participant verification

**Impact**: Enhanced contract security and fraud prevention.

---

### 11.7 Fraud-Resistant Contract Patterns

**Change**: Added best practices for automated contract creation and settlement.

**Patterns**:
- Ricardian contracts (human-readable + machine-executable)
- Event sourcing (immutable event log)
- Cryptographic verification (signatures, hash chains)
- State machine validation
- Net-zero constraint verification
- Multi-signature settlement
- Time-locked settlements
- Audit trails

**Impact**: Robust contract execution and settlement.

---

**Status**: Conceptual Proposal (Refined)  
**Next Action**: Review, refine, and prototype

