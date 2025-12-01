# Energy Catalogue

## Definition

An Energy Catalogue is a structured listing of available energy resources, services, or offerings published by providers. Catalogues represent the "offer" side of energy transactions, detailing what is available, in what quantities, at what locations, during which times, at what prices, with what constraints, and through what delivery methods.

Energy catalogues are the supply-side complement to energy intents - when a consumer's intent matches a provider's catalogue offering, the foundation for an energy contract is established.

**EnergyOffer as Core Primitive**: A catalogue can be thought of as a **bouquet of EnergyOffers**. Each **EnergyOffer** is the **core Beckn primitive** representing contract participation opportunities, published in `offerAttributes`. Offers specify **open roles** (BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, AGGREGATOR, GRID_OPERATOR) that participants can assume in EnergyContracts. Offers reference EnergyContracts that define computational billing logic.

## Why Energy Catalogues Matter

In traditional centralized energy systems:
- **Limited visibility**: Consumers see only their local utility's offerings
- **Opaque pricing**: Tariffs are complex and not easily comparable
- **No choice**: Single provider per geography, take-it-or-leave-it terms
- **Static offerings**: Limited ability for providers to advertise differentiated services

In decentralized energy markets with multiple providers, diverse resources, and varied service offerings, providers need a standardized way to:
- **Advertise services**: Make offerings discoverable across networks
- **Differentiate**: Highlight unique value propositions (green energy, fast charging, flexible pricing)
- **Update dynamically**: Reflect real-time availability, pricing changes, seasonal variations
- **Reach consumers**: Connect with intent-expressing consumers beyond geographic boundaries

Energy Catalogues solve this by providing a structured format for publishing supply that can be automatically matched with demand intents across distributed networks. The underlying **EnergyOffers** enable role-based contract participation.

## Structure of Energy Catalogues

Energy catalogues are returned through Beckn Protocol `on_discover` responses:

### Catalogue Response Structure

```json
{
  "context": {
    "action": "on_discover",
    "domain": "beckn.one:deg:ev-charging:*",
    "bpp_id": "bpp.example.com"
  },
  "message": {
    "catalogs": [{
      "beckn:descriptor": {
        "schema:name": "EV Charging Services Network",
        "beckn:shortDesc": "Comprehensive network of fast charging stations"
      },
      "beckn:validity": {
        "schema:startDate": "2024-10-01T00:00:00Z",
        "schema:endDate": "2025-01-15T23:59:59Z"
      },
      "beckn:items": [
        /* Array of available services/resources */
      ],
      "beckn:offers": [
        /* Array of EnergyOffers in offerAttributes */
      ]
    }]
  }
}
```

**Catalogue Components**:
- **Descriptor**: Catalogue name and description
- **Validity**: Time period for which catalogue is valid
- **Items**: Available resources/services (e.g., charging stations, energy offerings)
- **Offers**: Array of **EnergyOffers** (core Beckn primitives) in `offerAttributes`

### EnergyOffer Structure (Core Primitive)

Each offer in the catalogue is an **EnergyOffer** in `offerAttributes`:

