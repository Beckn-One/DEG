# EnergyContractP2PTrade - Validation Rules

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document defines validation rules for `EnergyContractP2PTrade` to ensure correct role combinations and roleInputs based on the trading mode (fixed price vs market-based).

---

## Mode Detection

The contract mode is determined by which roles are present:

- **Fixed Price Mode**: Contract contains `SELLER` and `BUYER` roles
- **Market-Based Mode**: Contract contains `MARKET_CLEARING_AGENT` and `PROSUMER` roles

**Rule**: A contract MUST use one mode or the other, not both.

---

## Fixed Price Mode Validation

### Required Roles

1. **SELLER role** (required)
   - `role`: Must be `SELLER` or `PROSUMER`
   - `filled`: Must be `true` before contract confirmation
   - `roleInputs` (required):
     - `sourceMeterId`: String (required)
     - `sourceType`: String (required)
     - **Pricing (ONE of the following)**:
       - `pricePerKWh`: Number (required for simple fixed price)
       - `currency`: String (required with pricePerKWh)
       - OR `tariff`: Object (required for tariff-based pricing)
       - OR `offerCurve`: Object (for market-based, use PROSUMER role instead)

2. **BUYER role** (required)
   - `role`: Must be `BUYER` or `CONSUMER`
   - `filled`: Must be `true` before contract confirmation
   - `roleInputs` (required):
     - `targetMeterId`: String (required)
     - `contractedQuantity`: Number (required, > 0)
     - `tradeStartTime`: DateTime (required)
     - `tradeEndTime`: DateTime (required, > tradeStartTime)

3. **GRID_OPERATOR role** (optional)
   - `role`: Must be `GRID_OPERATOR`
   - `filled`: Can be `true` or `false` (filled in cascaded_init)
   - `roleInputs` (required when filled):
     - `wheelingCharges`: Number (required, ≥ 0)
     - `current_buyer_trades_total`: Number (required, ≥ 0)
     - `current_seller_trade_total`: Number (required, ≥ 0)
     - `buyer_trade_cap`: Number (required, > 0)
     - `seller_trade_cap`: Number (required, > 0)

### Validation Rules

1. **SELLER roleInputs**:
   - **Mutual Exclusivity**: `pricePerKWh` and `tariff` MUST NOT both be provided (use one or the other)
   - **Simple Fixed Price** (if `pricePerKWh` provided):
     - `pricePerKWh` MUST be > 0
     - `currency` MUST be valid ISO 4217 code
   - **Tariff-Based** (if `tariff` provided):
     - `tariff.currency` MUST be valid ISO 4217 code
     - `tariff.elements` MUST have at least one element
     - Each element MUST have at least one `priceComponents` with `type: ENERGY`
     - If `restrictions.startTime` provided, `restrictions.endTime` MUST also be provided
     - `tariff.currency` MUST match contract currency (if specified)
   - `offerCurve` MUST NOT be provided (use PROSUMER role for market-based)

2. **BUYER roleInputs**:
   - `contractedQuantity` MUST be > 0
   - `tradeEndTime` MUST be > `tradeStartTime`
   - `offerCurve` MUST NOT be provided (use PROSUMER role for market-based)

3. **GRID_OPERATOR roleInputs** (when present):
   - `buyer_trade_cap` MUST be ≥ `current_buyer_trades_total`
   - `seller_trade_cap` MUST be ≥ `current_seller_trade_total`
   - Maximum trade volume = `min((buyer_trade_cap - current_buyer_trades_total), (seller_trade_cap - current_seller_trade_total))`
   - `contractedQuantity` MUST be ≤ maximum trade volume

4. **Revenue Flows**:
   - **Simple Fixed Price**: MUST include flow: `BUYER → SELLER` with formula using `contractedQuantity × pricePerKWh`
   - **Tariff-Based**: MUST include flow: `BUYER → SELLER` with formula using `computeTariffPrice(tariff, tradeStartTime, tradeEndTime, deliveredQuantity) × deliveredQuantity`
   - If GRID_OPERATOR present: MUST include flow: `BUYER → GRID_OPERATOR` with formula using `contractedQuantity × wheelingCharges` (or `deliveredQuantity` for tariff-based)
   - `netZero` MUST be `true`

---

## Market-Based Mode Validation

### Required Roles

1. **MARKET_CLEARING_AGENT role** (required)
   - `role`: Must be `MARKET_CLEARING_AGENT`
   - `filled`: Must be `true` (filled by MCA)
   - `roleInputs` (required):
     - `marketMakingFee`: Number (required, ≥ 0)
   - `roleInputs` (after market clearing, in `on_confirm`):
     - `clearingPrice`: Number (required, ≥ 0)
     - `clearedPower`: Object (required, keyed by PROSUMER era/meterId)

