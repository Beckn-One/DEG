# Energy Intent (also called Energy Objective)

## Definition

An Energy Intent expresses **what an actor values** - goals, preferences, constraints, and objectives. Also called Energy Objective, it guides optimization: actors accept EnergyOffers, participate in contracts, or update offer curves to maximize their expressed values. For at home EV charging, it may be reducing charging bill, while for charging on-the-go, it could be a combination of detour (from the intended route) + wait time and cost.

Intents are used in `discover` calls to find matching contracts. They are optional and can aid better discovery - they're expressions used by actors/algorithms for optimization and contract discovery.

## Why Energy Intents Matter

In decentralized energy markets, actors need to express their values to:
- **Guide optimization**: Algorithms use intents to select which offers to accept
- **Discover contracts**: Find EnergyOffers that align with expressed values
- **Update strategies**: Adjust offer curves based on changing objectives
- **Enable automation**: Allow agents to transact on behalf of actors

**Key Insight**: Intent = Objective = What you value. To maximize value, actors can accept offers, participate in contracts, or update offer parameters (e.g offer curves).

## Structure of Energy Intents

Energy intents appear in `discover` calls via `message.intent` (optional). They express values that guide contract discovery and participation:

### Intent in Discover Calls

Intent appears in `message.intent` of `discover` requests:

```json
{
  "context": {
    "action": "discover",
    "domain": "beckn.one:deg:ev-charging:*"
  },
  "message": {
    "intent": {
      "targetChargeKWh": 20,
      "deadline": "2024-12-15T18:00:00Z",
      "maxPricePerKWh": 0.12,
      "preferredSource": "SOLAR"
    },
    "spatial": [{
      "op": "s_dwithin",
      "targets": "$['beckn:availableAt'][*]['geo']",
      "geometry": {
        "type": "Point",
        "coordinates": [77.59, 12.94]
      },
      "distanceMeters": 10000
    }],
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.beckn:itemAttributes.connectorType == 'CCS2' && @.beckn:itemAttributes.maxPowerKW >= 50)]"
    }
  }
}
```

**Intent Components**:
- **Goals**: What the actor wants (targetChargeKWh, deadline)
- **Constraints**: Limits (maxPricePerKWh, preferredSource)
- **Preferences**: Desired attributes (location, timing, quality)

**Note**: Intent is used to find matching EnergyOffers. Once offers are selected, contracts are formed based on roles, not intents.

## How Intents Guide Optimization

Actors use intents to maximize their expressed values by:

1. **Accepting EnergyOffers**: Select offers that align with intent
2. **Participating in Contracts**: Assume roles in contracts that satisfy objectives
3. **Updating Offer Curves**: Adjust price/power curves based on changing values

**Example Flow**:
```
Intent: "Value: Charge 20 kWh by 9 PM, prefer solar, max ₹18/kWh, minimize cost."
  ↓
Discover finds EnergyOffers matching intent, with the lowest cost
  ↓
Actor accepts offer, assumes BUYER role
  ↓
Contract forms; billing computed from signals
```

## Energy Intents in Practice

### From EV Charging Implementation Guide

#### Discovery Intent: Find Chargers Within Boundary with Specifications

**Intent**: "Find CCS2 chargers with 50kW+ power within 10km of my location"

```json
{
  "message": {
    "spatial": [{
      "op": "s_dwithin",
      "targets": "$['beckn:availableAt'][*]['geo']",
      "geometry": {
        "type": "Point",
        "coordinates": [77.59, 12.94]
      },
      "distanceMeters": 10000
    }],
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.beckn:itemAttributes.connectorType == 'CCS2' && @.beckn:itemAttributes.maxPowerKW >= 50)]"
    }
  }
}
```

#### Discovery Intent: Find Available in Time Range

**Intent**: "Find CCS2 chargers available between 12:30 PM and 2:30 PM"

```json
{
  "message": {
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.beckn:itemAttributes.connectorType == 'CCS2' && @.beckn:availabilityWindow.schema:startTime <= '12:30:00' && @.beckn:availabilityWindow.schema:endTime >= '14:30:00')]"
    }
  }
}
```

#### Discovery Intent: Find Specific EVSE by ID

**Intent**: "Find charger IN*ECO*BTM*01*CCS2*A" (after scanning QR code)