```json
{
  "beckn:offers": [{
    "beckn:id": "offer-ccs2-60kw-kwh",
    "beckn:items": ["ev-charger-ccs2-001"],
    "beckn:price": {
      "currency": "INR",
      "value": 18.0,
      "applicableQuantity": {
        "unitCode": "KWH"
      }
    },
    "beckn:acceptedPaymentMethod": ["UPI", "CreditCard", "Wallet"],
    "beckn:offerAttributes": {
      "@type": "EnergyOffer",
      "offerId": "offer-ev-charging-001",
      "contractId": "contract-walk-in-001",
      "providerId": "bpp.cpo.example.com",
      "providerUri": "https://bpp.cpo.example.com",
      "openRole": "BUYER",
      "contract": {
        "@type": "EnergyContractEVCharging",
        "contractId": "contract-walk-in-001",
        "status": "PENDING",
        "createdAt": "2024-12-15T10:00:00Z",
        "roles": [
          {
            "role": "SELLER",
            "filledBy": "bpp.cpo.example.com",
            "filled": true,
            "roleInputs": {
              "pricePerKWh": 18.0,
              "currency": "INR",
              "connectorType": "CCS2",
              "maxPowerKW": 60,
              "minPowerKW": 5,
              "location": {
                "geo": {
                  "type": "Point",
                  "coordinates": [77.5946, 12.9716]
                },
                "address": {
                  "streetAddress": "EcoPower BTM Hub, 100 Ft Rd",
                  "addressLocality": "Bengaluru",
                  "postalCode": "560076"
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
        ],
        "inputParameters": {
          "validityWindow": {
            "startTime": "2024-12-15T06:00:00Z",
            "endTime": "2024-12-15T22:00:00Z"
          },
          "gracePeriodMinutes": 10
        },
        "inputSignals": [],
        "telemetrySources": [
          {
            "sourceId": "cdr-ev-charger-ccs2-001",
            "sourceType": "CHARGE_DATA_RECORD",
            "description": "Charge Data Record from EVSE",
            "required": true
          }
        ],
        "revenueFlows": {
          "flows": [
            {
              "from": "BUYER",
              "to": "SELLER",
              "formula": "roles.SELLER.roleInputs.pricePerKWh.value × telemetrySources.cdr-ev-charger-ccs2-001.energyKWh",
              "description": "BUYER pays SELLER based on energy consumed (from CDR) × price provided by SELLER"
            }
          ],
          "netZero": true
        },
        "qualityMetrics": {
          "metrics": [
            {
              "metricId": "averageChargingPower",
              "formula": "telemetrySources.cdr-ev-charger-ccs2-001.energyKWh / ((telemetrySources.cdr-ev-charger-ccs2-001.endTime - telemetrySources.cdr-ev-charger-ccs2-001.startTime) / 3600)",
              "unit": "kW",
              "description": "Average charging power in kilowatts"
            }
          ]
        }
      }
    }
  }]
}
```


**EnergyOffer Key Components**:
- **offerId**: Unique identifier
- **contractId**: Reference to EnergyContract
- **openRole**: Role available for participants (BUYER, SELLER, PROSUMER, etc.)
- **contract**: Optional full contract definition (shown above for EV charging)

**EnergyContractEVCharging Details (Specialized Contract Type)**:
- **Inherits from**: EnergyContract (base abstract schema)
- **SELLER Role Responsibilities**: SELLER must provide pricePerKWh, currency, connectorType, maxPowerKW, minPowerKW, location via `roleInputs` (each input has type, required, description, and nullable value)
- **Roles**: SELLER (CPO, filled with roleInputs values) and BUYER (open, empty roleInputs)
- **RoleInputs Structure**: Each input includes schema (type, required, description) and nullable value - if value is null, input not provided yet
- **Input Parameters**: Only fixed contract-level parameters (validityWindow, gracePeriodMinutes) - not role-specific
- **Telemetry Sources**: Charge Data Record (CDR) from EVSE for energy consumption
- **Revenue Flows**: BUYER pays SELLER = `roles.SELLER.roleInputs.pricePerKWh.value × energyKWh` (from CDR)
- **Quality Metrics**: Average charging power computed from CDR data
- **Status**: PENDING (becomes ACTIVE when BUYER assumes role and contract is confirmed)

## Types of Energy Catalogue Offerings

### Infrastructure Services

Catalogues listing physical infrastructure available for energy transactions:

**EV Charging Stations**:
- Location and accessibility
- Connector types and power ratings
- Availability windows
- Amenities (restroom, Wi-Fi, food)
- Real-time status
- **EnergyOffer**: Open BUYER role, fixed-price or dynamic contract

**Grid Connection Services**:
- Interconnection capacity available
- Connection approval processing
- Technical requirements
- Installation services

### Energy Supply

Catalogues listing energy available for purchase:

**Utility Grid Power**:
- Time-of-use tariffs
- Demand response programs
- Interruptible vs. firm power
- Voltage and phase specifications

**Distributed Generation (DER)**:
- Rooftop solar excess capacity
- Battery storage discharge windows
- Combined heat and power (CHP) availability
- Wind farm allocations
- **EnergyOffer**: Open BUYER role, may include OfferCurve for market-based trading

**Peer-to-Peer (P2P) Trading**:
- Prosumer excess energy
- Community solar shares
- Virtual power plant (VPP) aggregated capacity
- Time-based availability windows
- **EnergyOffer**: Open BUYER role, OfferCurve-based contracts

### Data and Analytics Services

Catalogues for energy-related data offerings:

