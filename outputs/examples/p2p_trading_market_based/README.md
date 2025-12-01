# P2P Trading Market-Based Examples - EnergyContractP2PTrade Pattern

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This directory contains complete JSON message examples for **market-based P2P energy trading** use cases using the `EnergyContractP2PTrade` pattern with `MARKET_CLEARING_AGENT` and `PROSUMER` roles. These examples demonstrate pay-as-clear pricing where prices are discovered at confirmation time after market clearing.

---

## Directory Structure

```
p2p_trading_market_based/
├── README.md
├── 01_discover/
│   └── discover-market-based-trading.json
├── 02_on_discover/
│   └── on-discover-market-clearing-agent.json
├── 03_init/
│   ├── init-consumer-with-offer-curve.json
│   └── init-solar-prosumer-with-offer-curve.json
├── 04_on_init/
│   └── on-init-consumer-confirmed.json
├── 05_cascaded_init/
│   └── cascaded-init-utility-approval.json
├── 06_cascaded_on_init/
│   └── cascaded-on-init-utility-approval.json
├── 07_confirm/
│   └── confirm-consumer-bid-commitment.json
├── 08_on_confirm/
│   ├── on-confirm-with-clearing-price.json
│   └── on-confirm-prosumer-with-clearing-price.json
├── 09_status/
│   └── status-market-trade.json
└── 10_on_status/
    └── on-status-market-trade-in-progress.json
```

---

## Key Features

### 1. Market-Based Mode

All examples use `EnergyContractP2PTrade` in **market-based mode** with:

- **MARKET_CLEARING_AGENT role**: Coordinates market clearing, provides `marketMakingFee`, `clearingPrice`, `clearedPower`
- **PROSUMER role**: Provides `offerCurve` expressing price/power preferences
- **Pay-as-clear pricing**: Prices discovered at confirmation time after market clearing
- **Status transitions**: `PENDING` (in init) → `ACTIVE` (in on_confirm after clearing)

### 2. Offer Curves

PROSUMERs express preferences via offer curves:

```json
{
  "offerCurve": {
    "currency": "INR",
    "minExport": -50,  // Negative = max withdrawal (buyer)
    "maxExport": 5,    // Positive = max export (seller)
    "curve": [
      { "price": 0.06, "powerKW": -50 },  // Willing to buy 50 kW at ₹0.06/kWh
      { "price": 0.07, "powerKW": 0 }     // No trade at ₹0.07/kWh
    ]
  }
}
```

**Sign Convention**:
- **Positive power**: Providing energy (seller/generator)
- **Negative power**: Receiving energy (buyer/consumer)

### 3. Market Clearing Flow

1. **Discovery**: Simple `discover` → MCA responds with `pricingModel: "PAY_AS_CLEAR"`
2. **Init**: PROSUMERs submit `init` with `offerCurve` in roleInputs
3. **Cascaded Init**: MCA cascades to Utility for load approval
4. **Confirm**: PROSUMERs commit to offer curves via `confirm`
5. **Market Clearing**: MCA aggregates all offer curves, finds clearing price
6. **on_confirm**: MCA sends `clearingPrice` and `clearedPower` per PROSUMER

### 4. Revenue Flows

**PROSUMER → MARKET_CLEARING_AGENT**:
```json
{
  "from": "PROSUMER",
  "to": "MARKET_CLEARING_AGENT",
  "formula": "(roles.MARKET_CLEARING_AGENT.roleInputs.clearingPrice + roles.MARKET_CLEARING_AGENT.roleInputs.marketMakingFee) × roles.MARKET_CLEARING_AGENT.roleInputs.clearedPower[PROSUMER.era]"
}
```

- **Positive clearedPower** (seller): PROSUMER receives payment
- **Negative clearedPower** (buyer): PROSUMER pays

**MARKET_CLEARING_AGENT → GRID_OPERATOR** (if GRID_OPERATOR role present):
```json
{
  "from": "MARKET_CLEARING_AGENT",
  "to": "GRID_OPERATOR",
  "formula": "abs(roles.MARKET_CLEARING_AGENT.roleInputs.clearedPower[PROSUMER.era]) × roles.GRID_OPERATOR.roleInputs.wheelingCharges"
}
```

