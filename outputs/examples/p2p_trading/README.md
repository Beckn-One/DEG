# P2P Trading Examples - EnergyContractP2PTrade Pattern (Fixed Price Mode)

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This directory contains complete JSON message examples for **fixed price P2P energy trading** use cases using the new `EnergyContractP2PTrade` pattern. These examples demonstrate the **Fixed Price Mode** with SELLER + BUYER roles and fixed `pricePerKWh`.

**Note**: For market-based trading with offer curves and market clearing, see `../p2p_trading_market_based/` directory.

---

## Directory Structure

```
p2p_trading/
├── README.md
├── 01_discover/
│   └── discover-solar-energy.json
├── 02_on_discover/
│   └── solar-energy-catalog.json
├── 03_select/
│   └── select-solar-energy-offer.json
├── 04_on_select/
│   └── on-select-solar-energy-offer.json
├── 05_init/
│   └── init-p2p-trade.json
├── 06_on_init/
│   └── on-init-p2p-trade.json
├── 07_cascaded_init/
│   └── cascaded-init-utility-registration.json
├── 08_cascaded_on_init/
│   └── cascaded-on-init-utility-registration.json
├── 09_confirm/
│   └── confirm-p2p-trade.json
├── 10_on_confirm/
│   └── on-confirm-p2p-trade.json
├── 11_status/
│   └── status-p2p-trade.json
├── 12_on_status/
│   └── on-status-p2p-trade-in-progress.json
└── 13_on_status_completed/
    └── on-status-p2p-trade-completed.json
```

---

## Key Features

### 1. EnergyContractP2PTrade Pattern - Fixed Price Mode

All examples use `EnergyContractP2PTrade` in **Fixed Price Mode** with `orderAttributes` (and `offerAttributes` in discovery). This specialized contract:

- **Inherits from** `EnergyContract` (core abstract schema)
- **Fixed Price Mode Roles**:
  - **SELLER**: Provides `sourceMeterId`, `sourceType`, `pricePerKWh`, `currency` (required) + optional fields
  - **BUYER**: Provides `targetMeterId`, `contractedQuantity`, `tradeStartTime`, `tradeEndTime` (required)
  - **GRID_OPERATOR** (optional): Provides `wheelingCharges`, trade capacity info (filled in cascaded_init/cascaded_confirm)
- **Status transitions**: `PENDING` (in init/select) → `ACTIVE` (in on_confirm) → `COMPLETED` (in on_status_completed)
- **Pricing**: Fixed `pricePerKWh` known upfront (not market-cleared)

### 2. Simple roleInputs Format

All examples use direct values in `roleInputs` (not full `RoleInput` objects):

```json
"roleInputs": {
  "sourceMeterId": "100200300",
  "sourceType": "SOLAR",
  "pricePerKWh": 0.15,
  "currency": "USD"
}
```

This makes examples cleaner and easier to read, while the schema still supports both formats (direct values OR full `RoleInput` objects with schema metadata).

### 3. Computational Contracts with Revenue Flows

Contracts define two revenue flows:

1. **BUYER → SELLER**: `contractedQuantity × pricePerKWh`
   ```json
   {
     "from": "BUYER",
     "to": "SELLER",
     "formula": "roles.BUYER.roleInputs.contractedQuantity × roles.SELLER.roleInputs.pricePerKWh",
     "description": "BUYER pays SELLER based on contracted quantity × price per kWh"
   }
   ```

2. **BUYER → GRID_OPERATOR**: `contractedQuantity × wheelingCharges`
   ```json
   {
     "from": "BUYER",
     "to": "GRID_OPERATOR",
     "formula": "roles.BUYER.roleInputs.contractedQuantity × roles.GRID_OPERATOR.roleInputs.wheelingCharges",
     "description": "BUYER pays GRID_OPERATOR for wheeling charges based on contracted quantity"
   }
   ```

### 4. GRID_OPERATOR Role and Trade Capacity

The GRID_OPERATOR role is filled during cascaded_init/cascaded_confirm calls and provides:

- **wheelingCharges**: Per-kWh charge for grid services
- **current_buyer_trades_total**: Current active buyer trades for the meter
- **current_seller_trade_total**: Current active seller trades for the meter
- **buyer_trade_cap**: Maximum allowed buyer trade volume
- **seller_trade_cap**: Maximum allowed seller trade volume

**Maximum trade volume** = `min((buyer_trade_cap - current_buyer_trades_total), (seller_trade_cap - current_seller_trade_total))`

### 5. Settlement Cycles in Fulfillment

Settlement cycles are moved to `fulfillment.attributes` (not in contract), as they are computed from meter readings in separate GRID_OPERATOR contracts:

```json
"fulfillment.attributes": {
  "@type": "EnergyTradeDelivery",
  "settlementCycles": [
    {
      "cycleId": "settle-2024-10-04-001",
      "startTime": "2024-10-04T00:00:00Z",
      "endTime": "2024-10-04T23:59:59Z",
      "status": "SETTLED",
      "amount": 1.75,
      "currency": "USD",
      "breakdown": {
        "energyCost": 1.5,
        "wheelingCharges": 0.25
      }
    }
  ]
}
```

---

## Example Flow

