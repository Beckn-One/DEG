# Energy Domain Schema Extensions

This directory contains detailed OpenAPI 3.1.1 attribute schema definitions for Energy domain extensions to the Beckn Protocol. These schemas define the structure of objects that compose within Beckn core attribute slots (`itemAttributes`, `offerAttributes`, `orderAttributes`, `fulfillmentAttributes`).

---

## Directory Structure

```
schema/
├── EnergyResource/
│   └── v0.2/
│       └── attributes.yaml          # Item.itemAttributes schema
├── EnergyOffer/
│   └── v1/
│       └── attributes.yaml          # Offer.offerAttributes schema (Core Beckn Primitive)
├── EnergyContract/
│   └── v1/
│       └── attributes.yaml          # Order.orderAttributes / Offer.offerAttributes schema (Core Abstract Schema)
├── EnergyTradeDelivery/
│   └── v0.2/
│       └── attributes.yaml          # Fulfillment.attributes schema
├── EnergyCoordination/
│   └── v1/
│       └── attributes.yaml          # Shared coordination schemas (OfferCurve, EnergyObjectives, Settlement)
├── GridNode/
│   └── v1/
│       └── attributes.yaml          # Grid node attributes (transformers, substations)
└── EnergyCredentials/
    └── v1/
        └── attributes.yaml          # W3C Verifiable Credentials for energy resources
```

---

## Schema Files

### EnergyOffer/v1/attributes.yaml (NEW - Core Beckn Primitive)

**Purpose**: Core Beckn primitive representing willingness to assume a role in an EnergyContract. This is the primary schema for `offerAttributes`.

**Attaches to**: `Offer.offerAttributes`

**Key Properties**:
- **Core**: `offerId`, `contractId`, `providerId`, `providerUri`, `openRole` (BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR)
- **Optional**: `contract` (full EnergyContract definition), `expectedInputs`, `contractSummary`, `credentials`

**Key Concept**: EnergyOffer is a bouquet of contract participation opportunities. Each offer references a contract and specifies an open role.

**Example Usage**: See `outputs/10_Conceptual_Refactor_Proposal.md` section 2.1

---

### EnergyContract/v1/attributes.yaml (NEW - Core Abstract Schema)

**Purpose**: Core abstract schema for computational energy contracts. Defines roles, revenue flows, and quality metrics as functions of external signals and telemetry.

**Attaches to**: 
- `Offer.offerAttributes` (for discovery - contract definition)
- `Order.orderAttributes` (during init/confirm flows - contract instance, status: PENDING → ACTIVE)

**Key Properties**:
- **Core**: `contractId`, `roles` (array of ContractRole), `status` (PENDING, ACTIVE, COMPLETED, TERMINATED), `createdAt`
- **Telescoping**: `inputParameters` (actual values by role), `inputSignals` (external signals), `telemetrySources` (fulfillment data), `revenueFlows` (RevenueFlowLogic), `qualityMetrics` (optional)
- **Extensions**: `credentials`, `verification` (DeDi protocol), `ricardianContract` (optional)

**Key Concept**: Contracts specify roles that need to be filled. Revenue flows are computed from input parameters, signals, and telemetry using formulas.

**Contract Roles**: BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR

**Example Usage**: See `outputs/10_Conceptual_Refactor_Proposal.md` section 2.2 and 3.1

---

### EnergyResource/v0.2/attributes.yaml

**Purpose**: Defines attributes for energy resources (generators, storage, consumers, infrastructure).

**Attaches to**: `Item.itemAttributes`

**Key Properties**:
- **Core**: `sourceType`, `deliveryMode`, `certificationStatus` (optional), `meterId`, `inverterId` (optional), `productionWindow`
- **Coordination Extensions**: `offerCurve` (use OfferCurve from EnergyCoordination), `constraints`, `objectives`

**Example Usage**: See `outputs/examples/ev_charging_demand_flexibility/discover-with-bid-curve.json`

---


### EnergyTradeDelivery/v0.2/attributes.yaml

**Purpose**: Defines attributes for energy trade deliveries (physical transfer, meter readings, telemetry).

**Attaches to**: `Fulfillment.attributes` (or `Fulfillment.deliveryAttributes`)

**Key Properties**:
- **Core**: `deliveryStatus`, `deliveryMode`, `deliveredQuantity`, `deliveryStartTime`, `deliveryEndTime`, `meterReadings`, `telemetry`, `settlementCycleId`
- **Coordination Extensions**: `offsetCommand` (optional), `deviationPenalty` (optional)

**Example Usage**: See `outputs/examples/p2p_trading_market_based/` directory

---

### EnergyCoordination/v1/attributes.yaml

**Purpose**: Defines shared coordination schemas used across multiple attribute slots.

