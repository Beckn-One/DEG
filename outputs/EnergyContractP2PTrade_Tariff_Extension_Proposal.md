# EnergyContractP2PTrade - Tariff Extension Proposal

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This proposal extends `EnergyContractP2PTrade` to support **full-fledged tariff objects** instead of just fixed `pricePerKWh`, enabling time-of-use pricing, tiered rates, and utility-style tariffs. The tariff structure is based on **OCPI (Open Charge Point Interface)** standard, with alignment to IEEE 2030.5 and OpenADR patterns.

---

## Motivation

**Current Limitation**: Fixed price mode only supports simple `pricePerKWh` (single number), which doesn't support:
- Time-of-use (TOU) pricing (peak/off-peak rates)
- Tiered pricing (different rates for different consumption levels)
- Demand charges
- Utility-style complex tariffs

**Use Case**: Buyer purchasing from utility company with time-of-day rates:
- Peak hours (6 PM - 10 PM): ₹0.20/kWh
- Off-peak hours (10 PM - 6 AM): ₹0.10/kWh
- Mid-peak hours (6 AM - 6 PM): ₹0.15/kWh

**Solution**: Extend SELLER roleInputs to accept either:
1. `pricePerKWh` (simple fixed price) - **existing**
2. `tariff` (full tariff object) - **new**
3. `offerCurve` (market-based) - **existing**

---

## OCPI Tariff Structure (Reference)

OCPI defines a comprehensive `Tariff` object:

```json
{
  "id": "TARIFF-001",
  "currency": "INR",
  "type": "REGULAR",
  "tariff_alt_text": [
    {
      "language": "en",
      "text": "Time-of-Use Tariff"
    }
  ],
  "tariff_alt_url": "https://example.com/tariff-details",
  "min_price": {
    "excl_vat": 0.10,
    "incl_vat": 0.10
  },
  "max_price": {
    "excl_vat": 0.20,
    "incl_vat": 0.20
  },
  "elements": [
    {
      "price_components": [
        {
          "type": "ENERGY",
          "price": 18.0,
          "vat": 0.0,
          "step_size": 1
        }
      ],
      "restrictions": {
        "start_time": "06:00",
        "end_time": "22:00",
        "day_of_week": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
        "reservation": "RESERVED"
      }
    },
    {
      "price_components": [
        {
          "type": "ENERGY",
          "price": 10.0,
          "vat": 0.0,
          "step_size": 1
        }
      ],
      "restrictions": {
        "start_time": "22:00",
        "end_time": "06:00",
        "day_of_week": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
      }
    }
  ],
  "energy_mix": {
    "is_green_energy": true,
    "energy_sources": [
      {
        "source": "SOLAR",
        "percentage": 100.0
      }
    ],
    "environ_impact": {
      "carbon_dioxide": 0.0
    },
    "supplier_name": "Green Energy Co",
    "energy_product_name": "100% Solar"
  }
}
```

**Key Components**:
- **elements**: Array of tariff elements, each with price components and restrictions
- **price_components**: Type (ENERGY, TIME, FLAT, PARKING_TIME), price, VAT, step_size
- **restrictions**: Time-of-day, day-of-week, reservation requirements
- **energy_mix**: Optional energy source information

---

## Proposed Schema Extension

### 1. New Tariff Schema

**File**: `outputs/schema/EnergyCoordination/v1/attributes.yaml` (add to shared schemas)

