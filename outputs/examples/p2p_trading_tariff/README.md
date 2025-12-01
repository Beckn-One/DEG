# P2P Trading Tariff Examples - EnergyContractP2PTrade Pattern

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This directory contains JSON message examples for **tariff-based P2P energy trading** use cases using the `EnergyContractP2PTrade` pattern with `SELLER` and `BUYER` roles, where the SELLER provides a **full tariff object** instead of a simple `pricePerKWh`. This enables time-of-use pricing, tiered rates, and utility-style complex tariffs.

**Note**: This is a variant of fixed price mode, using `tariff` object instead of `pricePerKWh`. For simple fixed price, see `../p2p_trading/`. For market-based trading, see `../p2p_trading_market_based/`.

---

## Key Features

### 1. Tariff-Based Pricing

All examples use `EnergyContractP2PTrade` in **tariff-based fixed price mode** with:

- **SELLER role**: Provides `tariff` object (instead of `pricePerKWh`)
- **BUYER role**: Provides `contractedQuantity`, `tradeStartTime`, `tradeEndTime`
- **Tariff structure**: Based on OCPI standard, supports time-of-use, tiered pricing
- **Status transitions**: `PENDING` (in init) → `ACTIVE` (in on_confirm) → `COMPLETED` (in on_status)

### 2. Tariff Object Structure

The `tariff` object in SELLER roleInputs includes:

```json
{
  "tariff": {
    "tariffId": "TOU-2024-001",
    "currency": "INR",
    "type": "REGULAR",
    "elements": [
      {
        "priceComponents": [
          {
            "type": "ENERGY",
            "price": 0.20,
            "vat": 18.0,
            "stepSize": 1
          }
        ],
        "restrictions": {
          "startTime": "18:00",
          "endTime": "22:00",
          "dayOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        }
      }
    ],
    "energyMix": {
      "isGreenEnergy": false,
      "energySources": [
        { "source": "COAL", "percentage": 60.0 },
        { "source": "SOLAR", "percentage": 40.0 }
      ]
    }
  }
}
```

**Key Components**:
- **elements**: Array of tariff elements, each with price components and time restrictions
- **priceComponents**: Type (ENERGY, TIME, FLAT), price, VAT, step_size
- **restrictions**: Time-of-day, day-of-week, tier limits (minKWh, maxKWh)
- **energyMix**: Optional energy source information

### 3. Time-of-Use Example

The examples demonstrate a **time-of-use tariff** with three periods:

- **Peak hours** (18:00 - 22:00, weekdays): ₹0.20/kWh
- **Off-peak hours** (22:00 - 06:00): ₹0.10/kWh
- **Mid-peak hours** (06:00 - 18:00): ₹0.15/kWh

### 4. Revenue Flow Computation

For tariff-based pricing, revenue flows compute price from tariff:

```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity"
}
```

**Tariff Computation Algorithm**:
1. Determine applicable tariff elements based on `tradeStartTime`, `tradeEndTime`, and time restrictions
2. For each time period, calculate energy delivered during that period
3. Apply price from matching tariff element's price component
4. Sum across all periods to get total cost

---

## Directory Structure

```
p2p_trading_tariff/
├── README.md
├── 01_discover/
│   └── discover-utility-tariff.json
├── 02_on_discover/
│   └── utility-tariff-catalog.json
├── 03_select/
│   └── (to be created)
├── 04_on_select/
│   └── (to be created)
├── 05_init/
│   └── init-tariff-trade.json
├── 06_on_init/
│   └── (to be created)
├── 07_confirm/
│   └── (to be created)
├── 08_on_confirm/
│   └── on-confirm-tariff-trade.json
├── 09_status/
│   └── (to be created)
└── 10_on_status/
    └── (to be created)
```

---

## Example Flow

### Discovery & Init
1. **discover** - Consumer searches for utility tariff-based trading
2. **on_discover** - Utility responds with `EnergyOffer` containing `EnergyContractP2PTrade` with SELLER role filled (tariff object)
3. **init** - Consumer submits BUYER roleInputs (targetMeterId, contractedQuantity, tradeStartTime, tradeEndTime)
4. **on_init** - Utility confirms trade terms

### Confirm & Settlement
5. **confirm** - Consumer commits to trade
6. **on_confirm** - Contract becomes ACTIVE, tariff structure locked
7. **status** - Request trade status
8. **on_status** - Trade in progress with delivery telemetry, tariff computation based on actual delivery times

---

## Comparison: Pricing Modes

| Aspect | Simple Fixed Price | Tariff-Based | Market-Based |
|-------|-------------------|--------------|--------------|
| **SELLER roleInputs** | `pricePerKWh` + `currency` | `tariff` object | N/A (use PROSUMER) |
| **Pricing Structure** | Single price | Time-of-use, tiered | Pay-as-clear |
| **Price Discovery** | Known upfront | Known upfront (tariff) | Discovered at confirmation |
| **Use Case** | Simple P2P trade | Utility-to-consumer | Market coordination |
| **Revenue Formula** | `contractedQuantity × pricePerKWh` | `computeTariffPrice(...) × deliveredQuantity` | `(clearingPrice + fee) × clearedPower` |

---

## Tariff Computation

The `computeTariffPrice` function computes price from tariff based on:

1. **Time Windows**: Match delivery time windows to tariff element restrictions
2. **Energy Allocation**: Distribute `deliveredQuantity` across time periods
3. **Price Application**: Apply price from matching tariff element's price component
4. **VAT Calculation**: Apply VAT if specified in price component

**Example Calculation**:
- Trade: 100 kWh from 18:00 to 06:00 (next day)
- Tariff: Peak (18:00-22:00) @ ₹0.20/kWh, Off-peak (22:00-06:00) @ ₹0.10/kWh
- Allocation: 40 kWh peak + 60 kWh off-peak
- Cost: (40 × 0.20) + (60 × 0.10) = ₹8.00 + ₹6.00 = ₹14.00

---

## Schema References

- **EnergyContractP2PTrade**: `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml`
- **Tariff**: `outputs/schema/EnergyCoordination/v1/attributes.yaml#/components/schemas/Tariff`
- **TariffElement**: `outputs/schema/EnergyCoordination/v1/attributes.yaml#/components/schemas/TariffElement`
- **TariffPriceComponent**: `outputs/schema/EnergyCoordination/v1/attributes.yaml#/components/schemas/TariffPriceComponent`

---

## Standards Alignment

The tariff structure is based on **OCPI (Open Charge Point Interface)** standard:
- `elements` array with `price_components` and `restrictions`
- `energy_mix` for renewable energy information
- Time-of-use support via `restrictions.startTime` and `restrictions.endTime`
- Tiered pricing via `restrictions.minKWh` and `restrictions.maxKWh`

---

## Important Notes

### Mutual Exclusivity

- `pricePerKWh` and `tariff` are **mutually exclusive** in SELLER roleInputs
- Use `pricePerKWh` for simple fixed price
- Use `tariff` for complex pricing (time-of-use, tiered, utility tariffs)

### Tariff Validation

- `tariff.elements` MUST have at least one element
- Each element MUST have at least one `priceComponents` with `type: ENERGY`
- If `restrictions.startTime` provided, `restrictions.endTime` MUST also be provided
- `tariff.currency` MUST match contract currency (if specified)

### Revenue Flow Computation

- Tariff computation requires `deliveredQuantity` (from telemetry)
- Computation happens at settlement time, not at contract confirmation
- Formula references `deliveredQuantity` which is available after fulfillment

---

**Status**: Examples created ✅

