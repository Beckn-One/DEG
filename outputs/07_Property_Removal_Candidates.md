# Property Removal Candidates
## Critical Evaluation of Energy* Schema Properties

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document provides a critical evaluation of all properties in the Energy* schemas to identify candidates for removal. Properties are evaluated based on:
1. **Immediate necessity**: Is it needed for core use cases?
2. **Use case coverage**: Does it support multiple use cases or just one?
3. **Derivability**: Can it be calculated from other properties?
4. **Redundancy**: Is it duplicated elsewhere in the schema?

---

## Evaluation Criteria

### Keep (Essential)
- Used in multiple use cases
- Cannot be derived from other properties
- Core to energy coordination

### Candidate for Removal
- **Single-use**: Only supports one narrow use case
- **Derivable**: Can be calculated from other properties
- **Redundant**: Duplicated in multiple places
- **Over-engineered**: More complex than needed
- **Not immediately needed**: Future-proofing that can be added later

---

## 1. EnergyResource Properties

### ✅ KEEP (Essential)

| Property | Reason |
|----------|--------|
| `sourceType` | Used in discovery/filtering across multiple use cases |
| `deliveryMode` | Used in discovery/filtering across multiple use cases |
| `meterId` | Essential for tracking and fulfillment across all use cases |
| `productionWindow` | Essential for time-based availability (all use cases) |
| `bidCurve` | **Core** to market clearing (EV demand flexibility, P2P market, VPP) |
| `constraints` | **Core** to bid curve execution (min/max power, ramp rate) |
| `objectives` | **Core** to objective-driven coordination (EV demand flexibility, demand flexibility) |

### ❌ CANDIDATE FOR REMOVAL

| Property | Reason | Alternative |
|----------|--------|-------------|
| **`certificationStatus`** | **Single-use**: Only for green energy certification use case. Not needed for core coordination. | Move to credentials/onboarding, or use `sourceVerification` |
| **`inverterId`** | **Single-use**: Only for P2P trading with inverters. Not needed for EV charging, demand flexibility, VPP. | Can be derived from `meterId` or moved to provider-level metadata |
| **`availableQuantity`** | **Derivable**: Can be derived from `bidCurve` (max powerKW × time) or `productionWindow`. Redundant. | Use `bidCurve` or `productionWindow` |
| **`sourceVerification`** | **Single-use**: Only for certification/verification use case. Not needed for core coordination. | Move to credentials/onboarding layer |
| **`productionAsynchronous`** | **Single-use**: Only for specific P2P trading scenarios where production happens before/after trade. Not needed for real-time coordination. | Can be handled via `productionWindow` timing |
| **`locationalPriceAdder`** | **Single-use**: Only for grid nodes (transformers/substations). Not needed for most resources. | Move to separate `GridNode` schema or make optional |
| **`gridConstraints`** | **Single-use**: Only for grid nodes. Not needed for most resources. | Move to separate `GridNode` schema or make optional |

**Recommendation**: Remove `certificationStatus`, `inverterId`, `availableQuantity`, `sourceVerification`, `productionAsynchronous`. Make `locationalPriceAdder` and `gridConstraints` optional or move to separate schema.

---

## 2. EnergyTradeOffer Properties

### ✅ KEEP (Essential)

| Property | Reason |
|----------|--------|
| `pricingModel` | Essential for all pricing scenarios |
| `settlementType` | Essential for all settlement scenarios |
| `validityWindow` | Essential for time-based offers |
| `bidCurve` | **Core** to market clearing |
| `constraints` | **Core** to bid curve execution |
| `clearingPrice` | **Core** to market clearing (set after aggregation) |
| `setpointKW` | **Core** to market clearing (optimal setpoint) |

### ❌ CANDIDATE FOR REMOVAL

