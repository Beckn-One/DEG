# Building Block Extensions Analysis
## Gap Analysis and Proposed Extensions for Decentralized Energy Exchange

**Version:** 1.0  
**Date:** December 2024

---

## Executive Summary

This document analyzes gaps in current Beckn Protocol building blocks for supporting decentralized energy exchange use cases (EV charging, demand flexibility, P2P trading, VPP coordination). It identifies required extensions, validates their simplicity and composability, and proposes implementation patterns.

**Key Finding**: Current building blocks are sufficient for basic use cases, but need extensions for:
1. **Bid curve aggregation** (new action)
2. **Market clearing via contracts** (synchronous confirmation pattern)
3. **Locational pricing** (grid nodes as resources)
4. **Settlement attributes** (multi-party revenue flows)

---

## 1. Gap Analysis Framework

### 1.1 Analysis Dimensions

We analyze gaps across three dimensions:

#### A. Functional Gaps
- What use cases cannot be expressed with current building blocks?
- What energy-specific concepts are missing?
- What coordination patterns need support?

#### B. Structural Gaps
- Are current attribute slots sufficient?
- Do we need new actions or modify existing ones?
- Are there missing primitives in the six-primitive model?

#### C. Integration Gaps
- How well do current blocks integrate with OCPI/OCPP/IEEE 2030.5?
- What protocol translation patterns are needed?
- Are there missing abstraction layers?

### 1.2 Use Case Coverage Matrix

| Use Case | Current Support | Gap | Proposed Solution |
|----------|----------------|-----|-------------------|
| **EV Charging (Basic)** | ✅ Full | None | N/A |
| **EV Charging (Demand Flexibility)** | ⚠️ Partial | Bid curves, market clearing | Bid curve aggregation action |
| **P2P Trading (Basic)** | ✅ Full | None | N/A |
| **P2P Trading (Market-Based)** | ⚠️ Partial | Bid curves, market clearing | Bid curve aggregation action |
| **Demand Flexibility** | ❌ None | Bid curves, objectives, market clearing | Bid curve aggregation + objective expression |
| **VPP Coordination** | ❌ None | Bid curve aggregation, market clearing, disaggregation | Bid curve aggregation action |
| **Grid Services** | ❌ None | Locational pricing, grid nodes | Grid nodes as resources + locational pricing |
| **Multi-Party Settlement** | ⚠️ Partial | Revenue flow breakdown | Settlement attributes extension |

**Legend**:
- ✅ Full: Use case fully supported
- ⚠️ Partial: Use case supported but missing advanced features
- ❌ None: Use case not supported

---

## 2. Detailed Gap Analysis by Use Case

### 2.1 EV Charging (Basic)

**Current Support**: ✅ Full

**Implementation**: Uses standard Beckn flow:
- `discover` / `on_discover`: Find charging stations
- `select` / `on_select`: Select charger and get quote
- `init` / `on_init`: Initialize order
- `confirm` / `on_confirm`: Confirm reservation
- `update` / `on_update`: Start/stop charging
- `track` / `on_track`: Monitor session
- `status` / `on_status`: Check status

**Attribute Slots Used**:
- `itemAttributes`: EVSE specifications (connectorType, maxPowerKW, etc.)
- `offerAttributes`: Pricing models (per-kWh, time-based slots)
- `fulfillmentAttributes`: Session management (reservation, charging status)

**Gap**: None for basic use case.

---

### 2.2 EV Charging (Demand Flexibility)

**Current Support**: ⚠️ Partial

**Gap**: Cannot express:
1. **Bid curves**: EV wants to charge at different rates based on price
2. **Market clearing**: Price discovery at confirmation time
3. **Objective expression**: "Charge 20 kWh by 6 PM, max ₹7/kWh"

**Example Scenario**:
- EV needs 20 kWh by 6 PM
- Expresses bid curve: "Charge at 11 kW if price ≤ ₹0.08/kWh, 5 kW if ≤ ₹0.10/kWh"
- Market clears at ₹0.09/kWh
- EV receives setpoint: Charge at ~8 kW (interpolated)

**Proposed Solution**:
- **Bid curve expression**: Add `bidCurve` to `itemAttributes` or `offerAttributes`
- **Bid curve aggregation**: New `aggregate` action
- **Market clearing**: Contract-based pattern with synchronous confirmation

