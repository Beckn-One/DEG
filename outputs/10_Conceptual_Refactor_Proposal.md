# Conceptual Refactor Proposal: Telescoping EnergyIntent & EnergyContract Architecture

**Version:** 1.0  
**Date:** December 2024  
**Status:** Conceptual Proposal

---

## Executive Summary

This document proposes a bold architectural refactoring that elevates **EnergyIntent** and **EnergyContract** to core abstract schemas with telescoping design (simple shells, growing optional complexity). The refactor enables:

1. **Simpler shells**: Core schemas with minimal required properties
2. **Telescoping complexity**: Optional nested structures for advanced use cases
3. **Multi-tenant**: Single schema pattern works across all use cases
4. **Contract-driven billing**: Contracts compute net-zero billing flows from input signals
5. **Intent as policy**: Intents represent actions/policies based on external factors (not objectives)
6. **Fraud-resistant contracts**: Integration with Decentralized Directory Protocol (DeDi) for integrity, validity, and authenticity verification

**Key Innovation**: 
- **EnergyIntent** is a stand-in for **policy**—defining actions taken in response to external factors (e.g., offer curve decides power for a given price, tariff decides price based on power and time of day)
- **EnergyContract** becomes a **computational agreement** that transforms input signals (meter readings, prices, states) into net-zero billing flows, rather than static price lists
- **Objectives** are separate from intents—optimization engines derive intents from objectives/constraints

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

### 2.1 EnergyIntent (Core Abstract Schema)

**Purpose**: Unified representation of energy-related **policy** or **action** to be taken based on external factors.

**Key Concept**: Intent is a **policy** that defines actions in response to external factors:
- **Offer Curve**: Decides power (positive for grid injection, negative for withdrawal) for a given price
- **Tariff**: Decides price based on power and time of day
- **Service Request**: Decides service parameters based on location and time constraints

**Note**: Objectives and constraints are **separate** from intents. Optimization engines derive intents from objectives/constraints.

**Shell (Minimal)**:
```json
{
  "@context": "https://deg.energy/schema/EnergyIntent/v1/context.jsonld",
  "@type": "EnergyIntent",
  "intentId": "intent-ev-001",
  "intentType": "OFFER_CURVE",  // Discriminator
  "participantEra": "ev-battery-001",
  "createdAt": "2024-12-15T10:00:00Z"
}
```

**Telescoping Structure**:
```yaml
EnergyIntent:
  type: object
  required: [intentId, intentType, participantEra, createdAt]
  properties:
    # Core (always present)
    intentId: string
    intentType: enum [OFFER_CURVE, SERVICE_REQUEST, TARIFF]
    participantEra: string  # ERA of intent originator
    createdAt: date-time
    
    # Type-specific data (telescoping)
    offerCurveData: OfferCurveIntent  # When intentType = OFFER_CURVE
    serviceRequestData: ServiceRequestIntent  # When intentType = SERVICE_REQUEST
    tariffData: TariffIntent  # When intentType = TARIFF
    
    # Optional extensions (telescoping)
    spatial: SpatialConstraints  # Location, radius, route (for service requests)
    temporal: TemporalConstraints  # Time windows (for tariffs, service requests)
    credentials: EnergyCredentials  # Required credentials for verification
```

**Where Used**:
- `message.intent` in `discover` requests
- `itemAttributes` when resources express their own intents
- `orderAttributes.intentIds[]` when contracts reference intents

---

### 2.2 EnergyContract (Core Abstract Schema)

**Purpose**: Computational agreement that transforms input signals into net-zero billing flows.

**Shell (Minimal)**:
```json
{
  "@context": "https://deg.energy/schema/EnergyContract/v1/context.jsonld",
  "@type": "EnergyContract",
  "contractId": "contract-001",
  "participants": [
    { "era": "ev-battery-001", "role": "BUYER" },
    { "era": "solar-panel-001", "role": "SELLER" }
  ],
  "intentIds": ["intent-ev-001", "intent-solar-001"],
  "status": "ACTIVE",
  "createdAt": "2024-12-15T14:00:00Z"
}
```

**Telescoping Structure**:
```yaml
EnergyContract:
  type: object
  required: [contractId, participants, intentIds, status, createdAt]
  properties:
    # Core (always present)
    contractId: string
    participants: array[Participant]  # ERAs and roles
    intentIds: array[string]  # References to matched EnergyIntents
    status: enum [PENDING, ACTIVE, COMPLETED, TERMINATED]
    createdAt: date-time
    
    # Input signals (telescoping)
    inputSignals: array[InputSignal]  # Meter readings, prices, states
    
    # Transformation logic (telescoping)
    billingLogic: BillingLogic  # Formulas, rules to compute flows
    
    # Output flows (telescoping)
    revenueFlows: array[RevenueFlow]  # Computed from billingLogic
    
    # Fulfillment tracking (telescoping)
    fulfillmentMode: enum [POST_FULFILLMENT, INCREMENTAL]
    settlementCycles: array[SettlementCycle]
    
    # Optional extensions (telescoping)
    credentials: EnergyCredentials  # Required credentials for verification
    verification: ContractVerification  # DeDi protocol verification data
```

