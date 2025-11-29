# Example Messages
## Complete Message Flows for Energy Coordination Use Cases

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This directory contains complete JSON message examples for energy coordination use cases, demonstrating how the proposed building block extensions work in practice.

---

## Directory Structure

```
examples/
├── README.md
├── ev_charging_demand_flexibility/
│   ├── discover-with-bid-curve.json
│   ├── on_discover-with-clearing-price.json
│   ├── select-with-clearing-price.json
│   ├── confirm-with-setpoint.json
│   └── on_confirm-with-setpoint.json
├── p2p_trading_market_based/
│   ├── discover-solar-resource-with-objectives.json
│   ├── discover-battery-resource-with-objectives.json
│   ├── discover-multiple-prosumers.json
│   ├── on_discover-aggregated.json
│   ├── aggregate-request.json
│   ├── on_aggregate-result.json
│   ├── order-with-settlement.json
│   └── confirm-with-setpoints.json
├── demand_flexibility/
│   ├── discover-with-objectives.json
│   ├── on_discover-with-clearing.json
│   └── confirm-with-setpoints.json
├── vpp_coordination/
│   ├── aggregate-neighborhood.json
│   ├── on_aggregate-vpp-result.json
│   └── confirm-distributed-setpoints.json
└── grid_services/
    ├── grid-node-catalogue.json
    ├── discover-with-locational-pricing.json
    └── confirm-with-offset-command.json
```

---

## Use Cases

### 1. EV Charging (Demand Flexibility)
- Bid curve expression
- Market clearing at confirmation
- Dynamic setpoint assignment

### 2. P2P Trading (Market-Based)
- Resource objectives in itemAttributes (solar generation, battery charging)
- Multiple prosumer bid curves
- Market aggregation
- Economic disaggregation
- Multi-party settlement

### 3. Demand Flexibility
- Objective-driven coordination
- Grid operator signals
- Device bid curves

### 4. VPP Coordination
- Multi-resource aggregation
- Neighborhood market clearing
- Setpoint distribution

### 5. Grid Services
- Grid nodes as resources
- Locational pricing
- Offset commands

---

---

## EnergyObjectives Usage

`EnergyObjectives` can be used in three contexts:

1. **`itemAttributes.objectives`** (EnergyResource) - Resource expresses its own goals
   - See: `p2p_trading_market_based/discover-solar-resource-with-objectives.json`
   - See: `p2p_trading_market_based/discover-battery-resource-with-objectives.json`

2. **`intent.objectives`** (EnergyIntent) - Consumer expresses demand goals
   - See: `ev_charging_demand_flexibility/discover-with-bid-curve.json`

3. **`orderAttributes.objectives`** (EnergyTradeContract) - Locked-in objectives in contract
   - See: `ev_charging_demand_flexibility/confirm-with-setpoint.json`
   - See: `ev_charging_demand_flexibility/on_confirm-with-setpoint.json`

For detailed usage guide, see: `outputs/09_EnergyObjectives_Usage_Guide.md`

---

**Status**: Complete