2. **PROSUMER role** (required, one or more)
   - `role`: Must be `PROSUMER`
   - `filled`: Must be `true` before contract confirmation
   - `roleInputs` (required):
     - `sourceMeterId`: String (required)
     - `sourceType`: String (required)
     - `offerCurve`: Object (required, OfferCurve structure)

3. **GRID_OPERATOR role** (optional)
   - Same as fixed price mode

### Validation Rules

1. **MARKET_CLEARING_AGENT roleInputs**:
   - `marketMakingFee` MUST be ≥ 0
   - `clearingPrice` MUST be null before market clearing, provided in `on_confirm`
   - `clearedPower` MUST be null before market clearing, provided in `on_confirm`
   - `clearedPower` keys MUST match PROSUMER `filledBy` values or `sourceMeterId` values
   - `clearedPower` values MUST be within `offerCurve.minExport` and `offerCurve.maxExport` for each PROSUMER

2. **PROSUMER roleInputs**:
   - `offerCurve.currency` MUST be valid ISO 4217 code
   - `offerCurve.minExport` MUST be ≤ `offerCurve.maxExport`
   - `offerCurve.curve` MUST have at least 1 point
   - `offerCurve.curve` points MUST be sorted by `price` (ascending)
   - `offerCurve.curve[0].powerKW` MUST equal `offerCurve.minExport`
   - `offerCurve.curve[-1].powerKW` MUST equal `offerCurve.maxExport`
   - `pricePerKWh` MUST NOT be provided (use offerCurve instead)

3. **OfferCurve Validation**:
   - All `curve` points MUST have `price` ≥ 0
   - `powerKW` values MUST be within `[minExport, maxExport]` range
   - For buyers (negative power): `minExport` < 0, `maxExport` ≤ 0
   - For sellers (positive power): `minExport` ≥ 0, `maxExport` > 0

4. **Market Clearing Validation**:
   - All PROSUMERs MUST have submitted `confirm` before market clearing
   - Clearing price MUST intersect all offer curves
   - `clearedPower` for each PROSUMER MUST be within their `offerCurve` range
   - Sum of all `clearedPower` values MUST balance (buyers = sellers, accounting for sign)

5. **GRID_OPERATOR roleInputs** (when present):
   - Same validation as fixed price mode
   - `clearedPower` values MUST respect trade capacity constraints

6. **Revenue Flows**:
   - MUST include flow: `PROSUMER → MARKET_CLEARING_AGENT` with formula using `(clearingPrice + marketMakingFee) × clearedPower`
   - If GRID_OPERATOR present: MUST include flow: `MARKET_CLEARING_AGENT → GRID_OPERATOR` with formula using `abs(clearedPower) × wheelingCharges`
   - `netZero` MUST be `true`

---

## Cross-Mode Validation

### Invalid Role Combinations

❌ **NOT ALLOWED**:
- SELLER + PROSUMER (mixed modes)
- BUYER + MARKET_CLEARING_AGENT (mixed modes)
- SELLER + MARKET_CLEARING_AGENT (mixed modes)
- BUYER + PROSUMER (mixed modes)
- Only SELLER (missing BUYER)
- Only BUYER (missing SELLER)
- Only MARKET_CLEARING_AGENT (missing PROSUMER)
- Only PROSUMER (missing MARKET_CLEARING_AGENT)

✅ **ALLOWED**:
- SELLER + BUYER (fixed price mode)
- SELLER + BUYER + GRID_OPERATOR (fixed price mode with grid operator)
- MARKET_CLEARING_AGENT + PROSUMER (market-based mode)
- MARKET_CLEARING_AGENT + PROSUMER + GRID_OPERATOR (market-based mode with grid operator)
- Multiple PROSUMER roles (market-based mode with multiple participants)

### RoleInputs Validation

1. **SELLER role**:
   - MUST NOT have `offerCurve` in fixed price mode
   - `offerCurve` is optional (for hybrid scenarios) but discouraged

2. **PROSUMER role**:
   - MUST NOT have `pricePerKWh` or `currency` (use `offerCurve.currency` instead)
   - MUST NOT have `contractedQuantity`, `tradeStartTime`, `tradeEndTime` (use `clearedPower` from MCA)

3. **BUYER role**:
   - MUST NOT have `offerCurve` (use PROSUMER role for market-based)

4. **MARKET_CLEARING_AGENT role**:
   - MUST NOT have `pricePerKWh`, `sourceMeterId`, `sourceType` (not applicable)

