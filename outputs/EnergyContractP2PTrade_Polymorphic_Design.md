# EnergyContractP2PTrade - Polymorphic Design

**Version:** 1.0  
**Date:** December 2024

---

## Overview

`EnergyContractP2PTrade` has been extended to support **three pricing modes** in a polymorphic design:

1. **Simple Fixed Price Mode**: Direct buyer-to-seller trades with fixed `pricePerKWh`
2. **Tariff-Based Mode**: Utility-style trades with time-of-use, tiered pricing via `tariff` object
3. **Market-Based Mode**: Market clearing agent coordinates multiple prosumers with offer curves

All modes share the same contract schema but use different role combinations and roleInputs structures.

---

## Trading Modes

### Mode 1: Simple Fixed Price Trading

**Roles**: `SELLER` + `BUYER` (+ optional `GRID_OPERATOR`)

**SELLER roleInputs** (required):
- `sourceMeterId`: String
- `sourceType`: String (SOLAR, WIND, etc.)
- `pricePerKWh`: Number (fixed price)
- `currency`: String

**BUYER roleInputs** (required):
- `targetMeterId`: String
- `contractedQuantity`: Number (kWh)
- `tradeStartTime`: DateTime
- `tradeEndTime`: DateTime

**Revenue Flows**:
- `BUYER → SELLER`: `contractedQuantity × pricePerKWh`
- `BUYER → GRID_OPERATOR`: `contractedQuantity × wheelingCharges` (if GRID_OPERATOR role present)

**Example Use Case**: Consumer buys 10 kWh from solar prosumer at fixed ₹0.15/kWh

---

### Mode 2: Tariff-Based Trading

**Roles**: `SELLER` + `BUYER` (+ optional `GRID_OPERATOR`)

**SELLER roleInputs** (required):
- `sourceMeterId`: String
- `sourceType`: String (GRID, SOLAR, etc.)
- `tariff`: Object (full tariff structure based on OCPI standard)

**BUYER roleInputs** (required):
- `targetMeterId`: String
- `contractedQuantity`: Number (kWh)
- `tradeStartTime`: DateTime
- `tradeEndTime`: DateTime

**Tariff Structure** (OCPI-based):
- `elements`: Array of tariff elements with price components and time restrictions
- `priceComponents`: Type (ENERGY, TIME, FLAT), price, VAT, step_size
- `restrictions`: Time-of-day, day-of-week, tier limits (minKWh, maxKWh)
- `energyMix`: Optional energy source information

**Revenue Flows**:
- `BUYER → SELLER`: `computeTariffPrice(tariff, tradeStartTime, tradeEndTime, deliveredQuantity) × deliveredQuantity`
- `BUYER → GRID_OPERATOR`: `deliveredQuantity × wheelingCharges` (if GRID_OPERATOR role present)

**Example Use Case**: Consumer buys from utility with time-of-use tariff:
- Peak hours (6 PM - 10 PM): ₹0.20/kWh
- Off-peak hours (10 PM - 6 AM): ₹0.10/kWh
- Mid-peak hours (6 AM - 6 PM): ₹0.15/kWh

**Note**: `pricePerKWh` and `tariff` are mutually exclusive in SELLER roleInputs.

---

### Mode 3: Market-Based Trading

**Roles**: `MARKET_CLEARING_AGENT` + `PROSUMER` (+ optional `GRID_OPERATOR`)

**MARKET_CLEARING_AGENT roleInputs** (required):
- `marketMakingFee`: Number (per kWh)

**MARKET_CLEARING_AGENT roleInputs** (after market clearing):
- `clearingPrice`: Number (per kWh) - provided in `on_confirm`
- `clearedPower`: Object (keyed by prosumer) - provided in `on_confirm`

**PROSUMER roleInputs** (required):
- `sourceMeterId`: String
- `sourceType`: String (SOLAR, WIND, BATTERY, CONSUMER, etc.)
- `offerCurve`: Object (OfferCurve structure)

**OfferCurve Structure**:
```json
{
  "currency": "INR",
  "minExport": -50,  // Negative = max withdrawal (buyer)
  "maxExport": 5,    // Positive = max export (seller)
  "curve": [
    { "price": 0.06, "powerKW": -50 },  // Willing to buy 50 kW at ₹0.06/kWh
    { "price": 0.07, "powerKW": 0 }     // No trade at ₹0.07/kWh
  ]
}
```

**Revenue Flows**:
- `PROSUMER → MARKET_CLEARING_AGENT`: `(clearingPrice + marketMakingFee) × clearedPower`
  - Positive clearedPower (seller): PROSUMER receives payment
  - Negative clearedPower (buyer): PROSUMER pays
- `MARKET_CLEARING_AGENT → GRID_OPERATOR`: `contractedQuantity × wheelingCharges` (if GRID_OPERATOR role present)

**Example Use Case**: Multiple prosumers submit offer curves, market clears at ₹0.0625/kWh, economic disaggregation distributes setpoints

---

## Polymorphic Design Principles

