# P2P Energy Trading Implementation Guide

## Overview

This implementation guide provides comprehensive instructions for implementing Peer-to-Peer (P2P) Energy Trading using Beckn Protocol v2 with composable schemas. This guide covers all transaction flows, field mappings, best practices, and migration from v1.

## Table of Contents

- [P2P Energy Trading Implementation Guide](#p2p-energy-trading-implementation-guide)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [What is P2P Energy Trading?](#what-is-p2p-energy-trading)
    - [Beckn Protocol v2 for Energy Trading](#beckn-protocol-v2-for-energy-trading)
  - [Architecture Overview](#architecture-overview)
    - [v2 Composable Schema Architecture](#v2-composable-schema-architecture)
    - [Schema Composition Points](#schema-composition-points)
    - [Key Differences from v1](#key-differences-from-v1)
    - [v1 to v2 Quick Reference](#v1-to-v2-quick-reference)
      - [Discover/Search Request](#discoversearch-request)
      - [Item Attributes](#item-attributes)
      - [Order Attributes](#order-attributes)
      - [Fulfillment Stops](#fulfillment-stops)
  - [Schema Overview](#schema-overview)
    - [EnergyResource (Item.itemAttributes)](#energyresource-itemitemattributes)
    - [EnergyTradeOffer (Offer.offerAttributes)](#energytradeoffer-offerofferattributes)
    - [EnergyTradeContract (Order.orderAttributes)](#energytradecontract-orderorderattributes)
    - [EnergyTradeDelivery (Fulfillment.attributes)](#energytradedelivery-fulfillmentattributes)
  - [Transaction Flows](#transaction-flows)
    - [1. Discover Flow](#1-discover-flow)
    - [2. Select Flow](#2-select-flow)
    - [3. Init Flow](#3-init-flow)
    - [4. Confirm Flow](#4-confirm-flow)
    - [5. Status Flow](#5-status-flow)
  - [Field Mapping Reference](#field-mapping-reference)
    - [v1 to v2 Field Mapping](#v1-to-v2-field-mapping)
    - [Meter ID Format Migration](#meter-id-format-migration)
  - [Integration Patterns](#integration-patterns)
    - [1. Attaching Attributes to Core Objects](#1-attaching-attributes-to-core-objects)
    - [2. JSON-LD Context Usage](#2-json-ld-context-usage)
    - [3. Discovery Filtering](#3-discovery-filtering)
  - [Best Practices](#best-practices)
    - [1. Discovery Optimization](#1-discovery-optimization)
    - [2. Meter ID Handling](#2-meter-id-handling)
    - [3. Settlement Cycle Management](#3-settlement-cycle-management)
    - [4. Meter Readings](#4-meter-readings)
    - [5. Telemetry Data](#5-telemetry-data)
    - [6. Error Handling](#6-error-handling)
  - [Migration from v1](#migration-from-v1)
    - [Key Changes](#key-changes)
    - [Migration Checklist](#migration-checklist)
    - [Example Migration](#example-migration)
  - [Examples](#examples)
    - [Complete Examples](#complete-examples)
    - [Example Scenarios](#example-scenarios)
  - [Additional Resources](#additional-resources)
  - [Support](#support)

Table of contents and section auto-numbering was done using [Markdown-All-In-One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one) vscode extension. Specifically `Markdown All in One: Create Table of Contents` and `Markdown All in One: Add/Update section numbers` commands accessible via vs code command pallete.

Example jsons were imported directly from source of truth elsewhere in this repo inline by inserting the pattern below within all json expand blocks, and running this [script](/scripts/embed_example_json.py), e.g. `python3 scripts/embed_example_json.py path_to_markdown_file.md`.

```
<details><summary><a href="/path_to_file_from_root">txt_with_json_keyword</a></summary>

</details>
``` 

---

## Introduction

### What is P2P Energy Trading?

Peer-to-Peer (P2P) energy trading enables energy producers (prosumers) to directly sell excess energy to consumers without going through traditional utility intermediaries. This enables:

- **Decentralized Energy Markets**: Direct trading between producers and consumers
- **Grid Optimization**: Better utilization of distributed energy resources (DERs)
- **Renewable Energy Promotion**: Incentivizes green energy production
- **Cost Efficiency**: Reduces transmission losses and intermediary costs

### Beckn Protocol v2 for Energy Trading

Beckn Protocol v2 provides a composable schema architecture that enables:
- **Modular Attribute Bundles**: Energy-specific attributes attached to core Beckn objects
- **JSON-LD Semantics**: Full semantic interoperability
- **Standards Alignment**: Integration with IEEE 2030.5 (mRID), OCPP, OCPI
- **Flexible Discovery**: Meter-based discovery and filtering

---

## Architecture Overview

### v2 Composable Schema Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Core Beckn Objects                    │
│  Item | Offer | Order | Fulfillment | Provider          │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Attach Attributes
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Energy* Attribute Bundles                    │
│  EnergyResource | EnergyTradeOffer | EnergyTradeContract │
│  EnergyTradeDelivery                                     │
└─────────────────────────────────────────────────────────┘
```

### Schema Composition Points

| Attribute Bundle | Attach To | Purpose |
|------------------|-----------|---------|
| **EnergyResource** | `Item.itemAttributes` | Energy source characteristics (source type, delivery mode, meter ID, availability) |
| **EnergyTradeOffer** | `Offer.offerAttributes` | Pricing models, settlement types, wheeling charges, validity windows |
| **EnergyTradeContract** | `Order.orderAttributes` | Contract status, meter IDs, settlement cycles, billing cycles |
| **EnergyTradeDelivery** | `Fulfillment.attributes` | Delivery status, meter readings, telemetry, settlement linkage |

### Key Differences from v1

| Aspect | v1 (Layer2) | v2 (Composable) |
|--------|-------------|-----------------|
| **Schema Extension** | `allOf` in paths | Composable attribute bundles |
| **Attribute Location** | `Item.attributes.*` | `Item.itemAttributes.*` |
| **Meter Format** | `der://meter/{id}` | IEEE 2030.5 mRID `{id}` |
| **JSON-LD** | Not used | Full JSON-LD support |
| **Modularity** | Monolithic | Modular bundles |

### v1 to v2 Quick Reference

For developers familiar with v1, here's a quick mapping guide:

#### Discover/Search Request

**v1 Format**:
```json
{
  "message": {
    "intent": {
      "item": {
        "quantity": {
          "selected": {
            "measure": {
              "value": "10",
              "unit": "kWH"
            }
          }
        }
      },
      "fulfillment": {
        "stops": [{
          "type": "end",
          "location": {
            "address": "der://uppcl.meter/98765456"
          },
          "time": {
            "range": {
              "start": "2024-10-04T10:00:00",
              "end": "2024-10-04T18:00:00"
            }
          }
        }]
      }
    }
  }
}
```

**v2 Format** (No intent object - uses JSONPath filters):
```json
{
  "message": {
    "text_search": "solar energy grid injection",
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.itemAttributes.sourceType == 'SOLAR' && @.itemAttributes.deliveryMode == 'GRID_INJECTION' && @.itemAttributes.availableQuantity >= 10.0 && @.itemAttributes.productionWindow.start <= '2024-10-04T10:00:00Z' && @.itemAttributes.productionWindow.end >= '2024-10-04T18:00:00Z')]"
    }
  }
}
```

**Changes**:
- ❌ **Removed**: `intent` object is not supported in v2 discover API
- ✅ **Quantity**: v1 `intent.item.quantity.selected.measure.value` → v2 `filters.expression` with `availableQuantity >= 10.0`
- ✅ **Time Range**: v1 `intent.fulfillment.stops[].time.range` → v2 `filters.expression` with `productionWindow.start <= '...' && productionWindow.end >= '...'`
- ✅ **All Parameters**: Expressed via JSONPath filters in v2

#### Item Attributes

**v1 Format**:
```json
{
  "Item": {
    "attributes": {
      "sourceType": "SOLAR",
      "meterId": "der://meter/100200300",
      "availableQuantity": 30.5
    }
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Item",
  "beckn:itemAttributes": {
    "@context": "./context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "meterId": "100200300",
    "availableQuantity": 30.5
  }
}
```

**Changes**:
- ⚠️ Path: `Item.attributes.*` → `beckn:itemAttributes.*`
- ⚠️ Meter format: `der://meter/100200300` → `100200300`
- ➕ Add `@context` and `@type` for JSON-LD

#### Order Attributes

**v1 Format**:
```json
{
  "Order": {
    "attributes": {
      "sourceMeterId": "der://pge.meter/100200300",
      "targetMeterId": "der://ssf.meter/98765456",
      "contractStatus": "ACTIVE"
    }
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Order",
  "beckn:orderAttributes": {
    "@context": "../EnergyTradeContract/v0.2/context.jsonld",
    "@type": "EnergyTradeContract",
    "sourceMeterId": "100200300",
    "targetMeterId": "98765456",
    "contractStatus": "ACTIVE"
  }
}
```

**Changes**:
- ⚠️ Path: `Order.attributes.*` → `beckn:orderAttributes.*`
- ⚠️ Meter format: `der://pge.meter/100200300` → `100200300`
- ➕ Add `@context` and `@type` for JSON-LD

#### Fulfillment Stops

**v1 Format**:
```json
{
  "Fulfillment": {
    "stops": [{
      "type": "start",
      "location": {
        "address": "der://uppcl.meter/92982739"
      }
    }, {
      "type": "end",
      "location": {
        "address": "der://uppcl.meter/98765456"
      }
    }]
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Fulfillment",
  "beckn:stops": [{
    "@type": "beckn:Stop",
    "beckn:type": "START",
    "beckn:location": {
      "@type": "beckn:Location",
      "beckn:address": "92982739"
    }
  }, {
    "@type": "beckn:Stop",
    "beckn:type": "END",
    "beckn:location": {
      "@type": "beckn:Location",
      "beckn:address": "98765456"
    }
  }]
}
```

**Changes**:
- ⚠️ Meter format: `der://uppcl.meter/92982739` → `92982739`
- ⚠️ Type case: `"start"` → `"START"`, `"end"` → `"END"`
- ➕ Add `@type` for JSON-LD

---

## Schema Overview

### EnergyResource (Item.itemAttributes)

**Purpose**: Describes tradable energy resources

**Key Attributes**:
- `sourceType`: SOLAR, BATTERY, GRID, HYBRID, RENEWABLE
- `deliveryMode`: EV_CHARGING, BATTERY_SWAP, V2G, GRID_INJECTION
- `meterId`: IEEE 2030.5 mRID (e.g., `"100200300"`)
- `availableQuantity`: Available energy in kWh
- `productionWindow`: Time window when energy is available
- `sourceVerification`: Verification status and certificates

**Example**:
```json
{
  "@context": "./context.jsonld",
  "@type": "EnergyResource",
  "sourceType": "SOLAR",
  "deliveryMode": "GRID_INJECTION",
  "meterId": "100200300",
  "availableQuantity": 30.5,
  "productionWindow": {
    "start": "2024-10-04T10:00:00Z",
    "end": "2024-10-04T18:00:00Z"
  }
}
```

### EnergyTradeOffer (Offer.offerAttributes)

**Purpose**: Defines pricing and settlement terms for energy trades

**Key Attributes**:
- `pricingModel`: PER_KWH, TIME_OF_DAY, SUBSCRIPTION, FIXED
- `settlementType`: REAL_TIME, HOURLY, DAILY, WEEKLY, MONTHLY
- `wheelingCharges`: Utility transmission charges
- `minimumQuantity` / `maximumQuantity`: Tradable quantity limits
- `validityWindow`: Offer validity period
- `timeOfDayRates`: Time-based pricing (for TIME_OF_DAY model)

**Example**:
```json
{
  "@context": "./context.jsonld",
  "@type": "EnergyTradeOffer",
  "pricingModel": "PER_KWH",
  "settlementType": "DAILY",
  "wheelingCharges": {
    "amount": 2.5,
    "currency": "USD",
    "description": "PG&E Grid Services wheeling charge"
  },
  "minimumQuantity": 1.0,
  "maximumQuantity": 100.0
}
```

### EnergyTradeContract (Order.orderAttributes)

**Purpose**: Tracks commercial agreements and contract lifecycle

**Key Attributes**:
- `contractStatus`: PENDING, ACTIVE, COMPLETED, TERMINATED
- `sourceMeterId` / `targetMeterId`: IEEE 2030.5 mRID
- `contractedQuantity`: Contracted energy in kWh
- `tradeStartTime` / `tradeEndTime`: Contract time window
- `settlementCycles`: Array of settlement periods
- `billingCycles`: Array of billing periods
- `wheelingCharges`: Utility charges breakdown

**Example**:
```json
{
  "@context": "./context.jsonld",
  "@type": "EnergyTradeContract",
  "contractStatus": "ACTIVE",
  "sourceMeterId": "100200300",
  "targetMeterId": "98765456",
  "contractedQuantity": 10.0,
  "settlementCycles": [...],
  "billingCycles": [...]
}
```

### EnergyTradeDelivery (Fulfillment.attributes)

**Purpose**: Tracks physical energy transfer and delivery status

**Key Attributes**:
- `deliveryStatus`: PENDING, IN_PROGRESS, COMPLETED, FAILED
- `deliveryMode`: EV_CHARGING, BATTERY_SWAP, V2G, GRID_INJECTION
- `deliveredQuantity`: Quantity delivered in kWh
- `meterReadings`: Array of meter readings (source, target, energy flow)
- `telemetry`: Energy flow telemetry (ENERGY, POWER, VOLTAGE, etc.)
- `settlementCycleId`: Link to settlement cycle

**Example**:
```json
{
  "@context": "./context.jsonld",
  "@type": "EnergyTradeDelivery",
  "deliveryStatus": "IN_PROGRESS",
  "deliveryMode": "GRID_INJECTION",
  "deliveredQuantity": 9.8,
  "meterReadings": [
    {
      "timestamp": "2024-10-04T12:00:00Z",
      "sourceReading": 1000.5,
      "targetReading": 990.3,
      "energyFlow": 10.2
    }
  ],
  "telemetry": [...]
}
```

---

## Transaction Flows

### 1. Discover Flow

**Purpose**: Search for available energy resources

**Endpoint**: `GET /beckn/discover`

**v1 to v2 Mapping**:
- v1 `message.intent.item.quantity.selected.measure` → v2 `message.filters.expression` (JSONPath filter on `availableQuantity`)
- v1 `message.intent.fulfillment.stops[].time.range.start` → v2 `message.filters.expression` (JSONPath filter on `productionWindow.start`)
- v1 `message.intent.fulfillment.stops[].time.range.end` → v2 `message.filters.expression` (JSONPath filter on `productionWindow.end`)
- **Note**: v2 does not support `intent` object. All search parameters are expressed via JSONPath filters.

<details>
<summary><a href="./examples/discover-request.json">Request Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "discover",
    "timestamp": "2024-10-04T10:00:00Z",
    "message_id": "msg-discover-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade",
    "location": {
      "city": {
        "code": "BLR",
        "name": "Bangalore"
      },
      "country": {
        "code": "IND",
        "name": "India"
      }
    }
  },
  "message": {
    "text_search": "solar energy grid injection",
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.itemAttributes.sourceType == 'SOLAR' && @.itemAttributes.deliveryMode == 'GRID_INJECTION' && @.itemAttributes.availableQuantity >= 10.0 && @.itemAttributes.productionWindow.start <= '2024-10-04T10:00:00Z' && @.itemAttributes.productionWindow.end >= '2024-10-04T18:00:00Z')]"
    }
  }
}


```
</details>

<details>
<summary><a href="./examples/discover-response.json">Response Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_discover",
    "timestamp": "2024-10-04T10:00:05Z",
    "message_id": "msg-on-discover-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "catalogs": [
      {
        "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
        "@type": "beckn:Catalog",
        "beckn:id": "catalog-energy-001",
        "beckn:descriptor": {
          "@type": "beckn:Descriptor",
          "schema:name": "Solar Energy Trading Catalog"
        },
        "beckn:items": [
          {
            "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
            "@type": "beckn:Item",
            "beckn:id": "energy-resource-solar-001",
            "beckn:descriptor": {
              "@type": "beckn:Descriptor",
              "schema:name": "Solar Energy - 30.5 kWh",
              "beckn:shortDesc": "Carbon Offset Certified Solar Energy",
              "beckn:longDesc": "High-quality solar energy from verified source with carbon offset certification"
            },
            "beckn:provider": {
              "@type": "beckn:Provider",
              "beckn:id": "provider-solar-farm-001"
            },
            "beckn:itemAttributes": {
              "@context": "./context.jsonld",
              "@type": "EnergyResource",
              "sourceType": "SOLAR",
              "deliveryMode": "GRID_INJECTION",
              "certificationStatus": "Carbon Offset Certified",
              "meterId": "100200300",
              "inverterId": "inv-12345",
              "availableQuantity": 30.5,
              "productionWindow": {
                "start": "2024-10-04T10:00:00Z",
                "end": "2024-10-04T18:00:00Z"
              },
              "sourceVerification": {
                "verified": true,
                "verificationDate": "2024-09-01T00:00:00Z",
                "certificates": [
                  "https://example.com/certs/solar-panel-cert.pdf"
                ]
              },
              "productionAsynchronous": true
            }
          }
        ],
        "beckn:offers": [
          {
            "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
            "@type": "beckn:Offer",
            "beckn:id": "offer-energy-001",
            "beckn:descriptor": {
              "@type": "beckn:Descriptor",
              "schema:name": "Daily Settlement Solar Energy Offer"
            },
            "beckn:provider": "provider-solar-farm-001",
            "beckn:items": ["energy-resource-solar-001"],
            "beckn:price": {
              "@type": "schema:PriceSpecification",
              "schema:price": 0.15,
              "schema:priceCurrency": "USD",
              "schema:unitText": "kWh"
            },
            "beckn:offerAttributes": {
              "@context": "../EnergyTradeOffer/v0.2/context.jsonld",
              "@type": "EnergyTradeOffer",
              "pricingModel": "PER_KWH",
              "settlementType": "DAILY",
              "wheelingCharges": {
                "amount": 2.5,
                "currency": "USD",
                "description": "PG&E Grid Services wheeling charge"
              },
              "minimumQuantity": 1.0,
              "maximumQuantity": 100.0,
              "validityWindow": {
                "start": "2024-10-04T00:00:00Z",
                "end": "2024-10-04T23:59:59Z"
              }
            }
          }
        ]
      }
    ]
  }
}


```
</details>

**Key Points**:
- **No Intent Object**: v2 does not support `intent` object in discover requests. All search parameters are expressed via JSONPath filters.
- **Quantity Filter**: Filter by `itemAttributes.availableQuantity >= 10.0` in JSONPath expression
- **Time Range Filter**: Filter by `productionWindow.start` and `productionWindow.end` to match desired trade time window
  - `productionWindow.start <= '2024-10-04T10:00:00Z'` - Energy available from start time or earlier
  - `productionWindow.end >= '2024-10-04T18:00:00Z'` - Energy available until end time or later
- **JSONPath Filters**: Use JSONPath filters to search by `itemAttributes.sourceType`, `itemAttributes.deliveryMode`, `itemAttributes.availableQuantity`, and `itemAttributes.productionWindow`
- **Response**: Includes full Item with EnergyResource attributes and Offer with EnergyTradeOffer attributes

### 2. Select Flow

**Purpose**: Select items and offers to build an order

**Endpoint**: `POST /beckn/select`

<details>
<summary><a href="./examples/select-request.json">Request Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "select",
    "timestamp": "2024-10-04T10:15:00Z",
    "message_id": "msg-select-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      }
    }
  }
}


```
</details>

<details>
<summary><a href="./examples/select-response.json">Response Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_select",
    "timestamp": "2024-10-04T10:15:05Z",
    "message_id": "msg-on-select-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:quote": {
        "@type": "beckn:Quotation",
        "beckn:price": {
          "@type": "schema:PriceSpecification",
          "schema:price": 1.5,
          "schema:priceCurrency": "USD",
          "schema:unitText": "kWh"
        },
        "beckn:breakup": [
          {
            "@type": "beckn:Breakup",
            "beckn:title": "Energy Cost (10 kWh @ $0.15/kWh)",
            "beckn:price": {
              "@type": "schema:PriceSpecification",
              "schema:price": 1.5,
              "schema:priceCurrency": "USD"
            }
          },
          {
            "@type": "beckn:Breakup",
            "beckn:title": "Wheeling Charges",
            "beckn:price": {
              "@type": "schema:PriceSpecification",
              "schema:price": 2.5,
              "schema:priceCurrency": "USD"
            }
          }
        ]
      }
    }
  }
}


```
</details>

**Key Points**:
- Select items by `beckn:id` and specify quantity
- Select offers by `beckn:id`
- Response includes priced quote with breakup

### 3. Init Flow

**Purpose**: Initialize order with fulfillment and payment details

**Endpoint**: `POST /beckn/init`

**v1 to v2 Mapping**:
- v1 `Order.fulfillments[].stops[].time.range` → v2 `Order.fulfillments[].stops[].time.range` (same structure)
- v1 `Order.fulfillments[].stops[].location.address` (der:// format) → v2 `Order.fulfillments[].stops[].location.address` (IEEE mRID format)
- v1 `Order.attributes.*` → v2 `Order.orderAttributes.*` (path change)

<details>
<summary><a href="./examples/init-request.json">Request Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "init",
    "timestamp": "2024-10-04T10:20:00Z",
    "message_id": "msg-init-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:fulfillments": [
        {
          "@type": "beckn:Fulfillment",
          "beckn:id": "fulfillment-energy-001",
          "beckn:type": "ENERGY_DELIVERY",
          "beckn:stops": [
            {
              "@type": "beckn:Stop",
              "beckn:id": "stop-start-001",
              "beckn:type": "START",
              "beckn:location": {
                "@type": "beckn:Location",
                "beckn:address": "100200300"
              },
              "beckn:time": {
                "@type": "beckn:Time",
                "beckn:range": {
                  "start": "2024-10-04T10:00:00Z",
                  "end": "2024-10-04T18:00:00Z"
                }
              }
            },
            {
              "@type": "beckn:Stop",
              "beckn:id": "stop-end-001",
              "beckn:type": "END",
              "beckn:location": {
                "@type": "beckn:Location",
                "beckn:address": "98765456"
              },
              "beckn:time": {
                "@type": "beckn:Time",
                "beckn:range": {
                  "start": "2024-10-04T10:00:00Z",
                  "end": "2024-10-04T18:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "beckn:payments": [
        {
          "@type": "beckn:Payment",
          "beckn:id": "payment-energy-001",
          "beckn:type": "ON-FULFILLMENT",
          "beckn:status": "NOT-PAID",
          "beckn:collected_by": "BPP"
        }
      ],
      "beckn:billing": {
        "@type": "beckn:Billing",
        "beckn:name": "Energy Consumer",
        "beckn:email": "consumer@example.com",
        "beckn:phone": "+1-555-0100"
      }
    }
  }
}


```
</details>

<details>
<summary><a href="./examples/init-response.json">Response Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_init",
    "timestamp": "2024-10-04T10:20:05Z",
    "message_id": "msg-on-init-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:fulfillments": [
        {
          "@type": "beckn:Fulfillment",
          "beckn:id": "fulfillment-energy-001",
          "beckn:type": "ENERGY_DELIVERY",
          "beckn:stops": [
            {
              "@type": "beckn:Stop",
              "beckn:id": "stop-start-001",
              "beckn:type": "START",
              "beckn:location": {
                "@type": "beckn:Location",
                "beckn:address": "100200300"
              }
            },
            {
              "@type": "beckn:Stop",
              "beckn:id": "stop-end-001",
              "beckn:type": "END",
              "beckn:location": {
                "@type": "beckn:Location",
                "beckn:address": "98765456"
              }
            }
          ]
        }
      ],
      "beckn:payments": [
        {
          "@type": "beckn:Payment",
          "beckn:id": "payment-energy-001",
          "beckn:type": "ON-FULFILLMENT",
          "beckn:status": "NOT-PAID",
          "beckn:collected_by": "BPP"
        }
      ],
      "beckn:orderAttributes": {
        "@context": "../EnergyTradeContract/v0.2/context.jsonld",
        "@type": "EnergyTradeContract",
        "contractStatus": "PENDING",
        "sourceMeterId": "100200300",
        "targetMeterId": "98765456",
        "inverterId": "inv-12345",
        "contractedQuantity": 10.0,
        "tradeStartTime": "2024-10-04T10:00:00Z",
        "tradeEndTime": "2024-10-04T18:00:00Z",
        "sourceType": "SOLAR",
        "certification": {
          "status": "Carbon Offset Certified",
          "certificates": [
            "https://example.com/certs/solar-panel-cert.pdf"
          ]
        }
      }
    }
  }
}


```
</details>

**Key Points**:
- **Fulfillment Stops**: Must include START and END stops (same as v1)
- **Time Range**: Include `beckn:time.range` in stops to specify delivery time window (same as v1)
- **Meter IDs**: Use IEEE mRID format (`"100200300"`) instead of v1's `der://` format (`"der://pge.meter/100200300"`)
- **Response**: Includes EnergyTradeContract attributes with PENDING status

### 4. Confirm Flow

**Purpose**: Confirm and activate the order

**Endpoint**: `POST /beckn/confirm`

<details>
<summary><a href="./examples/confirm-request.json">Request Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "confirm",
    "timestamp": "2024-10-04T10:25:00Z",
    "message_id": "msg-confirm-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:fulfillments": [
        {
          "@type": "beckn:Fulfillment",
          "beckn:id": "fulfillment-energy-001",
          "beckn:type": "ENERGY_DELIVERY"
        }
      ],
      "beckn:payments": [
        {
          "@type": "beckn:Payment",
          "beckn:id": "payment-energy-001",
          "beckn:type": "ON-FULFILLMENT",
          "beckn:status": "NOT-PAID",
          "beckn:collected_by": "BPP"
        }
      ]
    }
  }
}


```
</details>

<details>
<summary><a href="./examples/confirm-response.json">Response Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_confirm",
    "timestamp": "2024-10-04T10:25:05Z",
    "message_id": "msg-on-confirm-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:fulfillments": [
        {
          "@type": "beckn:Fulfillment",
          "beckn:id": "fulfillment-energy-001",
          "beckn:type": "ENERGY_DELIVERY",
          "beckn:state": {
            "@type": "beckn:State",
            "beckn:descriptor": {
              "@type": "beckn:Descriptor",
              "schema:name": "PENDING"
            }
          }
        }
      ],
      "beckn:payments": [
        {
          "@type": "beckn:Payment",
          "beckn:id": "payment-energy-001",
          "beckn:type": "ON-FULFILLMENT",
          "beckn:status": "NOT-PAID",
          "beckn:collected_by": "BPP"
        }
      ],
      "beckn:orderAttributes": {
        "@context": "../EnergyTradeContract/v0.2/context.jsonld",
        "@type": "EnergyTradeContract",
        "contractStatus": "ACTIVE",
        "sourceMeterId": "100200300",
        "targetMeterId": "98765456",
        "inverterId": "inv-12345",
        "contractedQuantity": 10.0,
        "tradeStartTime": "2024-10-04T10:00:00Z",
        "tradeEndTime": "2024-10-04T18:00:00Z",
        "sourceType": "SOLAR",
        "certification": {
          "status": "Carbon Offset Certified",
          "certificates": [
            "https://example.com/certs/solar-panel-cert.pdf"
          ]
        },
        "settlementCycles": [
          {
            "cycleId": "settle-2024-10-04-001",
            "startTime": "2024-10-04T00:00:00Z",
            "endTime": "2024-10-04T23:59:59Z",
            "status": "PENDING",
            "amount": 0.0,
            "currency": "USD"
          }
        ]
      }
    }
  }
}


```
</details>

**Key Points**:
- Contract status changes from PENDING to ACTIVE
- Settlement cycle is initialized
- Order is now active and ready for fulfillment

### 5. Status Flow

**Purpose**: Query order and delivery status

**Endpoint**: `POST /beckn/status`

<details>
<summary><a href="./examples/status-request.json">Request Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "status",
    "timestamp": "2024-10-04T15:00:00Z",
    "message_id": "msg-status-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001"
    }
  }
}


```
</details>

<details>
<summary><a href="./examples/status-response.json">Response Example</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_status",
    "timestamp": "2024-10-04T15:00:05Z",
    "message_id": "msg-on-status-001",
    "transaction_id": "txn-energy-001",
    "bap_id": "bap.energy-consumer.com",
    "bap_uri": "https://bap.energy-consumer.com",
    "bpp_id": "bpp.energy-provider.com",
    "bpp_uri": "https://bpp.energy-provider.com",
    "ttl": "PT30S",
    "domain": "energy-trade"
  },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-energy-001",
      "beckn:items": [
        {
          "beckn:id": "energy-resource-solar-001",
          "quantity": {
            "count": 10.0,
            "unit": "kWh"
          }
        }
      ],
      "beckn:offers": [
        {
          "beckn:id": "offer-energy-001"
        }
      ],
      "beckn:provider": {
        "beckn:id": "provider-solar-farm-001"
      },
      "beckn:fulfillments": [
        {
          "@type": "beckn:Fulfillment",
          "beckn:id": "fulfillment-energy-001",
          "beckn:type": "ENERGY_DELIVERY",
          "beckn:state": {
            "@type": "beckn:State",
            "beckn:descriptor": {
              "@type": "beckn:Descriptor",
              "schema:name": "IN_PROGRESS"
            }
          },
          "beckn:attributes": {
            "@context": "../EnergyTradeDelivery/v0.2/context.jsonld",
            "@type": "EnergyTradeDelivery",
            "deliveryStatus": "IN_PROGRESS",
            "deliveryMode": "GRID_INJECTION",
            "deliveredQuantity": 9.8,
            "deliveryStartTime": "2024-10-04T10:00:00Z",
            "deliveryEndTime": null,
            "meterReadings": [
              {
                "timestamp": "2024-10-04T10:00:00Z",
                "sourceReading": 1000.0,
                "targetReading": 990.0,
                "energyFlow": 10.0
              },
              {
                "timestamp": "2024-10-04T12:00:00Z",
                "sourceReading": 1000.5,
                "targetReading": 990.3,
                "energyFlow": 10.2
              },
              {
                "timestamp": "2024-10-04T14:00:00Z",
                "sourceReading": 1001.0,
                "targetReading": 990.8,
                "energyFlow": 10.2
              }
            ],
            "telemetry": [
              {
                "eventTime": "2024-10-04T12:00:00Z",
                "metrics": [
                  {
                    "name": "ENERGY",
                    "value": 5.8,
                    "unitCode": "KWH"
                  },
                  {
                    "name": "POWER",
                    "value": 2.5,
                    "unitCode": "KW"
                  },
                  {
                    "name": "VOLTAGE",
                    "value": 240.0,
                    "unitCode": "VLT"
                  }
                ]
              }
            ],
            "settlementCycleId": "settle-2024-10-04-001",
            "lastUpdated": "2024-10-04T15:30:00Z"
          }
        }
      ],
      "beckn:payments": [
        {
          "@type": "beckn:Payment",
          "beckn:id": "payment-energy-001",
          "beckn:type": "ON-FULFILLMENT",
          "beckn:status": "NOT-PAID",
          "beckn:collected_by": "BPP"
        }
      ],
      "beckn:orderAttributes": {
        "@context": "../EnergyTradeContract/v0.2/context.jsonld",
        "@type": "EnergyTradeContract",
        "contractStatus": "ACTIVE",
        "sourceMeterId": "100200300",
        "targetMeterId": "98765456",
        "inverterId": "inv-12345",
        "contractedQuantity": 10.0,
        "tradeStartTime": "2024-10-04T10:00:00Z",
        "tradeEndTime": "2024-10-04T18:00:00Z",
        "sourceType": "SOLAR",
        "certification": {
          "status": "Carbon Offset Certified",
          "certificates": [
            "https://example.com/certs/solar-panel-cert.pdf"
          ]
        },
        "settlementCycles": [
          {
            "cycleId": "settle-2024-10-04-001",
            "startTime": "2024-10-04T00:00:00Z",
            "endTime": "2024-10-04T23:59:59Z",
            "status": "PENDING",
            "amount": 0.0,
            "currency": "USD"
          }
        ],
        "lastUpdated": "2024-10-04T15:30:00Z"
      }
    }
  }
}


```
</details>

**Key Points**:
- Response includes EnergyTradeContract attributes (contract status)
- Response includes EnergyTradeDelivery attributes (delivery status, meter readings, telemetry)
- Meter readings show energy flow from source to target
- Telemetry provides real-time energy metrics

---

## Field Mapping Reference

### v1 to v2 Field Mapping

| v1 Location | v2 Location | Notes |
|-------------|-------------|-------|
| `Item.attributes.*` | `Item.itemAttributes.*` | Attribute path change |
| `Offer.attributes.*` | `Offer.offerAttributes.*` | Attribute path change |
| `Order.attributes.*` | `Order.orderAttributes.*` | Attribute path change |
| `Fulfillment.attributes.*` | `Fulfillment.attributes.*` | No change |
| `der://meter/{id}` | `{id}` (IEEE mRID) | Format change |
| `Tag.value` (energy source) | `itemAttributes.sourceType` | Direct attribute |
| `Tag.value` (settlement) | `offerAttributes.settlementType` | Direct attribute |

### Meter ID Format Migration

**v1 Format**: `der://pge.meter/100200300`  
**v2 Format**: `100200300` (IEEE 2030.5 mRID)

**Migration Rule**: Extract the numeric ID from the `der://` URI.

---

## Integration Patterns

### 1. Attaching Attributes to Core Objects

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
    "@context": "./context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "deliveryMode": "GRID_INJECTION",
    "meterId": "100200300"
  }
}
```

**Offer with EnergyTradeOffer**:
```json
{
  "@type": "beckn:Offer",
  "beckn:id": "offer-energy-001",
  "beckn:offerAttributes": {
    "@context": "../EnergyTradeOffer/v0.2/context.jsonld",
    "@type": "EnergyTradeOffer",
    "pricingModel": "PER_KWH",
    "settlementType": "DAILY"
  }
}
```

**Order with EnergyTradeContract**:
```json
{
  "@type": "beckn:Order",
  "beckn:id": "order-energy-001",
  "beckn:orderAttributes": {
    "@context": "../EnergyTradeContract/v0.2/context.jsonld",
    "@type": "EnergyTradeContract",
    "contractStatus": "ACTIVE",
    "sourceMeterId": "100200300",
    "targetMeterId": "98765456"
  }
}
```

**Fulfillment with EnergyTradeDelivery**:
```json
{
  "@type": "beckn:Fulfillment",
  "beckn:id": "fulfillment-energy-001",
  "beckn:attributes": {
    "@context": "../EnergyTradeDelivery/v0.2/context.jsonld",
    "@type": "EnergyTradeDelivery",
    "deliveryStatus": "IN_PROGRESS",
    "meterReadings": [...]
  }
}
```

### 2. JSON-LD Context Usage

All attribute bundles include `@context` and `@type`:
- `@context`: Points to the context.jsonld file for the attribute bundle
- `@type`: The schema type (EnergyResource, EnergyTradeOffer, etc.)

### 3. Discovery Filtering

Use JSONPath filters to search by energy attributes:

```json
{
  "filters": {
    "type": "jsonpath",
    "expression": "$[?(@.itemAttributes.sourceType == 'SOLAR' && @.itemAttributes.deliveryMode == 'GRID_INJECTION' && @.itemAttributes.availableQuantity >= 10.0)]"
  }
}
```

---

## Best Practices

### 1. Discovery Optimization

- **Index Key Fields**: Index `itemAttributes.sourceType`, `itemAttributes.deliveryMode`, `itemAttributes.meterId`, `itemAttributes.availableQuantity`
- **Use JSONPath Filters**: Leverage JSONPath for complex filtering
- **Minimal Fields**: Return minimal fields in list/search APIs (see profile.json)

### 2. Meter ID Handling

- **Use IEEE mRID Format**: Always use plain identifier (e.g., `"100200300"`), not `der://` format
- **PII Treatment**: Treat meter IDs as PII - do not index, redact in logs, encrypt at rest
- **Discovery**: Meter IDs enable meter-based discovery (provider names not required)

### 3. Settlement Cycle Management

- **Initialize on Confirm**: Create settlement cycle when order is confirmed
- **Update on Delivery**: Link deliveries to settlement cycles via `settlementCycleId`
- **Status Tracking**: Track settlement cycle status (PENDING → SETTLED → FAILED)
- **Amount Calculation**: Calculate settlement amount based on delivered quantity and pricing

### 4. Meter Readings

- **Regular Updates**: Update meter readings during delivery (every 15-30 minutes)
- **Energy Flow Calculation**: Calculate `energyFlow` as difference between readings
- **Source and Target**: Track both source and target meter readings
- **Timestamp Accuracy**: Use accurate timestamps (ISO 8601 format)

### 5. Telemetry Data

- **Metric Selection**: Include relevant metrics (ENERGY, POWER, VOLTAGE, CURRENT, FREQUENCY)
- **Unit Codes**: Use correct unit codes (KWH, KW, VLT, AMP, HZ)
- **Update Frequency**: Update telemetry every 5-15 minutes during active delivery
- **Data Retention**: Retain telemetry data for billing and audit purposes

### 6. Error Handling

- **Validation Errors**: Validate all required fields before processing
- **Meter ID Format**: Validate meter IDs are IEEE mRID format
- **Quantity Validation**: Ensure quantities are within min/max limits
- **Time Window Validation**: Validate production windows and validity windows

---

## Migration from v1

### Key Changes

1. **Attribute Paths**: Change `attributes.*` to `itemAttributes.*`, `offerAttributes.*`, `orderAttributes.*`
2. **Meter Format**: Convert `der://meter/{id}` to `{id}` (IEEE mRID)
3. **Tag Values**: Convert `Tag.value` to direct attribute fields
4. **JSON-LD**: Add `@context` and `@type` to all attribute objects

### Migration Checklist

- Update attribute paths (`attributes.*` → `itemAttributes.*`, etc.)
- Convert meter IDs from `der://` format to IEEE mRID
- Replace `Tag.value` with direct attribute fields
- Add JSON-LD context to all attribute objects
- Update discovery filters to use new attribute paths
- Update validation logic for new schema structure
- Test all transaction flows
- Update documentation

### Example Migration

**v1 Format**:
```json
{
  "Item": {
    "attributes": {
      "sourceType": "SOLAR",
      "meterId": "der://pge.meter/100200300"
    }
  },
  "Tag": {
    "value": "SOLAR"
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Item",
  "beckn:itemAttributes": {
    "@context": "./context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "meterId": "100200300"
  }
}
```

---

## Examples

### Complete Examples

All examples are available in:
- **Schema Examples**: `schema/EnergyResource/v0.2/examples/schema/`
  - `item-example.json` - EnergyResource
  - `offer-example.json` - EnergyTradeOffer
  - `order-example.json` - EnergyTradeContract
  - `fulfillment-example.json` - EnergyTradeDelivery

- **Transaction Flow Examples**: [`/examples/v2/P2P_Trading /`](../examples)
  - [`discover-request.json`](/examples/v2/P2P_Trading /discover-request.json) / [`discover-response.json`](/examples/v2/P2P_Trading /discover-response.json)
  - [`select-request.json`](/examples/v2/P2P_Trading /select-request.json) / [`select-response.json`](/examples/v2/P2P_Trading /select-response.json)
  - [`init-request.json`](/examples/v2/P2P_Trading /`init-request.json) / [`init-response.json`](/examples/v2/P2P_Trading /init-response.json)
  - [`confirm-request.json`](/examples/v2/P2P_Trading /confirm-request.json) / [`confirm-response.json`](/examples/v2/P2P_Trading /confirm-response.json)
  - [`status-request.json`](/examples/v2/P2P_Trading /status-request.json) / [`status-response.json`](/examples/v2/P2P_Trading /status-response.json)


### Example Scenarios

1. **Solar Energy Discovery**: Search for solar energy with grid injection delivery
2. **Daily Settlement**: Contract with daily settlement cycle
3. **Meter-Based Tracking**: Track energy flow using meter readings
4. **Telemetry Monitoring**: Monitor energy delivery with real-time telemetry

---

## Additional Resources

- **Field Mapping**: See `docs/v1_to_v2_field_mapping.md`
- **Taxonomy Reference**: See `docs/TAXONOMY.md`
- **Schema Definitions**: See `schema/Energy*/v0.2/attributes.yaml`
- **Context Files**: See `schema/Energy*/v0.2/context.jsonld`
- **Profile Configuration**: See `schema/EnergyResource/v0.2/profile.json`

---

## Support

For questions or issues:
- Review the examples in `schema/EnergyResource/v0.2/examples/`
- Check the schema definitions in `schema/Energy*/v0.2/attributes.yaml`
- Refer to the Beckn Protocol v2 documentation