---

### 2.3 P2P Trading (Basic)

**Current Support**: ✅ Full

**Implementation**: Uses standard Beckn flow with energy-specific attributes:
- `itemAttributes`: Energy resource specs (sourceType, deliveryMode, meterId)
- `offerAttributes`: Trading terms (pricingModel, settlementType, wheelingCharges)
- `orderAttributes`: Contract details (EnergyTradeContract)
- `fulfillmentAttributes`: Delivery tracking (EnergyTradeDelivery)

**Gap**: None for basic use case.

---

### 2.4 P2P Trading (Market-Based)

**Current Support**: ⚠️ Partial

**Gap**: Cannot express:
1. **Bid curves**: Prosumer expresses price/power pairs
2. **Market clearing**: Price discovery at confirmation time
3. **Multi-resource aggregation**: Aggregate multiple prosumers

**Example Scenario**:
- 10 solar prosumers publish catalogues with bid curves
- Consumer expresses intent: "Buy 50 kWh, max ₹6/kWh"
- Market aggregates bid curves, clears at ₹5.50/kWh
- Economic disaggregation: Each prosumer provides ~5 kWh

**Proposed Solution**:
- **Bid curve expression**: Add `bidCurve` to `offerAttributes`
- **Bid curve aggregation**: New `aggregate` action
- **Market clearing**: Contract-based pattern with synchronous confirmation

---

### 2.5 Demand Flexibility

**Current Support**: ❌ None

**Gap**: Cannot express:
1. **Objectives**: "Reduce consumption by 5 kW during peak hours"
2. **Bid curves**: "I'll reduce by 5 kW if price ≥ ₹0.15/kWh"
3. **Market clearing**: Aggregate demand reduction bids
4. **Setpoint disaggregation**: Distribute reduction across devices

**Example Scenario**:
- Grid operator signals: "Need 50 kW reduction, 2-4 PM"
- 20 smart devices express bid curves for demand reduction
- Market aggregates, clears at ₹0.12/kWh
- Each device receives setpoint based on bid curve

**Proposed Solution**:
- **Objective expression**: Add `objectives` to `itemAttributes`
- **Bid curve expression**: Add `bidCurve` to `itemAttributes`
- **Bid curve aggregation**: New `aggregate` action
- **Market clearing**: Contract-based pattern

---

### 2.6 VPP Coordination

**Current Support**: ❌ None

**Gap**: Cannot express:
1. **Bid curve aggregation**: Aggregate across multiple resources
2. **Market clearing**: Discover neighborhood clearing price
3. **Economic disaggregation**: Distribute setpoints to individual resources
4. **Protocol translation**: Map setpoints to OCPP/IEEE 2030.5

**Example Scenario**:
- Neighborhood VPP: 20 solar panels, 10 EV batteries, 5 home batteries
- All resources express bid curves
- Market aggregates, clears at ₹0.075/kWh
- Economic disaggregation: Each resource receives optimal setpoint
- Protocol translation: Setpoints sent to OCPP/IEEE 2030.5

**Proposed Solution**:
- **Bid curve aggregation**: New `aggregate` action
- **Market clearing**: Contract-based pattern
- **Economic disaggregation**: Part of `aggregate` response
- **Protocol translation**: Implementation detail (not in schema)

---

### 2.7 Grid Services

**Current Support**: ❌ None

**Gap**: Cannot express:
1. **Grid nodes as resources**: Transformers, substations
2. **Locational pricing**: Congestion-based price adders
3. **Grid constraints**: Reverse flow limits, capacity constraints
4. **Offset commands**: For flat bid curve plateaus

**Example Scenario**:
- Transformer at 75% load signals: "Add ₹0.03/kWh locational adder"
- Resources adjust bid curves
- Market clears with locational pricing
- Grid operator commands offsets for flat plateaus

**Proposed Solution**:
- **Grid nodes as resources**: Transformers are Energy Resources
- **Locational pricing**: Add `locationalPriceAdder` to `itemAttributes`
- **Grid constraints**: Add `gridConstraints` to `itemAttributes`
- **Offset commands**: Add `offsetCommand` to `orderAttributes` or `fulfillmentAttributes`

---

### 2.8 Multi-Party Settlement

**Current Support**: ⚠️ Partial

