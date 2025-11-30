# Conceptual Refactor Proposal: EnergyOffer & EnergyContract Architecture

**Version:** 2.0  
**Date:** December 2024  
**Status:** Conceptual Proposal (Revised)

---

## Executive Summary

This document proposes a bold architectural refactoring centered on **EnergyOffer** and **EnergyContract** with telescoping design (simple shells, growing optional complexity). The refactor enables:

1. **EnergyOffer as core Beckn primitive**: Goes in `offerAttributes` slot, represents willingness to assume roles in contracts
2. **EnergyContract as computational agreement**: Defines roles, revenue flows, and quality metrics as functions of external signals
3. **Role-based participation**: Contracts have open roles (buyer/seller/prosumer/market clearing agent/aggregator/grid operator) that participants fill
4. **Contract confirmation**: When all roles filled and input connections established
5. **EnergyIntent only in discover calls**: Used in `discover` calls to tie intent to contract discovery & participation, not part of core Beckn schema
6. **Fraud-resistant contracts**: Integration with Decentralized Directory Protocol (DeDi) for integrity, validity, and authenticity verification

**Key Innovation**: 
- **EnergyOffer** is the core Beckn primitive—a bouquet of contract participation opportunities with open roles
- **EnergyContract** is a **computational agreement** that specifies roles, revenue flows, and quality metrics as functions of external signals (prices, frequency, AGC setpoints) and telemetry
- **EnergyIntent** is used only in `discover` calls to tie intent to contract discovery & participation, not part of core Beckn schema
- **Role-based model**: CPOs publish contracts assuming seller role; EV users downselect and assume buyer role; contracts confirmed when all roles filled

---

## 1. Design Principles

### 1.1 Telescoping Design

**Principle**: Start with minimal required properties, add optional nested structures for complexity.

**Example**:
```json
// Shell (minimal)
{
  "@type": "EnergyOffer",
  "offerId": "offer-ev-charging-001",
  "contractId": "contract-walk-in-001",
  "providerId": "bpp.cpo.example.com",
  "providerUri": "https://bpp.cpo.example.com",
  "openRole": "BUYER"
}

// With depth (optional)
{
  "@type": "EnergyOffer",
  "offerId": "offer-ev-charging-001",
  "contractId": "contract-walk-in-001",
  "providerId": "bpp.cpo.example.com",
  "providerUri": "https://bpp.cpo.example.com",
  "openRole": "BUYER",
  "expectedInputs": [ /* nested */ ],
  "contractSummary": { /* nested */ },
  "credentials": { /* nested */ }
}
```

### 1.2 Multi-Tenant Pattern

**Principle**: Single schema pattern works across EV charging, P2P trading, VPP coordination, demand flexibility, etc.

**Example**: Same `EnergyOffer` and `EnergyContract` structure used for:
- Walk-in EV charging (fixed price)
- Demand flexibility (price-responsive with offer curves)
- P2P trading (market-based with offer curves)
- Service requests (location-based)

### 1.3 Contract as Computation

**Principle**: Contracts specify **how to compute** billing, not just **what to bill**.

**Example**: Instead of fixed prices, contracts contain:
- Input parameters from roles (e.g., price, offer curves)
- External signals (prices, frequency, AGC setpoints)
- Telemetry sources (meter readings, charge data records)
- Transformation logic (formulas, rules)
- Output: net-zero billing flows

### 1.4 EnergyIntent in Discover Calls

**Principle**: EnergyIntent is **only used in discover calls** to tie intent to contract discovery & participation. It is not part of the core Beckn schema.

**Key Distinction**:
- **EnergyIntent**: Expression of actor objectives used in `discover` calls to find matching contracts
- **EnergyOffer**: Core Beckn primitive in `offerAttributes` representing contract participation opportunities
- **EnergyContract**: Computational agreement with roles and revenue flows

**Usage**:
- EnergyIntent appears in `message.intent` of `discover` requests
- Used to match against available EnergyOffers/Contracts
- Not stored in contracts or offers
- Optional—actors can discover contracts directly without explicit intent

