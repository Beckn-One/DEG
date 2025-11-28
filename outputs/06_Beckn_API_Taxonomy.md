# Beckn API Taxonomy
## Complete Reference of Core Beckn API Slots and Properties

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document provides a comprehensive taxonomy of all core Beckn Protocol v2 API slots (attribute containers) and the properties of objects that go into those slots. This serves as a reference for understanding how domain-specific schemas (like EnergyResource, EnergyTradeOffer, etc.) compose with Beckn core objects.

---

## Table of Contents

1. [Attribute Slots Overview](#1-attribute-slots-overview)
2. [Core Objects and Their Attribute Slots](#2-core-objects-and-their-attribute-slots)
3. [Attribute Slot Properties](#3-attribute-slot-properties)
4. [Composition Pattern](#4-composition-pattern)
5. [Energy Domain Extensions](#5-energy-domain-extensions)

---

## 1. Attribute Slots Overview

**Attribute Slots** are JSON-LD aware containers (`Attributes` class) that attach domain-specific schemas to Beckn core objects. All attribute slots follow the same pattern:

```json
{
  "@context": "<schema-context-uri>",
  "@type": "<SchemaType>",
  "<property1>": "<value1>",
  "<property2>": "<value2>",
  ...
}
```

**Key Requirements**:
- MUST include `@context` (URI to context.jsonld)
- MUST include `@type` (schema type name)
- Additional properties allowed per JSON-LD context

---

## 2. Core Objects and Their Attribute Slots

### 2.1 Catalog

**Core Object**: `beckn:Catalog`

**Attribute Slots**: None (Catalog is a container, not extended via attributes)

**Core Properties**:
- `beckn:id`: Catalog identifier
- `beckn:descriptor`: Human-readable metadata
- `beckn:bppId`: BPP identifier
- `beckn:bppUri`: BPP URI endpoint
- `beckn:items`: Array of `beckn:Item` objects
- `beckn:offers`: Array of `beckn:Offer` objects
- `beckn:validity`: Time period when catalog is valid
- `beckn:isActive`: Whether catalog is active

---

### 2.2 Item

**Core Object**: `beckn:Item`

**Attribute Slot**: `beckn:itemAttributes`

**Core Properties**:
- `beckn:id`: Item identifier
- `beckn:descriptor`: Human-readable metadata (`schema:name`, `beckn:shortDesc`, `beckn:longDesc`, `schema:image`)
- `beckn:category`: Category classification (`CategoryCode`)
- `beckn:availableAt`: Array of `Location` objects (physical locations)
- `beckn:availabilityWindow`: Array of `TimePeriod` objects
- `beckn:rateable`: Whether item can be rated
- `beckn:rating`: Rating summary (`Rating`)
- `beckn:isActive`: Whether item is active
- `beckn:networkId`: Array of network identifiers
- `beckn:provider`: Provider reference (`Provider`)

**Attribute Slot Properties** (`beckn:itemAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required, e.g., "EnergyResource", "ChargingService")
- Additional properties per domain schema

**Example Energy Domain**:
- `sourceType`: SOLAR, BATTERY, GRID, HYBRID, RENEWABLE
- `deliveryMode`: EV_CHARGING, BATTERY_SWAP, V2G, GRID_INJECTION
- `meterId`: IEEE 2030.5 mRID
- `bidCurve`: Array of price/power pairs
- `objectives`: Energy objectives (goals, constraints)
- `locationalPriceAdder`: Grid node congestion pricing
- `gridConstraints`: Grid operational constraints

---

### 2.3 Offer

**Core Object**: `beckn:Offer`

**Attribute Slot**: `beckn:offerAttributes`

**Core Properties**:
- `beckn:id`: Offer identifier
- `beckn:descriptor`: Human-readable metadata
- `beckn:provider`: Provider reference
- `beckn:items`: Array of item identifiers this offer applies to
- `beckn:addOns`: Array of additional offers
- `beckn:addOnItems`: Array of additional items
- `beckn:isActive`: Whether offer is active
- `beckn:validity`: Offer validity window (`TimePeriod`)
- `beckn:price`: Price specification (`PriceSpecification`)
- `beckn:eligibleRegion`: Array of eligible regions (`Location`)
- `beckn:acceptedPaymentMethod`: Array of accepted payment methods

**Attribute Slot Properties** (`beckn:offerAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required, e.g., "EnergyTradeOffer", "EvChargingOffer")
- Additional properties per domain schema

**Example Energy Domain**:
- `pricingModel`: PER_KWH, TIME_OF_DAY, SUBSCRIPTION, FIXED, PAY_AS_CLEAR
- `settlementType`: REAL_TIME, HOURLY, DAILY, WEEKLY, MONTHLY
- `wheelingCharges`: Utility transmission charges
- `minimumQuantity` / `maximumQuantity`: Tradable quantity limits
- `validityWindow`: Offer validity period
- `timeOfDayRates`: Time-based pricing rates
- `bidCurve`: Array of price/power pairs
- `clearingPrice`: Market-cleared price
- `setpointKW`: Optimal power setpoint
- `locationalPriceAdder`: Locational pricing
- `locationalPrice`: Final price with locational adder

---

### 2.4 Order

**Core Object**: `beckn:Order`

**Attribute Slots**: 
- `beckn:orderAttributes` (order-level)
- `beckn:orderItemAttributes` (line-level, in `OrderItem`)

**Core Properties**:
- `beckn:id`: Order identifier
- `beckn:orderStatus`: Order lifecycle status (CREATED, PENDING, CONFIRMED, INPROGRESS, PARTIALLYFULFILLED, COMPLETED, CANCELLED, REJECTED, FAILED, RETURNED, REFUNDED, ONHOLD)
- `beckn:orderNumber`: Human-visible order number
- `beckn:seller`: Seller/provider reference
- `beckn:buyer`: Buyer reference (`Buyer`)
- `beckn:orderItems`: Array of order line items (`OrderItem`)
- `beckn:acceptedOffers`: Array of accepted offers
- `beckn:orderValue`: Total order value (`PriceSpecification`)
- `beckn:invoice`: Invoice reference
- `beckn:payment`: Payment instrument/status (`Payment`)
- `beckn:fulfillment`: Fulfillment details (`Fulfillment`)

**Attribute Slot Properties** (`beckn:orderAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required, e.g., "EnergyTradeContract")
- Additional properties per domain schema

**Example Energy Domain**:
- `contractStatus`: PENDING, ACTIVE, COMPLETED, TERMINATED
- `sourceMeterId` / `targetMeterId`: IEEE 2030.5 mRID
- `contractedQuantity`: Contracted energy in kWh
- `tradeStartTime` / `tradeEndTime`: Contract time window
- `settlementCycles`: Array of settlement periods
- `billingCycles`: Array of billing periods
- `wheelingCharges`: Utility charges breakdown
- `bidCurve`: Bid curve submitted during init
- `objectives`: Resource objectives
- `approvedMaxTradeKW`: Utility-approved trade limit
- `clearingPrice`: Market-cleared price (locked at confirmation)
- `setpointKW`: Confirmed power setpoint
- `locationalPrice`: Final price with locational adder
- `settlement`: Settlement information (revenue flows, settlement report)
- `offsetCommand`: Grid operator offset command

**Attribute Slot Properties** (`beckn:orderItemAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per domain schema (line-level specifics)

---

### 2.5 OrderItem

**Core Object**: `beckn:OrderItem`

**Attribute Slot**: `beckn:orderItemAttributes`

**Core Properties**:
- `beckn:lineId`: Unique line identifier within order
- `beckn:orderedItem`: Reference to catalog item (`Item.id`)
- `beckn:acceptedOffer`: Offer applied to this line (`Offer`)
- `beckn:quantity`: Ordered quantity (`Quantity`)
- `beckn:price`: Line price composition (`PriceSpecification`)

**Attribute Slot Properties** (`beckn:orderItemAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per domain schema (line-level options, substitutions, ESG, etc.)

---

### 2.6 Fulfillment

**Core Object**: `beckn:Fulfillment`

**Attribute Slot**: `beckn:deliveryAttributes` (also `beckn:attributes` in some contexts)

**Core Properties**:
- `beckn:id`: Fulfillment identifier
- `beckn:fulfillmentStatus`: Fulfillment status code
- `beckn:mode`: Fulfillment mode (DELIVERY, PICKUP, RESERVATION, DIGITAL)
- `trackingAction`: Tracking entrypoint (`TrackAction`)

**Attribute Slot Properties** (`beckn:deliveryAttributes` or `beckn:attributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required, e.g., "EnergyTradeDelivery", "EvChargingSession")
- Additional properties per domain schema

**Mode-Specific Mappings**:
- **DELIVERY**: Maps to `schema:ParcelDelivery` / `schema:DeliveryEvent` (endpoints, slot windows, route & events)
- **PICKUP**: Maps to `schema:Place` + `schema:openingHoursSpecification` (pickupPlace, counter codes, time windows)
- **RESERVATION**: Maps to `schema:Reservation` (reservationStatus, reservedTicket)
- **DIGITAL**: Maps to `schema:DataDownload` / `schema:MediaObject` (contentUrl, license, expiry)

**Example Energy Domain**:
- `deliveryStatus`: PENDING, IN_PROGRESS, COMPLETED, FAILED
- `deliveryMode`: EV_CHARGING, BATTERY_SWAP, V2G, GRID_INJECTION
- `deliveredQuantity`: Quantity delivered in kWh
- `deliveryStartTime` / `deliveryEndTime`: Delivery time window
- `meterReadings`: Array of meter readings during delivery
- `telemetry`: Energy flow telemetry data
- `settlementCycleId`: Associated settlement cycle identifier
- `offsetCommand`: Grid operator offset command
- `deviationPenalty`: Penalty for net imbalance

---

### 2.7 Payment

**Core Object**: `beckn:Payment`

**Attribute Slot**: `beckn:paymentAttributes`

**Core Properties**:
- `beckn:id`: Payment record identifier
- `beckn:paymentStatus`: Payment lifecycle status (INITIATED, PENDING, AUTHORIZED, CAPTURED, COMPLETED, FAILED, CANCELLED, REFUNDED, PARTIALLY_REFUNDED, CHARGEBACK, DISPUTED, EXPIRED, REVERSED, VOIDED, SETTLED, ON_HOLD, ADJUSTED)
- `beckn:amount`: Amount object (`MonetaryAmount` with currency and value)
- `beckn:paymentURL`: URL for payment processing/redirection
- `beckn:txnRef`: PSP/gateway/bank transaction reference
- `beckn:paidAt`: Timestamp of last terminal payment event
- `beckn:acceptedPaymentMethod`: Array of accepted payment methods
- `beckn:beneficiary`: Payment beneficiary (BPP, BAP)

**Attribute Slot Properties** (`beckn:paymentAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per payment rail (UPI: VPA/UTR; CARD: token/3DS; BNPL: plan/schedule)

---

### 2.8 Provider

**Core Object**: `beckn:Provider`

**Attribute Slot**: `beckn:providerAttributes`

**Core Properties**:
- `beckn:id`: Provider identifier
- `beckn:descriptor`: Human-readable metadata
- `beckn:validity`: Provider validity window
- `beckn:locations`: Array of physical locations (`Location`)
- `beckn:rateable`: Whether provider can be rated
- `beckn:rating`: Rating summary (`Rating`)

**Attribute Slot Properties** (`beckn:providerAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per domain schema (provider-level metadata)

---

### 2.9 Buyer

**Core Object**: `beckn:Buyer`

**Attribute Slot**: `beckn:buyerAttributes`

**Core Properties**:
- `beckn:id`: Buyer identifier (personId or orgId)
- `beckn:role`: Functional role (BUYER, SELLER, INTERMEDIARY, PAYER, PAYEE, FULFILLER)
- `beckn:displayName`: Human-readable display name
- `beckn:taxID`: Tax identifier

**Attribute Slot Properties** (`beckn:buyerAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per domain schema:
  - **buyer/identity.v1**: Contact details (email, phone, address)
  - **buyer/org-ids.v1**: Organization identifiers (LEI, GSTIN, ISIN, CUSIP)
  - **buyer/kyc.v1**: Jurisdictional compliance fields
  - **buyer/preferences.v1**: Delivery preferences, accessibility needs

---

### 2.10 Invoice

**Core Object**: `beckn:Invoice`

**Attribute Slot**: `beckn:invoiceAttributes`

**Core Properties**:
- `beckn:id`: Invoice identifier
- `beckn:number`: Human-visible invoice number
- `beckn:issueDate`: Invoice issue date
- `beckn:dueDate`: Payment due date
- `beckn:payee`: Seller/issuer reference
- `beckn:payer`: Buyer reference
- `beckn:totals`: Invoice totals (`PriceSpecification`)

**Attribute Slot Properties** (`beckn:invoiceAttributes`):
- `@context`: JSON-LD context URI (required)
- `@type`: Schema type (required)
- Additional properties per domain schema (tax regime: GST/VAT, e-invoice refs, legal boilerplate)

---

## 3. Attribute Slot Properties

### 3.1 Common Properties (All Attribute Slots)

All attribute slots share these required properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@context` | string (URI) | ✅ Yes | JSON-LD context URI for the domain schema |
| `@type` | string | ✅ Yes | JSON-LD type within the domain schema |

**Example**:
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyResource/v0.2/context.jsonld",
  "@type": "EnergyResource",
  "sourceType": "SOLAR",
  "deliveryMode": "GRID_INJECTION"
}
```

### 3.2 Attributes Class Structure

The `Attributes` class is a JSON-LD aware container:

```yaml
Attributes:
  type: object
  required: ["@context", "@type"]
  minProperties: 2
  additionalProperties: true
  properties:
    "@context":
      type: string
      format: uri
    "@type":
      type: string
```

**Key Points**:
- `additionalProperties: true` allows domain schemas to add any properties
- Properties are interpreted per the provided JSON-LD context
- Domain schemas define their own property structures

---

## 4. Composition Pattern

### 4.1 How Domain Schemas Compose

Domain schemas (like `EnergyResource`, `EnergyTradeOffer`) compose with Beckn core objects via attribute slots:

```
Beckn Core Object
  ├── Core Properties (beckn:id, beckn:descriptor, etc.)
  └── Attribute Slot (beckn:itemAttributes, beckn:offerAttributes, etc.)
      └── Domain Schema Object
          ├── @context (JSON-LD context URI)
          ├── @type (Schema type)
          └── Domain-specific properties
```

### 4.2 Example Composition

**Item with EnergyResource**:
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
  "@type": "beckn:Item",
  "beckn:id": "energy-resource-solar-001",
  "beckn:descriptor": {
    "@type": "beckn:Descriptor",
    "schema:name": "Solar Energy - 30.5 kWh"
  },
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "deliveryMode": "GRID_INJECTION",
    "meterId": "100200300",
    "bidCurve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 2 },
      { "price": 0.07, "powerKW": 5 }
    ]
  }
}
```

**Order with EnergyTradeContract + Settlement**:
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
  "@type": "beckn:Order",
  "beckn:id": "order-energy-001",
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyTradeContract/v0.2/context.jsonld",
    "@type": "EnergyTradeContract",
    "contractStatus": "COMPLETED",
    "clearingPrice": 0.0625,
    "setpointKW": -8.0,
    "settlement": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
      "@type": "Settlement",
      "revenueFlows": [...],
      "settlementReport": {...}
    }
  }
}
```

---

## 5. Energy Domain Extensions

### 5.1 Attribute Slot Mapping

| Domain Schema | Attribute Slot | Use Case |
|---------------|----------------|----------|
| **EnergyResource** | `Item.itemAttributes` | Energy source characteristics, bid curves, objectives, locational pricing |
| **EnergyTradeOffer** | `Offer.offerAttributes` | Pricing models, settlement types, bid curves, clearing prices |
| **EnergyTradeContract** | `Order.orderAttributes` | Contract status, meter IDs, settlement, clearing prices, setpoints |
| **EnergyTradeDelivery** | `Fulfillment.attributes` | Delivery status, meter readings, telemetry, offset commands |
| **GridNode** | `Item.itemAttributes` | Grid node characteristics, locational pricing, grid constraints |
| **Settlement** | `Order.orderAttributes` | Multi-party revenue flows, settlement reports |
| **EnergyObjectives** | `Item.itemAttributes`, `Order.orderAttributes` | Resource objectives, goals, constraints |
| **BidCurve** | `Item.itemAttributes`, `Offer.offerAttributes`, `Order.orderAttributes` | Price/power preferences for market clearing |

### 5.2 Coordination Extensions

**EnergyCoordination/v1** provides shared schemas used across multiple attribute slots:

| Schema | Used In | Purpose |
|--------|---------|---------|
| `BidCurvePoint` | `itemAttributes`, `offerAttributes`, `orderAttributes` | Price/power pair |
| `BidCurveConstraints` | `itemAttributes`, `offerAttributes`, `orderAttributes` | Operational constraints |
| `EnergyObjectives` | `itemAttributes`, `orderAttributes` | Goals and constraints |
| `LocationalPriceAdder` | `itemAttributes`, `offerAttributes` | Grid congestion pricing |
| `GridConstraints` | `itemAttributes` | Grid node constraints |
| `Settlement` | `orderAttributes` | Multi-party revenue flows |
| `OffsetCommand` | `orderAttributes`, `fulfillmentAttributes` | Grid operator commands |

---

## 6. Complete Attribute Slot Reference

### 6.1 Item.itemAttributes

**Attaches to**: `beckn:Item`

**Common Domain Schemas**:
- `EnergyResource` (P2P energy trading)
- `ChargingService` (EV charging)
- `GridNode` (Grid infrastructure nodes)

**Properties** (EnergyResource example):
- Core: `sourceType`, `deliveryMode`, `certificationStatus`, `meterId`, `inverterId`, `availableQuantity`, `productionWindow`, `sourceVerification`, `productionAsynchronous`
- Coordination: `bidCurve`, `constraints`, `objectives`, `locationalPriceAdder`, `gridConstraints`

---

### 6.2 Offer.offerAttributes

**Attaches to**: `beckn:Offer`

**Common Domain Schemas**:
- `EnergyTradeOffer` (P2P energy trading)
- `EvChargingOffer` (EV charging)

**Properties** (EnergyTradeOffer example):
- Core: `pricingModel`, `settlementType`, `wheelingCharges`, `minimumQuantity`, `maximumQuantity`, `validityWindow`, `timeOfDayRates`
- Coordination: `bidCurve`, `constraints`, `clearingPrice`, `setpointKW`, `locationalPriceAdder`, `locationalPrice`

---

### 6.3 Order.orderAttributes

**Attaches to**: `beckn:Order`

**Common Domain Schemas**:
- `EnergyTradeContract` (P2P energy trading)

**Properties** (EnergyTradeContract example):
- Core: `contractStatus`, `sourceMeterId`, `targetMeterId`, `inverterId`, `contractedQuantity`, `tradeStartTime`, `tradeEndTime`, `sourceType`, `certification`, `settlementCycles`, `billingCycles`, `wheelingCharges`, `lastUpdated`
- Coordination: `bidCurve`, `objectives`, `approvedMaxTradeKW`, `clearingPrice`, `setpointKW`, `locationalPrice`, `settlement`, `offsetCommand`

---

### 6.4 OrderItem.orderItemAttributes

**Attaches to**: `beckn:OrderItem`

**Common Domain Schemas**: Line-level specifics (options, substitutions, ESG)

**Properties**: Domain-specific (typically simpler than order-level)

---

### 6.5 Fulfillment.attributes (or deliveryAttributes)

**Attaches to**: `beckn:Fulfillment`

**Common Domain Schemas**:
- `EnergyTradeDelivery` (P2P energy trading)
- `EvChargingSession` (EV charging)

**Properties** (EnergyTradeDelivery example):
- Core: `deliveryStatus`, `deliveryMode`, `deliveredQuantity`, `deliveryStartTime`, `deliveryEndTime`, `meterReadings`, `telemetry`, `settlementCycleId`, `lastUpdated`
- Coordination: `offsetCommand`, `deviationPenalty`

---

### 6.6 Payment.paymentAttributes

**Attaches to**: `beckn:Payment`

**Common Domain Schemas**: Payment rail-specific (UPI, Card, BNPL, Wallet)

**Properties**: Rail-specific (VPA/UTR for UPI, token/3DS for Card, plan/schedule for BNPL)

---

### 6.7 Provider.providerAttributes

**Attaches to**: `beckn:Provider`

**Common Domain Schemas**: Provider-level metadata

**Properties**: Domain-specific (provider characteristics, certifications, etc.)

---

### 6.8 Buyer.buyerAttributes

**Attaches to**: `beckn:Buyer`

**Common Domain Schemas**:
- `buyer/identity.v1`: Contact details
- `buyer/org-ids.v1`: Organization identifiers
- `buyer/kyc.v1`: KYC compliance
- `buyer/preferences.v1`: Preferences

**Properties**: Domain-specific per schema type

---

### 6.9 Invoice.invoiceAttributes

**Attaches to**: `beckn:Invoice`

**Common Domain Schemas**: Tax regime specifics (GST/VAT, e-invoice refs)

**Properties**: Tax regime-specific

---

## 7. Summary Table

| Core Object | Attribute Slot | Domain Schema Examples | Coordination Extensions |
|-------------|----------------|------------------------|------------------------|
| `Item` | `itemAttributes` | EnergyResource, ChargingService, GridNode | bidCurve, objectives, locationalPriceAdder, gridConstraints |
| `Offer` | `offerAttributes` | EnergyTradeOffer, EvChargingOffer | bidCurve, clearingPrice, setpointKW, locationalPriceAdder |
| `Order` | `orderAttributes` | EnergyTradeContract | bidCurve, objectives, clearingPrice, setpointKW, settlement, offsetCommand |
| `OrderItem` | `orderItemAttributes` | Line-level specifics | (typically none) |
| `Fulfillment` | `attributes` / `deliveryAttributes` | EnergyTradeDelivery, EvChargingSession | offsetCommand, deviationPenalty |
| `Payment` | `paymentAttributes` | Payment rail-specific | (none) |
| `Provider` | `providerAttributes` | Provider metadata | (none) |
| `Buyer` | `buyerAttributes` | Identity, KYC, preferences | (none) |
| `Invoice` | `invoiceAttributes` | Tax regime specifics | (none) |

---

## 8. JSON-LD Context Resolution

### 8.1 Context URI Pattern

All attribute slots reference their domain schema context:

```
https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/{DomainSchema}/{Version}/context.jsonld
```

**Examples**:
- `EnergyResource/v0.2/context.jsonld`
- `EnergyTradeOffer/v0.2/context.jsonld`
- `EnergyCoordination/v1/context.jsonld`
- `EvChargingService/v1/context.jsonld`

### 8.2 Type Resolution

The `@type` value resolves to a class in the vocabulary:

```
{context-uri}#{TypeName}
```

**Example**:
- `@context`: `.../EnergyResource/v0.2/context.jsonld`
- `@type`: `EnergyResource`
- Resolves to: `.../EnergyResource/v0.2/vocab.jsonld#EnergyResource`

---

## 9. Best Practices

### 9.1 Schema Composition

1. **Always include `@context` and `@type`**: Required for JSON-LD resolution
2. **Use proper context URIs**: Point to the correct schema version
3. **Compose, don't extend**: Add new properties via attribute slots, don't modify core objects
4. **Reuse shared schemas**: Use `EnergyCoordination/v1` for coordination extensions

### 9.2 Property Naming

1. **Follow domain conventions**: Use domain-specific property names (e.g., `meterId`, `sourceType`)
2. **Use consistent units**: Power in kW, energy in kWh, prices per kWh
3. **Document enums**: Clearly document allowed values (SOLAR, BATTERY, etc.)

### 9.3 Versioning

1. **Version schemas independently**: Domain schemas version separately from core
2. **Maintain backward compatibility**: New versions should extend, not break
3. **Document breaking changes**: Clearly mark incompatible changes

---

**Status**: Complete  
**Next Action**: Use this taxonomy as reference for schema composition and validation