### 1. Role-Based Mode Detection

The contract mode is determined by which roles are present:

- **Fixed Price Mode** (Simple or Tariff): Contract contains `SELLER` and `BUYER` roles
  - **Simple Fixed Price**: SELLER provides `pricePerKWh` + `currency`
  - **Tariff-Based**: SELLER provides `tariff` object
- **Market-Based Mode**: Contract contains `MARKET_CLEARING_AGENT` and `PROSUMER` roles

### 2. Conditional RoleInputs

**SELLER role** (polymorphic):
- **Simple Fixed Price Mode**: Must provide `pricePerKWh` and `currency`
- **Tariff-Based Mode**: Must provide `tariff` object (mutually exclusive with `pricePerKWh`)
- **Market-Based Mode**: Not used (use `PROSUMER` role instead)
- Optional `offerCurve` for hybrid scenarios (discouraged)

**BUYER role** (fixed price only):
- Only used in fixed price mode
- Must provide `contractedQuantity`, `tradeStartTime`, `tradeEndTime`

**PROSUMER role** (market-based only):
- Only used in market-based mode
- Must provide `offerCurve` (not `pricePerKWh`)

**MARKET_CLEARING_AGENT role** (market-based only):
- Only used in market-based mode
- Provides `marketMakingFee` upfront
- Provides `clearingPrice` and `clearedPower` after market clearing

### 3. Revenue Flow Formulas

Revenue flows adapt based on mode:

**Simple Fixed Price Mode**:
```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "roles.BUYER.roleInputs.contractedQuantity × roles.SELLER.roleInputs.pricePerKWh"
}
```

**Tariff-Based Mode**:
```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity"
}
```

**Note**: Tariff computation requires `deliveredQuantity` (from telemetry) and matches delivery time windows to tariff element restrictions.

**Market-Based Mode**:
```json
{
  "from": "PROSUMER",
  "to": "MARKET_CLEARING_AGENT",
  "formula": "(roles.MARKET_CLEARING_AGENT.roleInputs.clearingPrice + roles.MARKET_CLEARING_AGENT.roleInputs.marketMakingFee) × roles.MARKET_CLEARING_AGENT.roleInputs.clearedPower[PROSUMER.era]"
}
```

---

## Market Clearing Flow

### 1. Discovery Phase
- Simple `discover` call (no offer curves yet)
- MCA responds with `on_discover` indicating `pricingModel: "PAY_AS_CLEAR"`

### 2. Init Phase
- PROSUMERs submit `init` with `offerCurve` in roleInputs
- MCA cascades to Utility for load approval
- Utility responds with `approvedMaxTradeKW` per meter

### 3. Confirm Phase
- PROSUMERs submit `confirm` (commits to offer curve)
- MCA collects all confirmed bids
- **Market clearing happens** (aggregate offer curves, find clearing price)
- MCA generates `market-clearing-price` signal
- MCA sends `on_confirm` with `clearingPrice` and `clearedPower` per PROSUMER

### 4. Settlement Phase
- Revenue flows computed using clearing price
- Settlement cycles tracked in `fulfillment.attributes`

---

## Schema Structure

```yaml
EnergyContractP2PTrade:
  allOf:
    - EnergyContract (base)
    - roles:
        anyOf:
          # Fixed Price Mode
          - P2PTradeSellerRole
          - P2PTradeBuyerRole
          # Market-Based Mode
          - P2PTradeMarketClearingAgentRole
          - P2PTradeProsumerRole
          # Optional (both modes)
          - P2PTradeGridOperatorRole
```

---

## Examples

### Simple Fixed Price Example
See: `outputs/examples/p2p_trading/`

### Tariff-Based Example
See: `outputs/examples/p2p_trading_tariff/`

### Market-Based Example
See: `outputs/examples/p2p_trading_market_based/`

---

## Benefits of Polymorphic Design

1. **Single Schema**: One contract schema handles all three pricing modes
2. **Type Safety**: Role combinations enforce mode correctness
3. **Backward Compatible**: Existing fixed price examples continue to work
4. **Standards Alignment**: Tariff structure based on OCPI (widely adopted)
5. **Extensible**: Easy to add new modes or roles in the future
6. **Clear Semantics**: Role names clearly indicate mode and responsibilities
7. **Utility Integration**: Enables utility-to-consumer trades with complex tariffs

---

## Migration Notes

- **Existing fixed price examples**: No changes needed, continue using `SELLER` + `BUYER` roles with `pricePerKWh`
- **New tariff-based examples**: Use `SELLER` + `BUYER` roles with `tariff` object (instead of `pricePerKWh`)
- **New market-based examples**: Use `MARKET_CLEARING_AGENT` + `PROSUMER` roles with `offerCurve`
- **Mutual Exclusivity**: `pricePerKWh` and `tariff` are mutually exclusive in SELLER roleInputs
- **Hybrid scenarios**: Can mix roles (e.g., SELLER with offerCurve) for flexibility (discouraged)

---

**Status**: ✅ Schema extended and validated

