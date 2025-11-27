# Use Case Sequence Diagrams
## Mermaid Sequence Diagrams for Energy Exchange Use Cases

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document contains Mermaid sequence diagrams for all energy exchange use cases, showing how Beckn Protocol building blocks (including proposed extensions) enable each use case. Each diagram shows:

- Beckn actions and responses
- Attribute slot usage
- Protocol integration points
- Bid curve flows (where applicable)
- Market clearing patterns (where applicable)

> **Pay-as-clear note**: For market-based flows (Sections 2, 4, 5, 6, 7) `select/on_select` is intentionally skipped. Participants confirm “pay-as-clear” bids, and `on_confirm` returns the binding clearing outcome once the market clears.

---

## Table of Contents

- [Use Case Sequence Diagrams](#use-case-sequence-diagrams)
  - [Mermaid Sequence Diagrams for Energy Exchange Use Cases](#mermaid-sequence-diagrams-for-energy-exchange-use-cases)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [1. EV Charging (Basic)](#1-ev-charging-basic)
  - [2. EV Charging (Demand Flexibility)](#2-ev-charging-demand-flexibility)
  - [3. P2P Trading (Basic)](#3-p2p-trading-basic)
  - [4. P2P Trading (Market-Based)](#4-p2p-trading-market-based)
  - [5. Demand Flexibility](#5-demand-flexibility)
  - [6. VPP Coordination](#6-vpp-coordination)
  - [7. Grid Services](#7-grid-services)
  - [Summary](#summary)

---

## 1. EV Charging (Basic)

**Use Case**: User discovers and reserves a charging slot at a fixed price

**Key Features**:
- Standard Beckn flow
- Fixed pricing
- Reservation-based

```mermaid
sequenceDiagram
    participant User
    participant BAP as EV User App (BAP)
    participant CDS as Catalog Discovery Service
    participant BPP as CPO Platform (BPP)
    participant EVSE as Charging Station

    Note over User,EVSE: Discovery Phase
    User->>BAP: Search for charging stations
    BAP->>CDS: discover(location, filters)
    CDS->>BPP: Route discover request
    BPP->>BPP: Filter catalog by location/filters
    BPP-->>CDS: on_discover(catalog with EVSEs)
    CDS-->>BAP: on_discover(catalog)
    BAP-->>User: Show available chargers

    Note over User,EVSE: Selection Phase
    User->>BAP: Select charger
    BAP->>BPP: select(item_id, quantity)
    BPP->>BPP: Generate quote
    BPP-->>BAP: on_select(quote with pricing)
    BAP-->>User: Show quote

    Note over User,EVSE: Initialization Phase
    User->>BAP: Provide payment details
    BAP->>BPP: init(order, payment)
    BPP->>BPP: Validate payment
    BPP-->>BAP: on_init(terms, payment auth)
    BAP-->>User: Show terms

    Note over User,EVSE: Confirmation Phase
    User->>BAP: Confirm reservation
    BAP->>BPP: confirm(order)
    BPP->>BPP: Create reservation
    BPP-->>BAP: on_confirm(reservation_id)
    BAP-->>User: Reservation confirmed

    Note over User,EVSE: Fulfillment Phase
    User->>EVSE: Plug in vehicle
    BAP->>BPP: update(start charging)
    BPP->>EVSE: OCPP: StartTransaction
    EVSE-->>BPP: OCPP: Transaction started
    BPP-->>BAP: on_update(session started)
    
    loop Every 30 seconds
        BAP->>BPP: track(order_id)
        BPP->>EVSE: OCPP: GetMeterValues
        EVSE-->>BPP: OCPP: MeterValues
        BPP-->>BAP: on_track(energy, power, cost)
        BAP-->>User: Show progress
    end

    User->>EVSE: Unplug vehicle
    EVSE->>BPP: OCPP: StopTransaction
    BPP->>BPP: Calculate final cost
    BPP->>BAP: on_update(session ended, final_cost)
    BAP->>BPP: update(stop charging)
    BPP-->>BAP: on_update(settlement complete)
    BAP-->>User: Show final bill
```

**Attribute Slots Used**:
- `itemAttributes`: EVSE specifications (connectorType, maxPowerKW, etc.)
- `offerAttributes`: Fixed pricing (per-kWh rate)
- `fulfillmentAttributes`: Session management (reservation, charging status)

---

## 2. EV Charging (Demand Flexibility)

**Use Case**: EV expresses bid curve, market clears at confirmation time, EV receives optimal setpoint

**Key Features**:
- Bid curve expression
- Market clearing at confirmation
- Dynamic setpoint assignment

```mermaid
sequenceDiagram
    participant User
    participant BAP as EV App (BAP)
    participant MCA as Market Clearing Agent (BPP)
    participant BPP as CPO Platform (BPP)
    participant EVSE as Charging Station

    Note over User,EVSE: Intent Expression with Bid Curve
    User->>BAP: Set charging goal (20 kWh by 6 PM)
    BAP->>BAP: Construct bid curve from objectives
    Note right of BAP: bidCurve:<br/>[{price: 0.08, powerKW: -11},<br/>{price: 0.10, powerKW: -5}]
    BAP->>MCA: discover(intent with bidCurve, objectives)
    Note right of MCA: objectives:<br/>{targetChargeKWh: 20,<br/>deadline: "18:00",<br/>maxPrice: 0.12}

    Note over User,EVSE: Market Clearing
    MCA->>MCA: Collect bid curves from all participants
    MCA->>MCA: aggregate(bidCurves)
    Note right of MCA: Aggregate supply/demand<br/>Find clearing price
    MCA->>MCA: Calculate clearing price: ₹0.09/kWh
    MCA->>MCA: Economic disaggregation:<br/>EV setpoint: -8 kW

    Note over User,EVSE: Catalogue Response with Clearing Price
    MCA-->>BAP: on_discover(catalog with clearing price)
    Note right of BAP: offerAttributes:<br/>{clearingPrice: 0.09,<br/>setpointKW: -8.0}

    Note over User,EVSE: Initialization Phase
    User->>BAP: Provide payment details
    BAP->>MCA: init(order, payment)
    MCA->>BPP: Route to CPO
    BPP-->>MCA: on_init(terms)
    MCA-->>BAP: on_init(terms)
    BAP-->>User: Show terms

    Note over User,EVSE: Synchronous Confirmation (Market Clearing)
    User->>BAP: Confirm order
    BAP->>MCA: confirm(order with accepted clearing price)
    Note right of MCA: Synchronous confirmation:<br/>Price locked at ₹0.09/kWh
    MCA->>MCA: Lock clearing price
    MCA->>BPP: confirm(order with setpoint)
    BPP->>EVSE: OCPP: SetChargingProfile(8 kW)
    EVSE-->>BPP: OCPP: Profile accepted
    BPP-->>MCA: on_confirm(setpoint applied)
    MCA-->>BAP: on_confirm(order confirmed, setpoint: -8 kW)
    Note right of BAP: orderAttributes:<br/>{setpointKW: -8.0,<br/>clearingPrice: 0.09}
    BAP-->>User: Order confirmed (8 kW charging)

    Note over User,EVSE: Fulfillment Phase
    User->>EVSE: Plug in vehicle
    BAP->>BPP: update(start charging)
    BPP->>EVSE: OCPP: StartTransaction
    EVSE->>EVSE: Charge at 8 kW (setpoint)
    EVSE-->>BPP: OCPP: Transaction started
    
    loop Every 30 seconds
        BAP->>BPP: track(order_id)
        BPP->>EVSE: OCPP: GetMeterValues
        EVSE-->>BPP: OCPP: MeterValues (8 kW actual)
        BPP-->>BAP: on_track(energy, power, cost at ₹0.09/kWh)
        BAP-->>User: Show progress
    end

    User->>EVSE: Unplug vehicle (20 kWh reached)
    EVSE->>BPP: OCPP: StopTransaction
    BPP->>BPP: Calculate final cost (20 kWh × ₹0.09)
    BPP->>BAP: on_update(session ended, final_cost)
    BAP-->>User: Show final bill
```

**Attribute Slots Used**:
- `itemAttributes.bidCurve`: EV's price/power preferences
- `itemAttributes.objectives`: Charging goals and constraints
- `offerAttributes.clearingPrice`: Market-cleared price
- `offerAttributes.setpointKW`: Optimal charging rate
- `orderAttributes.setpointKW`: Confirmed setpoint
- `orderAttributes.clearingPrice`: Locked clearing price

**Key Innovation**: Prices discovered at confirmation time, not at offer time.

---

## 3. P2P Trading (Basic)

**Use Case**: Consumer buys energy from prosumer at fixed price

**Key Features**:
- Standard Beckn flow
- Fixed pricing
- Meter-based settlement

```mermaid
sequenceDiagram
    participant Consumer
    participant BAP as Consumer App (BAP)
    participant CDS as Catalog Discovery Service
    participant BPP as Prosumer Platform (BPP)
    participant Utility as Utility BPP
    participant Meter as Smart Meter

    Note over Consumer,Meter: Discovery Phase
    Consumer->>BAP: Search for solar energy
    BAP->>CDS: discover(filters: sourceType=SOLAR)
    CDS->>BPP: Route discover request
    BPP->>BPP: Filter catalog
    BPP-->>CDS: on_discover(catalog with energy resources)
    CDS-->>BAP: on_discover(catalog)
    BAP-->>Consumer: Show available energy

    Note over Consumer,Meter: Selection Phase
    Consumer->>BAP: Select energy resource
    BAP->>BPP: select(item_id, quantity: 10 kWh)
    BPP->>BPP: Generate quote
    BPP-->>BAP: on_select(quote: ₹5.50/kWh)
    BAP-->>Consumer: Show quote (₹55 total)

    Note over Consumer,Meter: Initialization Phase
    Consumer->>BAP: Provide meter ID
    BAP->>BPP: init(order, meterId: 98765456)
    BPP->>Utility: cascaded init(verify meter, calculate wheeling)
    Utility->>Utility: Verify sanctioned load
    Utility->>Utility: Calculate wheeling charges
    Utility-->>BPP: on_init(wheeling: ₹1/kWh, allowed: 10 kW)
    BPP-->>BAP: cascaded_on_init(quote with wheeling)
    BAP-->>Consumer: Show final quote (₹65 total)

    Note over Consumer,Meter: Confirmation Phase
    Consumer->>BAP: Confirm order
    BAP->>BPP: confirm(order)
    BPP->>Utility: cascaded confirm(log trade)
    Utility->>Utility: Log trade, deduct sanctioned load
    Utility-->>BPP: on_confirm(trade logged)
    BPP-->>BAP: on_confirm(contract ACTIVE)
    BAP-->>Consumer: Order confirmed

    Note over Consumer,Meter: Fulfillment Phase
    Note right of Meter: Delivery window: 2-4 PM
    Meter->>Utility: Meter readings (every 15 min)
    Utility->>Utility: Calculate actual delivery
    Utility->>BPP: on_update(delivery status, meter readings)
    BPP->>BAP: cascaded on_update(delivery progress)
    BAP-->>Consumer: Show delivery progress

    Note over Consumer,Meter: Settlement Phase
    Utility->>Utility: Calculate final settlement
    Utility->>BPP: on_update(settlement: 10 kWh delivered)
    BPP->>BPP: Calculate final cost
    BPP->>BAP: cascaded on_update(settlement complete)
    BAP->>BPP: Payment (₹65)
    BPP-->>BAP: on_update(payment received)
    BAP-->>Consumer: Show final settlement
```

**Attribute Slots Used**:
- `itemAttributes`: Energy resource specs (sourceType, deliveryMode, meterId)
- `offerAttributes`: Trading terms (pricingModel, settlementType, wheelingCharges)
- `orderAttributes`: Contract details (EnergyTradeContract)
- `fulfillmentAttributes`: Delivery tracking (EnergyTradeDelivery)

---

## 4. P2P Trading (Market-Based)

**Use Case**: Multiple prosumers express bid curves, market clears, economic disaggregation distributes setpoints

**Key Features**:
- Bid curve aggregation
- Market clearing at confirmation
- Economic disaggregation

```mermaid
sequenceDiagram
    participant Consumer
    participant BAP as Consumer App (BAP)
    participant MCA as Market Clearing Agent (BPP)
    participant Prosumer1 as Solar Prosumer 1 (BPP)
    participant Prosumer2 as Solar Prosumer 2 (BPP)
    participant Utility as Utility BPP
    participant Meter1 as Meter 1
    participant Meter2 as Meter 2

    Note over Consumer,Meter2: Prosumers Publish Catalogues with Bid Curves
    Prosumer1->>MCA: Publish catalogue
    Note right of Prosumer1: offerAttributes.bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]
    Prosumer2->>MCA: Publish catalogue
    Note right of Prosumer2: offerAttributes.bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]

    Note over Consumer,Meter2: Consumer Expresses Intent
    Consumer->>BAP: Buy 50 kWh, max ₹6/kWh
    BAP->>MCA: discover(intent: 50 kWh, maxPrice: 0.06)
    Note right of BAP: Intent with quantity<br/>and price constraint

    Note over Consumer,Meter2: Market Clearing Agent Aggregates
    MCA->>MCA: Collect all bid curves
    MCA->>MCA: aggregate(bidCurves from 10 prosumers)
    Note right of MCA: Aggregate Supply Curve:<br/>Price 0.06 → 20 kW<br/>Price 0.07 → 50 kW
    MCA->>MCA: Find clearing price: ₹0.0625/kWh
    MCA->>MCA: Economic disaggregation:<br/>Each prosumer: ~5 kWh

    Note over Consumer,Meter2: Market Clearing Agent Responds
    MCA-->>BAP: on_discover(catalog with clearing price)
    Note right of BAP: offerAttributes:<br/>{clearingPrice: 0.0625,<br/>aggregateQuantity: 50 kWh}

    Note over Consumer,Meter2: Initialization Phase
    Consumer->>BAP: Provide meter ID
    BAP->>MCA: init(order, meterId: 98765456)
    MCA->>Utility: cascaded init(verify meter, calculate wheeling)
    Utility->>Utility: Verify sanctioned load
    Utility-->>MCA: on_init(wheeling: ₹1/kWh)
    MCA-->>BAP: on_init(terms with wheeling)
    BAP-->>Consumer: Show final quote

    Note over Consumer,Meter2: Synchronous Confirmation (Market Clearing)
    Consumer->>BAP: Confirm order
    BAP->>MCA: confirm(order with accepted clearing price)
    Note right of MCA: Synchronous confirmation:<br/>Price locked at ₹0.0625/kWh
    MCA->>MCA: Lock clearing price
    MCA->>MCA: Economic disaggregation:<br/>Prosumer1: 5 kWh<br/>Prosumer2: 5 kWh<br/>... (10 prosumers)
    
    loop For each prosumer
        MCA->>Prosumer1: confirm(order with setpoint: 5 kWh)
        Prosumer1->>Prosumer1: Apply setpoint
        Prosumer1-->>MCA: on_confirm(setpoint applied)
    end
    
    MCA->>Utility: cascaded confirm(log trades)
    Utility->>Utility: Log all trades
    Utility-->>MCA: on_confirm(trades logged)
    MCA-->>BAP: on_confirm(contract ACTIVE, setpoints distributed)
    Note right of BAP: orderAttributes:<br/>{clearingPrice: 0.0625,<br/>setpoints: [{era: "prosumer1", quantity: 5}, ...]}
    BAP-->>Consumer: Order confirmed

    Note over Consumer,Meter2: Fulfillment Phase
    Note right of Meter1: Each prosumer delivers<br/>at setpoint (5 kWh)
    Meter1->>Utility: Meter readings
    Meter2->>Utility: Meter readings
    Utility->>Utility: Aggregate delivery: 50 kWh
    Utility->>MCA: on_update(delivery: 50 kWh)
    MCA->>BAP: cascaded on_update(delivery progress)
    BAP-->>Consumer: Show delivery progress

    Note over Consumer,Meter2: Settlement Phase
    Utility->>Utility: Calculate final settlement
    Utility->>MCA: on_update(settlement: 50 kWh delivered)
    MCA->>MCA: Calculate revenue flows
    Note right of MCA: Revenue flows:<br/>- Prosumers: ₹3.125<br/>- Utility (wheeling): ₹50<br/>- Platform fee: ₹5<br/>- Tax: ₹5
    MCA->>BAP: cascaded on_update(settlement complete)
    BAP->>MCA: Payment (₹63.125 total)
    MCA-->>BAP: on_update(payment received)
    BAP-->>Consumer: Show final settlement
```

**Attribute Slots Used**:
- `offerAttributes.bidCurve`: Prosumer price/power preferences
- `offerAttributes.clearingPrice`: Market-cleared price
- `orderAttributes.clearingPrice`: Locked clearing price
- `orderAttributes.setpoints`: Distributed setpoints to prosumers
- `orderAttributes.settlement.revenueFlows`: Multi-party revenue distribution

**Key Innovation**: Market clearing at confirmation time, economic disaggregation distributes setpoints.

---

## 5. Demand Flexibility

**Use Case**: Grid operator signals need, devices express bid curves, market clears, setpoints distributed

**Key Features**:
- Objective-driven coordination
- Bid curve aggregation
- Demand reduction setpoints

```mermaid
sequenceDiagram
    participant GridOp as Grid Operator
    participant MCA as Market Clearing Agent (BPP)
    participant Device1 as Smart Device 1 (BAP)
    participant Device2 as Smart Device 2 (BAP)
    participant Device3 as Smart Device 3 (BAP)
    participant Protocol as IEEE 2030.5/OCPP

    Note over GridOp,Protocol: Grid Operator Signals Need
    GridOp->>MCA: Publish objective
    Note right of GridOp: objectives:<br/>{targetReductionKW: 50,<br/>timeWindow: "14:00-16:00",<br/>maxPrice: 0.15}

    Note over GridOp,Protocol: Devices Express Bid Curves
    Device1->>MCA: discover(intent with bidCurve)
    Note right of Device1: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -2},<br/>{price: 0.15, powerKW: -5}]
    Device2->>MCA: discover(intent with bidCurve)
    Note right of Device2: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -3},<br/>{price: 0.15, powerKW: -7}]
    Device3->>MCA: discover(intent with bidCurve)
    Note right of Device3: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -1},<br/>{price: 0.15, powerKW: -3}]

    Note over GridOp,Protocol: Market Clearing Agent Aggregates
    MCA->>MCA: Collect all bid curves (20 devices)
    MCA->>MCA: aggregate(bidCurves)
    Note right of MCA: Aggregate Demand Reduction:<br/>Price 0.12 → -6 kW<br/>Price 0.15 → -15 kW<br/>(from 3 devices shown)
    MCA->>MCA: Find clearing price: ₹0.13/kWh
    MCA->>MCA: Economic disaggregation:<br/>Device1: -3.5 kW<br/>Device2: -5.0 kW<br/>Device3: -2.0 kW<br/>... (total: 50 kW)

    Note over GridOp,Protocol: Market Clearing Agent Responds
    MCA-->>Device1: on_discover(catalog with clearing price)
    MCA-->>Device2: on_discover(catalog with clearing price)
    MCA-->>Device3: on_discover(catalog with clearing price)
    Note right of MCA: offerAttributes:<br/>{clearingPrice: 0.13,<br/>setpointKW: -3.5}

    Note over GridOp,Protocol: Initialization Phase
    Device1->>MCA: init(order)
    Device2->>MCA: init(order)
    Device3->>MCA: init(order)
    MCA-->>Device1: on_init(terms)
    MCA-->>Device2: on_init(terms)
    MCA-->>Device3: on_init(terms)

    Note over GridOp,Protocol: Synchronous Confirmation (Market Clearing)
    Device1->>MCA: confirm(order with accepted clearing price)
    Device2->>MCA: confirm(order with accepted clearing price)
    Device3->>MCA: confirm(order with accepted clearing price)
    Note right of MCA: Synchronous confirmation:<br/>Price locked at ₹0.13/kWh<br/>All devices confirm
    MCA->>MCA: Lock clearing price
    MCA->>MCA: Economic disaggregation:<br/>Distribute setpoints
    
    loop For each device
        MCA->>Device1: on_confirm(setpoint: -3.5 kW)
        Device1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: -70%)
        Protocol-->>Device1: Setpoint applied
    end
    
    MCA-->>Device1: on_confirm(contract ACTIVE, setpoint: -3.5 kW)
    MCA-->>Device2: on_confirm(contract ACTIVE, setpoint: -5.0 kW)
    MCA-->>Device3: on_confirm(contract ACTIVE, setpoint: -2.0 kW)
    Note right of Device1: orderAttributes:<br/>{setpointKW: -3.5,<br/>clearingPrice: 0.13}

    Note over GridOp,Protocol: Fulfillment Phase
    Note right of Protocol: Time window: 14:00-16:00
    Protocol->>Protocol: Devices reduce consumption<br/>at setpoints
    Protocol->>MCA: Telemetry (actual reduction)
    MCA->>MCA: Verify demand reduction: 50 kW
    MCA->>Device1: on_update(reduction verified: -3.5 kW)
    MCA->>Device2: on_update(reduction verified: -5.0 kW)
    MCA->>Device3: on_update(reduction verified: -2.0 kW)

    Note over GridOp,Protocol: Settlement Phase
    MCA->>MCA: Calculate final settlement
    Note right of MCA: Revenue flows:<br/>- Devices: ₹6.50 (50 kW × ₹0.13)<br/>- Grid operator: Payment
    MCA->>Device1: on_update(settlement: ₹0.455 for -3.5 kW)
    MCA->>Device2: on_update(settlement: ₹0.65 for -5.0 kW)
    MCA->>Device3: on_update(settlement: ₹0.26 for -2.0 kW)
    GridOp->>MCA: Payment (₹6.50 total)
    MCA-->>GridOp: on_update(payment received)
```

**Attribute Slots Used**:
- `itemAttributes.bidCurve`: Device price/power preferences for demand reduction
- `itemAttributes.objectives`: Grid operator objectives (target reduction, time window)
- `offerAttributes.clearingPrice`: Market-cleared price
- `offerAttributes.setpointKW`: Optimal demand reduction setpoint
- `orderAttributes.setpointKW`: Confirmed setpoint
- `orderAttributes.clearingPrice`: Locked clearing price

**Key Innovation**: Objective-driven coordination, devices autonomously respond to grid signals.

---

## 6. VPP Coordination

**Use Case**: Neighborhood VPP aggregates bid curves, market clears, economic disaggregation distributes setpoints

**Key Features**:
- Multi-resource aggregation
- Market clearing
- Economic disaggregation
- Protocol translation

```mermaid
sequenceDiagram
    participant VPPCoord as VPP Coordinator
    participant MCA as Market Clearing Agent (BPP)
    participant Solar1 as Solar Panel 1 (BAP)
    participant Solar2 as Solar Panel 2 (BAP)
    participant EV1 as EV Battery 1 (BAP)
    participant EV2 as EV Battery 2 (BAP)
    participant Battery1 as Home Battery 1 (BAP)
    participant Transformer as Neighborhood Transformer
    participant Protocol as IEEE 2030.5/OCPP

    Note over VPPCoord,Protocol: Resources Express Bid Curves
    Solar1->>MCA: discover(intent with bidCurve)
    Note right of Solar1: bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]
    Solar2->>MCA: discover(intent with bidCurve)
    EV1->>MCA: discover(intent with bidCurve)
    Note right of EV1: bidCurve:<br/>[{price: 0.08, powerKW: -11},<br/>{price: 0.10, powerKW: -5},<br/>{price: 0.12, powerKW: 0}]
    EV2->>MCA: discover(intent with bidCurve)
    Battery1->>MCA: discover(intent with bidCurve)
    Transformer->>MCA: Publish locational price adder
    Note right of Transformer: locationalPriceAdder:<br/>{basePrice: 0.10,<br/>currentLoadPercent: 75,<br/>priceAdderPerPercent: 0.001}

    Note over VPPCoord,Protocol: Market Clearing Agent Aggregates
    MCA->>MCA: Collect all bid curves
    Note right of MCA: 20 solar panels<br/>10 EV batteries<br/>5 home batteries<br/>1 transformer
    MCA->>MCA: aggregate(all bidCurves)
    Note right of MCA: Aggregate Supply:<br/>Price 0.06 → 40 kW<br/>Price 0.07 → 100 kW<br/><br/>Aggregate Demand:<br/>Price 0.08 → -110 kW<br/>Price 0.10 → -50 kW
    MCA->>MCA: Apply locational price adder
    MCA->>MCA: Find clearing price: ₹0.075/kWh
    MCA->>MCA: Economic disaggregation:<br/>Solar1: 3.5 kW<br/>Solar2: 3.5 kW<br/>EV1: -8.0 kW<br/>EV2: -8.0 kW<br/>Battery1: -2.0 kW

    Note over VPPCoord,Protocol: Market Clearing Agent Responds
    MCA-->>Solar1: on_discover(catalog with clearing price)
    MCA-->>Solar2: on_discover(catalog with clearing price)
    MCA-->>EV1: on_discover(catalog with clearing price)
    MCA-->>EV2: on_discover(catalog with clearing price)
    MCA-->>Battery1: on_discover(catalog with clearing price)
    Note right of MCA: offerAttributes:<br/>{clearingPrice: 0.075,<br/>locationalPrice: 0.175,<br/>setpointKW: varies}

    Note over VPPCoord,Protocol: Initialization Phase
    Solar1->>MCA: init(order)
    Solar2->>MCA: init(order)
    EV1->>MCA: init(order)
    EV2->>MCA: init(order)
    Battery1->>MCA: init(order)
    MCA-->>Solar1: on_init(terms)
    MCA-->>Solar2: on_init(terms)
    MCA-->>EV1: on_init(terms)
    MCA-->>EV2: on_init(terms)
    MCA-->>Battery1: on_init(terms)

    Note over VPPCoord,Protocol: Synchronous Confirmation (Market Clearing)
    Solar1->>MCA: confirm(order with accepted clearing price)
    Solar2->>MCA: confirm(order with accepted clearing price)
    EV1->>MCA: confirm(order with accepted clearing price)
    EV2->>MCA: confirm(order with accepted clearing price)
    Battery1->>MCA: confirm(order with accepted clearing price)
    Note right of MCA: Synchronous confirmation:<br/>Price locked at ₹0.075/kWh<br/>All resources confirm
    MCA->>MCA: Lock clearing price
    MCA->>MCA: Economic disaggregation:<br/>Distribute setpoints
    
    loop For each resource
        MCA->>Solar1: on_confirm(setpoint: 3.5 kW)
        Solar1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 70%)
        Protocol-->>Solar1: Setpoint applied
        
        MCA->>EV1: on_confirm(setpoint: -8.0 kW)
        EV1->>Protocol: OCPP: SetChargingProfile(8 kW)
        Protocol-->>EV1: Setpoint applied
    end
    
    MCA-->>Solar1: on_confirm(contract ACTIVE, setpoint: 3.5 kW)
    MCA-->>Solar2: on_confirm(contract ACTIVE, setpoint: 3.5 kW)
    MCA-->>EV1: on_confirm(contract ACTIVE, setpoint: -8.0 kW)
    MCA-->>EV2: on_confirm(contract ACTIVE, setpoint: -8.0 kW)
    MCA-->>Battery1: on_confirm(contract ACTIVE, setpoint: -2.0 kW)
    Note right of Solar1: orderAttributes:<br/>{setpointKW: 3.5,<br/>clearingPrice: 0.075,<br/>locationalPrice: 0.175}

    Note over VPPCoord,Protocol: Fulfillment Phase
    Protocol->>Protocol: Resources operate at setpoints
    Protocol->>MCA: Telemetry (actual power)
    MCA->>MCA: Verify VPP performance
    MCA->>Solar1: on_update(performance verified: 3.5 kW)
    MCA->>EV1: on_update(performance verified: -8.0 kW)

    Note over VPPCoord,Protocol: Settlement Phase
    MCA->>MCA: Calculate final settlement
    Note right of MCA: Revenue flows:<br/>- Solar panels: Generation revenue<br/>- EV batteries: Charging cost<br/>- Home batteries: Charging cost<br/>- Transformer: Locational adder revenue
    MCA->>Solar1: on_update(settlement: ₹0.2625 for 3.5 kW)
    MCA->>EV1: on_update(settlement: ₹1.40 for -8.0 kW)
    MCA-->>VPPCoord: on_update(VPP settlement complete)
```

**Attribute Slots Used**:
- `itemAttributes.bidCurve`: Resource price/power preferences
- `itemAttributes.locationalPriceAdder`: Transformer congestion pricing
- `offerAttributes.clearingPrice`: Market-cleared price
- `offerAttributes.locationalPrice`: Final price with locational adder
- `offerAttributes.setpointKW`: Optimal setpoint
- `orderAttributes.setpointKW`: Confirmed setpoint
- `orderAttributes.clearingPrice`: Locked clearing price
- `orderAttributes.locationalPrice`: Final price with locational adder

**Key Innovation**: VPP coordination emerges from individual resource bid curves, no central controller needed.

---

## 7. Grid Services

**Use Case**: Grid node signals congestion, resources respond with bid curves, market clears, setpoints distributed

**Key Features**:
- Grid nodes as resources
- Locational pricing
- Offset commands for flat plateaus

```mermaid
sequenceDiagram
    participant GridOp as Grid Operator
    participant Transformer as Transformer (Grid Node)
    participant MCA as Market Clearing Agent (BPP)
    participant Battery1 as Battery 1 (BAP)
    participant Battery2 as Battery 2 (BAP)
    participant Inverter1 as Inverter 1 (BAP)
    participant Protocol as IEEE 2030.5

    Note over GridOp,Protocol: Grid Node Signals Congestion
    GridOp->>Transformer: Update load status
    Transformer->>Transformer: Calculate congestion
    Note right of Transformer: currentLoadPercent: 85%<br/>locationalPriceAdder:<br/>{basePrice: 0.10,<br/>congestionMultiplier: 1.0,<br/>priceAdderPerPercent: 0.001}
    Transformer->>Transformer: Calculate current price: ₹0.185/kWh
    Transformer->>MCA: Publish catalogue with locational price adder
    Note right of Transformer: itemAttributes:<br/>{locationalPriceAdder: {...},<br/>gridConstraints: {<br/>maxReverseFlowKW: 50,<br/>currentLoadKW: 170}}

    Note over GridOp,Protocol: Resources Express Bid Curves
    Battery1->>MCA: discover(intent with bidCurve)
    Note right of Battery1: bidCurve:<br/>[{price: 0.12, powerKW: 0},<br/>{price: 0.15, powerKW: 7},<br/>{price: 0.18, powerKW: 10}]
    Battery2->>MCA: discover(intent with bidCurve)
    Inverter1->>MCA: discover(intent with bidCurve)
    Note right of Inverter1: bidCurve:<br/>[{price: 0.12, powerKW: 0},<br/>{price: 0.15, powerKW: 5},<br/>{price: 0.18, powerKW: 8}]

    Note over GridOp,Protocol: Market Clearing Agent Aggregates
    MCA->>MCA: Collect all bid curves
    MCA->>MCA: Apply locational price adder
    Note right of MCA: Base price: ₹0.10<br/>Locational adder: ₹0.085<br/>Final price: ₹0.185
    MCA->>MCA: aggregate(bidCurves with locational pricing)
    MCA->>MCA: Find clearing price: ₹0.17/kWh (with adder)
    MCA->>MCA: Economic disaggregation:<br/>Battery1: 8.5 kW<br/>Battery2: 8.5 kW<br/>Inverter1: 6.0 kW

    Note over GridOp,Protocol: Market Clearing Agent Responds
    MCA-->>Battery1: on_discover(catalog with clearing price)
    MCA-->>Battery2: on_discover(catalog with clearing price)
    MCA-->>Inverter1: on_discover(catalog with clearing price)
    Note right of MCA: offerAttributes:<br/>{clearingPrice: 0.085,<br/>locationalPrice: 0.17,<br/>setpointKW: varies}

    Note over GridOp,Protocol: Initialization Phase
    Battery1->>MCA: init(order)
    Battery2->>MCA: init(order)
    Inverter1->>MCA: init(order)
    MCA-->>Battery1: on_init(terms)
    MCA-->>Battery2: on_init(terms)
    MCA-->>Inverter1: on_init(terms)

    Note over GridOp,Protocol: Synchronous Confirmation (Market Clearing)
    Battery1->>MCA: confirm(order with accepted clearing price)
    Battery2->>MCA: confirm(order with accepted clearing price)
    Inverter1->>MCA: confirm(order with accepted clearing price)
    Note right of MCA: Synchronous confirmation:<br/>Price locked at ₹0.17/kWh<br/>All resources confirm
    MCA->>MCA: Lock clearing price
    MCA->>MCA: Economic disaggregation:<br/>Distribute setpoints
    
    Note over GridOp,Protocol: Check for Flat Plateau
    MCA->>Transformer: Check bid curve for flat plateau
    Transformer->>Transformer: Detect flat plateau at ₹0.15-0.18
    Transformer->>MCA: offsetCommand: {enabled: true, offsetKW: -2.0}
    Note right of Transformer: Command offset to<br/>break flat plateau
    
    MCA->>MCA: Apply offset command
    MCA->>Battery1: on_confirm(setpoint: 8.5 kW, offset: -2.0 kW)
    Battery1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 65%)
    Protocol-->>Battery1: Setpoint applied (6.5 kW after offset)
    
    MCA->>Battery2: on_confirm(setpoint: 8.5 kW, offset: -2.0 kW)
    Battery2->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 65%)
    Protocol-->>Battery2: Setpoint applied (6.5 kW after offset)
    
    MCA->>Inverter1: on_confirm(setpoint: 6.0 kW, offset: 0.0 kW)
    Inverter1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 75%)
    Protocol-->>Inverter1: Setpoint applied (6.0 kW)
    
    MCA-->>Battery1: on_confirm(contract ACTIVE, setpoint: 6.5 kW)
    MCA-->>Battery2: on_confirm(contract ACTIVE, setpoint: 6.5 kW)
    MCA-->>Inverter1: on_confirm(contract ACTIVE, setpoint: 6.0 kW)
    Note right of Battery1: orderAttributes:<br/>{setpointKW: 6.5,<br/>clearingPrice: 0.085,<br/>locationalPrice: 0.17,<br/>offsetCommand: {offsetKW: -2.0}}

    Note over GridOp,Protocol: Fulfillment Phase
    Protocol->>Protocol: Resources provide grid services<br/>at setpoints (with offset)
    Protocol->>Transformer: Monitor grid stability
    Transformer->>Transformer: Verify congestion reduction
    Transformer->>MCA: on_update(congestion reduced: 75% load)
    MCA->>Battery1: on_update(performance verified: 6.5 kW)
    MCA->>Battery2: on_update(performance verified: 6.5 kW)
    MCA->>Inverter1: on_update(performance verified: 6.0 kW)

    Note over GridOp,Protocol: Settlement Phase
    MCA->>MCA: Calculate final settlement
    Note right of MCA: Revenue flows:<br/>- Batteries: Grid services revenue<br/>- Inverter: Grid services revenue<br/>- Grid operator: Congestion management benefit
    MCA->>Battery1: on_update(settlement: ₹1.105 for 6.5 kW)
    MCA->>Battery2: on_update(settlement: ₹1.105 for 6.5 kW)
    MCA->>Inverter1: on_update(settlement: ₹1.02 for 6.0 kW)
    GridOp->>MCA: Payment (₹3.23 total)
    MCA-->>GridOp: on_update(payment received)
```

**Attribute Slots Used**:
- `itemAttributes.locationalPriceAdder`: Transformer congestion pricing
- `itemAttributes.gridConstraints`: Grid node constraints (reverse flow limits)
- `itemAttributes.bidCurve`: Resource price/power preferences
- `offerAttributes.clearingPrice`: Market-cleared base price
- `offerAttributes.locationalPrice`: Final price with locational adder
- `orderAttributes.setpointKW`: Confirmed setpoint
- `orderAttributes.offsetCommand`: Grid operator offset command
- `fulfillmentAttributes.offsetCommand`: Applied offset during fulfillment

**Key Innovation**: Grid nodes participate as resources, can command offsets for flat plateaus.

---

## Summary

All use cases leverage the same building blocks:
- ✅ **Bid curves**: Price/power preferences
- ✅ **Bid curve aggregation**: `aggregate` action
- ✅ **Market clearing**: Contract-based pattern with synchronous confirmation
- ✅ **Economic disaggregation**: Part of `aggregate` response
- ✅ **Locational pricing**: Grid nodes as resources
- ✅ **Settlement**: Multi-party revenue flows

**Key Pattern**: Market clearing emerges from contracts, prices discovered at confirmation time, not at offer time.

---

**Status**: Complete  
**Next Action**: Document protocol integration patterns (04_Protocol_Integration_Patterns.md)