```json
{
  "message": {
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.beckn:itemAttributes.evseId == 'IN*ECO*BTM*01*CCS2*A')]"
    }
  }
}
```

#### Selection Intent: Reserve Charging Slot

**Intent**: "Reserve 2.5 kWh at charger ev-charger-ccs2-001, accepting ₹18/kWh rate, total ₹100"

```json
{
  "message": {
    "order": {
      "beckn:orderValue": {
        "currency": "INR",
        "value": 100.0
      },
      "beckn:orderItems": [{
        "beckn:orderedItem": "ev-charger-ccs2-001",
        "beckn:quantity": 2.5,
        "beckn:acceptedOffer": {
          "beckn:id": "offer-ccs2-60kw-kwh",
          "beckn:price": {
            "value": 18.0,
            "applicableQuantity": {
              "unitCode": "KWH"
            }
          }
        }
      }],
      "beckn:fulfillment": {
        "beckn:mode": "RESERVATION",
        "beckn:deliveryAttributes": {
          "connectorType": "CCS2",
          "reservationId": "RESV-984532",
          "gracePeriodMinutes": 10
        }
      }
    }
  }
}
```

### P2P Energy Trading Intents (Conceptual)

#### Discovery Intent: Buy Solar Energy from Neighbors

**Intent**: "Buy 10 kWh solar energy from prosumers within 2km, delivery 2-4 PM, max ₹6/kWh, certified sellers only"

```json
{
  "context": {
    "action": "discover",
    "domain": "beckn.one:deg:p2p-trading:*"
  },
  "message": {
    "spatial": [{
      "op": "s_dwithin",
      "geometry": {
        "type": "Point",
        "coordinates": [12.9716, 77.5946]
      },
      "distanceMeters": 2000
    }],
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.energyType == 'solar' && @.price.value <= 6.0 && @.credentials[?(@.type == 'GreenCertification')])]"
    },
    "temporal": {
      "deliveryWindow": {
        "startTime": "14:00:00",
        "endTime": "16:00:00"
      }
    }
  }
}
```

#### Selection Intent: Accept Prosumer Offer

**Intent**: "Accept offer from household-solar-001 to buy 10 kWh at ₹5.50/kWh, delivery Nov 12 2-4 PM"

```json
{
  "message": {
    "order": {
      "seller": "household-solar-001.prosumer.example.com",
      "buyer": "apartment-complex-456.example.com",
      "orderItems": [{
        "orderedItem": "excess-solar-export-afternoon",
        "quantity": 10,
        "acceptedOffer": {
          "price": {
            "value": 5.50,
            "currency": "INR",
            "applicableQuantity": {
              "unitCode": "KWH"
            }
          }
        }
      }],
      "fulfillment": {
        "deliveryWindow": {
          "startTime": "2024-11-12T14:00:00Z",
          "endTime": "2024-11-12T16:00:00Z"
        },
        "meterReading": {
          "meteringAuthority": "SmartMeterCo",
          "attestationRequired": true
        }
      }
    }
  }
}
```

## Intent Usage in Discover

Intent appears in `discover` calls to guide contract discovery:

```
Actor expresses intent (values) → discover(intent)
  ↓
CDS/BPPs match intent against EnergyOffers
  ↓
Returns offers that align with expressed values
  ↓
Actor selects offer, assumes role in contract
```

**Note**: Intent is not stored in contracts. Contracts use roles and input signals, not intents.

## Relationship with Other Primitives

1. **Energy Resource**: Resources express intents (what they value)
2. **Energy Offer**: Intent guides selection of offers that align with values
3. **Energy Contract**: Contracts form when roles are filled, not based on intents
4. **Energy Credentials**: Intent may specify required credentials

## Summary

Energy Intent (also called Energy Objective) expresses **what an actor values**. Used in `discover` calls to find matching EnergyOffers. Actors maximize their expressed values by accepting offers, participating in contracts, or updating offer curves. Intent is not part of the required Beckn schema - it's an optimization guide used by actors/algorithms.

## See Also

- [Energy Offer](./Energy%20catalogue.md) - Contract participation opportunities that match intents
- [Energy Contract](./Energy%20contract.md) - Role-based agreements formed when offers are accepted
- [Energy Resource](./Energy%20resource.md) - Resources that express intents