**Current Implementation**: P2P trading uses `settlementCycles` in `orderAttributes`:
```json
{
  "settlementCycles": [{
    "cycleId": "settle-2024-10-04-001",
    "status": "SETTLED",
    "amount": 4.0,
    "breakdown": {
      "energyCost": 1.5,
      "wheelingCharges": 2.5
    }
  }]
}
```

**Gap**: Cannot express:
1. **Multi-party revenue flows**: Aggregator, customer, government, grid operator
2. **Revenue distribution**: Who gets what portion
3. **Tax breakdown**: Government taxes, fees
4. **Settlement report**: Unambiguous billing document

**Example Scenario**:
- P2P trade: ₹100 total
- Energy cost: ₹60 (to prosumer)
- Wheeling charges: ₹20 (to grid operator)
- Platform fee: ₹10 (to aggregator)
- Tax: ₹10 (to government)

**Proposed Solution**:
- **Settlement attributes**: Extend `orderAttributes` or create `settlementAttributes`
- **Revenue flows**: Array of revenue flow entries
- **Settlement report**: Structured billing document

---

## 3. Proposed Building Block Extensions

### 3.1 Bid Curve Expression

**Purpose**: Enable resources to express price/power preferences

**Where**: 
- `itemAttributes.bidCurve`: For resources expressing capability
- `offerAttributes.bidCurve`: For offers with dynamic pricing

**Structure**:
```json
{
  "bidCurve": [
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
```

**Semantics**:
- Negative power = consumption (charging, load)
- Positive power = generation (discharge, export)
- Zero power = no participation at that price
- Price in currency per kWh
- Power in kW

**Simplicity Check**: ✅
- Single concept: price/power pairs
- Composable with existing pricing models
- Emergent: enables market mechanisms

**Protocol Integration**:
- OCPP: Maps to SetChargingProfile
- IEEE 2030.5: Maps to opModFixedW
- OCPI: Maps to tariff structures

---

### 3.2 Bid Curve Aggregation Action

**Purpose**: Aggregate bid curves from multiple resources for market clearing

**Action**: `aggregate` / `on_aggregate`

**Request Structure**:
```json
{
  "context": {
    "action": "aggregate",
    "domain": "beckn.one:deg:energy-coordination:*"
  },
  "message": {
    "aggregationRequest": {
      "participants": [
        { "era": "solar-panel-001", "bidCurve": [...] },
        { "era": "ev-battery-002", "bidCurve": [...] },
        { "era": "transformer-zone-5", "locationalPriceAdder": {...} }
      ],
      "aggregationType": "MARKET_CLEARING",
      "timeWindow": {
        "start": "2024-12-15T14:00:00Z",
        "end": "2024-12-15T16:00:00Z"
      }
    }
  }
}
```

**Response Structure**:
```json
{
  "message": {
    "aggregationResult": {
      "clearingPrice": 0.075,
      "clearingQuantityKW": 50.0,
      "setpoints": [
        { "era": "solar-panel-001", "setpointKW": 3.5 },
        { "era": "ev-battery-002", "setpointKW": -8.0 }
      ],
      "locationalPrice": 0.13,
      "timestamp": "2024-12-15T14:00:00Z"
    }
  }
}
```

**Simplicity Check**: ✅
- Single action for aggregation
- Clear input/output structure
- Emergent: enables market clearing

**Protocol Integration**:
- Can be called by market clearing agent
- Returns setpoints ready for protocol translation

---

### 3.3 Market Clearing via Contracts

**Purpose**: Enable price discovery at synchronous confirmation stage

**Pattern**: Market clearing agent acts as BPP, participants as BAPs

**Flow**:
1. **Participants express bid curves** (via `discover` with bid curves in intent)
2. **Market clearing agent aggregates** (via `aggregate` action)
3. **Market clearing agent publishes catalogue** (via `on_discover` with clearing price)
4. **Participants confirm** (via `confirm` with accepted clearing price)
5. **Market clearing agent confirms** (via `on_confirm` with setpoints)

**Key Insight**: Prices discovered at confirmation time, not at offer time

