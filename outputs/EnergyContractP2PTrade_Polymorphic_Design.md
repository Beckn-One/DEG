# EnergyContractP2PTrade - Polymorphic Design

**Version:** 1.0  
**Date:** December 2024

---

## Overview

`EnergyContractP2PTrade` has been extended to support **two trading modes** in a polymorphic design:

1. **Fixed Price Mode**: Direct buyer-to-seller trades with fixed pricing
2. **Market-Based Mode**: Market clearing agent coordinates multiple prosumers with offer curves

Both modes share the same contract schema but use different role combinations and roleInputs structures.

---

## Trading Modes

### Mode 1: Fixed Price Trading

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

### Mode 2: Market-Based Trading

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

- **Fixed Price Mode**: Contract contains `SELLER` and `BUYER` roles
- **Market-Based Mode**: Contract contains `MARKET_CLEARING_AGENT` and `PROSUMER` roles

### 2. Conditional RoleInputs

**SELLER role** (polymorphic):
- **Fixed Price Mode**: Must provide `pricePerKWh` and `currency`
- **Market-Based Mode**: Not used (use `PROSUMER` role instead)
- Optional `offerCurve` for hybrid scenarios

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

**Fixed Price Mode**:
```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "roles.BUYER.roleInputs.contractedQuantity × roles.SELLER.roleInputs.pricePerKWh"
}
```

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

### Fixed Price Example
See: `outputs/examples/p2p_trading/`

### Market-Based Example
(To be created in `outputs/examples/p2p_trading_market_based/`)

---

## Benefits of Polymorphic Design

1. **Single Schema**: One contract schema handles both trading modes
2. **Type Safety**: Role combinations enforce mode correctness
3. **Backward Compatible**: Existing fixed price examples continue to work
4. **Extensible**: Easy to add new modes or roles in the future
5. **Clear Semantics**: Role names clearly indicate mode and responsibilities

---

## Migration Notes

- **Existing fixed price examples**: No changes needed, continue using `SELLER` + `BUYER` roles
- **New market-based examples**: Use `MARKET_CLEARING_AGENT` + `PROSUMER` roles with `offerCurve`
- **Hybrid scenarios**: Can mix roles (e.g., SELLER with offerCurve) for flexibility

---

**Status**: ✅ Schema extended and validated

