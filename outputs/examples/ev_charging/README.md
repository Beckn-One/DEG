# EV Charging Examples - EnergyContractEVCharging Pattern

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This directory contains complete JSON message examples for EV charging use cases using the new `EnergyContractEVCharging` pattern. These examples demonstrate how the refactored contract-based architecture works in practice, with computational contracts that define roles, revenue flows, and quality metrics.

---

## Directory Structure

```
ev_charging/
├── README.md
├── 01_discover/
│   └── discovery-within-a-circular-boundary.json
├── 02_on_discover/
│   └── time-based-ev-charging-slot-catalog.json
├── 03_select/
│   └── time-based-ev-charging-slot-select.json
├── 04_on_select/
│   └── time-based-ev-charging-slot-on-select.json
├── 05_init/
│   └── time-based-ev-charging-slot-init.json
├── 06_on_init/
│   └── time-based-ev-charging-slot-on-init.json
├── 07_confirm/
│   └── time-based-ev-charging-slot-confirm.json
├── 08_on_confirm/
│   └── time-based-ev-charging-slot-on-confirm.json
├── 09_update/
│   └── ev-charging-session-start-update.json
├── 10_on_update/
│   └── time-based-ev-charging-slot-on-update.json
├── 11_track/
│   └── time-based-ev-charging-slot-track.json
└── 12_on_track/
    └── time-based-ev-charging-slot-on-track.json
```

---

## Key Features

### 1. EnergyContractEVCharging Pattern

All examples use `EnergyContractEVCharging` in `orderAttributes` (and `offerAttributes` in discovery). This specialized contract:

- **Inherits from** `EnergyContract` (core abstract schema)
- **Defines SELLER roleInputs**: `pricePerKWh`, `currency`, `connectorType`, `maxPowerKW`, `minPowerKW`, `location` (required) + `buyerFinderFee`, `idleFeePolicy`, `discountPercentage` (optional)
- **Defines BUYER roleInputs**: `sessionPreferences`, `vehicleMake`, `vehicleModel` (optional)
- **Status transitions**: `PENDING` (in init/select) → `ACTIVE` (in on_confirm and after)

### 2. Simple roleInputs Format

All examples use direct values in `roleInputs` (not full `RoleInput` objects):

```json
"roleInputs": {
  "pricePerKWh": 18.0,
  "currency": "INR",
  "connectorType": "CCS2",
  "maxPowerKW": 60,
  "minPowerKW": 5,
  "location": { ... }
}
```

This makes examples cleaner and easier to read, while the schema still supports both formats (direct values OR full `RoleInput` objects with schema metadata).

### 3. Computational Contracts

Contracts define revenue flows as formulas:

```json
"revenueFlows": {
  "flows": [
    {
      "from": "BUYER",
      "to": "SELLER",
      "formula": "roles.SELLER.roleInputs.pricePerKWh × telemetrySources.cdr-ev-charger-ccs2-001.energyKWh",
      "description": "BUYER pays SELLER based on energy consumed (from CDR) × price provided by SELLER"
    }
  ],
  "netZero": true
}
```

### 4. Field Mapping

All functional fields from original examples have been mapped:

- **Item attributes** (socketCount, amenityFeature, ocppId, etc.) → Remain in `itemAttributes` as `EnergyResource`
- **Contract fields** → Mapped to `EnergyContractEVCharging`:
  - SELLER roleInputs: pricing, connector, power, location, fees
  - BUYER roleInputs: session preferences, vehicle info
  - inputParameters: validityWindow, gracePeriodMinutes, authorizationMode
  - telemetrySources: CDR source for billing
- **Session data** → In `fulfillment.deliveryAttributes` (ChargingSession schema)

---

## Example Flow

### Discovery & Selection
1. **discover** - Spatial search for charging stations
2. **on_discover** - Catalog with `EnergyOffer` containing `EnergyContractEVCharging` in `offerAttributes` (status: PENDING)
3. **select** - Select offer, contract in `orderAttributes` (status: PENDING)
4. **on_select** - Selection confirmed (status: PENDING)

### Init & Confirm
5. **init** - Initialize order with BUYER roleInputs (sessionPreferences, vehicleMake, vehicleModel) (status: PENDING)
6. **on_init** - Init confirmed (status: PENDING)
7. **confirm** - Final confirmation request (status: PENDING)
8. **on_confirm** - Contract activated (status: ACTIVE) ⭐

### Session Management
9. **update** - Session lifecycle updates (status: ACTIVE)
10. **on_update** - Updates acknowledged (status: ACTIVE)
11. **track** - Request real-time session data
12. **on_track** - Live telemetry data (status: ACTIVE)

---

## Contract Status Lifecycle

```
PENDING → ACTIVE → COMPLETED/TERMINATED
  ↑         ↑
init/    on_confirm
select   (and after)
```

- **PENDING**: Contract defined, roles filled, awaiting confirmation
- **ACTIVE**: Contract confirmed, session in progress
- **COMPLETED**: Session finished, billing computed
- **TERMINATED**: Contract cancelled/aborted

---

## Schema References

- **EnergyContractEVCharging**: `outputs/schema/EnergyContractEVCharging/v1/attributes.yaml`
- **EnergyContract** (base): `outputs/schema/EnergyContract/v1/attributes.yaml`
- **EnergyOffer**: `outputs/schema/EnergyOffer/v1/attributes.yaml`
- **EnergyResource**: `outputs/schema/EnergyResource/v0.2/attributes.yaml`

---

## JSON-LD Composition

All examples use proper JSON-LD composition:

- `@context`: Points to schema context files
- `@type`: Specifies the schema type (e.g., `EnergyContractEVCharging`)
- Attribute slots: `offerAttributes`, `orderAttributes`, `itemAttributes`, `deliveryAttributes`

---

## Migration from Original Examples

These examples replace the original `ChargingSession` and `ChargingOffer` schemas in `orderAttributes` with the new `EnergyContractEVCharging` pattern. Key differences:

1. **Contract-based**: All contract terms in `EnergyContractEVCharging` structure
2. **Role-based inputs**: SELLER and BUYER provide inputs via `roleInputs`
3. **Computational billing**: Revenue flows defined as formulas
4. **Telemetry-driven**: Billing computed from telemetry sources (CDR)

---

**Status**: Complete ✅