| Property | Reason | Alternative |
|----------|--------|-------------|
| **`wheelingCharges`** | **Single-use**: Only for P2P trading with utilities. Not needed for EV charging, demand flexibility, VPP. | Move to `orderAttributes` (settlement) or make optional |
| **`minimumQuantity`** | **Derivable**: Can be derived from `bidCurve` (min powerKW) or `constraints.minPowerKW`. Redundant. | Use `bidCurve` or `constraints` |
| **`maximumQuantity`** | **Derivable**: Can be derived from `bidCurve` (max powerKW) or `constraints.maxPowerKW`. Redundant. | Use `bidCurve` or `constraints` |
| **`timeOfDayRates`** | **Single-use**: Only for `TIME_OF_DAY` pricing model. Not needed for market clearing, demand flexibility. | Can be expressed via `bidCurve` with time windows, or make conditional on `pricingModel` |
| **`locationalPriceAdder`** | **Single-use**: Only for grid nodes. Not needed for most offers. | Move to separate schema or make optional |
| **`locationalPrice`** | **Derivable**: Can be calculated as `clearingPrice + locationalPriceAdder.currentPrice`. Redundant. | Calculate on-the-fly |

**Recommendation**: Remove `minimumQuantity`, `maximumQuantity`, `locationalPrice`. Make `wheelingCharges`, `timeOfDayRates`, `locationalPriceAdder` optional or conditional.

---

## 3. EnergyTradeContract Properties

### ✅ KEEP (Essential)

| Property | Reason |
|----------|--------|
| `contractStatus` | Essential for contract lifecycle |
| `sourceMeterId` | Essential for tracking |
| `targetMeterId` | Essential for tracking |
| `contractedQuantity` | Essential for contract terms |
| `tradeStartTime` / `tradeEndTime` | Essential for contract timing |
| `settlementCycles` | Essential for recurring contracts |
| `billingCycles` | Essential for billing |
| `bidCurve` | **Core** to market clearing (submitted during init) |
| `objectives` | **Core** to objective-driven coordination |
| `approvedMaxTradeKW` | **Core** to utility approval (demand flexibility) |
| `clearingPrice` | **Core** to market clearing (locked at confirmation) |
| `setpointKW` | **Core** to market clearing (confirmed setpoint) |
| `settlement` | **Core** to multi-party settlement |

### ❌ CANDIDATE FOR REMOVAL

| Property | Reason | Alternative |
|----------|--------|-------------|
| **`inverterId`** | **Single-use**: Only for P2P trading with inverters. Not needed for EV charging, demand flexibility, VPP. | Can be derived from `sourceMeterId` or moved to resource metadata |
| **`sourceType`** | **Redundant**: Already in `EnergyResource.itemAttributes`. Not needed at contract time. | Reference resource via `sourceMeterId` |
| **`certification`** | **Single-use**: Only for green energy certification. Not needed for core coordination. | Move to credentials/onboarding, or reference from resource |
| **`wheelingCharges`** | **Redundant**: Already in `settlement.revenueFlows` or `billingCycles.lineItems`. Duplicated. | Use `settlement` structure |
| **`lastUpdated`** | **Derivable**: Can be derived from `contractStatus` transitions or order updates. Redundant with Beckn core. | Use Beckn core `orderStatus` and timestamps |
| **`locationalPrice`** | **Derivable**: Can be calculated as `clearingPrice + locationalPriceAdder.currentPrice`. Redundant. | Calculate on-the-fly |
| **`offsetCommand`** | **Single-use**: Only for grid nodes breaking flat bid curve plateaus. Not needed for most contracts. | Move to `fulfillmentAttributes` or make optional |

**Recommendation**: Remove `inverterId`, `sourceType`, `certification`, `wheelingCharges`, `lastUpdated`, `locationalPrice`. Make `offsetCommand` optional or move to fulfillment.

---

## 4. EnergyTradeDelivery Properties

### ✅ KEEP (Essential)

| Property | Reason |
|----------|--------|
| `deliveryStatus` | Essential for fulfillment tracking |
| `deliveryMode` | Essential for fulfillment mode |
| `deliveredQuantity` | Essential for fulfillment tracking |
| `deliveryStartTime` / `deliveryEndTime` | Essential for fulfillment timing |
| `meterReadings` | Essential for energy flow tracking |
| `telemetry` | Essential for real-time monitoring |
| `settlementCycleId` | Essential for linking to settlement |