**Example**:
```json
// Step 1: EV expresses intent with bid curve
{
  "message": {
    "intent": {
      "bidCurve": [
        { "price": 0.08, "powerKW": -11 },
        { "price": 0.10, "powerKW": -5 }
      ],
      "objectives": {
        "targetChargeKWh": 20,
        "deadline": "2024-12-15T18:00:00Z"
      }
    }
  }
}

// Step 2: Market clearing agent aggregates
// (internal aggregate action)

// Step 3: Market clearing agent responds with clearing price
{
  "message": {
    "catalogs": [{
      "offers": [{
        "price": {
          "value": 0.09,  // Clearing price
          "currency": "INR"
        },
        "offerAttributes": {
          "clearingPrice": 0.09,
          "setpointKW": -8.0
        }
      }]
    }]
  }
}

// Step 4: EV confirms with clearing price
{
  "message": {
    "order": {
      "acceptedOffer": {
        "price": {
          "value": 0.09
        }
      }
    }
  }
}

// Step 5: Market clearing agent confirms with setpoint
{
  "message": {
    "order": {
      "orderAttributes": {
        "setpointKW": -8.0,
        "clearingPrice": 0.09
      }
    }
  }
}
```

**Simplicity Check**: ✅
- Uses existing Beckn actions
- No new actions needed
- Emergent: market clearing emerges from contract pattern

---

### 3.4 Grid Nodes as Energy Resources

**Purpose**: Enable transformers/substations to participate as resources

**Rationale**: 
- Grid nodes can signal locational price adders
- Grid nodes can command offsets for flat plateaus
- Grid nodes are owned by grid operators (fit Energy Resource pattern)

**Structure**:
```json
{
  "beckn:id": "transformer-zone-5",
  "beckn:descriptor": {
    "schema:name": "Neighborhood Transformer Zone 5"
  },
  "beckn:itemAttributes": {
    "@type": "GridNode",
    "locationalPriceAdder": {
      "basePrice": 0.10,
      "congestionMultiplier": 1.0,
      "currentLoadPercent": 75,
      "priceAdderPerPercent": 0.001,
      "currentPrice": 0.175
    },
    "gridConstraints": {
      "maxReverseFlowKW": 50,
      "maxForwardFlowKW": 200,
      "currentLoadKW": 150
    },
    "offsetCommand": {
      "enabled": false,
      "offsetKW": 0
    }
  }
}
```

**Simplicity Check**: ✅
- Fits existing Energy Resource pattern
- No new primitives needed
- Emergent: enables grid-aware coordination

---

### 3.5 Locational Pricing

**Purpose**: Enable congestion-aware routing and pricing

**Where**: 
- `itemAttributes.locationalPriceAdder`: For grid nodes
- `offerAttributes.locationalPriceAdder`: For offers with location-based pricing

**Structure**:
```json
{
  "locationalPriceAdder": {
    "basePrice": 0.10,
    "congestionMultiplier": 1.0,
    "currentLoadPercent": 75,
    "priceAdderPerPercent": 0.001,
    "currentPrice": 0.175,
    "formula": "basePrice + (currentLoadPercent * priceAdderPerPercent)"
  }
}
```

**Simplicity Check**: ✅
- Simple: base price + adder
- Composable: can be layered (national → state → city → neighborhood)
- Emergent: enables congestion-aware markets

---

### 3.6 Objective Expression

**Purpose**: Enable resources to express objectives rather than fixed commands

**Where**: 
- `itemAttributes.objectives`: For resources expressing goals
- `orderAttributes.objectives`: For contracts with objective-based fulfillment

**Structure**:
```json
{
  "objectives": {
    "targetChargeKWh": 20,
    "deadline": "2024-12-15T18:00:00Z",
    "maxPricePerKWh": 0.12,
    "preferredSource": "SOLAR",
    "constraints": {
      "minChargeKWh": 10,
      "maxChargeKWh": 60
    }
  }
}
```

**Simplicity Check**: ✅
- Simple: structured objectives
- Composable: can combine with bid curves
- Emergent: enables autonomous coordination

---

### 3.7 Settlement Attributes Extension

**Purpose**: Enable unambiguous billing with multi-party revenue flows

**Proposal**: Extend `orderAttributes` with `settlement` section

**Current State**: P2P trading uses `settlementCycles` in `orderAttributes`:
```json
{
  "settlementCycles": [{
    "cycleId": "settle-2024-10-04-001",
    "status": "SETTLED",
    "amount": 4.0,
    "breakdown": {
      "energyCost": 1.5,
      "wheelingCharges": 2.5
    }
  }]
}
```

