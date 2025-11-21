# P2P Energy Trading Implementation Guide <!-- omit from toc -->

## Overview <!-- omit from toc -->

This implementation guide provides comprehensive instructions for implementing Peer-to-Peer (P2P) Energy Trading using Beckn Protocol v2 with composable schemas. This guide covers all transaction flows, field mappings, best practices, and migration from v1.

## Table of Contents  <!-- omit from toc -->

- [1. Introduction](#1-introduction)
  - [1.1. What is P2P Energy Trading?](#11-what-is-p2p-energy-trading)
  - [1.2. Beckn Protocol v2 for Energy Trading](#12-beckn-protocol-v2-for-energy-trading)
- [3. Scope](#3-scope)
- [4. Intended Audience](#4-intended-audience)
- [5. Conventions and Terminology](#5-conventions-and-terminology)
- [6. Terminology](#6-terminology)
- [7. Reference Architecture](#7-reference-architecture)
  - [7.1. Architecture Diagram](#71-architecture-diagram)
  - [7.2. Actors](#72-actors)
  - [7.3. Schema Overview](#73-schema-overview)
    - [7.3.1. EnergyResource (Item.itemAttributes)](#731-energyresource-itemitemattributes)
    - [7.3.2. EnergyTradeOffer (Offer.offerAttributes)](#732-energytradeoffer-offerofferattributes)
    - [7.3.3. EnergyTradeContract (Order.orderAttributes)](#733-energytradecontract-orderorderattributes)
    - [7.3.4. EnergyTradeDelivery (Fulfillment.attributes)](#734-energytradedelivery-fulfillmentattributes)
  - [7.4. v2 Composable Schema Architecture](#74-v2-composable-schema-architecture)
    - [7.4.1. Schema Composition Points](#741-schema-composition-points)
    - [7.4.2. Key Differences from v1](#742-key-differences-from-v1)
    - [7.4.3. v1 to v2 Quick Reference](#743-v1-to-v2-quick-reference)
      - [7.4.3.1. Discover/Search Request](#7431-discoversearch-request)
      - [7.4.3.2. Item Attributes](#7432-item-attributes)
      - [7.4.3.3. Order Attributes](#7433-order-attributes)
      - [7.4.3.4. Fulfillment Stops](#7434-fulfillment-stops)
- [8. Creating an Open Network for Peer to Peer Energy Trading](#8-creating-an-open-network-for-peer-to-peer-energy-trading)
  - [8.1. Setting up a Registry](#81-setting-up-a-registry)
    - [8.1.1. For a Network Participant](#811-for-a-network-participant)
      - [8.1.1.1. Step 1 :  Claiming a Namespace](#8111-step-1---claiming-a-namespace)
      - [8.1.1.2. Step 2 :  Setting up a Registry](#8112-step-2---setting-up-a-registry)
      - [8.1.1.3. Step 3 :  Publishing subscriber details](#8113-step-3---publishing-subscriber-details)
    - [8.1.2. Step 4 :  Share details of the registry created with the Beckn One team](#812-step-4---share-details-of-the-registry-created-with-the-beckn-one-team)
    - [8.1.3. For a Network facilitator organization](#813-for-a-network-facilitator-organization)
      - [8.1.3.1. Step 1 :  Claiming a Namespace](#8131-step-1---claiming-a-namespace)
      - [8.1.3.2. Step 2 :  Setting up a Registry](#8132-step-2---setting-up-a-registry)
      - [8.1.3.3. Step 3 :  Publishing subscriber details](#8133-step-3---publishing-subscriber-details)
      - [8.1.3.4. Step 4 :  Share details of the registry created with the Beckn One team](#8134-step-4---share-details-of-the-registry-created-with-the-beckn-one-team)
  - [8.2. Setting up the Protocol Endpoints](#82-setting-up-the-protocol-endpoints)
    - [8.2.1. Installing Beckn ONIX](#821-installing-beckn-onix)
    - [8.2.2. Configuring Beckn ONIX for Peer to Peer Energy Trading](#822-configuring-beckn-onix-for-peer-to-peer-energy-trading)
    - [8.2.3. 10.2.3 Performing a test transaction](#823-1023-performing-a-test-transaction)
- [10. Transaction Flows](#10-transaction-flows)
  - [10.1. Discover Flow](#101-discover-flow)
  - [10.2. Select Flow](#102-select-flow)
  - [10.3. Init Flow](#103-init-flow)
  - [10.4. Confirm Flow](#104-confirm-flow)
  - [10.5. Status Flow](#105-status-flow)
- [11. Field Mapping Reference](#11-field-mapping-reference)
  - [11.1. v1 to v2 Field Mapping](#111-v1-to-v2-field-mapping)
  - [11.2. Meter ID Format Migration](#112-meter-id-format-migration)
- [12. Integration Patterns](#12-integration-patterns)
  - [12.1. Attaching Attributes to Core Objects](#121-attaching-attributes-to-core-objects)
  - [12.2. JSON-LD Context Usage](#122-json-ld-context-usage)
  - [12.3. Discovery Filtering](#123-discovery-filtering)
- [13. Best Practices](#13-best-practices)
  - [13.1. Discovery Optimization](#131-discovery-optimization)
  - [13.2. Meter ID Handling](#132-meter-id-handling)
  - [13.3. Settlement Cycle Management](#133-settlement-cycle-management)
  - [13.4. Meter Readings](#134-meter-readings)
  - [13.5. Telemetry Data](#135-telemetry-data)
  - [13.6. Error Handling](#136-error-handling)
- [14. Migration from v1](#14-migration-from-v1)
  - [14.1. Key Changes](#141-key-changes)
  - [14.2. Migration Checklist](#142-migration-checklist)
  - [14.3. Example Migration](#143-example-migration)
- [15. Examples](#15-examples)
  - [15.1. Complete Examples](#151-complete-examples)
  - [15.2. Example Scenarios](#152-example-scenarios)
- [16. Additional Resources](#16-additional-resources)
- [17. Support](#17-support)

Table of contents and section auto-numbering was done using [Markdown-All-In-One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one) vscode extension. Specifically `Markdown All in One: Create Table of Contents` and `Markdown All in One: Add/Update section numbers` commands accessible via vs code command pallete.

Example jsons were imported directly from source of truth elsewhere in this repo inline by inserting the pattern below within all json expand blocks, and running this [script](/scripts/embed_example_json.py), e.g. `python3 scripts/embed_example_json.py path_to_markdown_file.md`.

```
<details><summary><a href="/path_to_file_from_root">txt_with_json_keyword</a></summary>

</details>
``` 

---

# 1. Introduction

This document provides an implementation guidance for deploying peer to peer energy trading services using the Beckn Protocol ecosystem. 

## 1.1. What is P2P Energy Trading?

Peer-to-Peer (P2P) energy trading enables energy producers (prosumers) to directly sell excess energy to consumers without going through traditional utility intermediaries. This enables:

- **Decentralized Energy Markets**: Direct trading between producers and consumers
- **Grid Optimization**: Better utilization of distributed energy resources (DERs)
- **Renewable Energy Promotion**: Incentivizes green energy production
- **Cost Efficiency**: Reduces transmission losses and intermediary costs

## 1.2. Beckn Protocol v2 for Energy Trading

Beckn Protocol v2 provides a composable schema architecture that enables:
- **Modular Attribute Bundles**: Energy-specific attributes attached to core Beckn objects
- **JSON-LD Semantics**: Full semantic interoperability
- **Standards Alignment**: Integration with IEEE 2030.5 (mRID), OCPP, OCPI
- **Flexible Discovery**: Meter-based discovery and filtering

---

# 3. Scope

This document covers:

* Architecture patterns for EV charging marketplace implementation using Beckn Protocol  
* Discovery and charging mechanisms for charging EVs across multiple CPOs  
* Some recommendations for BAPs, BPPs and NFOs on how to map protocol API calls to internal systems (or vice-versa).  
* Real-time availability and pricing integration with OCPI-based systems  
* Session management and billing coordination between Beckn and OCPI protocols

This document does NOT cover:

* Detailed OCPI protocol specifications (refer to OCPI 2.2.1 documentation)  
* Physical charging infrastructure requirements and standards  
* Regulatory compliance beyond technical implementation (varies by jurisdiction)  
* Smart grid integration and load management systems

# 4. Intended Audience

* Consumer Application Developers (BAPs): Building EV driver-facing charging applications with unified cross-network access  
* e-Mobility Service Providers (eMSPs/BPPs): Implementing charging service aggregation platforms across multiple CPO networks  
* Charge Point Operators (CPOs): Understanding integration requirements for Beckn-enabled marketplace participation  
* Technology Integrators: Building bridges between existing OCPI infrastructure and new Beckn-based marketplaces  
* System Architects: Designing scalable, interoperable EV charging ecosystems  
* Business Stakeholders: Understanding technical capabilities and implementation requirements for EV charging marketplace strategies  
* Standards Organizations: Evaluating interoperability approaches for future EV charging standards development

# 5. Conventions and Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](https://github.com/beckn/protocol-specifications/blob/draft/docs/BECKN-010-Keyword-Definitions-for-Technical-Specifications.md).

# 6. Terminology

| Acronym | Full Form/Description | Description |
| ----- | ----- | ----- |
| BAP | Beckn Application Platform | Consumer-facing application that initiates transactions. Mapped to EV users and eMSPs. |
| BPP | Beckn Provider Platform | Service provider platform that responds to BAP requests. Mapped to CPOs.  |
| NFO | Network Facilitator Organization | Organization responsible for the adoption and growth of the network. Usually the custodian of the network’s registry. |
| CDS | Catalog Discovery Service | Enables discovery of charging services from BPPs in the network. |
| eMSP | e-Mobility Service Provider | Service provider that aggregates multiple CPOs. Generally onboarded by BAPs.  |
| CPO | Charge Point Operator | Entity that owns and operates charging infrastructure. Generally onboarded by BPPs.  |
| EVSE | Electric Vehicle Supply Equipment | Individual charging station unit. Owned and operated by CPOs |
| OCPI | Open Charge Point Interface | Protocol for communication between eMSPs and CPOs. |

> Note:
> This document does not detail the mapping between Beckn Protocol and OCPI. Please refer to [this](../../../docs/implementation-guides/v1-EOS/DEG00x_Mapping-OCPI-and-Beckn-Protocol-for-EV-Charging-Interoperability.md) document for the same.
> BPPs are NOT aggregators. Any CPO that has implemented a Beckn Protocol endpoint is a BPP. 
> For all sense and purposes, CPOs are essentially BPPs and eMSPs are essentially BAPs.

# 7. Reference Architecture

The section defines the reference ecosystem architecture that is used for building this implementation guide. 

## 7.1. Architecture Diagram

![](./assets/beckn-one-deg-arch.png)

## 7.2. Actors

1. Beckn One Global Root Registry  
2. Beckn One Catalog Discovery Service  
3. Beckn Application Platforms  
4. Beckn Provider Platforms  
5. EV Charging Registry

## 7.3. Schema Overview

### 7.3.1. EnergyResource (Item.itemAttributes)

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

### 7.3.2. EnergyTradeOffer (Offer.offerAttributes)

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

### 7.3.3. EnergyTradeContract (Order.orderAttributes)

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

### 7.3.4. EnergyTradeDelivery (Fulfillment.attributes)

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


## 7.4. v2 Composable Schema Architecture

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

### 7.4.1. Schema Composition Points

| Attribute Bundle | Attach To | Purpose |
|------------------|-----------|---------|
| **EnergyResource** | `Item.itemAttributes` | Energy source characteristics (source type, delivery mode, meter ID, availability) |
| **EnergyTradeOffer** | `Offer.offerAttributes` | Pricing models, settlement types, wheeling charges, validity windows |
| **EnergyTradeContract** | `Order.orderAttributes` | Contract status, meter IDs, settlement cycles, billing cycles |
| **EnergyTradeDelivery** | `Fulfillment.attributes` | Delivery status, meter readings, telemetry, settlement linkage |

### 7.4.2. Key Differences from v1

| Aspect | v1 (Layer2) | v2 (Composable) |
|--------|-------------|-----------------|
| **Schema Extension** | `allOf` in paths | Composable attribute bundles |
| **Attribute Location** | `Item.attributes.*` | `Item.itemAttributes.*` |
| **Meter Format** | `der://meter/{id}` | IEEE 2030.5 mRID `{id}` |
| **JSON-LD** | Not used | Full JSON-LD support |
| **Modularity** | Monolithic | Modular bundles |

### 7.4.3. v1 to v2 Quick Reference

For developers familiar with v1, here's a quick mapping guide:

#### 7.4.3.1. Discover/Search Request

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

#### 7.4.3.2. Item Attributes

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

#### 7.4.3.3. Order Attributes

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

#### 7.4.3.4. Fulfillment Stops

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



# 8. Creating an Open Network for Peer to Peer Energy Trading

To create an open network for energy trading requires all the producers, prosumers and consumers BAPs, BPPs, to be able to discover each other and become part of a common club. This club is manifested in the form of a Registry maintained by an NFO. 

## 8.1. Setting up a Registry

The NP Registry serves as the root of addressability and trust for all network participants. It maintains comprehensive details such as the participant’s globally unique identifier (ID), network address (Beckn API URL), public key, operational domains, and assigned role (e.g., BAP, BPP, CDS). In addition to managing participant registration, authentication, authorization, and permission control, the Registry oversees participant verification, activation, and overall lifecycle management, ensuring that only validated and authorized entities can operate within the network.

![](./assets/registry-arch.png)

You can publish your registries at [DeDi.global](https://publish.dedi.global/).

### 8.1.1. For a Network Participant

#### 8.1.1.1. Step 1 :  Claiming a Namespace

To get started, any platform that has implemented Beckn Protocol MUST create a globally unique namespace for themselves.   
All NPs (BAPs, BPPs, CDS’es) **MUST** register as a user on dedi.global and claim a unique namespace against their FQDN to become globally addressable. As part of the claiming process, the user must prove ownership of the namespace by verifying the ownership of their domain. Namespace would be at an organisation level. You can put your organisation name as the name of the namespace.

#### 8.1.1.2. Step 2 :  Setting up a Registry

Once the namespace is claimed, each NP **MUST** create a Beckn NP registry in the namespace to list their subscriber details. While creating the registry, the user **MUST** configure it with the [subscriber schema](https://gist.githubusercontent.com/nirmalnr/a6e5b17522169ecea4f3ccdd831af7e4/raw/7744f2542034db9675901b61b41c8228ea239074/beckn-subscriber-no-refs.schema.json). Example of a registry name can be `subscription-details`.

#### 8.1.1.3. Step 3 :  Publishing subscriber details

In the registry that is created, NPs **MUST** publish their subscription details including their ID, network endpoints, public keys, operational domains and assigned roles (BAP, BPP) as records.

*Detailed steps to create namespaces and registries in dedi.global can be found [here](https://github.com/dedi-global/docs/blob/0976607aabc6641d330a3d41a3bd89ab8790ea09/user-guides/namespace%20and%20registry%20creation.md).*

### 8.1.2. Step 4 :  Share details of the registry created with the Beckn One team

Once the registry is created and details are published, the namespace and the registry name of the newly created registry should be shared with the beckn one team.

### 8.1.3. For a Network facilitator organization

#### 8.1.3.1. Step 1 :  Claiming a Namespace

An NFO **MAY** register as a user on dedi.global and claim a unique namespace against their FQDN. As part of the claiming process, the user must prove ownership of that namespace by verifying the ownership of that domain. The NFO name can be set as the name of the namespace. 
*Note: A calibrated roll out of this infrastructure is planned and hence before it is open to the general public NFOs are advised to share their own domain and the domains of their NPs to the Beckn One team so that they can be whitelisted which will allow the NPs to verify the same using TXT records in their DNS.*

#### 8.1.3.2. Step 2 :  Setting up a Registry

Network facilitators **MAY** create registries under their own namespace using the [subscriber reference schema](https://gist.githubusercontent.com/nirmalnr/a6e5b17522169ecea4f3ccdd831af7e4/raw/b7cf8a47e6531ef22744b43e6305b8d8cc106e7b/beckn-subscriber-reference.schema.json) to point to either whole registries or records created by the NPs in their own namespaces.  Example of a registry name can be `subscription-details`.

#### 8.1.3.3. Step 3 :  Publishing subscriber details

In the registry that is created, NFOs **MAY** publish records which act as pointers to either whole registries or records created by the NPs records. The URL field in the record would be the lookup URL for a registry or a record as per DeDi protocol.

Example: For referencing another registry created by an NP, the record details created would be:

```json
{
  "url": "https://.dedi.global/dedi/lookup/example-company/subscription-details",
  "type": "Registry",
  "subscriber_id": "example-company.com"
}
```

Here `example-company` is the namespace of the NP, and all records added in the registry is referenced here. 

If only one record in the registry needs to be referenced, then the record details created would be:

```json
{
  "url": "https://.dedi.global/dedi/lookup/example-company/subscription-details/energy-bap",
  "type": "Record",
  "subscriber_id": "example-company.com"
}
```

Here `energy-bap` is the name of the record created by the NP in this registry. Only that record is referenced here.

*Detailed steps to create namespaces and registries in dedi.global can be found [here](https://github.com/dedi-global/docs/blob/0976607aabc6641d330a3d41a3bd89ab8790ea09/user-guides/namespace%20and%20registry%20creation.md).*

#### 8.1.3.4. Step 4 :  Share details of the registry created with the Beckn One team

Once the registry is created and details are published, the namespace and the registry name of the newly created registry should be shared with the beckn one team.

## 8.2. Setting up the Protocol Endpoints

This section contains instructions to set up and test the protocol stack for EV charging transactions. 

### 8.2.1. Installing Beckn ONIX

All NPs SHOULD install the Beckn ONIX adapter to quickly get set up and become Beckn Protocol compliant. Click [here](https://github.com/Beckn-One/beckn-onix?tab=readme-ov-file#automated-setup-recommended)) to learn how to set up Beckn ONIX.

### 8.2.2. Configuring Beckn ONIX for Peer to Peer Energy Trading

A detailed Configuration Guide is available [here](https://github.com/Beckn-One/beckn-onix/blob/main/CONFIG.md). A quick read of key concepts from the link is recommended.

Specifically, please use the following configuration:
1. Configure dediregistry plugin instead of registry plugin. Read more [here](https://github.com/Beckn-One/beckn-onix/tree/main/pkg/plugin/implementation/dediregistry).
2. Start with using Simplekeymanager plugin during development, read more [here](https://github.com/Beckn-One/beckn-onix/tree/main/pkg/plugin/implementation/simplekeymanager). For production deployment, you may setup vault.
3. For routing calls to Catalog Discovery Service, refer to routing configuration [here](https://github.com/Beckn-One/beckn-onix/blob/main/config/local-simple-routing-BAPCaller.yaml).

### 8.2.3. 10.2.3 Performing a test transaction

Step 1 : Download the postman collection, from [here](/testnet/postman-collections/v2/P2P_Trading).

Step 2 : Run API calls

If you are a BAP

1. Configure the collection/environment variables to the newly installed Beckn ONIX adapter URL and other variables in the collection.
2. Select the discover example and hit send
3. You should see the EV charging service catalog response

If you are a BPP

1. Configure the collection/environment variables to the newly installed Beckn ONIX adapter URL and other variables in the collection.
2. Select the on_status example and hit send
3. You should see the response in your console

---

# 10. Transaction Flows

## 10.1. Discover Flow

**Purpose**: Search for available energy resources

**Endpoint**: `POST /discover`

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

## 10.2. Select Flow

**Purpose**: Select items and offers to build an order

**Endpoint**: `POST /select`

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

## 10.3. Init Flow

**Purpose**: Initialize order with fulfillment and payment details

**Endpoint**: `POST /init`

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

## 10.4. Confirm Flow

**Purpose**: Confirm and activate the order

**Endpoint**: `POST /confirm`

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

## 10.5. Status Flow

**Purpose**: Query order and delivery status

**Endpoint**: `POST /status`

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

# 11. Field Mapping Reference

## 11.1. v1 to v2 Field Mapping

| v1 Location | v2 Location | Notes |
|-------------|-------------|-------|
| `Item.attributes.*` | `Item.itemAttributes.*` | Attribute path change |
| `Offer.attributes.*` | `Offer.offerAttributes.*` | Attribute path change |
| `Order.attributes.*` | `Order.orderAttributes.*` | Attribute path change |
| `Fulfillment.attributes.*` | `Fulfillment.attributes.*` | No change |
| `der://meter/{id}` | `{id}` (IEEE mRID) | Format change |
| `Tag.value` (energy source) | `itemAttributes.sourceType` | Direct attribute |
| `Tag.value` (settlement) | `offerAttributes.settlementType` | Direct attribute |

## 11.2. Meter ID Format Migration

**v1 Format**: `der://pge.meter/100200300`  
**v2 Format**: `100200300` (IEEE 2030.5 mRID)

**Migration Rule**: Extract the numeric ID from the `der://` URI.

---

# 12. Integration Patterns

## 12.1. Attaching Attributes to Core Objects

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

## 12.2. JSON-LD Context Usage

All attribute bundles include `@context` and `@type`:
- `@context`: Points to the context.jsonld file for the attribute bundle
- `@type`: The schema type (EnergyResource, EnergyTradeOffer, etc.)

## 12.3. Discovery Filtering

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

# 13. Best Practices

## 13.1. Discovery Optimization

- **Index Key Fields**: Index `itemAttributes.sourceType`, `itemAttributes.deliveryMode`, `itemAttributes.meterId`, `itemAttributes.availableQuantity`
- **Use JSONPath Filters**: Leverage JSONPath for complex filtering
- **Minimal Fields**: Return minimal fields in list/search APIs (see profile.json)

## 13.2. Meter ID Handling

- **Use IEEE mRID Format**: Always use plain identifier (e.g., `"100200300"`), not `der://` format
- **PII Treatment**: Treat meter IDs as PII - do not index, redact in logs, encrypt at rest
- **Discovery**: Meter IDs enable meter-based discovery (provider names not required)

## 13.3. Settlement Cycle Management

- **Initialize on Confirm**: Create settlement cycle when order is confirmed
- **Update on Delivery**: Link deliveries to settlement cycles via `settlementCycleId`
- **Status Tracking**: Track settlement cycle status (PENDING → SETTLED → FAILED)
- **Amount Calculation**: Calculate settlement amount based on delivered quantity and pricing

## 13.4. Meter Readings

- **Regular Updates**: Update meter readings during delivery (every 15-30 minutes)
- **Energy Flow Calculation**: Calculate `energyFlow` as difference between readings
- **Source and Target**: Track both source and target meter readings
- **Timestamp Accuracy**: Use accurate timestamps (ISO 8601 format)

## 13.5. Telemetry Data

- **Metric Selection**: Include relevant metrics (ENERGY, POWER, VOLTAGE, CURRENT, FREQUENCY)
- **Unit Codes**: Use correct unit codes (KWH, KW, VLT, AMP, HZ)
- **Update Frequency**: Update telemetry every 5-15 minutes during active delivery
- **Data Retention**: Retain telemetry data for billing and audit purposes

## 13.6. Error Handling

- **Validation Errors**: Validate all required fields before processing
- **Meter ID Format**: Validate meter IDs are IEEE mRID format
- **Quantity Validation**: Ensure quantities are within min/max limits
- **Time Window Validation**: Validate production windows and validity windows

---

# 14. Migration from v1

## 14.1. Key Changes

1. **Attribute Paths**: Change `attributes.*` to `itemAttributes.*`, `offerAttributes.*`, `orderAttributes.*`
2. **Meter Format**: Convert `der://meter/{id}` to `{id}` (IEEE mRID)
3. **Tag Values**: Convert `Tag.value` to direct attribute fields
4. **JSON-LD**: Add `@context` and `@type` to all attribute objects

## 14.2. Migration Checklist

- Update attribute paths (`attributes.*` → `itemAttributes.*`, etc.)
- Convert meter IDs from `der://` format to IEEE mRID
- Replace `Tag.value` with direct attribute fields
- Add JSON-LD context to all attribute objects
- Update discovery filters to use new attribute paths
- Update validation logic for new schema structure
- Test all transaction flows
- Update documentation

## 14.3. Example Migration

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

# 15. Examples

## 15.1. Complete Examples

All examples are available in:
- **Schema Examples**: `schema/EnergyResource/v0.2/examples/schema/`
  - `item-example.json` - EnergyResource
  - `offer-example.json` - EnergyTradeOffer
  - `order-example.json` - EnergyTradeContract
  - `fulfillment-example.json` - EnergyTradeDelivery

- **Transaction Flow Examples**: [`/examples/v2/P2P_Trading/`](../examples)
  - [`discover-request.json`](/examples/v2/P2P_Trading/discover-request.json) / [`discover-response.json`](/examples/v2/P2P_Trading/discover-response.json)
  - [`select-request.json`](/examples/v2/P2P_Trading/select-request.json) / [`select-response.json`](/examples/v2/P2P_Trading/select-response.json)
  - [`init-request.json`](/examples/v2/P2P_Trading/`init-request.json) / [`init-response.json`](/examples/v2/P2P_Trading/init-response.json)
  - [`confirm-request.json`](/examples/v2/P2P_Trading/confirm-request.json) / [`confirm-response.json`](/examples/v2/P2P_Trading/confirm-response.json)
  - [`status-request.json`](/examples/v2/P2P_Trading/status-request.json) / [`status-response.json`](/examples/v2/P2P_Trading/status-response.json)


## 15.2. Example Scenarios

1. **Solar Energy Discovery**: Search for solar energy with grid injection delivery
2. **Daily Settlement**: Contract with daily settlement cycle
3. **Meter-Based Tracking**: Track energy flow using meter readings
4. **Telemetry Monitoring**: Monitor energy delivery with real-time telemetry

---

# 16. Additional Resources

- **Field Mapping**: See `docs/v1_to_v2_field_mapping.md`
- **Taxonomy Reference**: See `docs/TAXONOMY.md`
- **Schema Definitions**: See `schema/Energy*/v0.2/attributes.yaml`
- **Context Files**: See `schema/Energy*/v0.2/context.jsonld`
- **Profile Configuration**: See `schema/EnergyResource/v0.2/profile.json`

---

# 17. Support

For questions or issues:
- Review the examples in `schema/EnergyResource/v0.2/examples/`
- Check the schema definitions in `schema/Energy*/v0.2/attributes.yaml`
- Refer to the Beckn Protocol v2 documentation