### ❌ CANDIDATE FOR REMOVAL

| Property | Reason | Alternative |
|----------|--------|-------------|
| **`lastUpdated`** | **Derivable**: Can be derived from `meterReadings` timestamps or Beckn core fulfillment updates. Redundant. | Use Beckn core fulfillment timestamps |
| **`offsetCommand`** | **Single-use**: Only for grid nodes. Not needed for most deliveries. | Move to separate grid services schema or make optional |
| **`deviationPenalty`** | **Single-use**: Only for market clearing agent with virtual meter. Not needed for most deliveries. | Move to settlement or make optional |

**Recommendation**: Remove `lastUpdated`. Make `offsetCommand` and `deviationPenalty` optional or move to separate schemas.

---

## 5. EnergyCoordination (Shared) Properties

### ✅ KEEP (Essential)

| Property | Reason |
|----------|--------|
| `BidCurvePoint` (price, powerKW) | **Core** to market clearing |
| `BidCurveConstraints` (minPowerKW, maxPowerKW, rampRateKWPerMin) | **Core** to bid curve execution |
| `EnergyObjectives` (targetChargeKWh, targetGenerationKWh, targetReductionKW, deadline, maxPricePerKWh) | **Core** to objective-driven coordination |
| `Settlement` (revenueFlows, settlementReport) | **Core** to multi-party settlement |
| `Party` (era, role) | **Core** to settlement |

### ❌ CANDIDATE FOR REMOVAL

| Property | Reason | Alternative |
|----------|--------|-------------|
| **`EnergyObjectives.minPricePerKWh`** | **Single-use**: Only for generators. Not needed for consumers, demand flexibility. | Can be expressed via `bidCurve` (first point) |
| **`EnergyObjectives.preferredSource`** | **Single-use**: Only for consumer preferences. Not needed for generators, grid services. | Can be expressed via discovery filters |
| **`EnergyObjectives.objectiveConstraints`** | **Redundant**: Overlaps with `BidCurveConstraints`. More complex than needed. | Use `BidCurveConstraints` |
| **`ObjectiveConstraints`** (all properties) | **Redundant**: Overlaps with `BidCurveConstraints`. Duplicated logic. | Use `BidCurveConstraints` |
| **`LocationalPriceAdder`** (entire schema) | **Single-use**: Only for grid nodes. Not needed for most resources. | Move to separate `GridNode` schema |
| **`GridConstraints`** (entire schema) | **Single-use**: Only for grid nodes. Not needed for most resources. | Move to separate `GridNode` schema |
| **`LocationalPriceAdder.formula`** | **Derivable**: Human-readable formula is redundant. Can be calculated. | Remove, calculate on-the-fly |
| **`LocationalPriceAdder.congestionMultiplier`** | **Over-engineered**: Typically 1.0. Not needed for simple cases. | Make optional, default to 1.0 |
| **`Settlement.settlementCycles`** | **Redundant**: Already in `EnergyTradeContract.settlementCycles`. Duplicated. | Reference from contract |
| **`SettlementReport.breakdown`** | **Derivable**: Can be calculated from `revenueFlows`. Redundant. | Calculate on-the-fly |
| **`OffsetCommand.enabled`** | **Over-engineered**: If `offsetKW` is present, command is enabled. Redundant. | Use `offsetKW` presence |

**Recommendation**: Remove `minPricePerKWh`, `preferredSource`, `objectiveConstraints`, `ObjectiveConstraints`, `formula`, `congestionMultiplier`, `settlementCycles` (from Settlement), `breakdown`, `enabled`. Move `LocationalPriceAdder` and `GridConstraints` to separate `GridNode` schema.

---

## 6. Summary of Removal Candidates

### High Priority (Remove Immediately)

