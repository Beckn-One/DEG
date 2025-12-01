# EnergyContractP2PTrade - Tariff Extension Implementation Summary

**Version:** 1.0  
**Date:** December 2024

---

## ✅ Implementation Complete

The `EnergyContractP2PTrade` schema has been successfully extended to support **tariff-based pricing** in addition to simple fixed price and market-based modes. The tariff structure is based on **OCPI (Open Charge Point Interface)** standard, enabling time-of-use pricing, tiered rates, and utility-style complex tariffs.

---

## 📁 Deliverables

### 1. Tariff Schemas ✅

**File**: `outputs/schema/EnergyCoordination/v1/attributes.yaml` (623 lines, +260 lines)

**New Schema Definitions**:
- `Tariff`: Main tariff object with elements, energy mix, pricing bounds
- `TariffElement`: Single tariff element with price components and restrictions
- `TariffPriceComponent`: Price component (ENERGY, TIME, FLAT, etc.) with VAT and step size

**Key Features**:
- Based on OCPI standard structure
- Supports time-of-use via `restrictions.startTime` and `restrictions.endTime`
- Supports tiered pricing via `restrictions.minKWh` and `restrictions.maxKWh`
- Optional `energyMix` for renewable energy information
- Multiple price components per element (ENERGY, TIME, FLAT, PARKING_TIME, AD_HOC_PAYMENT)

### 2. Contract Schema Extension ✅

**File**: `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml` (597 lines, +10 lines)

**Updates**:
- Extended `P2PTradeSellerRole.roleInputs` to include `tariff` option
- Updated description to clarify three pricing modes:
  1. Simple fixed price: `pricePerKWh` + `currency`
  2. Tariff-based: `tariff` object
  3. Market-based: `offerCurve` in PROSUMER role
- Added mutual exclusivity note: `pricePerKWh` and `tariff` cannot both be provided

### 3. Validation Rules ✅

**File**: `outputs/schema/EnergyContractP2PTrade/v1/VALIDATION_RULES.md` (updated)

**New Validation Rules**:
- Mutual exclusivity: `pricePerKWh` and `tariff` MUST NOT both be provided
- Tariff structure validation:
  - `tariff.elements` MUST have at least one element
  - Each element MUST have at least one `priceComponents` with `type: ENERGY`
  - If `restrictions.startTime` provided, `restrictions.endTime` MUST also be provided
  - `tariff.currency` MUST match contract currency (if specified)
- Revenue flow validation for tariff-based pricing
- Error messages for invalid tariff structures

### 4. Example Files ✅

**Directory**: `outputs/examples/p2p_trading_tariff/`

**Files Created** (4 files):
- `01_discover/` - discover-utility-tariff.json
- `02_on_discover/` - utility-tariff-catalog.json (with EnergyOffer + EnergyContractP2PTrade with tariff)
- `05_init/` - init-tariff-trade.json (SELLER with tariff object, BUYER with contractedQuantity)
- `08_on_confirm/` - on-confirm-tariff-trade.json (contract ACTIVE with tariff structure)

**Key Features**:
- Time-of-use tariff example with three periods:
  - Peak (18:00-22:00, weekdays): ₹0.20/kWh
  - Off-peak (22:00-06:00): ₹0.10/kWh
  - Mid-peak (06:00-18:00): ₹0.15/kWh
- Complete tariff structure with energy mix information
- Revenue flow formula using `computeTariffPrice` function

### 5. Documentation ✅

**Files Created/Updated**:
- `outputs/examples/p2p_trading_tariff/README.md` - Comprehensive guide for tariff-based examples
- `outputs/EnergyContractP2PTrade_Polymorphic_Design.md` - Updated to include tariff-based mode
- `outputs/EnergyContractP2PTrade_Tariff_Extension_Proposal.md` - Original proposal document

---

## 🔑 Key Design Decisions

### OCPI-Based Tariff Structure

The tariff structure is based on **OCPI (Open Charge Point Interface)** standard:
- `elements` array with `price_components` and `restrictions`
- `energy_mix` for renewable energy information
- Time-of-use support via `restrictions.startTime` and `restrictions.endTime`
- Tiered pricing via `restrictions.minKWh` and `restrictions.maxKWh`

**Benefits**:
- Widely adopted standard in EV charging industry
- Proven structure for complex pricing
- Interoperability with existing OCPI implementations

### Polymorphic Pricing Support

The SELLER role now supports **three pricing modes**:

1. **Simple Fixed Price**: `pricePerKWh` + `currency`
2. **Tariff-Based**: `tariff` object (mutually exclusive with `pricePerKWh`)
3. **Market-Based**: `offerCurve` in PROSUMER role

**Mutual Exclusivity**: `pricePerKWh` and `tariff` cannot both be provided in SELLER roleInputs.

### Revenue Flow Computation

For tariff-based pricing, revenue flows use a computation function:

```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity"
}
```

**Computation Algorithm**:
1. Match delivery time windows to tariff element restrictions
2. Distribute `deliveredQuantity` across time periods
3. Apply price from matching tariff element's price component
4. Sum across all periods to get total cost

---

## 📊 Statistics

- **Schema Lines Added**: +260 lines (EnergyCoordination), +10 lines (EnergyContractP2PTrade)
- **Tariff Examples**: 4 files created
- **Documentation Files**: 3 files created/updated
- **Validation Rules**: Comprehensive coverage added
- **Standards Alignment**: OCPI-based structure

---

## ✅ Validation

- **No linter errors**: All files validated
- **OpenAPI 3.1.1 compliant**: Schema validated
- **JSON-LD composition**: All examples use proper composition
- **Consistency**: Examples match schema definitions
- **Mutual exclusivity**: Validation rules enforce `pricePerKWh` vs `tariff` exclusivity

---

## 🎯 Use Cases Enabled

1. **Utility-to-Consumer Trades**: Time-of-use tariffs from utility companies
2. **Tiered Pricing**: Different rates for different consumption levels
3. **Demand Charges**: Time-based pricing for peak demand periods
4. **Renewable Energy Tariffs**: Tariffs with energy mix information
5. **Complex Pricing Structures**: Multiple price components (ENERGY, TIME, FLAT)

---

## 📚 Standards Alignment

- **OCPI**: Tariff structure based on OCPI `Tariff` object
- **IEEE 2030.5**: Compatible with IEEE pricing signals
- **OpenADR**: Compatible with OpenADR pricing structures

---

## 🔄 Backward Compatibility

- **Existing fixed price examples**: No changes needed, continue using `pricePerKWh`
- **New tariff-based examples**: Use `tariff` object instead of `pricePerKWh`
- **Schema evolution**: Polymorphic design allows all three modes in same schema

---

**Status**: ✅ Complete - All implementation steps completed successfully!