**Consumption Data**:
- Anonymized household/sector consumption patterns
- Peak demand analytics
- Load forecasting datasets

**Market Information**:
- Real-time pricing signals
- Forecast prices and availability
- Carbon intensity data
- Renewable generation forecasts

### Financial and Support Services

Catalogues for energy-adjacent services:

**Financing**:
- Solar installation loans
- EV purchase financing
- Energy efficiency retrofit funding

**Insurance and Guarantees**:
- Performance guarantees for solar installations
- Demand guarantee insurance
- Price hedging products

**Installation and Maintenance**:
- Solar panel installation services
- EV charger setup
- Battery storage commissioning
- Ongoing maintenance contracts

## Energy Catalogues in Practice

### From EV Charging Implementation Guide

#### Complete Catalogue Response

**Provider**: EcoPower Charging Pvt Ltd
**Catalogue**: EV Charging Services Network

```json
{
  "message": {
    "catalogs": [{
      "beckn:descriptor": {
        "schema:name": "EV Charging Services Network"
      },
      "beckn:items": [{
        "beckn:id": "ev-charger-ccs2-001",
        "beckn:descriptor": {
          "schema:name": "DC Fast Charger - CCS2 (60kW)"
        },
        "beckn:availableAt": [{
          "geo": {"coordinates": [77.5946, 12.9716]},
          "address": {
            "streetAddress": "EcoPower BTM Hub, 100 Ft Rd",
            "addressLocality": "Bengaluru"
          }
        }],
        "beckn:availabilityWindow": {
          "schema:startTime": "06:00:00",
          "schema:endTime": "22:00:00"
        },
        "beckn:itemAttributes": {
          "connectorType": "CCS2",
          "maxPowerKW": 60,
          "minPowerKW": 5,
          "socketCount": 2,
          "evseId": "IN*ECO*BTM*01*CCS2*A",
          "stationStatus": "Available",
          "amenityFeature": ["Restaurant", "Restroom", "Wi-Fi"]
        }
      }],
      "beckn:offers": [{
        "beckn:id": "offer-ccs2-60kw-kwh",
        "beckn:items": ["ev-charger-ccs2-001"],
        "beckn:price": {
          "currency": "INR",
          "value": 18.0,
          "applicableQuantity": {
            "unitCode": "KWH"
          }
        },
        "beckn:offerAttributes": {
          "@type": "EnergyOffer",
          "offerId": "offer-ev-charging-001",
          "contractId": "contract-walk-in-001",
          "providerId": "bpp.cpo.example.com",
          "openRole": "BUYER"
        }
      }]
    }]
  }
}
```

**Key Catalogue Elements**:
1. **Service Identity**: EVSE ID, provider ID, location
2. **Technical Specifications**: Connector type, power range, socket count
3. **Availability**: Operating hours 6 AM - 10 PM
4. **Status**: Real-time "Available" status
5. **Amenities**: Restaurant, restroom, Wi-Fi on-site
6. **EnergyOffer**: Open BUYER role in fixed-price contract
7. **Pricing**: ₹18/kWh

### P2P Energy Trading Catalogue (Conceptual)

#### Prosumer Solar Export Catalogue

**Provider**: Household Solar Battery 001
**Catalogue**: Excess Solar Energy Available

```json
{
  "message": {
    "catalogs": [{
      "beckn:descriptor": {
        "schema:name": "Excess Solar Energy - Afternoon Export"
      },
      "beckn:items": [{
        "beckn:id": "excess-solar-export-afternoon",
        "beckn:itemAttributes": {
          "energySource": "solar",
          "installedCapacity": "5kW",
          "greenCertified": true
        }
      }],
      "beckn:offers": [{
        "beckn:id": "solar-export-rate-afternoon",
        "beckn:items": ["excess-solar-export-afternoon"],
        "beckn:offerAttributes": {
          "@type": "EnergyOffer",
          "offerId": "offer-solar-export-001",
          "contractId": "contract-market-clearing-001",
          "providerId": "bpp.prosumer.example.com",
          "openRole": "BUYER",
          "expectedInputs": [
            {
              "name": "offerCurve",
              "type": "OfferCurve",
              "required": true
            }
          ]
        }
      }]
    }]
  }
}
```