**Key Innovation**: Contracts **compute** billing from signals, rather than storing fixed prices.

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

## 3. Intent Type Definitions

### 3.1 OfferCurveIntent

**Purpose**: Express price/power policy where power is determined by price.

**Policy**: "For a given price, I will inject/withdraw this amount of power from the grid"

**Structure**:
```json
{
  "intentType": "OFFER_CURVE",
  "offerCurveData": {
    "curve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 5 },
      { "price": 0.08, "powerKW": 10 },
      { "price": 0.10, "powerKW": -5 },
      { "price": 0.12, "powerKW": -11 }
    ],
    "constraints": {
      "minPowerKW": -11,
      "maxPowerKW": 10,
      "rampRateKWPerMin": 1.0
    }
  }
}
```

**Semantics**:
- **Positive powerKW**: Grid injection (generation, discharge)
- **Negative powerKW**: Withdrawal from grid (consumption, charging)
- **Zero powerKW**: No participation at that price

**Use Cases**:
- EV charging demand flexibility (negative power)
- Solar generation offers (positive power)
- Battery discharge/charge (both positive and negative)
- Demand reduction bids (negative power)

---

### 3.2 ServiceRequestIntent

**Purpose**: Express service needs (kWh needed, location constraints, time windows).

**Structure**:
```json
{
  "intentType": "SERVICE_REQUEST",
  "serviceRequestData": {
    "requiredKWh": 20,
    "spatial": {
      "type": "ROUTE",
      "route": {
        "waypoints": [
          { "lat": 12.9716, "lon": 77.5946 },
          { "lat": 12.9352, "lon": 77.6245 }
        ],
        "radiusMeters": 5000
      }
    },
    "temporal": {
      "deadline": "2024-12-15T18:00:00Z",
      "maxWaitTimeMinutes": 5
    },
    "preferences": {
      "maxPricePerKWh": 0.12,
      "preferredSource": "SOLAR"
    }
  }
}
```

**Use Cases**:
- EV charging along route
- Mobile energy delivery
- On-demand energy services

---

### 3.3 TariffIntent

**Purpose**: Express pricing structures (time-of-day, tiered, etc.).

**Structure**:
```json
{
  "intentType": "TARIFF",
  "tariffData": {
    "structure": "TIME_OF_DAY",
    "rates": [
      {
        "timeWindow": {
          "start": "00:00",
          "end": "06:00"
        },
        "pricePerKWh": 0.05,
        "currency": "INR"
      },
      {
        "timeWindow": {
          "start": "06:00",
          "end": "18:00"
        },
        "pricePerKWh": 0.10,
        "currency": "INR"
      },
      {
        "timeWindow": {
          "start": "18:00",
          "end": "24:00"
        },
        "pricePerKWh": 0.15,
        "currency": "INR"
      }
    ]
  }
}
```

**Use Cases**:
- Utility tariff publication
- CPO pricing models
- Grid operator pricing signals

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

### 7.1 EV Charging (Demand Flexibility)

**Intent** (Policy: "Charge at different power levels based on price"):
```json
{
  "@type": "EnergyIntent",
  "intentId": "intent-ev-001",
  "intentType": "OFFER_CURVE",
  "participantEra": "ev-battery-001",
  "offerCurveData": {
    "curve": [
      { "price": 0.08, "powerKW": -11 },
      { "price": 0.10, "powerKW": -5 },
      { "price": 0.12, "powerKW": 0 }
    ],
    "constraints": {
      "minPowerKW": -11,
      "maxPowerKW": 0,
      "rampRateKWPerMin": 1.0
    }
  }
}
```

**Note**: Objectives (e.g., "charge 20 kWh by 6 PM") are separate and used by optimization engines to derive this intent.

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

### 7.2 P2P Trading (Market-Based)

**Intent (Solar)** (Policy: "Inject power to grid at different levels based on price"):
```json
{
  "@type": "EnergyIntent",
  "intentId": "intent-solar-001",
  "intentType": "OFFER_CURVE",
  "participantEra": "solar-panel-001",
  "offerCurveData": {
    "curve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 5 },
      { "price": 0.08, "powerKW": 10 }
    ],
    "constraints": {
      "minPowerKW": 0,
      "maxPowerKW": 10,
      "rampRateKWPerMin": 0.5
    }
  }
}
```

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

### 7.3 Service Request (EV Charging Along Route)