**Attaches to**: Multiple attribute slots (via composition)

**Key Schemas**:
- **`OfferCurve`**: Unified offer curve structure with `currency`, `minExport`, `maxExport`, and `curve` array (replaces "bid curve")
- **`OfferCurvePoint`**: Price/power pair in offer curve
- **`EnergyObjectives`**: Goals and constraints (targetChargeKWh, targetGenerationKWh, targetReductionKW, deadline, maxPricePerKWh, minPricePerKWh (optional), preferredSource (optional))
- **`Settlement`**: Multi-party revenue flows (revenueFlows, settlementReport) - computed revenue flows for settlement
- **`SettlementReport`**: Billing document (reportId, totalAmount, currency, generatedAt)
- **`OffsetCommand`**: Grid operator commands
- **`AggregationRequest` / `AggregationResult`**: Market clearing schemas
- **`Participant`**: Participant in aggregation with offerCurve

**Note**: 
- `LocationalPriceAdder` and `GridConstraints` have been moved to the `GridNode` schema.
- OfferCurve replaces "bid curve" terminology. Positive power = export/generation, negative power = withdrawal/consumption.

**Example Usage**: See `outputs/examples/aggregate_action/` directory

---

### GridNode/v1/attributes.yaml

**Purpose**: Defines attributes for grid nodes (transformers, substations) as Energy Resources.

**Attaches to**: `Item.itemAttributes` (for grid infrastructure nodes)

**Key Properties**:
- **Grid Node Identification**: `nodeId`, `nodeType` (TRANSFORMER, SUBSTATION, DISTRIBUTION_NODE, TRANSMISSION_NODE)
- **Locational Pricing**: `locationalPriceAdder` (basePrice, currentLoadPercent, priceAdderPerPercent, currentPrice, congestionMultiplier (optional))
- **Grid Constraints**: `gridConstraints` (maxReverseFlowKW, maxForwardFlowKW, currentLoadKW, capacityKW)

**Example Usage**: See grid services use cases in `outputs/03_Use_Case_Sequence_Diagrams.md`

---

### EnergyCredentials/v1/attributes.yaml

**Purpose**: Defines attributes for W3C Verifiable Credentials in the energy domain.

**Attaches to**: `Item.itemAttributes`, `Order.orderAttributes`, or `Provider.providerAttributes`

**Key Properties**:
- **Credential Presentation**: `presentedCredentials` (array of Verifiable Credentials or Presentations)
- **Credential Requirements**: `requiredCredentials` (specify required credential types/claims)
- **Verification Status**: `verificationStatus` (verified, verificationType, lastVerified, verificationDetails)
- **Credential Querying**: `credentialQuery` (queryEndpoint, queryMethod, supportedCredentialTypes)

**Key Schemas**:
- `VerifiableCredential`: W3C VC structure (issuer, credentialSubject, proof, credentialStatus)
- `VerifiablePresentation`: Holder's presentation of credentials
- `CredentialReference`: Reference to credential stored elsewhere
- `VerificationStatus`: Current verification status with detailed check results
- `CredentialRequirement`: Specification of required credentials
- `CredentialQuery`: Query endpoint and method for requesting credentials

**Example Usage**: See `outputs/08_W3C_Verifiable_Credentials_Guide.md` for comprehensive guide

---

## Schema Composition Pattern

All schemas follow the JSON-LD composition pattern:

```json
{
  "@context": "<schema-context-uri>",
  "@type": "<SchemaType>",
  "<property1>": "<value1>",
  "<property2>": "<value2>",
  ...
}
```

**Required Properties**:
- `@context`: JSON-LD context URI (points to `context.jsonld`)
- `@type`: Schema type name (e.g., "EnergyResource", "EnergyTradeOffer")

**Additional Properties**: Defined per schema in the YAML files.

---

## Relationship to Protocol Specifications

These schemas are replicas and extensions of the schemas in:

```
../protocol-specifications-new/schema/Energy*/
```

**Key Differences**:
1. **New Core Schemas**: EnergyOffer (v1) and EnergyContract (v1) as core primitives
2. **Role-Based Participation**: Contracts use roles (BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR)
3. **Computational Contracts**: Revenue flows computed from input parameters, signals, and telemetry
4. **OfferCurve**: Unified terminology replacing "bid curve" (currency, minExport, maxExport, curve)
5. **Extended with Coordination**: Added offer curves, objectives, locational pricing, settlement, market clearing
6. **Detailed Documentation**: Comprehensive property descriptions and examples
7. **Composition Examples**: Shows how schemas compose within example JSONs
8. **Removed Deprecated Schemas**: EnergyTradeOffer and EnergyTradeContract have been removed (use EnergyOffer and EnergyContract instead)