**Proposed Extension**:
```json
{
  "settlement": {
    "settlementCycles": [...],
    "revenueFlows": [
      {
        "party": {
          "era": "prosumer-solar-001",
          "role": "SELLER"
        },
        "amount": 60.0,
        "currency": "INR",
        "description": "Energy sale"
      },
      {
        "party": {
          "era": "grid-operator-utility",
          "role": "GRID_OPERATOR"
        },
        "amount": 20.0,
        "currency": "INR",
        "description": "Wheeling charges"
      },
      {
        "party": {
          "era": "aggregator-platform",
          "role": "AGGREGATOR"
        },
        "amount": 10.0,
        "currency": "INR",
        "description": "Platform fee"
      },
      {
        "party": {
          "era": "government-tax",
          "role": "GOVERNMENT"
        },
        "amount": 10.0,
        "currency": "INR",
        "description": "Tax (10%)"
      }
    ],
    "settlementReport": {
      "reportId": "settle-report-2024-10-04-001",
      "totalAmount": 100.0,
      "currency": "INR",
      "generatedAt": "2024-10-04T18:30:00Z",
      "meterReadings": [...],
      "revenueFlows": [...]
    }
  }
}
```

**Alternative**: Create new `settlementAttributes` slot

**Decision**: **Extend `orderAttributes`** (simpler, no new slot needed)

**Simplicity Check**: ✅
- Simple: array of revenue flow entries
- Composable: can combine with meter data
- Emergent: enables complex settlements

---

## 4. Protocol Integration Patterns

### 4.1 OCPI Integration

**Role**: Roaming and roaming operator coordination

**Integration Points**:
- **Energy Resource Address**: OCPI `location_id` maps to ERA
- **Catalogue**: OCPI tariff and session data inform bid curves
- **Contract**: OCPI CDR (Charge Detail Record) provides settlement data

**Translation Pattern**:
```json
{
  "era": "ocpi.location.IN*ECO*BTM*01",
  "ocpiData": {
    "locationId": "IN*ECO*BTM*01",
    "tariffs": [{
      "price": 18.0,
      "currency": "INR",
      "unit": "KWH"
    }]
  },
  "bidCurve": [
    { "price": 0.15, "powerKW": 0 },
    { "price": 0.18, "powerKW": 60 }
  ]
}
```

**Toil Assessment**: ✅ Low
- Direct mapping: OCPI location_id → ERA
- Tariff → bid curve (simple conversion)
- CDR → settlement data (structured mapping)

---

### 4.2 OCPP Integration

**Role**: Charging station management and control

**Integration Points**:
- **Device Control**: OCPP `SetChargingProfile` receives setpoints from market clearing
- **Telemetry**: OCPP `MeterValues` provides real-time data for bid curve updates
- **Status**: OCPP `StatusNotification` informs availability

**Translation Pattern**:
```json
{
  "era": "ocpp.chargepoint.IN-ECO-BTM-01",
  "marketSetpoint": {
    "powerKW": 50,
    "price": 0.18,
    "source": "market-clearing"
  },
  "ocppCommand": {
    "action": "SetChargingProfile",
    "chargingProfile": {
      "chargingSchedule": {
        "chargingRateUnit": "A",
        "chargingSchedulePeriod": [{
          "startPeriod": 0,
          "limit": 50.0 * 1000 / 240  // Convert kW to Amps
        }]
      }
    }
  }
}
```

**Toil Assessment**: ✅ Low
- Setpoint → OCPP command (simple conversion)
- Meter values → telemetry (structured mapping)
- Status → availability (direct mapping)

---

### 4.3 IEEE 2030.5 Integration

**Role**: DER communication, control, and grid integration

**Integration Points**:
- **Device Control**: IEEE 2030.5 `DERControl` receives setpoints from market clearing
- **Telemetry**: IEEE 2030.5 `MeterReading` provides real-time data
- **Capability Discovery**: IEEE 2030.5 `DERCapability` informs bid curve construction

**Translation Pattern**:
```json
{
  "era": "ieee.der.solar-panel-001",
  "mRID": "100200300",
  "marketSetpoint": {
    "powerKW": 3.5,
    "price": 0.075
  },
  "ieee2030_5Command": {
    "method": "PUT",
    "uri": "/edev/100200300/der/dc",
    "body": {
      "DERControl": {
        "mRID": "100200300",
        "DERControlBase": {
          "opModFixedW": 7000  // 70.00% of 5 kW = 3.5 kW
        },
        "deviceCategory": "00000040",
        "startTime": 1702656000,
        "duration": 3600
      }
    }
  }
}
```

