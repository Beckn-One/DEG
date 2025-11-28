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

**Use Case**: Market clearing agent coordinates multiple participants (CPO representing EV charging demand, solar prosumers representing supply) with utility load approval, clears market at confirmation time

**Key Features**:
- Simple discover (returns clearing agent ID + "PAY_AS_CLEAR")
- Bid curves submitted during init
- Utility load approval via cascaded init
- Market clearing at confirmation (synchronous)
- Virtual meter balancing (net = 0, deviation penalties)

**Note**: This diagram focuses on market clearing coordination. The peer-to-peer trade between EV user and CPO is a separate flow not shown here.

```mermaid
sequenceDiagram
    participant CPO as CPO Platform (BPP)<br/>(Represents EV Charging Demand)
    participant MCA as Market Clearing Agent (BPP)<br/>(Virtual Meter: Net = 0)
    participant Utility as Utility BPP
    participant Solar as Solar Prosumer (BPP)

    Note over CPO,Solar: Discovery Phase (Simple)
    CPO->>MCA: discover(location, timeWindow)
    Note right of CPO: Simple discover:<br/>No bid curve yet
    MCA-->>CPO: on_discover(catalog: clearing agent)
    Note right of MCA: offerAttributes:<br/>{pricingModel: "PAY_AS_CLEAR",<br/>clearingAgentId: "mca-001"}
    
    Solar->>MCA: discover(location, timeWindow)
    MCA-->>Solar: on_discover(catalog: clearing agent)

    Note over CPO,Solar: Initialization Phase (Bid Curve Submission)
    CPO->>CPO: Construct bid curve from EV objectives
    Note right of CPO: bidCurve:<br/>[{price: 0.08, powerKW: -11},<br/>{price: 0.10, powerKW: -5},<br/>{price: 0.12, powerKW: 0}]
    CPO->>MCA: init(order with bidCurve, meterId, objectives)
    Note right of CPO: orderAttributes:<br/>{bidCurve: [...],<br/>objectives: {targetChargeKWh: 20,<br/>deadline: "18:00",<br/>maxPrice: 0.12},<br/>meterId: "98765456"}

    Note over CPO,Solar: Utility Load Approval (Cascaded)
    MCA->>Utility: cascaded init(verify meter,<br/>calculate approved max trade volume)
    Note right of Utility: Check sanctioned load<br/>for meter 98765456
    Utility->>Utility: Verify sanctioned load: 50 kW<br/>Calculate available capacity: 30 kW
    Utility-->>MCA: cascaded_on_init(approvedMaxTradeKW: 30,<br/>wheelingCharges: ₹1/kWh)
    Note right of Utility: Approved max trade:<br/>30 kW (relative to<br/>sanctioned load)

    Note over CPO,Solar: Clearing Agent Confirms Init
    MCA->>MCA: Store bid curve & approved limits
    MCA-->>CPO: on_init(terms confirmed,<br/>approvedMaxTradeKW: 30,<br/>clearingFees: ₹0.5/kWh)
    Note right of MCA: Bid curve stored<br/>Approved limits confirmed<br/>Ready for market clearing

    Note over CPO,Solar: Solar Prosumer Submits Bid
    Solar->>Solar: Construct bid curve from generation forecast
    Note right of Solar: bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]
    Solar->>MCA: init(order with bidCurve, meterId)
    MCA->>Utility: cascaded init(verify solar meter)
    Utility->>Utility: Verify sanctioned load: 10 kW<br/>Calculate available capacity: 5 kW
    Utility-->>MCA: cascaded_on_init(approvedMaxTradeKW: 5)
    MCA-->>Solar: on_init(terms confirmed,<br/>approvedMaxTradeKW: 5)

    Note over CPO,Solar: Confirmation Phase (Bid Commitment)
    CPO->>MCA: confirm(order, bid commitment)
    Note right of CPO: Commits to bid curve<br/>Accepts PAY_AS_CLEAR pricing
    Solar->>MCA: confirm(order, bid commitment)
    Note right of Solar: Commits to bid curve
    Note right of MCA: All participants have<br/>committed their bids

    Note over CPO,Solar: Market Clearing (After Confirmation)
    MCA->>MCA: Collect all confirmed bids
    Note right of MCA: Aggregate all bid curves:<br/>- CPO (EV demand): [-11, -5, 0] kW @ [0.08, 0.10, 0.12]<br/>- Solar (supply): [0, 2, 5] kW @ [0.05, 0.06, 0.07]<br/>- Other participants...
    MCA->>MCA: aggregate(all bidCurves)
    MCA->>MCA: Find clearing price: ₹0.075/kWh
    MCA->>MCA: Economic disaggregation:<br/>CPO setpoint: -8.0 kW<br/>Solar setpoint: 3.5 kW
    MCA->>MCA: Verify virtual meter balance:<br/>Net = -8.0 + 3.5 + ... = 0 ✓
    Note right of MCA: Virtual meter constraint:<br/>Net power flow = 0<br/>(any imbalance = deviation penalty)

    Note over CPO,Solar: Lock Trade & Deduct Sanctioned Load
    MCA->>Utility: cascaded confirm(lock trade,<br/>deduct from sanctioned load)
    Note right of MCA: Trade details:<br/>- CPO meter 98765456: -8.0 kW<br/>- Solar meter 100200300: +3.5 kW<br/>- Clearing price: ₹0.075/kWh
    Utility->>Utility: Deduct from sanctioned load:<br/>- Meter 98765456: 30 kW → 22 kW remaining<br/>- Meter 100200300: 5 kW → 1.5 kW remaining
    Note right of Utility: Prevents double dipping:<br/>Same sanctioned load capacity<br/>cannot be used for multiple trades
    Utility-->>MCA: cascaded_on_confirm(trade locked,<br/>sanctioned load deducted)
    Note right of Utility: Remaining capacity:<br/>- Meter 98765456: 22 kW<br/>- Meter 100200300: 1.5 kW

    Note over CPO,Solar: Clearing Agent Sends on_confirm (After Clearing)
    MCA-->>CPO: on_confirm(order confirmed,<br/>clearingPrice: ₹0.075/kWh,<br/>setpointKW: -8.0)
    Note right of CPO: orderAttributes:<br/>{setpointKW: -8.0,<br/>clearingPrice: 0.075,<br/>locationalPrice: 0.075}
    MCA-->>Solar: on_confirm(order confirmed,<br/>clearingPrice: ₹0.075/kWh,<br/>setpointKW: 3.5)
    Note right of Solar: orderAttributes:<br/>{setpointKW: 3.5,<br/>clearingPrice: 0.075}

    Note over CPO,Solar: Settlement & Deviation Penalty
    CPO->>CPO: Calculate actual delivery: 20 kWh
    CPO->>Utility: Report actual trade
    Solar->>Utility: Report actual trade: 3.5 kWh
    Utility->>Utility: Calculate net imbalance:<br/>Promised: -8.0 + 3.5 = -4.5 kW<br/>Actual: -8.0 + 3.5 = -4.5 kW<br/>Deviation: 0 kW ✓
    Utility->>MCA: on_update(settlement: 20 kWh,<br/>deviationPenalty: ₹0)
    MCA->>MCA: Calculate revenue flows:<br/>- CPO pays: 20 × ₹0.075 = ₹1.50<br/>- Solar receives: 3.5 × ₹0.075 = ₹0.2625<br/>- Clearing fee: ₹0.5/kWh
    MCA->>CPO: on_update(settlement complete,<br/>finalCost: ₹1.50)
    MCA->>Solar: on_update(settlement complete,<br/>revenue: ₹0.2625)
```