**Intent**:
```json
{
  "@type": "EnergyIntent",
  "intentId": "intent-route-001",
  "intentType": "SERVICE_REQUEST",
  "participantEra": "ev-battery-001",
  "serviceRequestData": {
    "requiredKWh": 20,
    "spatial": {
      "type": "ROUTE",
      "route": {
        "waypoints": [
          { "lat": 12.9716, "lon": 77.5946 },
          { "lat": 12.9352, "lon": 77.6245 }
        ],
        "radiusMeters": 5000
      }
    },
    "temporal": {
      "deadline": "2024-12-15T18:00:00Z",
      "maxWaitTimeMinutes": 5
    },
    "preferences": {
      "maxPricePerKWh": 0.12,
      "preferredSource": "SOLAR"
    }
  }
}
```

**Contract**:
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

### 8.1 Simplicity

**Before**: Many optional properties at root level
```json
{
  "bidCurve": [...],
  "objectives": {...},
  "settlement": {...},
  "clearingPrice": 0.075,
  "setpointKW": -8.0,
  "approvedMaxTradeKW": 30,
  // ... many more optional properties
}
```

**After**: Telescoping structure with clear organization
```json
{
  "@type": "EnergyIntent",
  "intentType": "BID_CURVE",
  "bidCurveData": { /* nested */ },
  "objectives": { /* nested */ }
}
```

---

### 8.2 Multi-Tenant

**Before**: Different schemas for different use cases
- `EnergyTradeContract` for P2P trading
- `EnergyCoordination` for coordination
- Separate structures for EV charging

**After**: Single schema pattern works across all use cases
- `EnergyIntent` for all intent types
- `EnergyContract` for all contract types

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
  "billingLogic": {
    "formula": "energyFlow * clearingPrice + ...",
    "revenueFlowRules": [...]
  },
  "inputSignals": [...]
}
```

---

### 8.4 Extensibility

**Before**: Adding new intent types requires schema changes

**After**: New intent types can be added via `intentType` discriminator
```json
{
  "intentType": "NEW_INTENT_TYPE",
  "newIntentTypeData": { /* nested */ }
}
```

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
| **Intent Representation** | Scattered in `intent`, `itemAttributes`, `offerAttributes` | Unified `EnergyIntent` schema as policy |
| **Intent vs. Objectives** | Mixed together | Separated: Intent = policy, Objectives = goals (used to derive intents) |
| **Offer Curve Terminology** | "Bid curve" and "offer curve" | Unified "offer curve" (positive = injection, negative = withdrawal) |
| **Contract Representation** | `EnergyTradeContract` with many optional properties | `EnergyContract` with telescoping structure |
| **Billing** | Static revenue flows | Computed from input signals and billing logic |
| **Intent Types** | Implicit (bid curves, objectives) | Explicit via `intentType` discriminator |
| **Multi-Tenant** | Different schemas for different use cases | Single schema pattern for all use cases |
| **Complexity** | Many optional properties at root | Telescoping nested structures |
| **Fraud Prevention** | Limited | DeDi protocol integration for integrity, validity, authenticity |
| **Contract Verification** | Manual | Automated via DeDi public key directory, revocation lists, membership checks |

---

---

## 11. Key Refinements from Initial Proposal

### 11.1 Intent as Policy (Not Objectives)

**Change**: Clarified that `EnergyIntent` represents **policy/action** based on external factors, not desired outcomes.

**Rationale**:
- Intent: "Charge at 11 kW if price ≤ ₹0.08/kWh" (policy)
- Objective: "Charge 20 kWh by 6 PM, minimize cost" (goal)
- Relationship: Optimization engines derive intents from objectives

**Impact**: Removed nesting of `objectives` and `constraints` from `EnergyIntent` schema.

---

### 11.2 Unified Offer Curve Terminology

**Change**: Eliminated "bid curve" term, unified under "offer curve" with signed power values.

**Rationale**:
- Positive power = grid injection (generation, discharge)
- Negative power = withdrawal from grid (consumption, charging)
- Single term reduces confusion and simplifies schema

**Impact**: Renamed `BidCurveIntent` to `OfferCurveIntent`, removed `direction` field.

---

### 11.3 DeDi Protocol Integration

**Change**: Added integration with Decentralized Directory Protocol for contract verification.

**Rationale**:
- **Integrity**: Cryptographic tamper-resistance via digital signatures
- **Validity**: Real-time revocation lists and expiration checking
- **Authenticity**: Public key directory for participant verification

**Impact**: Added `ContractVerification` schema with DeDi integration points.

---

### 11.4 Fraud-Resistant Contract Patterns

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

**Impact**: Enhanced contract robustness and fraud prevention.

---

### 11.5 Removed Backward Compatibility

**Change**: Removed migration strategy section since we're starting fresh.

**Rationale**: No need to maintain compatibility with existing schemas.

**Impact**: Cleaner proposal focused on optimal design.

---

**Status**: Conceptual Proposal (Refined)  
**Next Action**: Review, refine, and prototype