---

## 2. Core Abstract Schemas

### 2.1 EnergyOffer (Core Beckn Primitive)

**Purpose**: Represents willingness to assume a role in an EnergyContract. This is the **core Beckn primitive** that goes in `offerAttributes` slot.

**Key Concept**: 
- **EnergyOffer** is a bouquet of contract participation opportunities
- Each offer references a contract and specifies an **open role** (buyer/seller/prosumer/market clearing agent/aggregator/grid operator)
- Participants select offers to assume roles in contracts
- Offers are published by providers (e.g., CPOs assume seller role)
- **EnergyContract** can also slot into `offerAttributes` directly, allowing full contract definition to be included in offers for discovery

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
    openRole: enum [BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR]  # Role available in contract
    
    # Optional extensions (telescoping)
    contract: EnergyContract  # Full contract definition (can be included in offerAttributes)
    expectedInputs: array[InputSpec]  # Expected inputs from role (mirrors expectedRoleInputs from contract)
    contractSummary: ContractSummary  # Brief summary of contract terms (alternative to full contract)
    credentials: EnergyCredentials  # Required credentials for role
```

**Where Used**:
- `offerAttributes` in Beckn `Offer` objects
- Published in catalogues by providers (CPOs, aggregators, etc.)
- Selected by participants (EV users, prosumers, etc.)

**Note**: 
- Either `contract` (full EnergyContract definition) or `contractSummary` can be included in EnergyOffer
- **EnergyContract can also slot directly into `offerAttributes`** (alternative to EnergyOffer)
- Including the full contract allows participants to see all contract terms during discovery without additional lookups

---

### 2.2 EnergyContract (Core Abstract Schema)

**Purpose**: Computational agreement that defines roles, revenue flows, and quality metrics as functions of external signals and telemetry.

**Key Concept**: 
- Contracts specify **roles** (buyer, seller, prosumer, market clearing agent, aggregator, grid operator) that need to be filled
- Each role defines `expectedRoleInputs` (optional) specifying what inputs are expected
- Contracts define **revenue flows** and **quality metrics** as functions of:
  - Input parameters (actual values provided by roles)
  - External signals (prices, frequency, AGC setpoints)
  - Telemetry (meter readings, charge data records)
- Contracts are **confirmed** when all roles are filled and input connections established
- **EnergyContract** can slot into `offerAttributes` directly (in addition to being referenced by EnergyOffer)

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
    roles: array[ContractRole]  # Roles in contract (buyer, seller, prosumer, market clearing agent, aggregator, grid operator) with expectedRoleInputs
    status: enum [PENDING, ACTIVE, COMPLETED, TERMINATED]
    createdAt: date-time
    
    # Input parameters (telescoping) - actual values provided by roles
    inputParameters: object  # Keyed by role name, contains actual values provided
      # Example: { "SELLER": { "price": 0.12, "startTime": "..." }, "BUYER": { "accept": true } }
    
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
2. All expected inputs for each role are provided (values in `inputParameters`)
3. Connections to all trusted signals are established
4. All telemetry sources connected

**Where Used**:
- **Can slot into `offerAttributes` directly** (full contract definition in offers, alternative to EnergyOffer)
- Referenced by `EnergyOffer.contractId` (contract lookup by ID)
- Included in `EnergyOffer.contract` (nested contract definition within EnergyOffer)

**Note**: EnergyContract can be used in two ways:
1. **Directly in `offerAttributes`**: Full contract definition published as an offer
2. **Referenced by EnergyOffer**: EnergyOffer references contract by ID, optionally includes full contract in `contract` field

---

### 2.3 EnergyIntent (Used Only in Discover Calls)

**Purpose**: Expression of actor objectives used **only in `discover` calls** to tie intent to contract discovery & participation. **Not part of core Beckn schema**—appears only in `message.intent` of `discover` requests.

**Key Concept**: 
- **EnergyIntent** represents what an actor wants to achieve (objectives)
- Used in `discover` calls to find matching contracts/offers
- Optimization algorithms match intents to available offers/contracts
- Intent is **optional**—actors can discover contracts directly without explicit intent
- Not stored in contracts, offers, or other Beckn messages

**Example** (in `discover` request):
```json
{
  "context": {
    "action": "discover",
    "domain": "beckn.one:deg:ev-charging:*"
  },
  "message": {
    "intent": {
      "@type": "EnergyIntent",
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
  }
}
```

**Usage**:
- Appears in `message.intent` of `discover` requests
- Used to match against available EnergyOffers/Contracts in `on_discover` responses
- Not stored in contracts or offers
- Optional—actors can discover contracts directly without explicit intent

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

## 3. EnergyContract in offerAttributes

**EnergyContract can slot directly into `offerAttributes`** as an alternative to EnergyOffer. This allows full contract definitions to be published in catalogues without requiring a separate EnergyOffer wrapper.

**Example** (EnergyContract directly in offerAttributes):
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
  "@type": "beckn:Offer",
  "beckn:id": "offer-contract-direct-001",
  "beckn:offerAttributes": {
    "@context": "https://deg.energy/schema/EnergyContract/v1/context.jsonld",
    "@type": "EnergyContract",
    "contractId": "contract-walk-in-001",
    "roles": [
      {
        "role": "SELLER",
        "filledBy": "bpp.cpo.example.com",
        "filled": true,
        "expectedRoleInputs": [
          { "inputName": "price", "inputType": "NUMBER" },
          { "inputName": "startTime", "inputType": "DATE_TIME" }
        ]
      },
      {
        "role": "BUYER",
        "filledBy": null,
        "filled": false,
        "expectedRoleInputs": [
          { "inputName": "accept", "inputType": "BOOLEAN" }
        ]
      }
    ],
    "status": "PENDING",
    "revenueFlows": [ /* ... */ ]
  }
}
```

**When to use EnergyContract vs EnergyOffer in offerAttributes**:
- **EnergyContract directly**: When you want to publish the full contract definition without an offer wrapper
- **EnergyOffer**: When you want to provide offer metadata (providerId, providerUri, contractSummary) along with contract reference or definition

---

## 4. Contract Role and Input Definitions

### 4.1 ContractRole

**Purpose**: Define roles in a contract that need to be filled.

**Structure**:
```json
{
  "role": "BUYER",
  "filledBy": null,  // ERA or BPP ID when filled
  "filled": false,
  "expectedRoleInputs": [  // Optional sub-attribute
    {
      "inputName": "accept",
      "inputType": "BOOLEAN",
      "description": "Accept or reject the contract"
    }
  ]
}
```

**Offer Curves in Expected Role Inputs**:
Offer curves can be specified in `expectedRoleInputs` to allow **inflexible or flexible (price responsive) trading**:
- **Positive power values**: Providing energy to grid (injection/export)
- **Negative power values**: Receiving energy from grid (withdrawal/consumption)

**Offer Curve Structure**:
```json
{
  "offerCurve": {
    "currency": "INR",        // Currency for prices
    "minExport": -11,         // Minimum export (negative = maximum withdrawal)
    "maxExport": 10,           // Maximum export (positive = maximum generation)
    "curve": [                // Array of price/power pairs
      { "price": 0.08, "powerKW": -11 },  // Negative = receiving energy
      { "price": 0.10, "powerKW": -5 },
      { "price": 0.12, "powerKW": 0 },
      { "price": 0.14, "powerKW": 5 },    // Positive = providing energy
      { "price": 0.16, "powerKW": 10 }
    ]
  }
}
```

**Example with Offer Curve in Expected Role Inputs**:
```json
{
  "role": "PROSUMER",
  "filledBy": null,
  "filled": false,
  "expectedRoleInputs": [
    {
      "inputName": "offerCurve",
      "inputType": "OFFER_CURVE",
      "description": "Price-responsive offer curve (negative powers = withdrawal, positive = export)",
      "optional": true
    }
  ]
}
```

**Role Types**:
- `BUYER`: Energy consumer (e.g., EV user)
- `SELLER`: Energy provider (e.g., CPO, prosumer)
- `PROSUMER`: Producer and/or consumer (can be both, used in market clearing contracts)
- `MARKET_CLEARING_AGENT`: Market clearing agent that aggregates bids and clears market
- `AGGREGATOR`: Market intermediary that aggregates resources
- `GRID_OPERATOR`: Grid operator managing grid infrastructure and constraints

---

### 4.2 InputParameters in EnergyContract

**Purpose**: Actual values provided by each role when filling the contract. These correspond to the `expectedRoleInputs` defined in each `ContractRole`.

**Structure**:
`inputParameters` is an object keyed by role name, containing the actual values provided by each role.

**Example** (Inflexible Trading - Fixed Price):
```json
{
  "inputParameters": {
    "SELLER": {
      "price": 0.12,
      "startTime": "2024-12-15T14:00:00Z",
      "gracePeriod": "PT15M",
      "powerRating": 50.0
    },
    "BUYER": {
      "accept": true
    }
  }
}
```

**Example** (Flexible Trading - Price Responsive with Offer Curves):
```json
{
  "inputParameters": {
    "BUYER": {
      "offerCurve": {
        "currency": "INR",
        "minExport": -11,  // Minimum export (negative = maximum withdrawal/charging)
        "maxExport": 0,   // Maximum export (negative = no export, only withdrawal)
        "curve": [
          { "price": 0.08, "powerKW": -11 },  // Negative = receiving energy (charging)
          { "price": 0.10, "powerKW": -5 },
          { "price": 0.12, "powerKW": 0 }
        ]
      }
    },
    "SELLER": {
      "offerCurve": {
        "currency": "INR",
        "minExport": 0,   // Minimum export (no withdrawal)
        "maxExport": 10,  // Maximum export (generation)
        "curve": [
          { "price": 0.05, "powerKW": 0 },  // Positive = providing energy (generation)
          { "price": 0.06, "powerKW": 5 },
          { "price": 0.08, "powerKW": 10 }
        ]
      }
    }
  }
}
```

**Note**: 
- `expectedRoleInputs` in `ContractRole` defines **what is expected** (schema/type)
- `inputParameters` in `EnergyContract` contains **actual values provided** by roles
- Offer curves in `expectedRoleInputs` allow both **inflexible** (fixed price/power) and **flexible** (price-responsive) trading

---

### 4.3 RevenueFlowLogic

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
        "price": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * price - waitTimePenalty - curtailmentPenalty",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.chargeDataRecords[].energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" },
        "waitTimePenalty": {
          "formula": "max(0, (arrivalTime - startTime - gracePeriod) * penaltyRate)",
          "variables": {
            "arrivalTime": { "source": "telemetry", "path": "$.arrivalTime" },
            "startTime": { "source": "inputParameters", "path": "$.inputParameters.SELLER.startTime" },
            "gracePeriod": { "source": "inputParameters", "path": "$.inputParameters.SELLER.gracePeriod" },
            "penaltyRate": { "constant": 0.01 }
          }
        },
        "curtailmentPenalty": {
          "formula": "max(0, (requestedPower - actualPower) * curtailmentRate)",
          "variables": {
            "requestedPower": { "source": "inputParameters", "path": "$.inputParameters.BUYER.requestedPower" },
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

### 4.4 QualityMetricLogic

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

## 5. Input Signals and Telemetry Sources

**Purpose**: Reference external data sources for contract computation.

**Input Signals** (external dynamic data):
```json
{
  "inputSignals": [
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
      "signalId": "frequency-001",
      "signalType": "STATE",
      "source": {
        "era": "grid-operator",
        "endpoint": "https://grid.example.com/frequency"
      }
    }
  ]
}
```

**Telemetry Sources** (fulfillment data):
```json
{
  "telemetrySources": [
    {
      "sourceId": "meter-readings",
      "sourceType": "METER_READING",
      "source": {
        "era": "solar-panel-001",
        "meterId": "100200300",
        "endpoint": "https://meter-api.example.com/readings/100200300"
      },
      "format": "IEEE_2030_5",
      "refreshInterval": "PT15M"
    },
    {
      "sourceId": "cdr-source",
      "sourceType": "CHARGE_DATA_RECORD",
      "endpoint": "https://cpo.example.com/cdr/contract-walk-in-001",
      "fields": ["arrivalTime", "chargeStartTime", "chargeEndTime", "energyDelivered", "power"]
    }
  ]
}
```

**Signal Types**:
- `METER_READING`: Energy flow measurements
- `CHARGE_DATA_RECORD`: EV charging session data
- `PRICE`: Market prices, clearing prices
- `STATE`: Wait times, availability, congestion, frequency
- `COMMAND`: Setpoints, offsets

**Note**: Revenue flows (defined in section 4.3) reference these signals and telemetry sources using JSONPath expressions.

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
      "expectedRoleInputs": [
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
      "expectedRoleInputs": [
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
        "price": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * price - waitTimePenalty - curtailmentPenalty",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyDelivered" },
        "price": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" },
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

**EnergyOffer** (published in catalogue, with full contract in offerAttributes):
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
  "@type": "beckn:Offer",
  "beckn:id": "offer-ev-charging-001",
  "beckn:offerAttributes": {
    "@context": "https://deg.energy/schema/EnergyOffer/v1/context.jsonld",
    "@type": "EnergyOffer",
    "offerId": "offer-ev-charging-001",
    "contractId": "contract-walk-in-001",
    "providerId": "bpp.cpo.example.com",
    "providerUri": "https://bpp.cpo.example.com",
    "openRole": "BUYER",
    "contract": {
      "@context": "https://deg.energy/schema/EnergyContract/v1/context.jsonld",
      "@type": "EnergyContract",
      "contractId": "contract-walk-in-001",
      "roles": [
        {
          "role": "SELLER",
          "filledBy": "bpp.cpo.example.com",
          "filled": true,
          "expectedRoleInputs": [
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
          "expectedRoleInputs": [
            { "inputName": "accept", "inputType": "BOOLEAN" }
          ]
        }
      ],
      "status": "PENDING",
      "revenueFlows": [ /* ... */ ]
    }
  }
}
```

**Alternative**: EnergyOffer with contract summary (lighter weight):
```json
{
  "beckn:offerAttributes": {
    "@type": "EnergyOffer",
    "offerId": "offer-ev-charging-001",
    "contractId": "contract-walk-in-001",
    "openRole": "BUYER",
    "contractSummary": {
      "description": "Walk-in EV charging at ₹12/kWh",
      "powerRating": "50 kW",
      "gracePeriod": "15 minutes"
    }
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
    "SELLER": {
      "price": 0.12,
      "startTime": "2024-12-15T14:00:00Z",
      "gracePeriod": "PT15M",
      "powerRating": 50.0
    },
    "BUYER": {
      "accept": true
    }
  },
  "status": "ACTIVE"
}
```

**Note**: EnergyIntent (e.g., "charge 20 kWh by 6 PM, minimize cost") is used in `discover` calls by EV user's app to find matching contracts, but is not part of Beckn schema beyond discover calls.

---

### 7.2 EV Charging (Demand Flexibility with Market Clearing)

**Contract Definition** (published by Market Clearing Agent):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-demand-flex-001",
  "roles": [
    {
      "role": "MARKET_CLEARING_AGENT",
      "filledBy": "bpp.market-clearing-agent.com",
      "filled": true,
      "expectedRoleInputs": []  // MCA has no expected inputs, generates market_clearing_price signal
    },
    {
      "role": "PROSUMER",
      "filledBy": null,
      "filled": false,
      "expectedRoleInputs": [
        { 
          "inputName": "offerCurve", 
          "inputType": "OFFER_CURVE", 
          "optional": true,
          "description": "Offer curve with positive powers (export/generation) or negative powers (withdrawal/consumption)"
        }
      ]
    }
  ],
  "status": "PENDING",
  "inputSignals": [
    {
      "signalId": "market-clearing-price",
      "signalType": "PRICE",
      "source": { 
        "era": "market-clearing-agent",
        "generatedBy": "MARKET_CLEARING_AGENT",
        "description": "Market clearing price generated after market clears, intersects with prosumer bid curves to decide cleared power"
      }
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
      "party": { "role": "PROSUMER" },
      "formula": "-(marketClearingPrice + marketMakingFee) * clearedPower",
      "description": "Prosumer pays (market clearing price + market making fee) × cleared power",
      "variables": {
        "marketClearingPrice": { "source": "inputSignals", "path": "$.market-clearing-price.price" },
        "marketMakingFee": { "constant": 0.01 },
        "clearedPower": { 
          "source": "inputSignals", 
          "path": "$.market-clearing-price.clearedPower",
          "description": "Cleared power determined by intersection of market clearing price with prosumer offer curve"
        }
      }
    },
    {
      "party": { "role": "MARKET_CLEARING_AGENT" },
      "formula": "(marketClearingPrice + marketMakingFee) * clearedPower",
      "description": "MCA receives (market clearing price + market making fee) × cleared power",
      "variables": {
        "marketClearingPrice": { "source": "inputSignals", "path": "$.market-clearing-price.price" },
        "marketMakingFee": { "constant": 0.01 },
        "clearedPower": { "source": "inputSignals", "path": "$.market-clearing-price.clearedPower" }
      }
    }
  ]
}
```

**EnergyOffer** (for prosumer role):
```json
{
  "@type": "EnergyOffer",
  "offerId": "offer-demand-flex-prosumer-001",
  "contractId": "contract-demand-flex-001",
  "providerId": "bpp.market-clearing-agent.com",
  "providerUri": "https://bpp.market-clearing-agent.com",
  "openRole": "PROSUMER",
  "expectedInputs": [
    {
      "inputName": "offerCurve",
      "inputType": "OFFER_CURVE",
      "description": "Offer curve with positive powers (export) or negative powers (withdrawal)"
    }
  ]
}
```

**Contract Confirmation** (when prosumer provides offer curve):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-demand-flex-001",
  "roles": [
    { "role": "MARKET_CLEARING_AGENT", "filledBy": "bpp.market-clearing-agent.com", "filled": true },
    { "role": "PROSUMER", "filledBy": "bap.ev-user-app.com", "filled": true }
  ],
  "inputParameters": {
    "PROSUMER": {
      "offerCurve": {
        "currency": "INR",
        "minExport": -11,  // Maximum withdrawal (charging)
        "maxExport": 0,   // No export, only withdrawal
        "curve": [
          { "price": 0.08, "powerKW": -11 },
          { "price": 0.10, "powerKW": -5 },
          { "price": 0.12, "powerKW": 0 }
        ]
      }
    }
  },
  "status": "ACTIVE"
}
```

**Note**: After market clearing:
1. MCA generates `market-clearing-price` signal (price and cleared power for each prosumer)
2. Revenue flows computed: Prosumer pays `(marketClearingPrice + marketMakingFee) * clearedPower`
3. MCA receives the same amount from prosumer

**MCA Contract with Grid Operator** (for deviation pricing):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-mca-grid-operator-001",
  "roles": [
    {
      "role": "MARKET_CLEARING_AGENT",
      "filledBy": "bpp.market-clearing-agent.com",
      "filled": true,
      "expectedRoleInputs": []
    },
    {
      "role": "GRID_OPERATOR",
      "filledBy": "bpp.grid-operator.com",
      "filled": true,
      "expectedRoleInputs": []
    }
  ],
  "status": "ACTIVE",
  "inputSignals": [
    {
      "signalId": "total-cleared-bids",
      "signalType": "STATE",
      "source": { "era": "market-clearing-agent" },
      "description": "Total cleared bids (negative powers, withdrawals)"
    },
    {
      "signalId": "total-cleared-offers",
      "signalType": "STATE",
      "source": { "era": "market-clearing-agent" },
      "description": "Total cleared offers (positive powers, exports)"
    }
  ],
  "revenueFlows": [
    {
      "party": { "role": "MARKET_CLEARING_AGENT" },
      "formula": "-deviationPrice * (totalClearedBids - totalClearedOffers - 0)",
      "description": "MCA pays grid operator for deviation from zero net flow",
      "variables": {
        "deviationPrice": { "constant": 0.05 },
        "totalClearedBids": { "source": "inputSignals", "path": "$.total-cleared-bids.value" },
        "totalClearedOffers": { "source": "inputSignals", "path": "$.total-cleared-offers.value" }
      }
    },
    {
      "party": { "role": "GRID_OPERATOR" },
      "formula": "deviationPrice * (totalClearedBids - totalClearedOffers - 0)",
      "description": "Grid operator receives payment for deviation",
      "variables": {
        "deviationPrice": { "constant": 0.05 },
        "totalClearedBids": { "source": "inputSignals", "path": "$.total-cleared-bids.value" },
        "totalClearedOffers": { "source": "inputSignals", "path": "$.total-cleared-offers.value" }
      }
    }
  ]
}
```

**Note**: The MCA has a virtual meter (net power flow = 0). Any deviation from zero (imbalance between total cleared bids and total cleared offers) incurs a deviation penalty paid to the grid operator, incentivizing the MCA to balance supply and demand.

---

### 7.3 P2P Trading (Market-Based)

**Contract Definition** (published by Market Clearing Agent):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-p2p-001",
  "roles": [
    {
      "role": "SELLER",
      "filledBy": null,
      "filled": false,
      "expectedRoleInputs": [
        { "inputName": "offerCurve", "inputType": "OFFER_CURVE", "optional": true }
      ]
    },
    {
      "role": "BUYER",
      "filledBy": null,
      "filled": false,
      "expectedRoleInputs": [
        { "inputName": "offerCurve", "inputType": "OFFER_CURVE", "optional": true }
      ]
    }
  ],
  "status": "PENDING",
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
  "telemetrySources": [
    {
      "sourceId": "meter-readings",
      "sourceType": "METER_READING",
      "endpoint": "https://meter-api.example.com/readings"
    }
  ],
  "revenueFlows": [
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * clearingPrice",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "clearingPrice": { "source": "inputSignals", "path": "$.clearing-price-001.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * clearingPrice - wheelingCharges - platformFee - tax",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "clearingPrice": { "source": "inputSignals", "path": "$.clearing-price-001.price" },
        "wheelingCharges": { "source": "telemetry", "transform": "multiply", "constant": 0.02 },
        "platformFee": { "source": "telemetry", "transform": "multiply", "constant": 0.01 },
        "tax": { "source": "telemetry", "transform": "multiply", "constant": 0.01 }
      }
    }
  ]
}
```

**Note**: EnergyIntent (e.g., "sell 10 kWh solar energy, min ₹0.06/kWh") is used in `discover` calls to find matching contracts, but is not part of the contract schema.

---

### 7.4 Service Request (EV Charging Along Route)

**Contract Definition** (published by CPO):
```json
{
  "@type": "EnergyContract",
  "contractId": "contract-route-001",
  "roles": [
    {
      "role": "SELLER",
      "filledBy": "bpp.cpo.example.com",
      "filled": true,
      "expectedRoleInputs": [
        { "inputName": "price", "inputType": "NUMBER" },
        { "inputName": "maxWaitTime", "inputType": "DURATION" }
      ]
    },
    {
      "role": "BUYER",
      "filledBy": null,
      "filled": false,
      "expectedRoleInputs": [
        { "inputName": "accept", "inputType": "BOOLEAN" },
        { "inputName": "route", "inputType": "ROUTE", "optional": true }
      ]
    }
  ],
  "status": "PENDING",
  "inputSignals": [
    {
      "signalId": "wait-time-001",
      "signalType": "STATE",
      "source": { "era": "cpo-station-001" }
    }
  ],
  "telemetrySources": [
    {
      "sourceId": "meter-reading-001",
      "sourceType": "METER_READING",
      "source": { "era": "cpo-station-001" }
    }
  ],
  "revenueFlows": [
    {
      "party": { "role": "SELLER" },
      "formula": "energyFlow * pricePerKWh",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "pricePerKWh": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" }
      }
    },
    {
      "party": { "role": "BUYER" },
      "formula": "-energyFlow * pricePerKWh",
      "variables": {
        "energyFlow": { "source": "telemetry", "path": "$.energyFlow" },
        "pricePerKWh": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" }
      }
    }
  ]
}
```

**Note**: EnergyIntent with route constraints (e.g., "kWh needed along route with wait time < 5min") is used in `discover` calls to find matching contracts, but is not part of the contract schema.

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
- Contracts define **open roles** (buyer/seller/prosumer/market clearing agent/aggregator/grid operator)
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
        "price": { "source": "inputParameters", "path": "$.inputParameters.SELLER.price" }
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

## 11. Next Steps

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
| **Role-Based Participation** | Unclear how participants join | Contracts have **open roles** (buyer/seller/prosumer/market clearing agent/aggregator/grid operator) that participants fill |
| **Contract Confirmation** | Unclear when contract is active | When **all roles filled** and input connections established |
| **Billing** | Static revenue flows | Computed from input parameters, signals, and telemetry |
| **Offer Curve Terminology** | "Bid curve" and "offer curve" | Unified "offer curve" (positive = injection, negative = withdrawal) |
| **Multi-Tenant** | Different schemas for different use cases | Single schema pattern for all use cases |
| **Complexity** | Many optional properties at root | Telescoping nested structures |
| **Fraud Prevention** | Limited | DeDi protocol integration for integrity, validity, authenticity |
| **Contract Verification** | Manual | Automated via DeDi public key directory, revocation lists, membership checks |

---

---

## 12. Key Refinements from Initial Proposal

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

**Change**: Contracts now have **open roles** that need to be filled, with `expectedRoleInputs` as optional sub-attribute.

**Rationale**:
- Contracts specify roles (buyer/seller/prosumer/market clearing agent/aggregator/grid operator)
- Each role has `expectedRoleInputs` (optional) defining what inputs are expected
- Participants fill roles by selecting offers and providing required inputs
- Contracts confirmed when:
  1. All roles are filled
  2. All expected inputs for each role are provided
  3. Connections to all trusted signals are established

**Impact**: Clear participation model with explicit input requirements and confirmation criteria.

---

### 11.3 Contract as Computational Agreement

**Change**: Contracts define revenue flows and quality metrics as functions of inputs, signals, and telemetry.

**Rationale**:
- Revenue flows computed from input parameters (e.g., seller specifies price)
- Telemetry sources provide fulfillment data (e.g., CDR, meter readings)
- External signals provide dynamic pricing (e.g., clearing price, frequency)

**Impact**: Dynamic, signal-driven billing instead of static prices.

---

### 11.4 EnergyIntent Only in Discover Calls

**Change**: `EnergyIntent` is now used **only in `discover` calls** to tie intent to contract discovery & participation. It is not part of core Beckn schema.

**Rationale**:
- Intent represents actor objectives (e.g., "charge 20 kWh by 6 PM")
- Used in `discover` calls to find matching contracts/offers
- Appears only in `message.intent` of `discover` requests
- Not stored in contracts, offers, or other Beckn messages

**Impact**: Cleaner separation—intent used for discovery, offers/contracts for transactions.

---

### 11.5 Offer Curves in Expected Role Inputs

**Change**: Offer curves are now specified in `expectedRoleInputs` (optional sub-attribute of `ContractRole`), allowing both inflexible and flexible (price responsive) trading.

**Rationale**:
- **Inflexible trading**: Fixed price and power specified directly
- **Flexible trading**: Offer curve with price/power pairs
- **Positive power values**: Providing energy to grid (injection)
- **Negative power values**: Receiving energy from grid (withdrawal)
- All offer curves allowed in `expectedRoleInputs`

**Impact**: Unified approach for both fixed-price and price-responsive contracts.

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