```yaml
Tariff:
  type: object
  description: >
    Comprehensive tariff structure based on OCPI standard.
    Supports time-of-use pricing, tiered rates, and utility-style tariffs.
    Can be used in SELLER roleInputs instead of pricePerKWh for fixed price mode.
  additionalProperties: false
  required: [currency, elements]
  properties:
    tariffId:
      type: string
      description: Unique tariff identifier (optional, for reference).
      example: "TARIFF-TOU-001"
      x-jsonld: { "@id": "schema:identifier" }

    currency:
      type: string
      description: Currency code (ISO 4217).
      example: "INR"
      x-jsonld: { "@id": "schema:currency" }

    type:
      type: string
      enum: [REGULAR, AD_HOC_PAYMENT, PROFILE_CHEAP, PROFILE_FAST, PROFILE_GREEN]
      description: >
        Tariff type (OCPI enum).
        REGULAR: Standard tariff
        AD_HOC_PAYMENT: One-time payment
        PROFILE_*: Profile-based tariffs
      default: "REGULAR"
      x-jsonld: { "@id": "ocpi:type" }

    tariffAltText:
      type: array
      description: Human-readable tariff description in multiple languages.
      items:
        type: object
        properties:
          language:
            type: string
            example: "en"
          text:
            type: string
            example: "Time-of-Use Tariff - Peak/Off-Peak"
      x-jsonld: { "@id": "ocpi:tariff_alt_text" }

    tariffAltUrl:
      type: string
      format: uri
      description: URL to detailed tariff information.
      example: "https://utility.com/tariffs/tou-001"
      x-jsonld: { "@id": "ocpi:tariff_alt_url" }

    minPrice:
      type: object
      description: Minimum price (excl/incl VAT).
      properties:
        exclVat:
          type: number
          minimum: 0
          description: Price excluding VAT.
        inclVat:
          type: number
          minimum: 0
          description: Price including VAT.
      x-jsonld: { "@id": "ocpi:min_price" }

    maxPrice:
      type: object
      description: Maximum price (excl/incl VAT).
      properties:
        exclVat:
          type: number
          minimum: 0
        inclVat:
          type: number
          minimum: 0
      x-jsonld: { "@id": "ocpi:max_price" }

    elements:
      type: array
      description: >
        Array of tariff elements, each defining price components and restrictions.
        Multiple elements allow time-of-use, tiered pricing, etc.
      items:
        $ref: '#/components/schemas/TariffElement'
      minItems: 1
      x-jsonld: { "@id": "ocpi:elements" }

    energyMix:
      type: object
      description: >
        Optional. Energy source information (OCPI EnergyMix).
        Specifies renewable energy percentage, carbon footprint, etc.
      properties:
        isGreenEnergy:
          type: boolean
          description: Whether energy is from renewable sources.
        energySources:
          type: array
          items:
            type: object
            properties:
              source:
                type: string
                enum: [SOLAR, WIND, HYDRO, NUCLEAR, COAL, GAS, OTHER]
              percentage:
                type: number
                minimum: 0
                maximum: 100
        environImpact:
          type: object
          properties:
            carbonDioxide:
              type: number
              description: CO2 emissions in g/kWh.
        supplierName:
          type: string
        energyProductName:
          type: string
      x-jsonld: { "@id": "ocpi:energy_mix" }

TariffElement:
  type: object
  description: >
    A single tariff element with price components and restrictions.
    Multiple elements enable time-of-use, tiered pricing, etc.
  additionalProperties: false
  required: [priceComponents]
  properties:
    priceComponents:
      type: array
      description: Array of price components (ENERGY, TIME, FLAT, etc.).
      items:
        $ref: '#/components/schemas/TariffPriceComponent'
      minItems: 1
      x-jsonld: { "@id": "ocpi:price_components" }

    restrictions:
      type: object
      description: >
        Optional. Restrictions on when this tariff element applies.
        Enables time-of-use, day-of-week, reservation requirements, etc.
      properties:
        startTime:
          type: string
          pattern: '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
          description: Start time (HH:MM format, 24-hour).
          example: "06:00"
        endTime:
          type: string
          pattern: '^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
          description: End time (HH:MM format, 24-hour).
          example: "22:00"
        dayOfWeek:
          type: array
          items:
            type: string
            enum: [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]
          description: Days of week when this element applies.
        minKWh:
          type: number
          minimum: 0
          description: Minimum energy (kWh) for this tier to apply.
        maxKWh:
          type: number
          minimum: 0
          description: Maximum energy (kWh) for this tier to apply.
        reservation:
          type: string
          enum: [RESERVED, NOT_RESERVED]
          description: Whether reservation is required.
      x-jsonld: { "@id": "ocpi:restrictions" }

TariffPriceComponent:
  type: object
  description: >
    A single price component within a tariff element.
    Based on OCPI price_component structure.
  additionalProperties: false
  required: [type, price]
  properties:
    type:
      type: string
      enum: [ENERGY, TIME, FLAT, PARKING_TIME, AD_HOC_PAYMENT]
      description: >
        Price component type (OCPI enum).
        ENERGY: Per kWh pricing
        TIME: Per hour/minute pricing
        FLAT: Flat fee
        PARKING_TIME: Parking time fee
        AD_HOC_PAYMENT: One-time payment
      x-jsonld: { "@id": "ocpi:type" }

    price:
      type: number
      minimum: 0
      description: >
        Price per unit.
        For ENERGY: price per kWh
        For TIME: price per hour (or minute if step_size < 60)
        For FLAT: flat fee amount
      example: 18.0
      x-jsonld: { "@id": "schema:price" }

    vat:
      type: number
      minimum: 0
      default: 0
      description: Value-added tax percentage.
      example: 18.0
      x-jsonld: { "@id": "ocpi:vat" }

    stepSize:
      type: integer
      minimum: 1
      default: 1
      description: >
        Step size in seconds.
        For ENERGY: typically 1 (per kWh)
        For TIME: typically 3600 (per hour) or 60 (per minute)
      example: 1
      x-jsonld: { "@id": "ocpi:step_size" }
```

