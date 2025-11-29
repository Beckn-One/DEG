# Energy Domain Schema Extensions

This directory contains detailed OpenAPI 3.1.1 attribute schema definitions for Energy domain extensions to the Beckn Protocol. These schemas define the structure of objects that compose within Beckn core attribute slots (`itemAttributes`, `offerAttributes`, `orderAttributes`, `fulfillmentAttributes`).

---

## Directory Structure

```
schema/
├── EnergyResource/
│   └── v0.2/
│       └── attributes.yaml          # Item.itemAttributes schema
├── EnergyTradeOffer/
│   └── v0.2/
│       └── attributes.yaml          # Offer.offerAttributes schema
├── EnergyTradeContract/
│   └── v0.2/
│       └── attributes.yaml          # Order.orderAttributes schema
├── EnergyTradeDelivery/
│   └── v0.2/
│       └── attributes.yaml          # Fulfillment.attributes schema
├── EnergyCoordination/
│   └── v1/
│       └── attributes.yaml          # Shared coordination schemas
├── GridNode/
│   └── v1/
│       └── attributes.yaml          # Grid node attributes (transformers, substations)
└── EnergyCredentials/
    └── v1/
        └── attributes.yaml          # W3C Verifiable Credentials for energy resources
```

---

## Schema Files

### EnergyResource/v0.2/attributes.yaml

**Purpose**: Defines attributes for energy resources (generators, storage, consumers, infrastructure).

**Attaches to**: `Item.itemAttributes`

**Key Properties**:
- **Core**: `sourceType`, `deliveryMode`, `certificationStatus` (optional), `meterId`, `inverterId` (optional), `productionWindow`
- **Coordination Extensions**: `bidCurve`, `constraints`, `objectives`

**Example Usage**: See `outputs/examples/ev_charging_demand_flexibility/discover-with-bid-curve.json`

---

### EnergyTradeOffer/v0.2/attributes.yaml

**Purpose**: Defines attributes for energy trade offers (pricing, settlement, availability).

**Attaches to**: `Offer.offerAttributes`

**Key Properties**:
- **Core**: `pricingModel`, `settlementType`, `wheelingCharges` (optional), `minimumQuantity`, `maximumQuantity`, `validityWindow`, `timeOfDayRates` (optional)
- **Coordination Extensions**: `bidCurve`, `constraints`, `clearingPrice`, `setpointKW`

**Example Usage**: See `outputs/examples/p2p_trading_market_based/` directory

---

### EnergyTradeContract/v0.2/attributes.yaml

**Purpose**: Defines attributes for energy trade contracts (commercial agreements, settlement, billing).

**Attaches to**: `Order.orderAttributes`

**Key Properties**:
- **Core**: `contractStatus`, `sourceMeterId`, `targetMeterId`, `inverterId` (optional), `contractedQuantity`, `tradeStartTime`, `tradeEndTime`, `settlementCycles`, `billingCycles`
- **Coordination Extensions**: `bidCurve`, `objectives`, `approvedMaxTradeKW`, `clearingPrice`, `setpointKW`, `settlement`, `offsetCommand` (optional)

**Example Usage**: See `outputs/examples/p2p_trading_market_based/order-with-settlement.json`

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
- `BidCurvePoint`: Price/power pair
- `BidCurveConstraints`: Operational constraints
- `EnergyObjectives`: Goals and constraints (targetChargeKWh, targetGenerationKWh, targetReductionKW, deadline, maxPricePerKWh, minPricePerKWh (optional), preferredSource (optional))
- `Settlement`: Multi-party revenue flows (revenueFlows, settlementReport)
- `SettlementReport`: Billing document (reportId, totalAmount, currency, generatedAt)
- `OffsetCommand`: Grid operator commands
- `AggregationRequest` / `AggregationResult`: Market clearing schemas

**Note**: `LocationalPriceAdder` and `GridConstraints` have been moved to the `GridNode` schema.

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
1. **Extended with Coordination**: Added bid curves, objectives, locational pricing, settlement, market clearing
2. **Detailed Documentation**: Comprehensive property descriptions and examples
3. **Composition Examples**: Shows how schemas compose within example JSONs

---

## Usage in Example JSONs

These schemas are used in the example JSON messages in:

- `outputs/examples/ev_charging_demand_flexibility/`
- `outputs/examples/p2p_trading_market_based/`
- `outputs/examples/aggregate_action/`

**Example Composition**:

```json
{
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "deliveryMode": "GRID_INJECTION",
    "bidCurve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 2 },
      { "price": 0.07, "powerKW": 5 }
    ]
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

**Status**: Complete  
**Version**: 1.0  
**Last Updated**: December 2024

