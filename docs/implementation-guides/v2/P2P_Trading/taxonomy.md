# P2P Energy Trading Taxonomy Reference

## Overview

This document provides a comprehensive reference for all enumerations and taxonomies used in P2P Energy Trading schemas.

## Energy Source Types

**Schema**: `EnergyResource.sourceType`, `EnergyTradeContract.sourceType`

| Value | Description | Use Case |
|-------|-------------|----------|
| `SOLAR` | Solar photovoltaic energy | Solar panels, rooftop solar |
| `BATTERY` | Battery storage energy | Battery systems, energy storage |
| `GRID` | Grid-sourced energy | Traditional utility grid |
| `HYBRID` | Hybrid energy source | Combination of multiple sources |
| `RENEWABLE` | Renewable energy (unspecified) | General renewable energy category |

**Notes**:
- Source type influences pricing but not workflow
- Source verification occurs at onboarding but can change post-onboarding
- Example: Switching from solar to diesel backup

## Delivery Modes

**Schema**: `EnergyResource.deliveryMode`, `EnergyTradeDelivery.deliveryMode`

| Value | Description | Use Case |
|-------|-------------|----------|
| `EV_CHARGING` | Electric vehicle charging | Direct EV charging |
| `BATTERY_SWAP` | Battery swap service | Battery exchange stations |
| `V2G` | Vehicle-to-Grid | EVs feeding energy back to grid |
| `GRID_INJECTION` | Grid injection | Energy injected into utility grid |

**Notes**:
- Used as discovery filter to match consumer requirements
- Determines delivery mechanism for energy transfer

## Pricing Models

**Schema**: `EnergyTradeOffer.pricingModel`

| Value | Description | Use Case |
|-------|-------------|----------|
| `PER_KWH` | Per kilowatt-hour pricing | Standard energy pricing |
| `TIME_OF_DAY` | Time-of-day pricing | Variable rates by time period |
| `SUBSCRIPTION` | Subscription-based pricing | Fixed monthly/annual pricing |
| `FIXED` | Fixed price | Flat rate pricing |

**Notes**:
- `TIME_OF_DAY` requires `timeOfDayRates` array
- `PER_KWH` is most common for P2P energy trading

## Settlement Types

**Schema**: `EnergyTradeOffer.settlementType`

| Value | Description | Frequency | Use Case |
|-------|-------------|-----------|----------|
| `REAL_TIME` | Real-time settlement | Continuous | Instant payment processing |
| `HOURLY` | Hourly settlement | Every hour | High-frequency trading |
| `DAILY` | Daily settlement | Once per day | Standard P2P trading |
| `WEEKLY` | Weekly settlement | Once per week | Long-term contracts |
| `MONTHLY` | Monthly settlement | Once per month | Subscription-based trading |

**Notes**:
- Determines when payments are processed
- Default: `DAILY` (see profile.json)
- Settlement cycles tracked in `EnergyTradeContract.settlementCycles`

## Contract Status

**Schema**: `EnergyTradeContract.contractStatus`

| Value | Description | Lifecycle Stage |
|-------|-------------|-----------------|
| `PENDING` | Contract pending activation | After init, before confirm |
| `ACTIVE` | Contract is active | After confirm, during fulfillment |
| `COMPLETED` | Contract completed | After successful fulfillment |
| `TERMINATED` | Contract terminated | Cancelled or failed |

**Notes**:
- Decouples trade from fulfillment
- Generator, transmitter, and consumer operate independently
- Status progression: PENDING → ACTIVE → COMPLETED

## Delivery Status

**Schema**: `EnergyTradeDelivery.deliveryStatus`

| Value | Description | Stage |
|-------|-------------|-------|
| `PENDING` | Delivery pending | Before delivery starts |
| `IN_PROGRESS` | Delivery in progress | Active energy transfer |
| `COMPLETED` | Delivery completed | Successful completion |
| `FAILED` | Delivery failed | Failed or cancelled |

**Notes**:
- Handles recurring or continuous fulfillment scenarios
- Multiple deliveries can be tied to a single contract
- Status updates as meter readings arrive

## Settlement Cycle Status

**Schema**: `EnergyTradeContract.settlementCycles[].status`

| Value | Description | Stage |
|-------|-------------|-------|
| `PENDING` | Settlement pending | Awaiting settlement |
| `SETTLED` | Settlement completed | Payment processed |
| `FAILED` | Settlement failed | Payment processing failed |

**Notes**:
- Each settlement cycle tracks its own status
- Status updates when settlement is processed
- Failed settlements may be retried

## Billing Cycle Status

**Schema**: `EnergyTradeContract.billingCycles[].status`

| Value | Description | Stage |
|-------|-------------|-------|
| `PENDING` | Billing pending | Awaiting payment |
| `PAID` | Payment received | Payment completed |
| `OVERDUE` | Payment overdue | Payment past due date |

**Notes**:
- Supports ongoing connections billed periodically
- Multiple billing cycles per contract
- Status updates when payment is received

## Telemetry Metric Names

**Schema**: `EnergyTradeDelivery.telemetry[].metrics[].name`