### 2. Extend SELLER roleInputs

**File**: `outputs/schema/EnergyContractP2PTrade/v1/attributes.yaml`

Update `P2PTradeSellerRole.roleInputs` to add `tariff`:

```yaml
roleInputs:
  type: object
  description: >
    SELLER must provide: sourceMeterId, sourceType, and ONE of:
    - pricePerKWh + currency (simple fixed price)
    - tariff (full tariff object for time-of-use, tiered pricing)
    - offerCurve (market-based mode, use PROSUMER role instead)
  additionalProperties: false
  required: [sourceMeterId, sourceType]
  properties:
    # ... existing properties ...
    
    tariff:
      $ref: '../EnergyContract/v1/attributes.yaml#/components/schemas/RoleInput'
      description: >
        Optional. Full tariff object for time-of-use, tiered pricing, utility tariffs.
        Reference: ../EnergyCoordination/v1/attributes.yaml#/components/schemas/Tariff
        Use instead of pricePerKWh for complex pricing structures.
        Mutually exclusive with pricePerKWh (use one or the other).
```

**Note**: `tariff` and `pricePerKWh` are mutually exclusive. Validation should ensure only one is provided.

---

## Polymorphic Pricing Support

The SELLER role now supports **three pricing modes**:

1. **Simple Fixed Price** (`pricePerKWh` + `currency`):
   ```json
   {
     "pricePerKWh": 0.15,
     "currency": "INR"
   }
   ```

2. **Tariff Object** (`tariff`):
   ```json
   {
     "tariff": {
       "currency": "INR",
       "elements": [
         {
           "priceComponents": [
             {
               "type": "ENERGY",
               "price": 0.20,
               "vat": 0.0,
               "stepSize": 1
             }
           ],
           "restrictions": {
             "startTime": "18:00",
             "endTime": "22:00",
             "dayOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
           }
         },
         {
           "priceComponents": [
             {
               "type": "ENERGY",
               "price": 0.10,
               "vat": 0.0,
               "stepSize": 1
             }
           ],
           "restrictions": {
             "startTime": "22:00",
             "endTime": "06:00"
           }
         }
       ]
     }
   }
   ```

3. **Market-Based** (`offerCurve` in PROSUMER role):
   ```json
   {
     "offerCurve": {
       "currency": "INR",
       "minExport": 0,
       "maxExport": 10,
       "curve": [
         { "price": 0.05, "powerKW": 0 },
         { "price": 0.10, "powerKW": 10 }
       ]
     }
   }
   ```

---

## Revenue Flow Formula Updates

For tariff-based pricing, revenue flows need to compute price from tariff:

**Fixed Price Mode (simple)**:
```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "roles.BUYER.roleInputs.contractedQuantity × roles.SELLER.roleInputs.pricePerKWh"
}
```

**Fixed Price Mode (tariff)**:
```json
{
  "from": "BUYER",
  "to": "SELLER",
  "formula": "computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity",
  "description": "Compute price from tariff based on time-of-use and tiered rates"
}
```

**Note**: Tariff computation requires:
- `deliveredQuantity` (from telemetry)
- `tradeStartTime` and `tradeEndTime` (from BUYER roleInputs)
- Tariff elements with time restrictions

---

## Example: Utility-to-Buyer Trade

### Discovery (on_discover)

