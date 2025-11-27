# Schema Extension Specifications
## JSON-LD Schema Extensions for Energy Coordination Building Blocks

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document specifies JSON-LD schema extensions for the building blocks identified in the gap analysis. These extensions enable bid curve expression, objective-driven coordination, locational pricing, market clearing, and multi-party settlement.

**Schema Architecture**: Following the existing pattern:
- `context.jsonld`: JSON-LD context mapping
- `vocab.jsonld`: RDF vocabulary definitions
- Attribute bundles attach to Beckn core objects via `itemAttributes`, `offerAttributes`, `orderAttributes`, `fulfillmentAttributes`

---

## Table of Contents

1. [Bid Curve Schema](#1-bid-curve-schema)
2. [Objective Expression Schema](#2-objective-expression-schema)
3. [Locational Pricing Schema](#3-locational-pricing-schema)
4. [Grid Node Schema](#4-grid-node-schema)
5. [Settlement Schema](#5-settlement-schema)
6. [Aggregate Action Schema](#6-aggregate-action-schema)
7. [Complete Context Examples](#7-complete-context-examples)

---

## 1. Bid Curve Schema

### 1.1 Purpose

Enable resources to express price/power preferences as bid curves for market-based coordination.

### 1.2 Context Extension

**File**: `EnergyCoordination/v1/context.jsonld`

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "bidCurve": "beckn:bidCurve",
    "bidCurvePoint": "beckn:BidCurvePoint",
    "price": "schema:price",
    "powerKW": "beckn:powerKW",
    "constraints": "beckn:bidCurveConstraints",
    "minPowerKW": "beckn:minPowerKW",
    "maxPowerKW": "beckn:maxPowerKW",
    "rampRateKWPerMin": "beckn:rampRateKWPerMin"
  },
  "@graph": []
}
```

### 1.3 Vocabulary Definition

**File**: `EnergyCoordination/v1/vocab.jsonld`

```json
{
  "@context": {
    "@version": 1.1,
    "beckn": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/#",
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@graph": [
    {
      "@id": "beckn:bidCurve",
      "@type": "rdf:Property",
      "rdfs:label": "Bid Curve",
      "rdfs:comment": "Array of price/power pairs expressing resource opportunity cost or willingness to transact.",
      "rdfs:domain": ["beckn:EnergyResource", "beckn:EnergyOffer"],
      "schema:rangeIncludes": "beckn:BidCurvePoint"
    },
    {
      "@id": "beckn:BidCurvePoint",
      "@type": "rdfs:Class",
      "rdfs:label": "Bid Curve Point",
      "rdfs:comment": "A single price/power pair in a bid curve.",
      "schema:rangeIncludes": {
        "@id": "schema:Number"
      }
    },
    {
      "@id": "beckn:powerKW",
      "@type": "rdf:Property",
      "rdfs:label": "Power (kW)",
      "rdfs:comment": "Power level in kilowatts. Negative values indicate consumption (charging, load), positive values indicate generation (discharge, export), zero indicates no participation.",
      "rdfs:domain": "beckn:BidCurvePoint",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:bidCurveConstraints",
      "@type": "rdfs:Class",
      "rdfs:label": "Bid Curve Constraints",
      "rdfs:comment": "Operational constraints for bid curve execution.",
      "schema:rangeIncludes": {
        "@id": "schema:Number"
      }
    },
    {
      "@id": "beckn:minPowerKW",
      "@type": "rdf:Property",
      "rdfs:label": "Minimum Power (kW)",
      "rdfs:comment": "Minimum power level in kilowatts.",
      "rdfs:domain": "beckn:bidCurveConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:maxPowerKW",
      "@type": "rdf:Property",
      "rdfs:label": "Maximum Power (kW)",
      "rdfs:comment": "Maximum power level in kilowatts.",
      "rdfs:domain": "beckn:bidCurveConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:rampRateKWPerMin",
      "@type": "rdf:Property",
      "rdfs:label": "Ramp Rate (kW/min)",
      "rdfs:comment": "Maximum rate of power change in kilowatts per minute.",
      "rdfs:domain": "beckn:bidCurveConstraints",
      "schema:rangeIncludes": "schema:Number"
    }
  ]
}
```

### 1.4 Usage Examples

**In itemAttributes (Resource Bid Curve)**:
```json
{
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyResource",
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
}
```

**In offerAttributes (Offer Bid Curve)**:
```json
{
  "beckn:offerAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyOffer",
    "bidCurve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 2 },
      { "price": 0.07, "powerKW": 5 }
    ],
    "constraints": {
      "minPowerKW": 0,
      "maxPowerKW": 5,
      "rampRateKWPerMin": 0.5
    }
  }
}
```

---

## 2. Objective Expression Schema

### 2.1 Purpose

Enable resources to express objectives (goals, constraints, preferences) rather than fixed commands.

### 2.2 Context Extension

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "objectives": "beckn:objectives",
    "targetChargeKWh": "beckn:targetChargeKWh",
    "targetGenerationKWh": "beckn:targetGenerationKWh",
    "targetReductionKW": "beckn:targetReductionKW",
    "deadline": "schema:endTime",
    "maxPricePerKWh": "beckn:maxPricePerKWh",
    "minPricePerKWh": "beckn:minPricePerKWh",
    "preferredSource": "beckn:preferredSource",
    "objectiveConstraints": "beckn:objectiveConstraints",
    "minChargeKWh": "beckn:minChargeKWh",
    "maxChargeKWh": "beckn:maxChargeKWh",
    "minGenerationKWh": "beckn:minGenerationKWh",
    "maxGenerationKWh": "beckn:maxGenerationKWh"
  },
  "@graph": []
}
```

### 2.3 Vocabulary Definition

```json
{
  "@graph": [
    {
      "@id": "beckn:objectives",
      "@type": "rdf:Property",
      "rdfs:label": "Objectives",
      "rdfs:comment": "Resource objectives expressing goals, constraints, and preferences for energy transactions.",
      "rdfs:domain": ["beckn:EnergyResource", "beckn:EnergyOrder"],
      "schema:rangeIncludes": "beckn:EnergyObjectives"
    },
    {
      "@id": "beckn:EnergyObjectives",
      "@type": "rdfs:Class",
      "rdfs:label": "Energy Objectives",
      "rdfs:comment": "Structured objectives for energy resources."
    },
    {
      "@id": "beckn:targetChargeKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Target Charge (kWh)",
      "rdfs:comment": "Target energy to charge (for batteries, EVs).",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:targetGenerationKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Target Generation (kWh)",
      "rdfs:comment": "Target energy to generate (for solar, wind).",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:targetReductionKW",
      "@type": "rdf:Property",
      "rdfs:label": "Target Reduction (kW)",
      "rdfs:comment": "Target demand reduction (for demand flexibility).",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:maxPricePerKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Maximum Price (per kWh)",
      "rdfs:comment": "Maximum acceptable price per kilowatt-hour.",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:minPricePerKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Minimum Price (per kWh)",
      "rdfs:comment": "Minimum acceptable price per kilowatt-hour (for generators).",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:preferredSource",
      "@type": "rdf:Property",
      "rdfs:label": "Preferred Source",
      "rdfs:comment": "Preferred energy source type (SOLAR, BATTERY, GRID, etc.).",
      "rdfs:domain": "beckn:EnergyObjectives",
      "schema:rangeIncludes": "schema:Text"
    },
    {
      "@id": "beckn:objectiveConstraints",
      "@type": "rdfs:Class",
      "rdfs:label": "Objective Constraints",
      "rdfs:comment": "Constraints for objective fulfillment."
    },
    {
      "@id": "beckn:minChargeKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Minimum Charge (kWh)",
      "rdfs:comment": "Minimum acceptable charge level.",
      "rdfs:domain": "beckn:objectiveConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:maxChargeKWh",
      "@type": "rdf:Property",
      "rdfs:label": "Maximum Charge (kWh)",
      "rdfs:comment": "Maximum acceptable charge level.",
      "rdfs:domain": "beckn:objectiveConstraints",
      "schema:rangeIncludes": "schema:Number"
    }
  ]
}
```

### 2.4 Usage Examples

**In itemAttributes (Resource Objectives)**:
```json
{
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyResource",
    "objectives": {
      "targetChargeKWh": 20,
      "deadline": "2024-12-15T18:00:00Z",
      "maxPricePerKWh": 0.12,
      "preferredSource": "SOLAR",
      "objectiveConstraints": {
        "minChargeKWh": 10,
        "maxChargeKWh": 60
      }
    }
  }
}
```

**In orderAttributes (Contract Objectives)**:
```json
{
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyOrder",
    "objectives": {
      "targetReductionKW": 50,
      "deadline": "2024-12-15T16:00:00Z",
      "maxPricePerKWh": 0.15
    }
  }
}
```

---

## 3. Locational Pricing Schema

### 3.1 Purpose

Enable grid nodes to signal locational price adders for congestion-aware pricing.

### 3.2 Context Extension

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "locationalPriceAdder": "beckn:locationalPriceAdder",
    "basePrice": "beckn:basePrice",
    "congestionMultiplier": "beckn:congestionMultiplier",
    "currentLoadPercent": "beckn:currentLoadPercent",
    "priceAdderPerPercent": "beckn:priceAdderPerPercent",
    "currentPrice": "beckn:currentPrice",
    "formula": "beckn:formula"
  },
  "@graph": []
}
```

### 3.3 Vocabulary Definition

```json
{
  "@graph": [
    {
      "@id": "beckn:locationalPriceAdder",
      "@type": "rdf:Property",
      "rdfs:label": "Locational Price Adder",
      "rdfs:comment": "Price adder based on grid location and congestion.",
      "rdfs:domain": ["beckn:GridNode", "beckn:EnergyOffer"],
      "schema:rangeIncludes": "beckn:LocationalPriceAdder"
    },
    {
      "@id": "beckn:LocationalPriceAdder",
      "@type": "rdfs:Class",
      "rdfs:label": "Locational Price Adder",
      "rdfs:comment": "Structure for locational pricing calculation."
    },
    {
      "@id": "beckn:basePrice",
      "@type": "rdf:Property",
      "rdfs:label": "Base Price",
      "rdfs:comment": "Base price per kilowatt-hour before locational adder.",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:congestionMultiplier",
      "@type": "rdf:Property",
      "rdfs:label": "Congestion Multiplier",
      "rdfs:comment": "Multiplier for congestion calculation (typically 1.0).",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:currentLoadPercent",
      "@type": "rdf:Property",
      "rdfs:label": "Current Load (%)",
      "rdfs:comment": "Current load as percentage of capacity.",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:priceAdderPerPercent",
      "@type": "rdf:Property",
      "rdfs:label": "Price Adder Per Percent",
      "rdfs:comment": "Price adder per percentage point of load.",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:currentPrice",
      "@type": "rdf:Property",
      "rdfs:label": "Current Price",
      "rdfs:comment": "Current price including locational adder (calculated).",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:formula",
      "@type": "rdf:Property",
      "rdfs:label": "Formula",
      "rdfs:comment": "Formula for calculating locational price (human-readable).",
      "rdfs:domain": "beckn:LocationalPriceAdder",
      "schema:rangeIncludes": "schema:Text"
    }
  ]
}
```

### 3.4 Usage Examples

**In itemAttributes (Grid Node)**:
```json
{
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "GridNode",
    "locationalPriceAdder": {
      "basePrice": 0.10,
      "congestionMultiplier": 1.0,
      "currentLoadPercent": 75,
      "priceAdderPerPercent": 0.001,
      "currentPrice": 0.175,
      "formula": "basePrice + (currentLoadPercent * priceAdderPerPercent)"
    }
  }
}
```

**In offerAttributes (Offer with Locational Pricing)**:
```json
{
  "beckn:offerAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyOffer",
    "locationalPriceAdder": {
      "basePrice": 0.10,
      "currentLoadPercent": 75,
      "priceAdderPerPercent": 0.001,
      "currentPrice": 0.175
    }
  }
}
```

---

## 4. Grid Node Schema

### 4.1 Purpose

Enable transformers and substations to participate as Energy Resources with grid constraints.

### 4.2 Context Extension

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "GridNode": "beckn:GridNode",
    "gridConstraints": "beckn:gridConstraints",
    "maxReverseFlowKW": "beckn:maxReverseFlowKW",
    "maxForwardFlowKW": "beckn:maxForwardFlowKW",
    "currentLoadKW": "beckn:currentLoadKW",
    "capacityKW": "beckn:capacityKW",
    "offsetCommand": "beckn:offsetCommand",
    "offsetKW": "beckn:offsetKW",
    "enabled": "schema:enabled"
  },
  "@graph": []
}
```

