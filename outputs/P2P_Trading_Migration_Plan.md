# P2P Trading Examples Migration Plan

**Date:** December 2024  
**Status:** Planning Phase

---

## Overview

This document outlines the plan to migrate P2P trading examples from `examples/v2/P2P_Trading` to `outputs/examples/p2p_trading` using the new `EnergyContractP2PTrade` pattern, similar to the EV charging migration.

---

## Current State Analysis

### Existing Examples Structure

```
examples/v2/P2P_Trading/
├── discover-request.json
├── discover-response.json
├── select-request.json
├── select-response.json
├── init-request.json
├── init-response.json
├── cascaded-init-request.json
├── cascaded-on-init-response.json
├── confirm-request.json
├── confirm-response.json
├── status-request.json
├── status-response.json
└── status-response-completed.json
```

### Key Fields Identified

#### 1. EnergyTradeContract (in `orderAttributes`)
- `contractStatus`: PENDING, ACTIVE, COMPLETED
- `sourceMeterId`: SELLER's meter ID (required)
- `targetMeterId`: BUYER's meter ID (required)
- `inverterId`: SELLER's inverter ID (optional)
- `contractedQuantity`: Energy quantity in kWh (required)
- `tradeStartTime`: Start time of trade window (required)
- `tradeEndTime`: End time of trade window (required)
- `sourceType`: Energy source type (SOLAR, WIND, etc.) (required)
- `certification`: Certification details (optional)
- `settlementCycles`: Settlement cycle info (optional, in completed status)
- `lastUpdated`: Last update timestamp (optional)

#### 2. EnergyTradeOffer (in `offerAttributes`)
- `pricingModel`: PER_KWH
- `settlementType`: DAILY
- `wheelingCharges`: {amount, currency, description} (optional)
- `minimumQuantity`: Minimum trade quantity (optional)
- `maximumQuantity`: Maximum trade quantity (optional)
- `validityWindow`: {start, end} (optional)

#### 3. EnergyTradeDelivery (in `fulfillment.attributes`)
- `deliveryStatus`: IN_PROGRESS, COMPLETED
- `deliveryMode`: GRID_INJECTION
- `deliveredQuantity`: Actual delivered energy
- `deliveryStartTime`, `deliveryEndTime`
- `meterReadings`: Array of meter readings
- `telemetry`: Array of telemetry data
- `settlementCycleId`: Reference to settlement cycle

---

## Proposed EnergyContractP2PTrade Schema

### Role-Based Structure

#### SELLER Role (PROSUMER)
**Required roleInputs:**
- `sourceMeterId`: String - SELLER's meter identifier
- `sourceType`: String - Energy source type (SOLAR, WIND, BATTERY, etc.)
- `pricePerKWh`: Number - Price per kilowatt-hour
- `currency`: String - Currency code (USD, INR, etc.)

**Optional roleInputs:**
- `inverterId`: String - Inverter identifier
- `certification`: Object - Certification details {status, certificates[]}
- `pricingModel`: String - Pricing model (PER_KWH, FIXED, etc.)
- `settlementType`: String - Settlement type (DAILY, HOURLY, etc.)
- `minimumQuantity`: Number - Minimum trade quantity in kWh
- `maximumQuantity`: Number - Maximum trade quantity in kWh
- `validityWindow`: Object - Offer validity {start, end}

**Note:** `wheelingCharges` is provided by GRID_OPERATOR role, not SELLER.

#### BUYER Role (CONSUMER)
**Required roleInputs:**
- `targetMeterId`: String - BUYER's meter identifier
- `contractedQuantity`: Number - Energy quantity in kWh
- `tradeStartTime`: DateTime - Start time of trade window
- `tradeEndTime`: DateTime - End time of trade window

**Optional roleInputs:**
- `preferredSourceType`: String - Preferred energy source type
- `preferredCertification`: Object - Preferred certification requirements

#### GRID_OPERATOR Role
**Required roleInputs:**
- `wheelingCharges`: Number - Wheeling charges per kWh
- `current_buyer_trades_total`: Number - Current total of all active buyer trades for this meter in kWh
- `current_seller_trade_total`: Number - Current total of all active seller trades for this meter in kWh
- `buyer_trade_cap`: Number - Maximum allowed buyer trade volume for this meter in kWh
- `seller_trade_cap`: Number - Maximum allowed seller trade volume for this meter in kWh

**Note:** This role is filled during cascaded_init and cascaded_confirm calls. Maximum trade volume is minimum of (buyer_trade_cap - current_buyer_trades_total) and (seller_trade_cap - current_seller_trade_total).

---

## Questions for Review

1. **Role Assignment:**
   - Should `sourceType` and `certification` be in SELLER's roleInputs, or should they remain at contract root level? 
   A: SELLER's roleInputs. 
   - Should `pricingModel`, `settlementType`, `wheelingCharges` from `EnergyTradeOffer` move to SELLER's roleInputs?
   A: For wheeling_charges, please add it to a new role `GRID_OPERATOR`, who will provide wheeling_charges, current_buyer_trades_total, current_seller_trade_total, buyer_trade_cap, seller_trade_cap (maximum trade volume is minimum of the cap-total for buyer & seller). This will be filled in cascaded_init and cascaded_confirm call.

2. **Contract Root vs Role Inputs:**
   - Should `contractedQuantity`, `tradeStartTime`, `tradeEndTime` be in BUYER's roleInputs or in `inputParameters`? No
   - Should `sourceMeterId` and `targetMeterId` be in roleInputs or in `inputParameters`? roleInputs.