1. **`EnergyResource.availableQuantity`** - Derivable from bid curve
2. **`EnergyResource.sourceVerification`** - Single-use, move to credentials
3. **`EnergyResource.productionAsynchronous`** - Single-use, handle via timing
4. **`EnergyTradeOffer.minimumQuantity`** - Derivable from bid curve
5. **`EnergyTradeOffer.maximumQuantity`** - Derivable from bid curve
6. **`EnergyTradeOffer.locationalPrice`** - Derivable
7. **`EnergyTradeContract.sourceType`** - Redundant with resource
8. **`EnergyTradeContract.certification`** - Single-use, move to credentials
9. **`EnergyTradeContract.wheelingCharges`** - Redundant with settlement
10. **`EnergyTradeContract.lastUpdated`** - Derivable from Beckn core
11. **`EnergyTradeContract.locationalPrice`** - Derivable
12. **`EnergyTradeDelivery.lastUpdated`** - Derivable from Beckn core
13. **`EnergyObjectives.objectiveConstraints`** - Redundant with BidCurveConstraints
14. **`ObjectiveConstraints`** (entire schema) - Redundant
15. **`LocationalPriceAdder.formula`** - Derivable
16. **`LocationalPriceAdder.congestionMultiplier`** - Over-engineered
17. **`Settlement.settlementCycles`** - Redundant with contract
18. **`SettlementReport.breakdown`** - Derivable
19. **`OffsetCommand.enabled`** - Redundant

### Medium Priority (Make Optional or Conditional)

1. **`EnergyResource.certificationStatus`** - Single-use, make optional
2. **`EnergyResource.inverterId`** - Single-use, make optional
3. **`EnergyResource.locationalPriceAdder`** - Single-use, move to GridNode
4. **`EnergyResource.gridConstraints`** - Single-use, move to GridNode
5. **`EnergyTradeOffer.wheelingCharges`** - Single-use, make optional
6. **`EnergyTradeOffer.timeOfDayRates`** - Single-use, make conditional
7. **`EnergyTradeOffer.locationalPriceAdder`** - Single-use, move to GridNode
8. **`EnergyTradeContract.inverterId`** - Single-use, make optional
9. **`EnergyTradeContract.offsetCommand`** - Single-use, move to fulfillment
10. **`EnergyTradeDelivery.offsetCommand`** - Single-use, make optional
11. **`EnergyTradeDelivery.deviationPenalty`** - Single-use, make optional
12. **`EnergyObjectives.minPricePerKWh`** - Single-use, make optional
13. **`EnergyObjectives.preferredSource`** - Single-use, make optional
14. **`LocationalPriceAdder`** (entire schema) - Move to GridNode
15. **`GridConstraints`** (entire schema) - Move to GridNode

### Low Priority (Keep but Document as Optional)

1. **`EnergyResource.certificationStatus`** - Keep for green energy use cases
2. **`EnergyTradeOffer.timeOfDayRates`** - Keep for TIME_OF_DAY pricing model
3. **`EnergyTradeContract.certification`** - Keep for green energy use cases

---

## 7. Recommended Actions

### Phase 1: Remove High Priority Candidates (19 properties)

Remove all derivable and redundant properties immediately. This simplifies the schema without losing functionality.

### Phase 2: Refactor Single-Use Properties (15 properties)

1. **Create `GridNode` schema**: Move `LocationalPriceAdder` and `GridConstraints` to separate schema
2. **Make optional**: Add `optional: true` to single-use properties
3. **Move to credentials**: Move certification/verification properties to credentials layer
4. **Move to fulfillment**: Move `offsetCommand` to fulfillment attributes

### Phase 3: Consolidate Redundant Structures

1. **Remove `ObjectiveConstraints`**: Use `BidCurveConstraints` instead
2. **Remove `Settlement.settlementCycles`**: Reference from contract
3. **Remove `SettlementReport.breakdown`**: Calculate from `revenueFlows`

---

## 8. Impact Analysis

### Use Cases Affected