---

## Example Flow

### Discovery & Init
1. **discover** - Consumer searches for market-based trading
2. **on_discover** - MCA responds with `EnergyOffer` containing `EnergyContractP2PTrade` (MARKET_CLEARING_AGENT role filled, PROSUMER role open)
3. **init** - Consumer submits offer curve (negative power = buyer)
4. **init** - Solar prosumer submits offer curve (positive power = seller)
5. **on_init** - MCA confirms offer curves received
6. **cascaded_init** - MCA requests utility approval for all meters
7. **cascaded_on_init** - Utility provides trade capacity and wheeling charges

### Confirm & Market Clearing
8. **confirm** - Consumer commits to offer curve
9. **Market Clearing** - MCA aggregates all offer curves, finds clearing price (₹0.0625/kWh)
10. **on_confirm** - MCA sends clearing results:
    - Consumer: `clearedPower: -50.0 kW` (receives 50 kWh)
    - Solar Prosumer: `clearedPower: 5.0 kW` (provides 5 kWh)
    - Status: `ACTIVE` ⭐

### Status Tracking
11. **status** - Request trade status
12. **on_status** - Trade in progress with delivery telemetry and settlement cycles

---

## Contract Status Lifecycle

```
PENDING → ACTIVE → COMPLETED
  ↑         ↑         ↑
init     on_confirm  on_status
         (after      (completed)
         clearing)
```

- **PENDING**: Offer curves submitted, awaiting market clearing
- **ACTIVE**: Market cleared, `clearingPrice` and `clearedPower` provided
- **COMPLETED**: Trade finished, settlement computed

---

## Comparison: Fixed Price vs Market-Based

| Aspect | Fixed Price Mode | Market-Based Mode |
|-------|-----------------|-------------------|
| **Roles** | SELLER + BUYER | MARKET_CLEARING_AGENT + PROSUMER |
| **Pricing** | Fixed `pricePerKWh` | Pay-as-clear (discovered at confirmation) |
| **Price Expression** | `pricePerKWh` in SELLER roleInputs | `offerCurve` in PROSUMER roleInputs |
| **Quantity** | `contractedQuantity` in BUYER roleInputs | `clearedPower` from MCA after clearing |
| **Market Clearing** | Not applicable | MCA aggregates offer curves, finds clearing price |
| **Revenue Formula** | `contractedQuantity × pricePerKWh` | `(clearingPrice + marketMakingFee) × clearedPower` |

---

## Schema References

- **EnergyContractP2PTrade**: `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml`
- **EnergyContract** (base): `outputs/schema/EnergyContract/v1/attributes.yaml`
- **EnergyOffer**: `outputs/schema/EnergyOffer/v1/attributes.yaml`
- **OfferCurve**: `outputs/schema/EnergyCoordination/v1/attributes.yaml`

---

## JSON-LD Composition

All examples use proper JSON-LD composition:

- `@context`: Points to schema context files
- `@type`: Specifies the schema type (e.g., `EnergyContractP2PTrade`)
- Attribute slots: `offerAttributes`, `orderAttributes`, `fulfillment.attributes`

---

## Important Notes

### Market Clearing Agent

- Acts as a special peer coordinating multiple PROSUMERs
- Has virtual meter (net power flow = 0)
- Incentivized to balance supply and demand through deviation penalties
- Generates `market-clearing-price` signal after clearing

### Offer Curves

- Submitted during `init` (not `discover`)
- Committed during `confirm`
- Market clears after all `confirm` calls received
- Clearing results provided in `on_confirm`

### Trade Capacity

- Utility provides `approvedMaxTradeKW` per meter via cascaded_init
- Maximum trade volume = `min((buyer_trade_cap - current_buyer_trades_total), (seller_trade_cap - current_seller_trade_total))`
- Prevents double-dipping by deducting from sanctioned loads

---

**Status**: Complete ✅