3. **Telemetry Sources:**
   - Should meter readings be defined as `telemetrySources` in the contract? 
   A: Not in this P2P contract. There could be multiple P2P contracts. But each seller & buyer will
      have a seperate contract with GRID OPERATOR, where any deviation from say current_buyer_trade_total will be billed at utility tariff or market rate.
      That contract will use meter telemetry to measure the deviation.
   - How should we reference source and target meters in revenue flow formulas?
   A: in those contracts seperate from P2P trade (but still affected by the trade, since current_buyer_trade_total changes after each P2P trade)

4. **Revenue Flows:**
   - Should revenue flow be: `BUYER → SELLER` based on `contractedQuantity × pricePerKWh`? 
    A: Yes
   - How should `wheelingCharges` be handled in revenue flows? (BUYER → GRID_OPERATOR?) 
    A: `contractedQuantity × wheelingCharges` should flow from BUYER → GRID_OPERATOR

5. **Settlement Cycles:**
   - Should `settlementCycles` remain in contract or move to `fulfillment.attributes`?
   A: move to `fulfillment.attributes`
   - How should settlement be computed from meter readings?
   A: Meter readings are used not for P2P contract itself, but for side contracts seller & buyer have with the grid operator.


6. **Cascaded Init:**
   - The cascaded init example shows utility registration. Should this be a separate contract type or handled via contract roles?
   A: Handled via contract roles.

---

## Proposed Schema Structure

```yaml
EnergyContractP2PTrade:
  allOf:
    - $ref: '../EnergyContract/v1/attributes.yaml#/components/schemas/EnergyContract'
    - type: object
      properties:
        roles:
          items:
            anyOf:
              - $ref: '#/components/schemas/P2PTradeSellerRole'
              - $ref: '#/components/schemas/P2PTradeBuyerRole'
              - $ref: '#/components/schemas/P2PTradeGridOperatorRole'
              - $ref: '../EnergyContract/v1/attributes.yaml#/components/schemas/ContractRole'

P2PTradeSellerRole:
  role: SELLER | PROSUMER
  roleInputs:
    # Required
    sourceMeterId: string
    sourceType: string (SOLAR, WIND, BATTERY, etc.)
    pricePerKWh: number
    currency: string
    
    # Optional
    inverterId: string
    certification: object
    pricingModel: string
    settlementType: string
    minimumQuantity: number
    maximumQuantity: number
    validityWindow: object

P2PTradeBuyerRole:
  role: BUYER | CONSUMER
  roleInputs:
    # Required
    targetMeterId: string
    contractedQuantity: number
    tradeStartTime: datetime
    tradeEndTime: datetime
    
    # Optional
    preferredSourceType: string
    preferredCertification: object

P2PTradeGridOperatorRole:
  role: GRID_OPERATOR
  roleInputs:
    # Required (filled in cascaded_init/cascaded_confirm)
    wheelingCharges: number (per kWh)
    current_buyer_trades_total: number (kWh)
    current_seller_trade_total: number (kWh)
    buyer_trade_cap: number (kWh)
    seller_trade_cap: number (kWh)
```

### Revenue Flows

The contract defines two revenue flows:

1. **BUYER → SELLER**: `contractedQuantity × pricePerKWh`
   - Formula: `roles.BUYER.roleInputs.contractedQuantity × roles.SELLER.roleInputs.pricePerKWh`

2. **BUYER → GRID_OPERATOR**: `contractedQuantity × wheelingCharges`
   - Formula: `roles.BUYER.roleInputs.contractedQuantity × roles.GRID_OPERATOR.roleInputs.wheelingCharges`

### Telemetry and Meter Readings

- **Meter readings are NOT in this P2P contract**
- Meter readings are used in separate contracts between SELLER/BUYER and GRID_OPERATOR
- These separate contracts measure deviation from `current_buyer_trade_total` / `current_seller_trade_total`
- Deviation is billed at utility tariff or market rate
- The P2P contract affects these separate contracts by changing the `current_*_trades_total` values

### Settlement Cycles

- Settlement cycles move to `fulfillment.attributes` (not in contract)
- Settlement is computed in separate GRID_OPERATOR contracts using meter telemetry

---

## Migration Steps

1. **Phase 1: Schema Design** (Current)
   - ✅ Analyze existing examples
   - ✅ Design `EnergyContractP2PTrade` schema
   - ✅ Incorporate feedback and answers to questions
   - ✅ Create schema file with GRID_OPERATOR role

2. **Phase 2: Schema Implementation** ✅
   - ✅ Create `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml`
   - ✅ Ensure consistency with `EnergyContract` base schema
   - ✅ Validate OpenAPI 3.1.1 compliance
   - ✅ Add GRID_OPERATOR role with required fields
   - ✅ Remove wheelingCharges from SELLER role

3. **Phase 3: Example Creation**
   - Create `outputs/examples/p2p_trading/` directory structure
   - Map all fields from old examples to new structure
   - Create 13 example files (discover, select, init, confirm, status, cascaded init)
   - Use simple `roleInputs` format (direct values)

4. **Phase 4: Documentation**
   - Create README for P2P trading examples
   - Document field mappings
   - Document contract lifecycle

---

## Next Steps

1. **Review this plan and schema proposal**
2. **Answer questions above**
3. **Approve `EnergyContractP2PTrade` schema design**
4. **Proceed with implementation**

---

**Status:** ✅ Schema created and updated based on feedback. Ready for example creation.