| Use Case | Impact | Mitigation |
|----------|--------|------------|
| **EV Charging (Basic)** | ✅ None | No changes needed |
| **EV Charging (Demand Flexibility)** | ⚠️ Minor | Remove `availableQuantity`, use `bidCurve` |
| **P2P Trading (Basic)** | ⚠️ Minor | Remove `inverterId`, `certification`, use resource reference |
| **P2P Trading (Market-Based)** | ⚠️ Minor | Remove `availableQuantity`, use `bidCurve` |
| **Demand Flexibility** | ✅ None | No changes needed |
| **VPP Coordination** | ✅ None | No changes needed |
| **Grid Services** | ⚠️ Medium | Move `LocationalPriceAdder` and `GridConstraints` to `GridNode` schema |

### Breaking Changes

- **Removing `availableQuantity`**: Clients must derive from `bidCurve` or `productionWindow`
- **Removing `inverterId`**: Clients must use `meterId` or resource metadata
- **Moving grid properties**: Grid nodes must use separate `GridNode` schema

---

## 9. Final Recommendation

**Remove 19 high-priority properties immediately**. This reduces schema complexity by ~30% without losing core functionality.

**Refactor 15 medium-priority properties** to be optional or moved to separate schemas. This maintains backward compatibility while simplifying the core schema.

**Result**: A simpler, more focused schema that supports all core use cases while removing unnecessary complexity.

---

**Status**: ✅ COMPLETED  
**Implementation Date**: December 2024

## 10. Implementation Summary

### Properties Removed
- ✅ `EnergyResource.availableQuantity` - Removed (derivable from bid curve)
- ✅ `EnergyResource.sourceVerification` - Moved to EnergyCredentials schema (W3C VC)
- ✅ `EnergyResource.productionAsynchronous` - Removed (handle via timing)
- ✅ `EnergyResource.locationalPriceAdder` - Moved to GridNode schema
- ✅ `EnergyResource.gridConstraints` - Moved to GridNode schema
- ✅ `EnergyTradeOffer.locationalPriceAdder` - Removed (moved to GridNode)
- ✅ `EnergyTradeOffer.locationalPrice` - Removed (derivable)
- ✅ `EnergyTradeContract.sourceType` - Removed (redundant with resource)
- ✅ `EnergyTradeContract.certification` - Moved to EnergyCredentials schema (W3C VC)
- ✅ `EnergyTradeContract.wheelingCharges` - Removed (redundant with settlement)
- ✅ `EnergyTradeContract.lastUpdated` - Removed (derivable from Beckn core)
- ✅ `EnergyTradeContract.locationalPrice` - Removed (derivable)
- ✅ `EnergyTradeDelivery.lastUpdated` - Removed (derivable from Beckn core)
- ✅ `EnergyObjectives.objectiveConstraints` - Removed (redundant with BidCurveConstraints)
- ✅ `ObjectiveConstraints` (entire schema) - Removed (redundant)
- ✅ `Settlement.settlementCycles` - Removed (reference from contract)
- ✅ `SettlementReport.breakdown` - Removed (derivable from revenueFlows)
- ✅ `LocationalPriceAdder.formula` - Removed (derivable)
- ✅ `LocationalPriceAdder.congestionMultiplier` - Made optional (defaults to 1.0)
- ✅ `OffsetCommand.enabled` - Removed (redundant, use offsetKW presence)

### Properties Kept (as requested)
- ✅ `EnergyTradeOffer.minimumQuantity` - Kept (can change in real-time)
- ✅ `EnergyTradeOffer.maximumQuantity` - Kept (can change in real-time)

### New Schemas Created
- ✅ `GridNode/v1/attributes.yaml` - Created for grid node-specific properties (LocationalPriceAdder, GridConstraints)
- ✅ `EnergyCredentials/v1/attributes.yaml` - Created for W3C Verifiable Credentials integration (replaces sourceVerification, certification)

### Files Updated
- ✅ All schema YAML files
- ✅ All example JSON files
- ✅ All documentation markdown files