---

## Status Transitions

### Fixed Price Mode

```
PENDING → ACTIVE → COMPLETED
  ↑         ↑         ↑
init/    on_confirm  on_status
select   (all roles  (completed)
         filled)
```

**Validation**:
- `status: PENDING`: SELLER and BUYER roles filled, GRID_OPERATOR optional
- `status: ACTIVE`: All required roles filled, contract confirmed
- `status: COMPLETED`: Trade finished, settlement computed

### Market-Based Mode

```
PENDING → ACTIVE → COMPLETED
  ↑         ↑         ↑
init     on_confirm  on_status
         (after      (completed)
         clearing)
```

**Validation**:
- `status: PENDING`: MARKET_CLEARING_AGENT and PROSUMER roles filled, offer curves submitted
- `status: ACTIVE`: Market cleared, `clearingPrice` and `clearedPower` provided
- `status: COMPLETED`: Trade finished, settlement computed

---

## Revenue Flow Validation

### Fixed Price Mode

**Required flows** (Simple Fixed Price):
1. `BUYER → SELLER`: `contractedQuantity × pricePerKWh`
2. `BUYER → GRID_OPERATOR`: `contractedQuantity × wheelingCharges` (if GRID_OPERATOR present)

**Required flows** (Tariff-Based):
1. `BUYER → SELLER`: `computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity`
2. `BUYER → GRID_OPERATOR`: `deliveredQuantity × roles.GRID_OPERATOR.roleInputs.wheelingCharges` (if GRID_OPERATOR present)

**Validation**:
- Formula MUST reference valid roleInputs paths
- For tariff-based: Tariff computation requires `deliveredQuantity` (from telemetry), `tradeStartTime`, `tradeEndTime`
- `netZero` MUST be `true` (sum of all flows = 0)

### Market-Based Mode

**Required flows**:
1. `PROSUMER → MARKET_CLEARING_AGENT`: `(clearingPrice + marketMakingFee) × clearedPower[PROSUMER.era]`
2. `MARKET_CLEARING_AGENT → GRID_OPERATOR`: `abs(clearedPower[PROSUMER.era]) × wheelingCharges` (if GRID_OPERATOR present)

**Validation**:
- Formula MUST reference `clearingPrice` and `clearedPower` (available after clearing)
- `clearedPower` MUST be keyed by PROSUMER identifier
- `netZero` MUST be `true` (sum of all flows = 0)

---

## Implementation Notes

### Schema-Level Validation

The OpenAPI schema enforces:
- Required fields in roleInputs
- Type constraints (String, Number, Object, DateTime)
- Enum values for roles
- Structure of nested objects (OfferCurve, etc.)

### Application-Level Validation

Applications MUST validate:
- Role combinations (mode detection)
- Cross-field constraints (e.g., `tradeEndTime > tradeStartTime`)
- Business rules (e.g., trade capacity limits)
- Market clearing logic (offer curve aggregation, clearing price calculation)

### Runtime Validation

At runtime:
- Before `confirm`: Validate all required roleInputs are provided
- After market clearing: Validate `clearingPrice` and `clearedPower` are within constraints
- Before settlement: Validate revenue flows are computable and net-zero

---

## Error Messages

### Invalid Role Combination

```
Error: Invalid role combination. EnergyContractP2PTrade supports two modes:
- Fixed Price: SELLER + BUYER roles
- Market-Based: MARKET_CLEARING_AGENT + PROSUMER roles
Found: [SELLER, PROSUMER] (mixed modes)
```

### Missing Required RoleInputs

```
Error: PROSUMER roleInputs missing required field: offerCurve
Required for market-based mode. Provide offerCurve with currency, minExport, maxExport, and curve array.
```

### Invalid OfferCurve

```
Error: Invalid offerCurve structure
- curve[0].powerKW (0) does not match minExport (-50)
- curve points not sorted by price
- powerKW values outside [minExport, maxExport] range
```

### Market Clearing Validation

```
Error: Market clearing validation failed
- clearingPrice (0.0625) does not intersect all offer curves
- clearedPower (6.0) exceeds offerCurve.maxExport (5.0) for prosumer-001
- Sum of clearedPower values does not balance: buyers (-50) ≠ sellers (45)
```

### Tariff Validation

```
Error: Invalid tariff structure
- tariff.elements must have at least one element
- Each element must have at least one priceComponents with type: ENERGY
- restrictions.startTime (18:00) provided but restrictions.endTime missing
- tariff.currency (USD) does not match contract currency (INR)
```

---

**Status**: Complete ✅