---

## Usage in Example JSONs

These schemas are used in the example JSON messages in:

- `outputs/examples/ev_charging_demand_flexibility/`
- `outputs/examples/p2p_trading_market_based/`
- `outputs/examples/aggregate_action/`

**Example Composition**:

```json
{
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
            { "inputName": "price", "inputType": "NUMBER" }
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
      "status": "PENDING"
    }
  },
  "beckn:orderAttributes": {
    "@context": "https://deg.energy/schema/EnergyContract/v1/context.jsonld",
    "@type": "EnergyContract",
    "contractId": "contract-walk-in-001",
    "roles": [
      { "role": "SELLER", "filledBy": "bpp.cpo.example.com", "filled": true },
      { "role": "BUYER", "filledBy": "bap.ev-user-app.com", "filled": true }
    ],
    "status": "ACTIVE",
    "inputParameters": {
      "SELLER": { "price": 0.12 },
      "BUYER": { "accept": true }
    },
    "revenueFlows": [ /* ... */ ]
  },
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "deliveryMode": "GRID_INJECTION",
    "offerCurve": {
      "currency": "INR",
      "minExport": 0,
      "maxExport": 5,
      "curve": [
        { "price": 0.05, "powerKW": 0 },
        { "price": 0.06, "powerKW": 2 },
        { "price": 0.07, "powerKW": 5 }
      ]
    }
  }
}
```

---

## Validation

These schemas can be validated using:

1. **OpenAPI Validator**: Validate YAML structure
2. **JSON-LD Validator**: Validate JSON-LD context and type resolution
3. **SHACL Validator**: Validate data shapes (if `shacl_attributes.jsonld` exists)

---

## Related Documentation

- **Taxonomy**: See `outputs/06_Beckn_API_Taxonomy.md` for complete reference of all Beckn API slots
- **Schema Extensions**: See `outputs/05_Schema_Extensions.md` for JSON-LD context and vocabulary definitions
- **Building Blocks**: See `outputs/02_Building_Block_Extensions.md` for architectural rationale
- **Sequence Diagrams**: See `outputs/03_Use_Case_Sequence_Diagrams.md` for use case flows

---

---

## Schema Migration Guide

### From EnergyTradeOffer to EnergyOffer

**Old Schema** (DEPRECATED):
```json
{
  "beckn:offerAttributes": {
    "@type": "EnergyTradeOffer",
    "pricingModel": "PER_KWH",
    "bidCurve": [ /* ... */ ]
  }
}
```

**New Schema**:
```json
{
  "beckn:offerAttributes": {
    "@type": "EnergyOffer",
    "offerId": "offer-001",
    "contractId": "contract-001",
    "providerId": "bpp.cpo.example.com",
    "providerUri": "https://bpp.cpo.example.com",
    "openRole": "BUYER",
    "contract": { /* EnergyContract definition */ }
  }
}
```

### From EnergyTradeContract to EnergyContract

**Old Schema** (DEPRECATED):
```json
{
  "beckn:orderAttributes": {
    "@type": "EnergyTradeContract",
    "contractStatus": "ACTIVE",
    "sourceMeterId": "100200300",
    "targetMeterId": "98765456"
  }
}
```

**New Schema**:
```json
{
  "beckn:orderAttributes": {
    "@type": "EnergyContract",
    "contractId": "contract-001",
    "roles": [
      { "role": "SELLER", "filledBy": "bpp.cpo.example.com", "filled": true },
      { "role": "BUYER", "filledBy": "bap.ev-user-app.com", "filled": true }
    ],
    "status": "ACTIVE",
    "inputParameters": { /* ... */ },
    "revenueFlows": { /* ... */ }
  }
}
```

### From bidCurve to offerCurve

**Old Schema** (DEPRECATED):
```json
{
  "bidCurve": [
    { "price": 0.05, "powerKW": 0 },
    { "price": 0.06, "powerKW": 2 }
  ]
}
```

**New Schema**:
```json
{
  "offerCurve": {
    "currency": "INR",
    "minExport": 0,
    "maxExport": 5,
    "curve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 2 },
      { "price": 0.07, "powerKW": 5 }
    ]
  }
}
```

### Role Updates

**Old Roles**: BUYER, SELLER, TRADER

**New Roles**: BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR

- **PROSUMER**: Producer and/or consumer (used in market clearing contracts)
- **MARKET_CLEARING_AGENT**: Market clearing agent that aggregates bids and clears market
- **AGGREGATOR**: Market intermediary (replaces TRADER)
- **GRID_OPERATOR**: Grid operator managing grid infrastructure

---

**Status**: Complete  
**Version**: 2.0  
**Last Updated**: December 2024