| Value | Description | Unit Code | Use Case |
|-------|-------------|-----------|----------|
| `ENERGY` | Energy delivered | `KWH` | Total energy in kilowatt-hours |
| `POWER` | Power level | `KW` | Instantaneous power in kilowatts |
| `FLOW_RATE` | Energy flow rate | `KW` | Rate of energy transfer |
| `VOLTAGE` | Voltage level | `VLT` | Grid voltage in volts |
| `CURRENT` | Current level | `AMP` | Current in amperes |
| `FREQUENCY` | Frequency | `HZ` | Grid frequency in hertz |
| `POWER_QUALITY` | Power quality metric | dimensionless | Power quality indicator |

**Notes**:
- All metrics use `schema:QuantitativeValue` structure
- Unit codes must match metric type
- Update frequency: Every 5-15 minutes during active delivery

## Payment Types

**Schema**: Core `Payment.type` (not in Energy* schemas)

| Value | Description | Timing |
|-------|-------------|--------|
| `PRE-ORDER` | Payment before order | Before order confirmation |
| `ON-FULFILLMENT` | Payment during fulfillment | During energy delivery |
| `POST-FULFILLMENT` | Payment after fulfillment | After delivery completion |

**Notes**:
- Defined in core Payment schema
- Most common for energy trading: `ON-FULFILLMENT`

## Payment Status

**Schema**: Core `Payment.status` (not in Energy* schemas)

| Value | Description |
|-------|-------------|
| `PAID` | Payment received |
| `NOT-PAID` | Payment not yet received |

## Payment Collected By

**Schema**: Core `Payment.collected_by` (not in Energy* schemas)

| Value | Description |
|-------|-------------|
| `BAP` | Collected by Buyer App Platform |
| `BPP` | Collected by Provider Platform |

**Notes**:
- BPP collection is most common for energy trading
- BAP collection requires pre-payment

## Fulfillment Stop Types

**Schema**: Core `Stop.type` (not in Energy* schemas)

| Value | Description | Required Fields |
|-------|-------------|-----------------|
| `START` | Source location | `location.address` (source meter ID) |
| `END` | Target location | `location.address` (target meter ID) |

**Notes**:
- At least one END stop is required
- Meter IDs in `location.address` use IEEE mRID format
- START stop: Source meter (generator)
- END stop: Target meter (consumer)

## Certification Status Examples

**Schema**: `EnergyResource.certificationStatus` (free-form string)

Common values:
- `"Carbon Offset Certified"`
- `"Green Energy Certified"`
- `"Renewable Energy Certified"`
- `"ISO 14001 Certified"`

**Notes**:
- Free-form string (not an enum)
- Used for compliance and marketing
- Detailed certificates in `sourceVerification.certificates`

## Unit Codes

**Schema**: `EnergyTradeDelivery.telemetry[].metrics[].unitCode`

| Metric | Unit Code | Description |
|--------|-----------|-------------|
| `ENERGY` | `KWH` | Kilowatt-hours |
| `POWER` | `KW` | Kilowatts |
| `FLOW_RATE` | `KW` | Kilowatts |
| `VOLTAGE` | `VLT` | Volts |
| `CURRENT` | `AMP` | Amperes |
| `FREQUENCY` | `HZ` | Hertz |
| `POWER_QUALITY` | (dimensionless) | No unit |

## Summary Table

| Category | Enum Values | Schema Location |
|----------|-------------|----------------|
| Energy Source Types | SOLAR, BATTERY, GRID, HYBRID, RENEWABLE | `EnergyResource.sourceType`, `EnergyTradeContract.sourceType` |
| Delivery Modes | EV_CHARGING, BATTERY_SWAP, V2G, GRID_INJECTION | `EnergyResource.deliveryMode`, `EnergyTradeDelivery.deliveryMode` |
| Pricing Models | PER_KWH, TIME_OF_DAY, SUBSCRIPTION, FIXED | `EnergyTradeOffer.pricingModel` |
| Settlement Types | REAL_TIME, HOURLY, DAILY, WEEKLY, MONTHLY | `EnergyTradeOffer.settlementType` |
| Contract Status | PENDING, ACTIVE, COMPLETED, TERMINATED | `EnergyTradeContract.contractStatus` |
| Delivery Status | PENDING, IN_PROGRESS, COMPLETED, FAILED | `EnergyTradeDelivery.deliveryStatus` |
| Settlement Cycle Status | PENDING, SETTLED, FAILED | `EnergyTradeContract.settlementCycles[].status` |
| Billing Cycle Status | PENDING, PAID, OVERDUE | `EnergyTradeContract.billingCycles[].status` |
| Telemetry Metrics | ENERGY, POWER, FLOW_RATE, VOLTAGE, CURRENT, FREQUENCY, POWER_QUALITY | `EnergyTradeDelivery.telemetry[].metrics[].name` |

## Usage Guidelines

1. **Enum Values**: Always use uppercase with underscores (e.g., `SOLAR`, `GRID_INJECTION`)
2. **Case Sensitivity**: Enum values are case-sensitive
3. **Validation**: Validate enum values against this taxonomy
4. **Extensibility**: Do not add custom enum values; use free-form strings for extensions
5. **Documentation**: Document any custom values used in certification status or other free-form fields