**Toil Assessment**: ✅ Low
- Setpoint → IEEE 2030.5 command (percentage calculation)
- Meter readings → telemetry (structured mapping)
- Capability → bid curve (direct mapping)

---

## 5. Summary of Extensions

### 5.1 New Actions

| Action | Purpose | Status |
|--------|---------|--------|
| `aggregate` / `on_aggregate` | Bid curve aggregation for market clearing | ✅ **Required** |

### 5.2 Attribute Slot Extensions

| Slot | Extension | Purpose | Status |
|------|-----------|---------|--------|
| `itemAttributes` | `bidCurve` | Express price/power preferences | ✅ **Required** |
| `itemAttributes` | `objectives` | Express goals and constraints | ✅ **Required** |
| `itemAttributes` | `locationalPriceAdder` | Grid node congestion pricing | ✅ **Required** |
| `itemAttributes` | `gridConstraints` | Grid node constraints | ✅ **Required** |
| `offerAttributes` | `bidCurve` | Dynamic pricing offers | ✅ **Required** |
| `offerAttributes` | `locationalPriceAdder` | Location-based pricing | ✅ **Required** |
| `orderAttributes` | `objectives` | Objective-based contracts | ✅ **Required** |
| `orderAttributes` | `settlement.revenueFlows` | Multi-party revenue flows | ✅ **Required** |
| `orderAttributes` | `settlement.settlementReport` | Settlement billing document | ✅ **Required** |
| `fulfillmentAttributes` | `offsetCommand` | Grid operator offset commands | ✅ **Required** |

### 5.3 New Resource Types

| Resource Type | Purpose | Status |
|---------------|---------|--------|
| `GridNode` | Transformers, substations as resources | ✅ **Required** |

### 5.4 Patterns

| Pattern | Purpose | Status |
|----------|---------|--------|
| Market Clearing via Contracts | Price discovery at confirmation | ✅ **Required** |

---

## 6. Simplicity Validation

### 6.1 Developer Comprehension

Each extension can be understood in < 5 minutes:
- ✅ **Bid curves**: Price/power pairs (2 min)
- ✅ **Bid curve aggregation**: Single action (3 min)
- ✅ **Market clearing**: Contract pattern (5 min)
- ✅ **Locational pricing**: Base price + adder (2 min)
- ✅ **Objectives**: Structured goals (3 min)
- ✅ **Settlement**: Revenue flow array (4 min)

### 6.2 Composability

Extensions combine naturally:
- ✅ Bid curves + objectives = agentic coordination
- ✅ Bid curves + locational pricing = grid-aware markets
- ✅ Market clearing + settlement = complete transaction
- ✅ Grid nodes + bid curves = congestion management

### 6.3 Emergent Patterns

Combining blocks creates useful patterns:
- ✅ Bid curve aggregation → Market clearing → Economic disaggregation
- ✅ Grid nodes + locational pricing → Congestion-aware routing
- ✅ Objectives + bid curves → Autonomous resource coordination
- ✅ Settlement + revenue flows → Multi-party billing

---

## 7. Next Steps

1. ✅ **Gap Analysis**: Complete (this document)
2. ⏳ **Sequence Diagrams**: Create Mermaid diagrams for each use case
3. ⏳ **Protocol Integration**: Document detailed integration patterns
4. ⏳ **Schema Design**: Design JSON-LD schemas for extensions
5. ⏳ **Example Messages**: Create complete message flows

---

## Appendix: Reference Documents

- [Architectural Approach and Plan](./01_Architectural_Approach_and_Plan.md)
- [Agentic Coordination Architecture](../ref_docs/agentic_coordination_arch.md)
- [EV Charging Implementation Guide](../docs/implementation-guides/v2/EV_Charging_V0.8-draft.md)
- [P2P Trading Implementation Guide](../docs/implementation-guides/v2/P2P_Trading/P2P_Trading_implementation_guide_DRAFT.md)

---

**Status**: Complete  
**Next Action**: Create sequence diagrams (03_Use_Case_Sequence_Diagrams.md)