```json
{
  "beckn:offerAttributes": {
    "@type": "EnergyOffer",
    "contract": {
      "@type": "EnergyContractP2PTrade",
      "roles": [
        {
          "role": "SELLER",
          "filledBy": "utility-company.com",
          "filled": true,
          "roleInputs": {
            "sourceMeterId": "grid-meter-001",
            "sourceType": "GRID",
            "tariff": {
              "tariffId": "TOU-2024-001",
              "currency": "INR",
              "type": "REGULAR",
              "tariffAltText": [
                {
                  "language": "en",
                  "text": "Time-of-Use Tariff - Residential"
                }
              ],
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
                },
                {
                  "priceComponents": [
                    {
                      "type": "ENERGY",
                      "price": 0.10,
                      "vat": 18.0,
                      "stepSize": 1
                    }
                  ],
                  "restrictions": {
                    "startTime": "22:00",
                    "endTime": "06:00"
                  }
                },
                {
                  "priceComponents": [
                    {
                      "type": "ENERGY",
                      "price": 0.15,
                      "vat": 18.0,
                      "stepSize": 1
                    }
                  ],
                  "restrictions": {
                    "startTime": "06:00",
                    "endTime": "18:00"
                  }
                }
              ],
              "energyMix": {
                "isGreenEnergy": false,
                "energySources": [
                  {
                    "source": "COAL",
                    "percentage": 60.0
                  },
                  {
                    "source": "SOLAR",
                    "percentage": 40.0
                  }
                ],
                "environImpact": {
                  "carbonDioxide": 450.0
                },
                "supplierName": "State Utility Co",
                "energyProductName": "Mixed Grid Power"
              }
            }
          }
        },
        {
          "role": "BUYER",
          "filledBy": null,
          "filled": false,
          "roleInputs": {}
        }
      ]
    }
  }
}
```

### Confirm (with tariff-based pricing)

```json
{
  "beckn:orderAttributes": {
    "@type": "EnergyContractP2PTrade",
    "status": "ACTIVE",
    "roles": [
      {
        "role": "SELLER",
        "filledBy": "utility-company.com",
        "filled": true,
        "roleInputs": {
          "sourceMeterId": "grid-meter-001",
          "sourceType": "GRID",
          "tariff": {
            "currency": "INR",
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
                  "endTime": "22:00"
                }
              },
              {
                "priceComponents": [
                  {
                    "type": "ENERGY",
                    "price": 0.10,
                    "vat": 18.0,
                    "stepSize": 1
                  }
                ],
                "restrictions": {
                  "startTime": "22:00",
                  "endTime": "06:00"
                }
              }
            ]
          }
        }
      },
      {
        "role": "BUYER",
        "filledBy": "consumer-app.com",
        "filled": true,
        "roleInputs": {
          "targetMeterId": "98765456",
          "contractedQuantity": 100.0,
          "tradeStartTime": "2024-10-04T18:00:00Z",
          "tradeEndTime": "2024-10-05T06:00:00Z"
        }
      }
    ],
    "revenueFlows": {
      "flows": [
        {
          "from": "BUYER",
          "to": "SELLER",
          "formula": "computeTariffPrice(roles.SELLER.roleInputs.tariff, roles.BUYER.roleInputs.tradeStartTime, roles.BUYER.roleInputs.tradeEndTime, deliveredQuantity) × deliveredQuantity",
          "description": "Compute price from time-of-use tariff: peak (18:00-22:00) @ ₹0.20/kWh, off-peak (22:00-06:00) @ ₹0.10/kWh"
        }
      ],
      "netZero": true
    }
  }
}
```

---

## Validation Rules

1. **Mutual Exclusivity**: `pricePerKWh` and `tariff` MUST NOT both be provided
2. **Tariff Structure**: `tariff.elements` MUST have at least one element
3. **Price Components**: Each element MUST have at least one `priceComponents` with `type: ENERGY`
4. **Time Restrictions**: If `restrictions.startTime` provided, `restrictions.endTime` MUST also be provided
5. **Currency Consistency**: `tariff.currency` MUST match contract currency (if specified)

---

## Benefits

1. **Standards Alignment**: Based on OCPI (widely adopted in EV charging)
2. **Polymorphic Design**: Same schema supports simple fixed price, tariff, and market-based
3. **Utility Integration**: Enables utility-to-consumer trades with complex tariffs
4. **Time-of-Use Support**: Native support for peak/off-peak pricing
5. **Tiered Pricing**: Supports consumption-based tiered rates
6. **Energy Mix Transparency**: Optional energy source information

---

## Implementation Steps

1. ✅ Add `Tariff`, `TariffElement`, `TariffPriceComponent` schemas to `EnergyCoordination/v1/attributes.yaml`
2. ✅ Extend `P2PTradeSellerRole.roleInputs` to include `tariff`
3. ✅ Update validation rules to enforce mutual exclusivity
4. ✅ Create example JSON files for tariff-based trades
5. ✅ Update revenue flow formulas to support tariff computation
6. ✅ Document tariff computation algorithm

---

**Status**: Proposal ready for review ✅