### 4.3 Vocabulary Definition

```json
{
  "@graph": [
    {
      "@id": "beckn:GridNode",
      "@type": "rdfs:Class",
      "rdfs:label": "Grid Node",
      "rdfs:comment": "A grid infrastructure node (transformer, substation) that can signal locational pricing and constraints.",
      "rdfs:subClassOf": "beckn:EnergyResource"
    },
    {
      "@id": "beckn:gridConstraints",
      "@type": "rdf:Property",
      "rdfs:label": "Grid Constraints",
      "rdfs:comment": "Operational constraints for grid nodes.",
      "rdfs:domain": "beckn:GridNode",
      "schema:rangeIncludes": "beckn:GridConstraints"
    },
    {
      "@id": "beckn:GridConstraints",
      "@type": "rdfs:Class",
      "rdfs:label": "Grid Constraints",
      "rdfs:comment": "Structure for grid operational constraints."
    },
    {
      "@id": "beckn:maxReverseFlowKW",
      "@type": "rdf:Property",
      "rdfs:label": "Maximum Reverse Flow (kW)",
      "rdfs:comment": "Maximum reverse power flow (from distribution to transmission) in kilowatts.",
      "rdfs:domain": "beckn:GridConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:maxForwardFlowKW",
      "@type": "rdf:Property",
      "rdfs:label": "Maximum Forward Flow (kW)",
      "rdfs:comment": "Maximum forward power flow (from transmission to distribution) in kilowatts.",
      "rdfs:domain": "beckn:GridConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:currentLoadKW",
      "@type": "rdf:Property",
      "rdfs:label": "Current Load (kW)",
      "rdfs:comment": "Current load in kilowatts.",
      "rdfs:domain": "beckn:GridConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:capacityKW",
      "@type": "rdf:Property",
      "rdfs:label": "Capacity (kW)",
      "rdfs:comment": "Total capacity in kilowatts.",
      "rdfs:domain": "beckn:GridConstraints",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:offsetCommand",
      "@type": "rdf:Property",
      "rdfs:label": "Offset Command",
      "rdfs:comment": "Grid operator command to apply offset for flat bid curve plateaus.",
      "rdfs:domain": ["beckn:GridNode", "beckn:EnergyOrder", "beckn:EnergyFulfillment"],
      "schema:rangeIncludes": "beckn:OffsetCommand"
    },
    {
      "@id": "beckn:OffsetCommand",
      "@type": "rdfs:Class",
      "rdfs:label": "Offset Command",
      "rdfs:comment": "Structure for grid operator offset commands."
    },
    {
      "@id": "beckn:offsetKW",
      "@type": "rdf:Property",
      "rdfs:label": "Offset (kW)",
      "rdfs:comment": "Power offset in kilowatts to apply.",
      "rdfs:domain": "beckn:OffsetCommand",
      "schema:rangeIncludes": "schema:Number"
    }
  ]
}
```