### Discovery & Selection
1. **discover** - Search for solar energy resources
2. **on_discover** - Catalog with `EnergyOffer` containing `EnergyContractP2PTrade` in `offerAttributes` (status: PENDING, SELLER role filled)
3. **select** - Select offer, contract in `orderAttributes` (status: PENDING)
4. **on_select** - Selection confirmed with quote breakdown (status: PENDING)

### Init & Cascaded Init
5. **init** - Initialize order with BUYER roleInputs (targetMeterId, contractedQuantity, tradeStartTime, tradeEndTime) (status: PENDING)
6. **on_init** - Init confirmed (status: PENDING)
7. **cascaded_init** - Cascaded call to utility/GRID_OPERATOR for trade capacity and wheeling charges
8. **cascaded_on_init** - GRID_OPERATOR role filled with capacity info and wheeling charges (status: PENDING)

### Confirm
9. **confirm** - Final confirmation request with all roles filled (status: PENDING)
10. **on_confirm** - Contract activated (status: ACTIVE) ⭐

### Status Tracking
11. **status** - Request trade status
12. **on_status** - Trade in progress with delivery telemetry and settlement cycles (status: ACTIVE)
13. **on_status_completed** - Trade completed with final settlement (status: COMPLETED)

---

## Contract Status Lifecycle

```
PENDING → ACTIVE → COMPLETED
  ↑         ↑         ↑
init/    on_confirm  on_status
select   (all roles  (completed)
         filled)
```

- **PENDING**: Contract defined, roles being filled, awaiting confirmation
- **ACTIVE**: Contract confirmed, trade in progress
- **COMPLETED**: Trade finished, settlement computed

---

## Field Mapping

All functional fields from original examples have been mapped:

- **Item attributes** (sourceType, deliveryMode, certificationStatus, etc.) → Remain in `itemAttributes` as `EnergyResource`
- **Contract fields** → Mapped to `EnergyContractP2PTrade`:
  - SELLER roleInputs: sourceMeterId, sourceType, pricePerKWh, currency, inverterId, certification
  - BUYER roleInputs: targetMeterId, contractedQuantity, tradeStartTime, tradeEndTime
  - GRID_OPERATOR roleInputs: wheelingCharges, trade capacity info (filled in cascaded_init)
- **Delivery data** → In `fulfillment.attributes` (EnergyTradeDelivery schema)
- **Settlement cycles** → In `fulfillment.attributes` (not in contract)

---

## Schema References

- **EnergyContractP2PTrade**: `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml`
- **EnergyContract** (base): `outputs/schema/EnergyContract/v1/attributes.yaml`
- **EnergyOffer**: `outputs/schema/EnergyOffer/v1/attributes.yaml`
- **EnergyResource**: `outputs/schema/EnergyResource/v0.2/attributes.yaml`
- **EnergyTradeDelivery**: `outputs/schema/EnergyTradeDelivery/v0.2/attributes.yaml`

---

## JSON-LD Composition

All examples use proper JSON-LD composition:

- `@context`: Points to schema context files
- `@type`: Specifies the schema type (e.g., `EnergyContractP2PTrade`)
- Attribute slots: `offerAttributes`, `orderAttributes`, `itemAttributes`, `fulfillment.attributes`

---

## Comparison: Fixed Price vs Market-Based

| Aspect | Fixed Price Mode (this directory) | Market-Based Mode (`../p2p_trading_market_based/`) |
|-------|-----------------------------------|-----------------------------------------------------|
| **Roles** | SELLER + BUYER | MARKET_CLEARING_AGENT + PROSUMER |
| **Pricing** | Fixed `pricePerKWh` | Pay-as-clear (discovered at confirmation) |
| **Price Expression** | `pricePerKWh` in SELLER roleInputs | `offerCurve` in PROSUMER roleInputs |
| **Quantity** | `contractedQuantity` in BUYER roleInputs | `clearedPower` from MCA after clearing |
| **Market Clearing** | Not applicable | MCA aggregates offer curves, finds clearing price |
| **Use Case** | Direct buyer-seller trade | Multiple prosumers, market coordination |

## Migration from Original Examples

These examples replace the original `EnergyTradeContract` and `EnergyTradeOffer` schemas with the new `EnergyContractP2PTrade` pattern. Key differences:

1. **Contract-based**: All contract terms in `EnergyContractP2PTrade` structure
2. **Role-based inputs**: SELLER, BUYER, and GRID_OPERATOR provide inputs via `roleInputs`
3. **Computational billing**: Revenue flows defined as formulas
4. **GRID_OPERATOR integration**: Trade capacity and wheeling charges provided via cascaded_init
5. **Settlement in fulfillment**: Settlement cycles moved to `fulfillment.attributes`
6. **Polymorphic design**: Same schema supports both fixed price and market-based modes

---

## Important Notes

### Meter Readings and Telemetry

- **Meter readings are NOT in the P2P contract**
- Meter readings are used in separate contracts between SELLER/BUYER and GRID_OPERATOR
- These separate contracts measure deviation from `current_buyer_trade_total` / `current_seller_trade_total`
- Deviation is billed at utility tariff or market rate
- The P2P contract affects these separate contracts by changing the `current_*_trades_total` values

### Trade Capacity Calculation

The maximum trade volume is calculated as:
```
min((buyer_trade_cap - current_buyer_trades_total), (seller_trade_cap - current_seller_trade_total))
```

This ensures that:
- Buyer doesn't exceed sanctioned load
- Seller doesn't exceed generation capacity
- Grid constraints are respected

---

**Status**: Complete ✅