**Attribute Slots Used**:
- `offerAttributes.pricingModel`: "PAY_AS_CLEAR" pricing model
- `orderAttributes.bidCurve`: Bid curve submitted during init
- `orderAttributes.objectives`: Charging goals and constraints (for CPO)
- `orderAttributes.approvedMaxTradeKW`: Utility-approved trade limit
- `orderAttributes.clearingPrice`: Market-cleared price (from on_confirm)
- `orderAttributes.setpointKW`: Confirmed setpoint (from on_confirm)
- `fulfillmentAttributes.deviationPenalty`: Penalty for net imbalance

**Key Innovation**: 
- Market clearing agent is a special peer with virtual meter (net = 0)
- Simple discover returns clearing agent ID and pricing model
- Bid curves submitted during init (not discover)
- Utility load approval via cascaded init
- Prices discovered at confirmation time (synchronous market clearing)
- Trade locking and sanctioned load deduction prevents double dipping
- Deviation penalties incentivize balancing
- Focus on coordination pattern, not end-to-end user flow

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

    Note over Consumer,Meter2: Discovery Phase (Simple)
    Consumer->>BAP: Buy 50 kWh, max ₹6/kWh
    BAP->>MCA: discover(intent: 50 kWh, maxPrice: 0.06)
    Note right of BAP: Simple discover:<br/>No bid curve yet
    MCA-->>BAP: on_discover(catalog: clearing agent)
    Note right of MCA: offerAttributes:<br/>{pricingModel: "PAY_AS_CLEAR",<br/>clearingAgentId: "mca-001"}

    Note over Consumer,Meter2: Initialization Phase (Bid Curve Submission)
    Consumer->>BAP: Confirm participation
    BAP->>BAP: Construct bid curve from intent
    Note right of BAP: bidCurve:<br/>[{price: 0.06, powerKW: -50},<br/>{price: 0.07, powerKW: 0}]
    BAP->>MCA: init(order with bidCurve, meterId: 98765456)
    
    Prosumer1->>MCA: init(order with bidCurve, meterId: 100200300)
    Note right of Prosumer1: bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]
    Prosumer2->>MCA: init(order with bidCurve, meterId: 100200301)
    Note right of Prosumer2: bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]

    Note over Consumer,Meter2: Utility Load Approval (Cascaded)
    MCA->>Utility: cascaded init(verify meters,<br/>calculate approved max trade volumes)
    Utility->>Utility: Verify sanctioned loads<br/>for all meters
    Utility-->>MCA: cascaded_on_init(approvedMaxTradeKW per meter,<br/>wheeling: ₹1/kWh)
    MCA-->>BAP: on_init(terms confirmed,<br/>approvedMaxTradeKW, wheeling)
    MCA-->>Prosumer1: on_init(terms confirmed,<br/>approvedMaxTradeKW)
    MCA-->>Prosumer2: on_init(terms confirmed,<br/>approvedMaxTradeKW)
    BAP-->>Consumer: Terms confirmed (PAY_AS_CLEAR)

    Note over Consumer,Meter2: Confirmation Phase (Bid Commitment)
    Consumer->>BAP: Confirm bid participation
    BAP->>MCA: confirm(order, bid commitment)
    Note right of BAP: Commits to bid curve<br/>Accepts PAY_AS_CLEAR pricing
    Prosumer1->>MCA: confirm(order, bid commitment)
    Prosumer2->>MCA: confirm(order, bid commitment)
    Note right of MCA: All participants have<br/>committed their bids

    Note over Consumer,Meter2: Market Clearing (After Confirmation)
    MCA->>MCA: Collect all confirmed bids
    Note right of MCA: Aggregate all bid curves:<br/>- Consumer: [-50, 0] kW @ [0.06, 0.07]<br/>- Prosumer1: [0, 2, 5] kW @ [0.05, 0.06, 0.07]<br/>- Prosumer2: [0, 2, 5] kW @ [0.05, 0.06, 0.07]<br/>- Other prosumers...
    MCA->>MCA: aggregate(all bidCurves)
    MCA->>MCA: Find clearing price: ₹0.0625/kWh
    MCA->>MCA: Economic disaggregation:<br/>Prosumer1: 5 kWh<br/>Prosumer2: 5 kWh<br/>... (10 prosumers, ~5 kWh each)

    Note over Consumer,Meter2: Lock Trade & Deduct Sanctioned Load
    MCA->>Utility: cascaded confirm(lock trades,<br/>deduct from sanctioned loads)
    Note right of MCA: Trade details for all meters:<br/>- Consumer meter: -50 kW<br/>- Prosumer meters: +5 kW each
    Utility->>Utility: Deduct from sanctioned loads<br/>for all meters
    Note right of Utility: Prevents double dipping:<br/>Same sanctioned load capacity<br/>cannot be used for multiple trades
    Utility-->>MCA: cascaded_on_confirm(trades locked,<br/>sanctioned loads deducted)

    Note over Consumer,Meter2: Clearing Agent Sends on_confirm (After Clearing)
    MCA-->>BAP: on_confirm(order confirmed,<br/>clearingPrice: ₹0.0625/kWh,<br/>aggregateQuantity: 50 kWh)
    Note right of BAP: orderAttributes:<br/>{clearingPrice: 0.0625,<br/>setpoints: [{era: "prosumer1", quantity: 5}, ...]}
    MCA-->>Prosumer1: on_confirm(order confirmed,<br/>clearingPrice: ₹0.0625/kWh,<br/>setpointKW: 5.0)
    MCA-->>Prosumer2: on_confirm(order confirmed,<br/>clearingPrice: ₹0.0625/kWh,<br/>setpointKW: 5.0)
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

    Note over GridOp,Protocol: Discovery Phase (Simple)
    Device1->>MCA: discover(location, timeWindow)
    Device2->>MCA: discover(location, timeWindow)
    Device3->>MCA: discover(location, timeWindow)
    Note right of Device1: Simple discover:<br/>No bid curve yet
    MCA-->>Device1: on_discover(catalog: clearing agent)
    MCA-->>Device2: on_discover(catalog: clearing agent)
    MCA-->>Device3: on_discover(catalog: clearing agent)
    Note right of MCA: offerAttributes:<br/>{pricingModel: "PAY_AS_CLEAR",<br/>clearingAgentId: "mca-001"}

    Note over GridOp,Protocol: Initialization Phase (Bid Curve Submission)
    Device1->>Device1: Construct bid curve from objectives
    Note right of Device1: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -2},<br/>{price: 0.15, powerKW: -5}]
    Device1->>MCA: init(order with bidCurve, meterId, objectives)
    Device2->>Device2: Construct bid curve
    Note right of Device2: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -3},<br/>{price: 0.15, powerKW: -7}]
    Device2->>MCA: init(order with bidCurve, meterId, objectives)
    Device3->>Device3: Construct bid curve
    Note right of Device3: bidCurve:<br/>[{price: 0.10, powerKW: 0},<br/>{price: 0.12, powerKW: -1},<br/>{price: 0.15, powerKW: -3}]
    Device3->>MCA: init(order with bidCurve, meterId, objectives)
    MCA-->>Device1: on_init(terms confirmed)
    MCA-->>Device2: on_init(terms confirmed)
    MCA-->>Device3: on_init(terms confirmed)

    Note over GridOp,Protocol: Confirmation Phase (Bid Commitment)
    Device1->>MCA: confirm(order, bid commitment)
    Device2->>MCA: confirm(order, bid commitment)
    Device3->>MCA: confirm(order, bid commitment)
    Note right of MCA: All devices have<br/>committed their bids

    Note over GridOp,Protocol: Market Clearing (After Confirmation)
    MCA->>MCA: Collect all confirmed bids (20 devices)
    MCA->>MCA: aggregate(all bidCurves)
    Note right of MCA: Aggregate Demand Reduction:<br/>Price 0.12 → -6 kW<br/>Price 0.15 → -15 kW<br/>(from 3 devices shown)
    MCA->>MCA: Find clearing price: ₹0.13/kWh
    MCA->>MCA: Economic disaggregation:<br/>Device1: -3.5 kW<br/>Device2: -5.0 kW<br/>Device3: -2.0 kW<br/>... (total: 50 kW)

    Note over GridOp,Protocol: Clearing Agent Sends on_confirm (After Clearing)
    MCA-->>Device1: on_confirm(order confirmed,<br/>clearingPrice: ₹0.13/kWh,<br/>setpointKW: -3.5)
    MCA-->>Device2: on_confirm(order confirmed,<br/>clearingPrice: ₹0.13/kWh,<br/>setpointKW: -5.0)
    MCA-->>Device3: on_confirm(order confirmed,<br/>clearingPrice: ₹0.13/kWh,<br/>setpointKW: -2.0)
    Note right of Device1: orderAttributes:<br/>{setpointKW: -3.5,<br/>clearingPrice: 0.13}
    
    Device1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: -70%)
    Device2->>Protocol: IEEE 2030.5: DERControl(opModFixedW: -83%)
    Device3->>Protocol: IEEE 2030.5: DERControl(opModFixedW: -50%)
    Protocol-->>Device1: Setpoint applied
    Protocol-->>Device2: Setpoint applied
    Protocol-->>Device3: Setpoint applied

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
    participant MCA as Market Clearing Agent (BPP)
    participant Solar as Solar Resources (BAP)<br/>(Multiple panels)
    participant EV as EV Batteries (BAP)<br/>(Multiple vehicles)
    participant Battery as Home Batteries (BAP)<br/>(Multiple batteries)
    participant Transformer as Grid Node (BPP)<br/>(Neighborhood Transformer)
    participant Utility as Utility BPP

    Note over MCA,Utility: Discovery Phase (Simple)
    Solar->>MCA: discover(location, timeWindow)
    EV->>MCA: discover(location, timeWindow)
    Battery->>MCA: discover(location, timeWindow)
    Note right of Solar: Simple discover:<br/>No bid curve yet
    Transformer->>MCA: Publish locational price adder
    Note right of Transformer: locationalPriceAdder:<br/>{basePrice: 0.10,<br/>currentLoadPercent: 75,<br/>priceAdderPerPercent: 0.001}
    MCA-->>Solar: on_discover(catalog: clearing agent)
    MCA-->>EV: on_discover(catalog: clearing agent)
    MCA-->>Battery: on_discover(catalog: clearing agent)
    Note right of MCA: offerAttributes:<br/>{pricingModel: "PAY_AS_CLEAR",<br/>clearingAgentId: "mca-001"}

    Note over MCA,Utility: Initialization Phase (Bid Curve Submission)
    Solar->>Solar: Construct bid curve from generation forecast
    Note right of Solar: bidCurve:<br/>[{price: 0.05, powerKW: 0},<br/>{price: 0.06, powerKW: 2},<br/>{price: 0.07, powerKW: 5}]
    Solar->>MCA: init(order with bidCurve, meterIds)
    EV->>EV: Construct bid curve from charging objectives
    Note right of EV: bidCurve:<br/>[{price: 0.08, powerKW: -11},<br/>{price: 0.10, powerKW: -5},<br/>{price: 0.12, powerKW: 0}]
    EV->>MCA: init(order with bidCurve, meterIds)
    Battery->>Battery: Construct bid curve
    Battery->>MCA: init(order with bidCurve, meterIds)
    MCA->>Utility: cascaded init(verify meters,<br/>calculate approved max trade volumes)
    Utility->>Utility: Verify sanctioned loads<br/>for all meters
    Utility-->>MCA: cascaded_on_init(approvedMaxTradeKW per meter)
    MCA-->>Solar: on_init(terms confirmed,<br/>approvedMaxTradeKW per meter)
    MCA-->>EV: on_init(terms confirmed,<br/>approvedMaxTradeKW per meter)
    MCA-->>Battery: on_init(terms confirmed,<br/>approvedMaxTradeKW per meter)

    Note over MCA,Utility: Confirmation Phase (Bid Commitment)
    Solar->>MCA: confirm(order, bid commitment)
    EV->>MCA: confirm(order, bid commitment)
    Battery->>MCA: confirm(order, bid commitment)
    Note right of MCA: All resources have<br/>committed their bids

    Note over MCA,Utility: Market Clearing (After Confirmation)
    MCA->>MCA: Collect all confirmed bids
    Note right of MCA: 20 solar panels<br/>10 EV batteries<br/>5 home batteries<br/>1 transformer
    MCA->>MCA: aggregate(all bidCurves)
    Note right of MCA: Aggregate Supply:<br/>Price 0.06 → 40 kW<br/>Price 0.07 → 100 kW<br/><br/>Aggregate Demand:<br/>Price 0.08 → -110 kW<br/>Price 0.10 → -50 kW
    MCA->>MCA: Apply locational price adder
    MCA->>MCA: Find clearing price: ₹0.075/kWh
    MCA->>MCA: Economic disaggregation:<br/>Solar: 3.5 kW each (avg)<br/>EV: -8.0 kW each (avg)<br/>Battery: -2.0 kW each (avg)

    Note over MCA,Utility: Lock Trade & Deduct Sanctioned Load
    MCA->>Utility: cascaded confirm(lock trades,<br/>deduct from sanctioned loads)
    Note right of MCA: Trade details for all meters:<br/>- Solar meters: +3.5 kW each<br/>- EV meters: -8.0 kW each<br/>- Battery meters: -2.0 kW each
    Utility->>Utility: Deduct from sanctioned loads<br/>for all meters
    Note right of Utility: Prevents double dipping:<br/>Same sanctioned load capacity<br/>cannot be used for multiple trades
    Utility-->>MCA: cascaded_on_confirm(trades locked,<br/>sanctioned loads deducted)

    Note over MCA,Utility: Clearing Agent Sends on_confirm (After Clearing)
    MCA-->>Solar: on_confirm(order confirmed,<br/>clearingPrice: ₹0.075/kWh,<br/>setpointKW: 3.5 per panel)
    MCA-->>EV: on_confirm(order confirmed,<br/>clearingPrice: ₹0.075/kWh,<br/>setpointKW: -8.0 per vehicle)
    MCA-->>Battery: on_confirm(order confirmed,<br/>clearingPrice: ₹0.075/kWh,<br/>setpointKW: -2.0 per battery)
    Note right of Solar: orderAttributes:<br/>{setpointKW: 3.5,<br/>clearingPrice: 0.075,<br/>locationalPrice: 0.175}

    Note over MCA,Utility: Fulfillment Phase
    Note right of Solar: Resources operate at setpoints<br/>(IEEE 2030.5/OCPP)
    Solar->>MCA: Telemetry (actual power)
    EV->>MCA: Telemetry (actual power)
    Battery->>MCA: Telemetry (actual power)
    MCA->>MCA: Verify VPP performance
    MCA->>Solar: on_update(performance verified)
    MCA->>EV: on_update(performance verified)
    MCA->>Battery: on_update(performance verified)

    Note over MCA,Utility: Settlement Phase
    MCA->>MCA: Calculate final settlement
    Note right of MCA: Revenue flows:<br/>- Solar panels: Generation revenue<br/>- EV batteries: Charging cost<br/>- Home batteries: Charging cost<br/>- Transformer: Locational adder revenue
    MCA->>Solar: on_update(settlement complete)
    MCA->>EV: on_update(settlement complete)
    MCA->>Battery: on_update(settlement complete)
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

    Note over GridOp,Protocol: Discovery Phase (Simple)
    Battery1->>MCA: discover(location, timeWindow)
    Battery2->>MCA: discover(location, timeWindow)
    Inverter1->>MCA: discover(location, timeWindow)
    Note right of Battery1: Simple discover:<br/>No bid curve yet
    MCA-->>Battery1: on_discover(catalog: clearing agent)
    MCA-->>Battery2: on_discover(catalog: clearing agent)
    MCA-->>Inverter1: on_discover(catalog: clearing agent)
    Note right of MCA: offerAttributes:<br/>{pricingModel: "PAY_AS_CLEAR",<br/>clearingAgentId: "mca-001"}

    Note over GridOp,Protocol: Initialization Phase (Bid Curve Submission)
    Battery1->>Battery1: Construct bid curve
    Note right of Battery1: bidCurve:<br/>[{price: 0.12, powerKW: 0},<br/>{price: 0.15, powerKW: 7},<br/>{price: 0.18, powerKW: 10}]
    Battery1->>MCA: init(order with bidCurve, meterId)
    Battery2->>Battery2: Construct bid curve
    Battery2->>MCA: init(order with bidCurve, meterId)
    Inverter1->>Inverter1: Construct bid curve
    Note right of Inverter1: bidCurve:<br/>[{price: 0.12, powerKW: 0},<br/>{price: 0.15, powerKW: 5},<br/>{price: 0.18, powerKW: 8}]
    Inverter1->>MCA: init(order with bidCurve, meterId)
    MCA-->>Battery1: on_init(terms confirmed)
    MCA-->>Battery2: on_init(terms confirmed)
    MCA-->>Inverter1: on_init(terms confirmed)

    Note over GridOp,Protocol: Confirmation Phase (Bid Commitment)
    Battery1->>MCA: confirm(order, bid commitment)
    Battery2->>MCA: confirm(order, bid commitment)
    Inverter1->>MCA: confirm(order, bid commitment)
    Note right of MCA: All resources have<br/>committed their bids

    Note over GridOp,Protocol: Market Clearing (After Confirmation)
    MCA->>MCA: Collect all confirmed bids
    MCA->>MCA: Apply locational price adder
    Note right of MCA: Base price: ₹0.10<br/>Locational adder: ₹0.085<br/>Final price: ₹0.185
    MCA->>MCA: aggregate(bidCurves with locational pricing)
    MCA->>MCA: Find clearing price: ₹0.17/kWh (with adder)
    MCA->>MCA: Economic disaggregation:<br/>Battery1: 8.5 kW<br/>Battery2: 8.5 kW<br/>Inverter1: 6.0 kW
    
    Note over GridOp,Protocol: Check for Flat Plateau
    MCA->>Transformer: Check bid curve for flat plateau
    Transformer->>Transformer: Detect flat plateau at ₹0.15-0.18
    Transformer->>MCA: offsetCommand: {enabled: true, offsetKW: -2.0}
    Note right of Transformer: Command offset to<br/>break flat plateau
    MCA->>MCA: Apply offset command

    Note over GridOp,Protocol: Clearing Agent Sends on_confirm (After Clearing)
    MCA-->>Battery1: on_confirm(order confirmed,<br/>clearingPrice: ₹0.085/kWh,<br/>locationalPrice: ₹0.17/kWh,<br/>setpointKW: 8.5, offsetKW: -2.0)
    MCA-->>Battery2: on_confirm(order confirmed,<br/>clearingPrice: ₹0.085/kWh,<br/>locationalPrice: ₹0.17/kWh,<br/>setpointKW: 8.5, offsetKW: -2.0)
    MCA-->>Inverter1: on_confirm(order confirmed,<br/>clearingPrice: ₹0.085/kWh,<br/>locationalPrice: ₹0.17/kWh,<br/>setpointKW: 6.0, offsetKW: 0.0)
    Note right of Battery1: orderAttributes:<br/>{setpointKW: 6.5,<br/>clearingPrice: 0.085,<br/>locationalPrice: 0.17,<br/>offsetCommand: {offsetKW: -2.0}}
    
    Battery1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 65%)
    Battery2->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 65%)
    Inverter1->>Protocol: IEEE 2030.5: DERControl(opModFixedW: 75%)
    Protocol-->>Battery1: Setpoint applied (6.5 kW after offset)
    Protocol-->>Battery2: Setpoint applied (6.5 kW after offset)
    Protocol-->>Inverter1: Setpoint applied (6.0 kW)

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