### 4.4 Usage Examples

**Grid Node as Energy Resource**:
```json
{
  "beckn:id": "transformer-zone-5",
  "beckn:descriptor": {
    "schema:name": "Neighborhood Transformer Zone 5"
  },
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "GridNode",
    "locationalPriceAdder": {
      "basePrice": 0.10,
      "currentLoadPercent": 75,
      "priceAdderPerPercent": 0.001,
      "currentPrice": 0.175
    },
    "gridConstraints": {
      "maxReverseFlowKW": 50,
      "maxForwardFlowKW": 200,
      "currentLoadKW": 150,
      "capacityKW": 200
    }
  }
}
```

**Offset Command in Order**:
```json
{
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyOrder",
    "offsetCommand": {
      "enabled": true,
      "offsetKW": -2.0
    }
  }
}
```

---

## 5. Settlement Schema

### 5.1 Purpose

Enable unambiguous billing with multi-party revenue flows.

### 5.2 Context Extension

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "settlement": "beckn:settlement",
    "revenueFlows": "beckn:revenueFlows",
    "revenueFlow": "beckn:RevenueFlow",
    "party": "beckn:party",
    "era": "beckn:era",
    "role": "beckn:role",
    "amount": "schema:amount",
    "currency": "schema:currency",
    "description": "schema:description",
    "settlementReport": "beckn:settlementReport",
    "reportId": "beckn:reportId",
    "totalAmount": "beckn:totalAmount",
    "generatedAt": "schema:dateCreated",
    "meterReadings": "beckn:meterReadings"
  },
  "@graph": []
}
```

### 5.3 Vocabulary Definition

```json
{
  "@graph": [
    {
      "@id": "beckn:settlement",
      "@type": "rdf:Property",
      "rdfs:label": "Settlement",
      "rdfs:comment": "Settlement information including revenue flows and billing report.",
      "rdfs:domain": "beckn:EnergyOrder",
      "schema:rangeIncludes": "beckn:Settlement"
    },
    {
      "@id": "beckn:Settlement",
      "@type": "rdfs:Class",
      "rdfs:label": "Settlement",
      "rdfs:comment": "Structure for settlement and revenue distribution."
    },
    {
      "@id": "beckn:revenueFlows",
      "@type": "rdf:Property",
      "rdfs:label": "Revenue Flows",
      "rdfs:comment": "Array of revenue flow entries for multi-party settlement.",
      "rdfs:domain": "beckn:Settlement",
      "schema:rangeIncludes": "beckn:RevenueFlow"
    },
    {
      "@id": "beckn:RevenueFlow",
      "@type": "rdfs:Class",
      "rdfs:label": "Revenue Flow",
      "rdfs:comment": "A single revenue flow entry for a party."
    },
    {
      "@id": "beckn:party",
      "@type": "rdf:Property",
      "rdfs:label": "Party",
      "rdfs:comment": "Party receiving revenue.",
      "rdfs:domain": "beckn:RevenueFlow",
      "schema:rangeIncludes": "beckn:Party"
    },
    {
      "@id": "beckn:Party",
      "@type": "rdfs:Class",
      "rdfs:label": "Party",
      "rdfs:comment": "Structure for party identification."
    },
    {
      "@id": "beckn:era",
      "@type": "rdf:Property",
      "rdfs:label": "Energy Resource Address",
      "rdfs:comment": "Energy Resource Address of the party.",
      "rdfs:domain": "beckn:Party",
      "schema:rangeIncludes": "schema:Text"
    },
    {
      "@id": "beckn:role",
      "@type": "rdf:Property",
      "rdfs:label": "Role",
      "rdfs:comment": "Role of the party (SELLER, BUYER, GRID_OPERATOR, AGGREGATOR, GOVERNMENT).",
      "rdfs:domain": "beckn:Party",
      "schema:rangeIncludes": "schema:Text"
    },
    {
      "@id": "beckn:settlementReport",
      "@type": "rdf:Property",
      "rdfs:label": "Settlement Report",
      "rdfs:comment": "Structured billing document for settlement.",
      "rdfs:domain": "beckn:Settlement",
      "schema:rangeIncludes": "beckn:SettlementReport"
    },
    {
      "@id": "beckn:SettlementReport",
      "@type": "rdfs:Class",
      "rdfs:label": "Settlement Report",
      "rdfs:comment": "Structured billing document."
    },
    {
      "@id": "beckn:reportId",
      "@type": "rdf:Property",
      "rdfs:label": "Report ID",
      "rdfs:comment": "Unique identifier for the settlement report.",
      "rdfs:domain": "beckn:SettlementReport",
      "schema:rangeIncludes": "schema:Text"
    },
    {
      "@id": "beckn:totalAmount",
      "@type": "rdf:Property",
      "rdfs:label": "Total Amount",
      "rdfs:comment": "Total settlement amount.",
      "rdfs:domain": "beckn:SettlementReport",
      "schema:rangeIncludes": "schema:MonetaryAmount"
    }
  ]
}
```

### 5.4 Usage Examples

**Settlement in orderAttributes**:
```json
{
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    "@type": "EnergyOrder",
    "settlement": {
      "settlementCycles": [{
        "cycleId": "settle-2024-10-04-001",
        "status": "SETTLED",
        "amount": 100.0,
        "currency": "INR"
      }],
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
        "generatedAt": "2024-10-04T18:30:00Z"
      }
    }
  }
}
```

---

## 6. Aggregate Action Schema

### 6.1 Purpose

Enable bid curve aggregation for market clearing.

### 6.2 Action Structure

**Request** (`aggregate`):
```json
{
  "context": {
    "version": "2.0.0",
    "action": "aggregate",
    "domain": "beckn.one:deg:energy-coordination:*",
    "timestamp": "2024-12-15T14:00:00Z",
    "message_id": "msg-aggregate-001",
    "transaction_id": "txn-aggregate-001",
    "bap_id": "bap.market-clearing-agent.com",
    "bap_uri": "https://bap.market-clearing-agent.com",
    "bpp_id": "bpp.market-clearing-agent.com",
    "bpp_uri": "https://bpp.market-clearing-agent.com",
    "ttl": "PT30S"
  },
  "message": {
    "aggregationRequest": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
      "@type": "AggregationRequest",
      "participants": [
        {
          "era": "solar-panel-001",
          "bidCurve": [
            { "price": 0.05, "powerKW": 0 },
            { "price": 0.06, "powerKW": 2 },
            { "price": 0.07, "powerKW": 5 }
          ]
        },
        {
          "era": "ev-battery-002",
          "bidCurve": [
            { "price": 0.08, "powerKW": -11 },
            { "price": 0.10, "powerKW": -5 },
            { "price": 0.12, "powerKW": 0 }
          ]
        },
        {
          "era": "transformer-zone-5",
          "locationalPriceAdder": {
            "basePrice": 0.10,
            "currentLoadPercent": 75,
            "priceAdderPerPercent": 0.001
          }
        }
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

**Response** (`on_aggregate`):
```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_aggregate",
    "domain": "beckn.one:deg:energy-coordination:*",
    "timestamp": "2024-12-15T14:00:05Z",
    "message_id": "msg-on-aggregate-001",
    "transaction_id": "txn-aggregate-001",
    "bap_id": "bap.market-clearing-agent.com",
    "bap_uri": "https://bap.market-clearing-agent.com",
    "bpp_id": "bpp.market-clearing-agent.com",
    "bpp_uri": "https://bpp.market-clearing-agent.com",
    "ttl": "PT30S"
  },
  "message": {
    "aggregationResult": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
      "@type": "AggregationResult",
      "clearingPrice": 0.075,
      "clearingQuantityKW": 50.0,
      "setpoints": [
        {
          "era": "solar-panel-001",
          "setpointKW": 3.5
        },
        {
          "era": "ev-battery-002",
          "setpointKW": -8.0
        }
      ],
      "locationalPrice": 0.175,
      "timestamp": "2024-12-15T14:00:00Z"
    }
  }
}
```

### 6.3 Vocabulary Definition

```json
{
  "@graph": [
    {
      "@id": "beckn:AggregationRequest",
      "@type": "rdfs:Class",
      "rdfs:label": "Aggregation Request",
      "rdfs:comment": "Request for bid curve aggregation."
    },
    {
      "@id": "beckn:participants",
      "@type": "rdf:Property",
      "rdfs:label": "Participants",
      "rdfs:comment": "Array of participants with bid curves.",
      "rdfs:domain": "beckn:AggregationRequest",
      "schema:rangeIncludes": "beckn:Participant"
    },
    {
      "@id": "beckn:aggregationType",
      "@type": "rdf:Property",
      "rdfs:label": "Aggregation Type",
      "rdfs:comment": "Type of aggregation (MARKET_CLEARING, CAPACITY_AGGREGATION, etc.).",
      "rdfs:domain": "beckn:AggregationRequest",
      "schema:rangeIncludes": "schema:Text"
    },
    {
      "@id": "beckn:AggregationResult",
      "@type": "rdfs:Class",
      "rdfs:label": "Aggregation Result",
      "rdfs:comment": "Result of bid curve aggregation."
    },
    {
      "@id": "beckn:clearingPrice",
      "@type": "rdf:Property",
      "rdfs:label": "Clearing Price",
      "rdfs:comment": "Market clearing price per kilowatt-hour.",
      "rdfs:domain": "beckn:AggregationResult",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:clearingQuantityKW",
      "@type": "rdf:Property",
      "rdfs:label": "Clearing Quantity (kW)",
      "rdfs:comment": "Clearing quantity in kilowatts.",
      "rdfs:domain": "beckn:AggregationResult",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:setpoints",
      "@type": "rdf:Property",
      "rdfs:label": "Setpoints",
      "rdfs:comment": "Array of setpoints for each participant.",
      "rdfs:domain": "beckn:AggregationResult",
      "schema:rangeIncludes": "beckn:Setpoint"
    },
    {
      "@id": "beckn:Setpoint",
      "@type": "rdfs:Class",
      "rdfs:label": "Setpoint",
      "rdfs:comment": "Power setpoint for a resource."
    },
    {
      "@id": "beckn:setpointKW",
      "@type": "rdf:Property",
      "rdfs:label": "Setpoint (kW)",
      "rdfs:comment": "Power setpoint in kilowatts.",
      "rdfs:domain": "beckn:Setpoint",
      "schema:rangeIncludes": "schema:Number"
    },
    {
      "@id": "beckn:locationalPrice",
      "@type": "rdf:Property",
      "rdfs:label": "Locational Price",
      "rdfs:comment": "Final price including locational adder.",
      "rdfs:domain": "beckn:AggregationResult",
      "schema:rangeIncludes": "schema:Number"
    }
  ]
}
```

---

## 7. Complete Context Examples

### 7.1 Combined Context File

**File**: `EnergyCoordination/v1/context.jsonld`

```json
{
  "@context": {
    "@version": 1.1,
    "schema": "https://schema.org/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "beckn": "./vocab.jsonld#",
    
    "EnergyCoordination": "beckn:EnergyCoordination",
    
    "bidCurve": "beckn:bidCurve",
    "bidCurvePoint": "beckn:BidCurvePoint",
    "powerKW": "beckn:powerKW",
    "constraints": "beckn:bidCurveConstraints",
    "minPowerKW": "beckn:minPowerKW",
    "maxPowerKW": "beckn:maxPowerKW",
    "rampRateKWPerMin": "beckn:rampRateKWPerMin",
    
    "objectives": "beckn:objectives",
    "targetChargeKWh": "beckn:targetChargeKWh",
    "targetGenerationKWh": "beckn:targetGenerationKWh",
    "targetReductionKW": "beckn:targetReductionKW",
    "deadline": "schema:endTime",
    "maxPricePerKWh": "beckn:maxPricePerKWh",
    "minPricePerKWh": "beckn:minPricePerKWh",
    "preferredSource": "beckn:preferredSource",
    "objectiveConstraints": "beckn:objectiveConstraints",
    "minChargeKWh": "beckn:minChargeKWh",
    "maxChargeKWh": "beckn:maxChargeKWh",
    
    "locationalPriceAdder": "beckn:locationalPriceAdder",
    "basePrice": "beckn:basePrice",
    "congestionMultiplier": "beckn:congestionMultiplier",
    "currentLoadPercent": "beckn:currentLoadPercent",
    "priceAdderPerPercent": "beckn:priceAdderPerPercent",
    "currentPrice": "beckn:currentPrice",
    "formula": "beckn:formula",
    
    "GridNode": "beckn:GridNode",
    "gridConstraints": "beckn:gridConstraints",
    "maxReverseFlowKW": "beckn:maxReverseFlowKW",
    "maxForwardFlowKW": "beckn:maxForwardFlowKW",
    "currentLoadKW": "beckn:currentLoadKW",
    "capacityKW": "beckn:capacityKW",
    "offsetCommand": "beckn:offsetCommand",
    "offsetKW": "beckn:offsetKW",
    
    "settlement": "beckn:settlement",
    "revenueFlows": "beckn:revenueFlows",
    "revenueFlow": "beckn:RevenueFlow",
    "party": "beckn:party",
    "era": "beckn:era",
    "role": "beckn:role",
    "settlementReport": "beckn:settlementReport",
    "reportId": "beckn:reportId",
    "totalAmount": "beckn:totalAmount",
    
    "clearingPrice": "beckn:clearingPrice",
    "clearingQuantityKW": "beckn:clearingQuantityKW",
    "setpoints": "beckn:setpoints",
    "setpointKW": "beckn:setpointKW",
    "locationalPrice": "beckn:locationalPrice"
  },
  "@graph": []
}
```

---

## 8. Integration with Existing Schemas

### 8.1 Extending EvChargingService Schema

**Add to `EvChargingService/v1/context.jsonld`**:
```json
{
  "@context": {
    "energyCoordination": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    
    "bidCurve": "energyCoordination:bidCurve",
    "objectives": "energyCoordination:objectives",
    "locationalPriceAdder": "energyCoordination:locationalPriceAdder",
    "setpointKW": "energyCoordination:setpointKW",
    "clearingPrice": "energyCoordination:clearingPrice"
  }
}
```

### 8.2 Extending EnergyTradeOffer Schema

**Add to `EnergyTradeOffer/v0.2/context.jsonld`**:
```json
{
  "@context": {
    "energyCoordination": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    
    "bidCurve": "energyCoordination:bidCurve",
    "locationalPriceAdder": "energyCoordination:locationalPriceAdder",
    "clearingPrice": "energyCoordination:clearingPrice"
  }
}
```

### 8.3 Extending EnergyTradeContract Schema

**Add to `EnergyTradeContract/v0.2/context.jsonld`**:
```json
{
  "@context": {
    "energyCoordination": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/EnergyCoordination/v1/context.jsonld",
    
    "objectives": "energyCoordination:objectives",
    "setpointKW": "energyCoordination:setpointKW",
    "clearingPrice": "energyCoordination:clearingPrice",
    "settlement": "energyCoordination:settlement",
    "offsetCommand": "energyCoordination:offsetCommand"
  }
}
```

---

## 9. Summary

### 9.1 Schema Extensions Summary

| Extension | Context File | Vocab File | Attribute Slot |
|-----------|--------------|------------|----------------|
| **Bid Curve** | `EnergyCoordination/v1/context.jsonld` | `EnergyCoordination/v1/vocab.jsonld` | `itemAttributes`, `offerAttributes` |
| **Objectives** | `EnergyCoordination/v1/context.jsonld` | `EnergyCoordination/v1/vocab.jsonld` | `itemAttributes`, `orderAttributes` |
| **Locational Pricing** | `EnergyCoordination/v1/context.jsonld` | `EnergyCoordination/v1/vocab.jsonld` | `itemAttributes`, `offerAttributes` |
| **Grid Node** | `EnergyCoordination/v1/context.jsonld` | `EnergyCoordination/v1/vocab.jsonld` | `itemAttributes` |
| **Settlement** | `EnergyCoordination/v1/context.jsonld` | `EnergyCoordination/v1/vocab.jsonld` | `orderAttributes` |
| **Aggregate Action** | Core Beckn v2 | `EnergyCoordination/v1/vocab.jsonld` | `message.aggregationRequest` |

### 9.2 Schema Design Principles

1. **Composability**: Extensions compose with existing schemas
2. **Reusability**: Single context file for all coordination extensions
3. **Backward Compatibility**: Extensions are optional, existing schemas work without them
4. **JSON-LD Compliance**: Proper `@context` and `@type` usage
5. **Semantic Clarity**: Clear property names and descriptions

---

**Status**: Complete  
**Next Action**: Create example messages (outputs/examples/)