**Key Catalogue Elements**:
1. **Energy Source**: Solar, green certified
2. **Capacity**: 5kW installation
3. **Availability**: 10 AM - 4 PM daily
4. **EnergyOffer**: Open BUYER role, expects OfferCurve for market clearing
5. **Contract**: Market-clearing contract computes billing from clearing price × cleared power

## Catalogue Lifecycle in Transactions

### Phase 1: Publishing

**Actor**: Provider (via BPP)
**Process**: Create and maintain catalogue

```
Provider defines services → BPP structures catalogue → Registers with CDS
  ↓
Catalogue indexed for discovery (contains bouquet of EnergyOffers)
  ↓
Real-time updates (availability, pricing)
```

### Phase 2: Discovery Matching

**Actors**: CDS, BPP
**Process**: Filter catalogue based on consumer intent

```
CDS receives discover intent → Routes to relevant BPPs
  ↓
BPP filters catalogue based on intent constraints
  ↓
Returns matching items and EnergyOffers in on_discover
```

**Example**: Intent for "CCS2, 50kW+, within 10km" → Catalogue filtered to matching chargers with EnergyOffers

### Phase 3: Selection Response

**Actor**: BPP
**Process**: Generate detailed quote for selected EnergyOffer

```
BPP receives select → Validates selection → Generates quote (on_select)
```

### Phase 4: Contract Formation

**Process**: EnergyOffer selected → Participant assumes role → Energy Contract forms

```
Init/Confirm flow → Participant assumes open role → Contract confirmed
```

## Catalogue Composition

Catalogues can include multiple dimensions:

### Resource Attributes
- **Identity**: Unique IDs (EVSE ID, resource ERA)
- **Type**: Category, subcategory, classification
- **Specifications**: Technical parameters (power, capacity, connector type)
- **Location**: Geographic coordinates, address, accessibility

### Availability
- **Operating hours**: Start/end times, days of week
- **Real-time status**: Available, occupied, offline, reserved
- **Capacity**: Current vs. total capacity
- **Scheduling**: Future availability windows

### Commercial Terms (via EnergyOffers)
- **Pricing**: Per-unit rates, subscription models, time-of-use tariffs
- **Payment**: Accepted methods, prepaid vs. postpaid
- **Fees**: Platform fees, idle fees, cancellation fees
- **Minimums/maximums**: Minimum purchase, maximum capacity
- **Open Roles**: BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, etc.

### Service Quality
- **Ratings**: User reviews and average ratings
- **Reliability**: Uptime percentage, historical performance
- **Support**: Customer service availability, response times
- **Amenities**: Additional services or features

### Credentials and Compliance
- **Certifications**: Safety standards, green energy attestations
- **Licenses**: Operational permits, regulatory compliance
- **Insurance**: Liability coverage, performance guarantees
- **Attestations**: Third-party verifications

## Relationship with Other Primitives

1. **Energy Resource**: Catalogues list available resources (with ERAs)
2. **Energy Resource Address**: Each catalogue item has an ERA for addressability
3. **Energy Credentials**: Catalogue includes or references resource credentials
4. **Energy Intent**: Catalogues are filtered/matched against consumer intents
5. **Energy Offer**: Catalogues contain a bouquet of EnergyOffers (core Beckn primitives)
6. **Energy Contract**: EnergyOffer references contract; contract forms when roles filled

## Summary

Energy Catalogues are the supply-side voice in the Digital Energy Grid - enabling structured, machine-readable publication of energy offerings that can be automatically matched with consumer intents across distributed networks. From charging station listings to prosumer solar exports, catalogues make diverse energy services discoverable, comparable, and accessible.

A catalogue can be thought of as a **bouquet of EnergyOffers** - each offer is the core Beckn primitive representing contract participation opportunities with open roles. When an energy intent matches an energy catalogue offering (EnergyOffer), an energy contract is established - **this cycle of intent matched with catalogue, forming a contract, is the fundamental interaction loop in the Digital Energy Grid**.

## See Also

- [Energy Intent](./Energy%20intent.md) - The demand side that matches with catalogues
- [Energy Contract](./Energy%20contract.md) - What emerges when EnergyOffer is accepted and roles filled
- [Energy Resource](./Energy%20resource.md) - Resources listed in catalogues
- [Energy Credentials](./Energy%20credentials.md) - Credentials referenced in catalogues
- [EV Charging Implementation Guide](../docs/implementation-guides/v2/EV_Charging_V0.8-draft.md) - Catalogue examples in practice

