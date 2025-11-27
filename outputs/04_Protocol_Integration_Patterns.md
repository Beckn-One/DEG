# Protocol Integration Patterns
## Detailed Integration Patterns for OCPI, OCPP, and IEEE 2030.5

**Version:** 1.0  
**Date:** December 2024

---

## Overview

This document provides detailed integration patterns for translating between Beckn Protocol building blocks (including proposed extensions) and existing energy protocols: OCPI, OCPP, and IEEE 2030.5. The goal is to minimize translation toil while enabling seamless coordination across protocol boundaries.

**Key Principle**: Reuse protocol enums and structures, don't reinvent them. The coordination layer provides a thin glue that enables interoperability.

---

## Table of Contents

1. [OCPI Integration](#1-ocpi-integration)
2. [OCPP Integration](#2-ocpp-integration)
3. [IEEE 2030.5 Integration](#3-ieee-20305-integration)
4. [Bid Curve Translation Patterns](#4-bid-curve-translation-patterns)
5. [Market Clearing Integration](#5-market-clearing-integration)
6. [Translation Toil Assessment](#6-translation-toil-assessment)

---

## 1. OCPI Integration

### 1.1 Role and Scope

**OCPI (Open Charge Point Interface)** focuses on:
- **Roaming**: eMSP ↔ CPO communication
- **Tariff Management**: Pricing information exchange
- **Session Management**: Charging session data
- **CDR (Charge Detail Record)**: Settlement data

**Integration Boundary**: OCPI handles roaming and tariff coordination; Beckn/DEG handles market coordination and discovery.

### 1.2 Energy Resource Address Mapping

**OCPI → Beckn**:
```json
{
  "ocpi": {
    "location_id": "IN*ECO*BTM*01",
    "evse_uid": "IN*ECO*BTM*01*CCS2*A"
  },
  "beckn": {
    "era": "ocpi.location.IN*ECO*BTM*01",
    "itemAttributes": {
      "evseId": "IN*ECO*BTM*01*CCS2*A",
      "ocpiLocationId": "IN*ECO*BTM*01"
    }
  }
}
```

**Mapping Rules**:
- OCPI `location_id` → Beckn ERA prefix: `ocpi.location.{location_id}`
- OCPI `evse_uid` → Beckn `itemAttributes.evseId`
- OCPI `evse_uid` format: `{Country}*{CPO}*{Location}*{Unit}*{Connector}*{Instance}`

**Translation Toil**: ✅ **Very Low** - Direct string mapping

---

### 1.3 Catalogue Discovery Mapping

**OCPI Location → Beckn Item**:

```json
// OCPI Location Response
{
  "id": "IN*ECO*BTM*01",
  "name": "EcoPower BTM Hub",
  "coordinates": {
    "latitude": "12.9716",
    "longitude": "77.5946"
  },
  "evses": [{
    "uid": "IN*ECO*BTM*01*CCS2*A",
    "connectors": [{
      "id": "1",
      "standard": "IEC_62196_T2_COMBO",
      "format": "SOCKET",
      "power_type": "AC_3_PHASE",
      "max_voltage": 500,
      "max_amperage": 200,
      "max_electric_power": 60000
    }]
  }]
}

// Beckn Item (in on_discover)
{
  "beckn:id": "ev-charger-ccs2-001",
  "beckn:descriptor": {
    "schema:name": "DC Fast Charger - CCS2 (60kW)"
  },
  "beckn:availableAt": [{
    "geo": {
      "type": "Point",
      "coordinates": [77.5946, 12.9716]
    }
  }],
  "beckn:itemAttributes": {
    "evseId": "IN*ECO*BTM*01*CCS2*A",
    "ocpiLocationId": "IN*ECO*BTM*01",
    "connectorType": "CCS2",  // Mapped from OCPI standard
    "connectorFormat": "SOCKET",  // Direct from OCPI
    "powerType": "DC",  // Derived from OCPI power_type
    "maxPowerKW": 60,  // Converted from max_electric_power (W → kW)
    "maxVoltage": 500,  // Direct from OCPI
    "maxAmperage": 200  // Direct from OCPI
  }
}
```

**Mapping Rules**:
- OCPI `coordinates` → Beckn `availableAt[].geo`
- OCPI `standard` → Beckn `connectorType` (enum mapping)
- OCPI `format` → Beckn `connectorFormat` (direct)
- OCPI `power_type` → Beckn `powerType` (enum mapping)
- OCPI `max_electric_power` (W) → Beckn `maxPowerKW` (kW)

**Translation Toil**: ✅ **Low** - Simple field mapping with unit conversion

---

### 1.4 Tariff to Bid Curve Translation

**OCPI Tariff → Beckn Bid Curve**:

```json
// OCPI Tariff
{
  "id": "TARIFF-001",
  "currency": "INR",
  "elements": [{
    "price_components": [{
      "type": "ENERGY",
      "price": 18.0,
      "vat": 0.0,
      "step_size": 1
    }],
    "restrictions": {
      "start_time": "06:00",
      "end_time": "22:00"
    }
  }]
}

// Beckn Bid Curve (for demand flexibility)
{
  "itemAttributes": {
    "bidCurve": [
      { "price": 0.15, "powerKW": 0 },
      { "price": 0.18, "powerKW": 60 }
    ],
    "constraints": {
      "availableWindow": {
        "start": "06:00:00",
        "end": "22:00:00"
      }
    }
  }
}
```

**Translation Algorithm**:
```python
def ocpi_tariff_to_bid_curve(ocpi_tariff, max_power_kw):
    """
    Convert OCPI tariff to bid curve.
    
    For fixed pricing:
    - Base price point: (tariff_price, 0)
    - Max power point: (tariff_price, max_power_kw)
    
    For time-of-use:
    - Create bid curve for each time period
    """
    base_price = ocpi_tariff['elements'][0]['price_components'][0]['price']
    
    # Convert to per-kWh (if needed)
    price_per_kwh = base_price / 1000 if base_price > 100 else base_price
    
    bid_curve = [
        {"price": price_per_kwh * 0.83, "powerKW": 0},  # 83% of base (willing to charge at lower price)
        {"price": price_per_kwh, "powerKW": max_power_kw}  # Base price at max power
    ]
    
    return bid_curve
```

**Translation Toil**: ✅ **Low** - Simple price conversion with optional time-of-use handling

---

### 1.5 CDR to Settlement Mapping

**OCPI CDR → Beckn Settlement**:

```json
// OCPI CDR (Charge Detail Record)
{
  "id": "CDR-001",
  "auth_id": "AUTH-001",
  "auth_method": "AUTH_REQUEST",
  "location": {
    "id": "IN*ECO*BTM*01",
    "name": "EcoPower BTM Hub"
  },
  "evse": {
    "uid": "IN*ECO*BTM*01*CCS2*A",
    "connector_id": "1"
  },
  "currency": "INR",
  "tariffs": [{
    "id": "TARIFF-001",
    "currency": "INR",
    "elements": [{
      "price_components": [{
        "type": "ENERGY",
        "price": 18.0,
        "vat": 0.0
      }]
    }]
  }],
  "charging_periods": [{
    "start_date_time": "2024-12-15T14:00:00Z",
    "dimensions": [{
      "type": "ENERGY",
      "volume": 5.5
    }]
  }],
  "total_cost": 99.0,
  "total_energy": 5.5,
  "total_time": 1800
}

// Beckn Settlement (in orderAttributes)
{
  "orderAttributes": {
    "settlement": {
      "settlementCycles": [{
        "cycleId": "settle-2024-12-15-001",
        "status": "SETTLED",
        "amount": 99.0,
        "currency": "INR",
        "breakdown": {
          "energyCost": 99.0,
          "energyQuantity": 5.5,
          "energyUnit": "KWH"
        },
        "meterReadings": [{
          "timestamp": "2024-12-15T14:00:00Z",
          "energyFlow": 5.5,
          "unit": "KWH"
        }]
      }],
      "revenueFlows": [{
        "party": {
          "era": "ocpi.location.IN*ECO*BTM*01",
          "role": "SELLER"
        },
        "amount": 99.0,
        "currency": "INR",
        "description": "Energy sale"
      }]
    }
  }
}
```

**Mapping Rules**:
- OCPI `total_cost` → Beckn `settlement.amount`
- OCPI `total_energy` → Beckn `settlement.breakdown.energyQuantity`
- OCPI `charging_periods` → Beckn `settlement.meterReadings`
- OCPI `currency` → Beckn `settlement.currency`

**Translation Toil**: ✅ **Low** - Structured field mapping

---

### 1.6 OCPI Integration Summary

| Integration Point | OCPI Source | Beckn Target | Toil Level |
|-------------------|--------------|--------------|------------|
| **ERA Mapping** | `location_id`, `evse_uid` | `era`, `itemAttributes.evseId` | ✅ Very Low |
| **Catalogue Discovery** | `Location`, `EVSE` | `Item`, `itemAttributes` | ✅ Low |
| **Tariff → Bid Curve** | `Tariff.elements` | `itemAttributes.bidCurve` | ✅ Low |
| **CDR → Settlement** | `CDR` | `orderAttributes.settlement` | ✅ Low |
| **Session Status** | `Session.status` | `fulfillmentAttributes.status` | ✅ Very Low |

**Overall Toil Assessment**: ✅ **Low** - OCPI integration is straightforward with direct field mappings.

---

## 2. OCPP Integration

### 2.1 Role and Scope

**OCPP (Open Charge Point Protocol)** focuses on:
- **Device Control**: Charging station management
- **Telemetry**: Real-time meter readings
- **Status Management**: Availability and fault reporting
- **Configuration**: Device settings and profiles

**Integration Boundary**: OCPP handles device-level control; Beckn/DEG handles market coordination and setpoint distribution.

### 2.2 Device Control: Setpoint → OCPP SetChargingProfile

**Market Setpoint → OCPP Command**:

```json
// Beckn Market Setpoint (from orderAttributes)
{
  "orderAttributes": {
    "setpointKW": -8.0,  // Negative = charging
    "clearingPrice": 0.09,
    "objectives": {
      "targetChargeKWh": 20,
      "deadline": "2024-12-15T18:00:00Z"
    }
  }
}

// OCPP SetChargingProfile Command
{
  "action": "SetChargingProfile",
  "chargePointId": "IN-ECO-BTM-01",
  "connectorId": 1,
  "csChargingProfiles": {
    "chargingProfileId": 1,
    "stackLevel": 0,
    "chargingProfilePurpose": "TxDefaultProfile",
    "chargingProfileKind": "Relative",
    "chargingSchedule": {
      "chargingRateUnit": "A",  // Amperes
      "chargingSchedulePeriod": [{
        "startPeriod": 0,
        "limit": 33.33  // 8 kW / 240 V = 33.33 A
      }],
      "duration": 9000  // 2.5 hours to charge 20 kWh at 8 kW
    }
  }
}
```

**Translation Algorithm**:
```python
def market_setpoint_to_ocpp_profile(setpoint_kw, voltage_v=240, connector_id=1):
    """
    Convert market setpoint to OCPP SetChargingProfile.
    
    Args:
        setpoint_kw: Power setpoint in kW (negative for charging)
        voltage_v: Charging voltage (default 240V for AC, 400V for DC)
        connector_id: OCPP connector ID
    
    Returns:
        OCPP SetChargingProfile structure
    """
    # Convert kW to Amperes
    power_w = abs(setpoint_kw) * 1000
    current_a = power_w / voltage_v
    
    # Round to nearest 0.1 A
    current_a = round(current_a, 1)
    
    ocpp_profile = {
        "action": "SetChargingProfile",
        "connectorId": connector_id,
        "csChargingProfiles": {
            "chargingProfileId": 1,
            "stackLevel": 0,
            "chargingProfilePurpose": "TxDefaultProfile",
            "chargingProfileKind": "Relative",
            "chargingSchedule": {
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": [{
                    "startPeriod": 0,
                    "limit": current_a
                }]
            }
        }
    }
    
    return ocpp_profile
```

**Translation Toil**: ✅ **Very Low** - Simple unit conversion (kW → Amperes)

---

### 2.3 Telemetry: OCPP MeterValues → Beckn Telemetry

**OCPP MeterValues → Beckn Fulfillment Attributes**:

```json
// OCPP MeterValues
{
  "action": "MeterValues",
  "chargePointId": "IN-ECO-BTM-01",
  "connectorId": 1,
  "transactionId": 12345,
  "meterValue": [{
    "timestamp": "2024-12-15T14:30:00Z",
    "sampledValue": [{
      "value": "5500",  // Energy in Wh
      "context": "Sample.Periodic",
      "format": "Raw",
      "measurand": "Energy.Active.Import.Register",
      "location": "Outlet",
      "unit": "Wh"
    }, {
      "value": "8000",  // Power in W
      "context": "Sample.Periodic",
      "format": "Raw",
      "measurand": "Power.Active.Import",
      "location": "Outlet",
      "unit": "W"
    }, {
      "value": "240",  // Voltage in V
      "context": "Sample.Periodic",
      "format": "Raw",
      "measurand": "Voltage",
      "location": "Outlet",
      "unit": "V"
    }]
  }]
}

// Beckn Fulfillment Attributes
{
  "fulfillmentAttributes": {
    "telemetry": [{
      "eventTime": "2024-12-15T14:30:00Z",
      "metrics": [{
        "name": "ENERGY",
        "value": 5.5,  // Converted from Wh to kWh
        "unitCode": "KWH"
      }, {
        "name": "POWER",
        "value": 8.0,  // Converted from W to kW
        "unitCode": "KW"
      }, {
        "name": "VOLTAGE",
        "value": 240.0,
        "unitCode": "VLT"
      }]
    }]
  }
}
```

**Translation Algorithm**:
```python
def ocpp_meter_values_to_beckn_telemetry(ocpp_meter_values):
    """
    Convert OCPP MeterValues to Beckn telemetry.
    
    OCPP measurands → Beckn metric names:
    - Energy.Active.Import.Register → ENERGY
    - Power.Active.Import → POWER
    - Voltage → VOLTAGE
    - Current.Import → CURRENT
    - Frequency → FREQUENCY
    """
    telemetry = []
    
    for meter_value in ocpp_meter_values.get('meterValue', []):
        metrics = []
        
        for sampled_value in meter_value.get('sampledValue', []):
            measurand = sampled_value.get('measurand', '')
            value = float(sampled_value.get('value', 0))
            unit = sampled_value.get('unit', '')
            
            # Map OCPP measurand to Beckn metric name
            metric_name = {
                'Energy.Active.Import.Register': 'ENERGY',
                'Energy.Active.Export.Register': 'ENERGY',
                'Power.Active.Import': 'POWER',
                'Power.Active.Export': 'POWER',
                'Voltage': 'VOLTAGE',
                'Current.Import': 'CURRENT',
                'Current.Export': 'CURRENT',
                'Frequency': 'FREQUENCY'
            }.get(measurand, 'UNKNOWN')
            
            # Convert units
            if unit == 'Wh' and metric_name == 'ENERGY':
                value = value / 1000  # Wh → kWh
                unit_code = 'KWH'
            elif unit == 'W' and metric_name == 'POWER':
                value = value / 1000  # W → kW
                unit_code = 'KW'
            elif unit == 'V':
                unit_code = 'VLT'
            elif unit == 'A':
                unit_code = 'AMP'
            elif unit == 'Hz':
                unit_code = 'HZ'
            else:
                unit_code = unit
            
            metrics.append({
                "name": metric_name,
                "value": value,
                "unitCode": unit_code
            })
        
        telemetry.append({
            "eventTime": meter_value.get('timestamp'),
            "metrics": metrics
        })
    
    return telemetry
```

**Translation Toil**: ✅ **Low** - Structured mapping with unit conversion

---

### 2.4 Status: OCPP StatusNotification → Beckn Availability

**OCPP Status → Beckn Item Status**:

```json
// OCPP StatusNotification
{
  "action": "StatusNotification",
  "chargePointId": "IN-ECO-BTM-01",
  "connectorId": 1,
  "connectorStatus": "Available",
  "errorCode": "NoError",
  "timestamp": "2024-12-15T14:30:00Z"
}

// Beckn Item Attributes
{
  "itemAttributes": {
    "stationStatus": "Available",  // Direct mapping
    "connectorStatus": "Available",
    "lastStatusUpdate": "2024-12-15T14:30:00Z"
  }
}
```

**Status Mapping**:
| OCPP Status | Beckn Status | Notes |
|-------------|--------------|-------|
| `Available` | `Available` | Direct mapping |
| `Preparing` | `Occupied` | Charging preparation |
| `Charging` | `Occupied` | Active charging |
| `SuspendedEVSE` | `OutOfService` | Suspended by EVSE |
| `SuspendedEV` | `Occupied` | Suspended by EV |
| `Finishing` | `Occupied` | Charging finishing |
| `Reserved` | `Occupied` | Reserved |
| `Unavailable` | `OutOfService` | Unavailable |
| `Faulted` | `OutOfService` | Fault condition |

**Translation Toil**: ✅ **Very Low** - Direct enum mapping

---

### 2.5 Bid Curve Construction from OCPP Capabilities

**OCPP GetConfiguration → Beckn Bid Curve**:

```json
// OCPP GetConfiguration Response
{
  "configurationKey": [{
    "key": "ChargePointMaxPower",
    "value": "60000",  // 60 kW
    "readonly": false
  }, {
    "key": "ChargePointMinPower",
    "value": "5000",  // 5 kW
    "readonly": false
  }, {
    "key": "MeterValueSampleInterval",
    "value": "30",  // 30 seconds
    "readonly": false
  }]
}

// Beckn Bid Curve (constructed from capabilities)
{
  "itemAttributes": {
    "bidCurve": [
      { "price": 0.15, "powerKW": 0 },
      { "price": 0.18, "powerKW": 60 }
    ],
    "constraints": {
      "minPowerKW": 5,
      "maxPowerKW": 60,
      "rampRateKWPerMin": 1.0
    }
  }
}
```

**Translation Algorithm**:
```python
def ocpp_capabilities_to_bid_curve(ocpp_config, base_price_per_kwh):
    """
    Construct bid curve from OCPP capabilities.
    
    Creates a simple bid curve with:
    - Zero power at 83% of base price
    - Max power at base price
    """
    max_power_w = int(ocpp_config.get('ChargePointMaxPower', 60000))
    min_power_w = int(ocpp_config.get('ChargePointMinPower', 5000))
    
    max_power_kw = max_power_w / 1000
    min_power_kw = min_power_w / 1000
    
    bid_curve = [
        {"price": base_price_per_kwh * 0.83, "powerKW": 0},
        {"price": base_price_per_kwh, "powerKW": max_power_kw}
    ]
    
    constraints = {
        "minPowerKW": min_power_kw,
        "maxPowerKW": max_power_kw,
        "rampRateKWPerMin": 1.0  # Default assumption
    }
    
    return {
        "bidCurve": bid_curve,
        "constraints": constraints
    }
```

**Translation Toil**: ✅ **Low** - Simple construction from device capabilities

---

### 2.6 OCPP Integration Summary

| Integration Point | OCPP Source | Beckn Target | Toil Level |
|-------------------|-------------|--------------|------------|
| **Setpoint → SetChargingProfile** | Market setpoint (kW) | `SetChargingProfile` (A) | ✅ Very Low |
| **MeterValues → Telemetry** | `MeterValues` | `fulfillmentAttributes.telemetry` | ✅ Low |
| **StatusNotification → Availability** | `connectorStatus` | `itemAttributes.stationStatus` | ✅ Very Low |
| **Capabilities → Bid Curve** | `GetConfiguration` | `itemAttributes.bidCurve` | ✅ Low |
| **Transaction → Fulfillment** | `StartTransaction` / `StopTransaction` | `fulfillmentAttributes` | ✅ Low |

**Overall Toil Assessment**: ✅ **Low** - OCPP integration requires unit conversion but is straightforward.

---

## 3. IEEE 2030.5 Integration

### 3.1 Role and Scope

**IEEE 2030.5 (Smart Energy Profile 2.0)** focuses on:
- **DER Control**: Grid-integrated distributed energy resources
- **Device Discovery**: EndDeviceList and capability queries
- **Telemetry**: MeterReading and DERStatus
- **Grid Services**: Frequency regulation, voltage support

**Integration Boundary**: IEEE 2030.5 handles DER communication; Beckn/DEG handles market coordination and setpoint distribution.

### 3.2 Device Discovery: EndDeviceList → Energy Resources

**IEEE 2030.5 Discovery → Beckn Resources**:

```json
// IEEE 2030.5 GET /edev
{
  "EndDeviceList": {
    "EndDevice": [{
      "mRID": "100200300",
      "sFDI": "12345678",
      "lFDI": "ABCDEF1234567890",
      "deviceCategory": "00000040",  // Bit 21 = Photovoltaic System
      "FunctionSetAssignmentsListLink": {
        "href": "/edev/100200300/fsa"
      },
      "DERListLink": {
        "href": "/edev/100200300/der"
      }
    }, {
      "mRID": "200300400",
      "deviceCategory": "00000080",  // Bit 22 = Storage System
      "DERListLink": {
        "href": "/edev/200300400/der"
      }
    }]
  }
}

// Beckn Resources (in on_discover)
{
  "beckn:items": [{
    "beckn:id": "ieee.der.solar-panel-001",
    "beckn:itemAttributes": {
      "mRID": "100200300",
      "deviceCategory": "PHOTOVOLTAIC_SYSTEM",
      "era": "ieee.der.100200300"
    }
  }, {
    "beckn:id": "ieee.der.battery-001",
    "beckn:itemAttributes": {
      "mRID": "200300400",
      "deviceCategory": "STORAGE_SYSTEM",
      "era": "ieee.der.200300400"
    }
  }]
}
```

**Device Category Mapping**:
| IEEE 2030.5 Bit | Device Category | Beckn Enum |
|-----------------|------------------|------------|
| Bit 6 (0x40) | Photovoltaic System | `PHOTOVOLTAIC_SYSTEM` |
| Bit 7 (0x80) | Storage System | `STORAGE_SYSTEM` |
| Bit 8 (0x100) | Electric Vehicle | `ELECTRIC_VEHICLE` |
| Bit 9 (0x200) | EVSE | `EVSE` |
| Bit 10 (0x400) | Combined PV and Storage | `HYBRID_SYSTEM` |

**Translation Toil**: ✅ **Low** - Bitmap to enum mapping

---

### 3.3 DER Capability → Bid Curve Construction

**IEEE 2030.5 DERCapability → Beckn Bid Curve**:

```json
// IEEE 2030.5 GET /edev/{mRID}/der
{
  "DER": {
    "DERCapability": {
      "modesSupported": "00000080",  // Bit 7 = opModFixedW
      "rtgMaxW": 5000,  // 5 kW
      "rtgMaxVar": 2000,  // 2 kVAR
      "rtgMaxWh": 10000,  // 10 kWh (for storage)
      "rtgRampUpWPerS": 100,  // 100 W/s ramp rate
      "rtgRampDownWPerS": 100
    }
  }
}

// Beckn Bid Curve (constructed from capabilities)
{
  "itemAttributes": {
    "bidCurve": [
      { "price": 0.05, "powerKW": 0 },
      { "price": 0.06, "powerKW": 2 },
      { "price": 0.07, "powerKW": 5 }
    ],
    "constraints": {
      "maxPowerKW": 5,
      "minPowerKW": 0,
      "rampRateKWPerMin": 6.0  // 100 W/s = 6 kW/min
    }
  }
}
```

**Translation Algorithm**:
```python
def ieee_der_capability_to_bid_curve(der_capability, base_price_per_kwh=0.06):
    """
    Construct bid curve from IEEE 2030.5 DER capability.
    
    Creates a bid curve with:
    - Zero power at 83% of base price
    - 40% power at 90% of base price
    - Max power at base price
    """
    rtg_max_w = der_capability.get('rtgMaxW', 0)
    rtg_max_kw = rtg_max_w / 1000
    
    # Ramp rate conversion: W/s → kW/min
    ramp_up_w_per_s = der_capability.get('rtgRampUpWPerS', 100)
    ramp_rate_kw_per_min = (ramp_up_w_per_s * 60) / 1000
    
    bid_curve = [
        {"price": base_price_per_kwh * 0.83, "powerKW": 0},
        {"price": base_price_per_kwh * 0.90, "powerKW": rtg_max_kw * 0.4},
        {"price": base_price_per_kwh, "powerKW": rtg_max_kw}
    ]
    
    constraints = {
        "maxPowerKW": rtg_max_kw,
        "minPowerKW": 0,
        "rampRateKWPerMin": ramp_rate_kw_per_min
    }
    
    return {
        "bidCurve": bid_curve,
        "constraints": constraints
    }
```

**Translation Toil**: ✅ **Low** - Simple construction from device capabilities

---

### 3.4 Market Setpoint → IEEE 2030.5 DERControl

**Market Setpoint → IEEE 2030.5 Command**:

```json
// Beckn Market Setpoint (from orderAttributes)
{
  "orderAttributes": {
    "setpointKW": 3.5,  // Positive = generation
    "clearingPrice": 0.075,
    "objectives": {
      "targetGenerationKWh": 7.0,
      "deadline": "2024-12-15T16:00:00Z"
    }
  },
  "itemAttributes": {
    "mRID": "100200300",
    "constraints": {
      "maxPowerKW": 5.0
    }
  }
}

// IEEE 2030.5 DERControl Command
{
  "method": "PUT",
  "uri": "/edev/100200300/der/dc",
  "body": {
    "DERControl": {
      "mRID": "100200300",
      "DERControlBase": {
        "opModFixedW": 7000,  // 70.00% of 5 kW = 3.5 kW
        "opModTargetVar": 0   // No reactive power control
      },
      "deviceCategory": "00000040",  // Photovoltaic System
      "startTime": 1702656000,  // Unix timestamp
      "duration": 7200  // 2 hours
    }
  }
}
```

**Translation Algorithm**:
```python
def market_setpoint_to_ieee_der_control(setpoint_kw, mrid, max_power_kw, device_category, start_time, duration):
    """
    Convert market setpoint to IEEE 2030.5 DERControl.
    
    Args:
        setpoint_kw: Power setpoint in kW (positive = generation, negative = consumption)
        mrid: IEEE 2030.5 mRID
        max_power_kw: Maximum power rating in kW
        device_category: IEEE 2030.5 device category bitmap
        start_time: Unix timestamp for start
        duration: Duration in seconds
    
    Returns:
        IEEE 2030.5 DERControl structure
    """
    # Calculate percentage of max power
    # IEEE 2030.5 uses int16 in hundredths of percent
    percent_of_max = (setpoint_kw / max_power_kw) * 100
    op_mod_fixed_w = int(percent_of_max * 100)  # Convert to hundredths
    
    # Clamp to valid range (-10000 to 10000)
    op_mod_fixed_w = max(-10000, min(10000, op_mod_fixed_w))
    
    der_control = {
        "method": "PUT",
        "uri": f"/edev/{mrid}/der/dc",
        "body": {
            "DERControl": {
                "mRID": mrid,
                "DERControlBase": {
                    "opModFixedW": op_mod_fixed_w,
                    "opModTargetVar": 0  # No reactive power by default
                },
                "deviceCategory": device_category,
                "startTime": start_time,
                "duration": duration
            }
        }
    }
    
    return der_control
```

**Translation Toil**: ✅ **Low** - Percentage calculation with range clamping

---

### 3.5 Telemetry: IEEE 2030.5 MeterReading → Beckn Telemetry

**IEEE 2030.5 MeterReading → Beckn Fulfillment Attributes**:

```json
// IEEE 2030.5 GET /edev/{mRID}/mr
{
  "MeterReading": {
    "ReadingSetList": {
      "ReadingSet": [{
        "ReadingList": {
          "Reading": [{
            "value": 3500,  // Power in W
            "timePeriod": {
              "start": 1702656000
            },
            "ReadingType": {
              "accumulationBehaviour": "instantaneous",
              "commodity": "energy",
              "dataQualifier": "average",
              "flowDirection": 1,  // 1 = Forward (generation), 2 = Reverse (consumption)
              "measuringPeriod": 0,
              "unit": "W"
            }
          }]
        }
      }]
    }
  }
}

// Beckn Fulfillment Attributes
{
  "fulfillmentAttributes": {
    "telemetry": [{
      "eventTime": "2024-12-15T14:00:00Z",
      "metrics": [{
        "name": "POWER",
        "value": 3.5,  // Converted from W to kW
        "unitCode": "KW",
        "flowDirection": "FORWARD"  // 1 = FORWARD, 2 = REVERSE
      }]
    }]
  }
}
```

**Translation Algorithm**:
```python
def ieee_meter_reading_to_beckn_telemetry(ieee_meter_reading):
    """
    Convert IEEE 2030.5 MeterReading to Beckn telemetry.
    
    IEEE 2030.5 ReadingType → Beckn metric names:
    - commodity="energy", unit="W" → POWER
    - commodity="energy", unit="Wh" → ENERGY
    - unit="V" → VOLTAGE
    - unit="A" → CURRENT
    - unit="Hz" → FREQUENCY
    """
    telemetry = []
    
    reading_sets = ieee_meter_reading.get('MeterReading', {}).get('ReadingSetList', {}).get('ReadingSet', [])
    
    for reading_set in reading_sets:
        readings = reading_set.get('ReadingList', {}).get('Reading', [])
        metrics = []
        
        for reading in readings:
            value = reading.get('value', 0)
            reading_type = reading.get('ReadingType', {})
            unit = reading_type.get('unit', '')
            commodity = reading_type.get('commodity', '')
            flow_direction = reading_type.get('flowDirection', 0)
            
            # Map to Beckn metric
            if commodity == 'energy' and unit == 'W':
                metric_name = 'POWER'
                value = value / 1000  # W → kW
                unit_code = 'KW'
            elif commodity == 'energy' and unit == 'Wh':
                metric_name = 'ENERGY'
                value = value / 1000  # Wh → kWh
                unit_code = 'KWH'
            elif unit == 'V':
                metric_name = 'VOLTAGE'
                unit_code = 'VLT'
            elif unit == 'A':
                metric_name = 'CURRENT'
                unit_code = 'AMP'
            elif unit == 'Hz':
                metric_name = 'FREQUENCY'
                unit_code = 'HZ'
            else:
                continue  # Skip unknown metrics
            
            # Map flow direction
            flow_direction_str = 'FORWARD' if flow_direction == 1 else 'REVERSE'
            
            metrics.append({
                "name": metric_name,
                "value": value,
                "unitCode": unit_code,
                "flowDirection": flow_direction_str
            })
        
        if metrics:
            time_period = readings[0].get('timePeriod', {}) if readings else {}
            start_time = time_period.get('start', 0)
            
            telemetry.append({
                "eventTime": datetime.fromtimestamp(start_time).isoformat() + 'Z',
                "metrics": metrics
            })
    
    return telemetry
```

**Translation Toil**: ✅ **Low** - Structured mapping with unit conversion

---

### 3.6 DERStatus → Beckn Status

**IEEE 2030.5 DERStatus → Beckn Item Status**:

```json
// IEEE 2030.5 GET /edev/{mRID}/der/stat
{
  "DERStatus": {
    "readingTime": 1702656000,
    "statW": 3500,  // Current active power in W
    "statVar": 0,   // Current reactive power in VAR
    "statVA": 3500,  // Current apparent power in VA
    "statWh": 10000  // Current energy (for storage) in Wh
  }
}

// Beckn Item Attributes
{
  "itemAttributes": {
    "currentPowerKW": 3.5,  // Converted from W to kW
    "currentEnergyKWh": 10.0,  // Converted from Wh to kWh
    "status": "ACTIVE",
    "lastStatusUpdate": "2024-12-15T14:00:00Z"
  }
}
```

**Translation Toil**: ✅ **Very Low** - Simple unit conversion

---

### 3.7 Grid Topology Awareness

**IEEE 2030.5 DeviceInformation → Grid Node Mapping**:

```json
// IEEE 2030.5 GET /edev/{mRID}/di
{
  "DeviceInformation": {
    "deviceInformationLink": {
      "href": "/edev/100200300/di"
    },
    "pollRate": 900
  }
}

// Custom Grid Topology Map (maintained by coordination layer)
{
  "gridTopology": {
    "transformer-zone-5": {
      "era": "transformer.zone-5",
      "devices": [
        { "mRID": "100200300", "era": "ieee.der.solar-panel-001" },
        { "mRID": "200300400", "era": "ieee.der.battery-001" }
      ],
      "locationalPriceAdder": {
        "basePrice": 0.10,
        "currentLoadPercent": 75,
        "priceAdderPerPercent": 0.001
      }
    }
  }
}
```

**Translation Toil**: ✅ **Low** - Custom topology mapping (not in IEEE 2030.5 spec)

---

### 3.8 IEEE 2030.5 Integration Summary

| Integration Point | IEEE 2030.5 Source | Beckn Target | Toil Level |
|-------------------|-------------------|--------------|------------|
| **EndDeviceList → Resources** | `GET /edev` | `beckn:items` | ✅ Low |
| **DERCapability → Bid Curve** | `GET /edev/{mRID}/der` | `itemAttributes.bidCurve` | ✅ Low |
| **Setpoint → DERControl** | Market setpoint (kW) | `PUT /edev/{mRID}/der/dc` | ✅ Low |
| **MeterReading → Telemetry** | `GET /edev/{mRID}/mr` | `fulfillmentAttributes.telemetry` | ✅ Low |
| **DERStatus → Status** | `GET /edev/{mRID}/der/stat` | `itemAttributes.status` | ✅ Very Low |
| **Grid Topology** | Custom mapping | `itemAttributes.locationalPriceAdder` | ✅ Low |

**Overall Toil Assessment**: ✅ **Low** - IEEE 2030.5 integration requires percentage calculations but is well-structured.

---

## 4. Bid Curve Translation Patterns

### 4.1 Fixed Pricing → Bid Curve

**Pattern**: Convert fixed price to simple bid curve

```python
def fixed_price_to_bid_curve(price_per_kwh, max_power_kw):
    """
    Convert fixed price to bid curve.
    
    Creates a simple bid curve:
    - Zero power at 83% of price (willing to participate at lower price)
    - Max power at base price
    """
    return [
        {"price": price_per_kwh * 0.83, "powerKW": 0},
        {"price": price_per_kwh, "powerKW": max_power_kw}
    ]
```

**Use Cases**:
- OCPI tariffs → Bid curves
- OCPP capabilities → Bid curves
- IEEE 2030.5 DER capabilities → Bid curves

---

### 4.2 Time-of-Use Pricing → Bid Curve

**Pattern**: Convert time-of-use tariff to time-dependent bid curves

```python
def time_of_use_to_bid_curves(tou_tariff, max_power_kw):
    """
    Convert time-of-use tariff to multiple bid curves.
    
    Returns bid curves for each time period.
    """
    bid_curves = {}
    
    for period in tou_tariff['periods']:
        price = period['price_per_kwh']
        start_time = period['start_time']
        end_time = period['end_time']
        
        bid_curves[f"{start_time}-{end_time}"] = [
            {"price": price * 0.83, "powerKW": 0},
            {"price": price, "powerKW": max_power_kw}
        ]
    
    return bid_curves
```

**Use Cases**:
- OCPI time-of-use tariffs
- Utility time-of-use rates

---

### 4.3 Opportunity Cost → Bid Curve

**Pattern**: Construct bid curve from resource opportunity cost

```python
def opportunity_cost_to_bid_curve(resource_state, objectives, forecasts):
    """
    Construct bid curve from resource opportunity cost.
    
    For generators:
    - Base price = marginal cost
    - Higher prices = more generation
    
    For consumers:
    - Base price = willingness to pay
    - Lower prices = more consumption
    """
    base_price = calculate_opportunity_cost(resource_state, objectives)
    
    if forecasts:
        forecast_price = forecasts.get('expectedPrice', base_price)
        base_price = (base_price + forecast_price) / 2
    
    # Generate price/power pairs
    bid_curve = []
    for power_level in power_levels:
        price = base_price + calculate_price_adjustment(power_level)
        bid_curve.append({
            "price": price,
            "powerKW": power_level
        })
    
    return sorted(bid_curve, key=lambda x: x['price'])
```

**Use Cases**:
- EV charging (opportunity cost = urgency)
- Battery storage (opportunity cost = state of charge)
- Solar generation (opportunity cost = curtailment risk)

---

## 5. Market Clearing Integration

### 5.1 Bid Curve Aggregation

**Pattern**: Aggregate bid curves from multiple resources

```python
def aggregate_bid_curves(bid_curves, locational_adders=None):
    """
    Aggregate bid curves from multiple resources.
    
    Steps:
    1. Sort all price points
    2. For each price, sum power from all curves
    3. Apply locational adders if provided
    4. Return aggregated supply and demand curves
    """
    # Collect all price points
    all_prices = set()
    for curve in bid_curves:
        for point in curve:
            all_prices.add(point['price'])
    
    # Sort prices
    sorted_prices = sorted(all_prices)
    
    # Aggregate supply and demand
    aggregated_supply = []
    aggregated_demand = []
    
    for price in sorted_prices:
        supply_power = 0
        demand_power = 0
        
        for curve in bid_curves:
            for i, point in enumerate(curve):
                if point['price'] <= price:
                    power = point['powerKW']
                    if power > 0:
                        supply_power += power
                    elif power < 0:
                        demand_power += abs(power)
        
        # Apply locational adders
        if locational_adders:
            for node, adder in locational_adders.items():
                if price >= adder['basePrice']:
                    price += adder['currentPrice'] - adder['basePrice']
        
        aggregated_supply.append({"price": price, "powerKW": supply_power})
        aggregated_demand.append({"price": price, "powerKW": demand_power})
    
    return {
        "supplyCurve": aggregated_supply,
        "demandCurve": aggregated_demand
    }
```

---

### 5.2 Market Clearing Algorithm

**Pattern**: Find clearing price from aggregated curves

```python
def clear_market(aggregated_supply, aggregated_demand):
    """
    Find market clearing price.
    
    Steps:
    1. Find intersection of supply and demand curves
    2. Interpolate if needed
    3. Return clearing price and quantity
    """
    # Find intersection
    clearing_price = None
    clearing_quantity = None
    
    for i in range(len(aggregated_supply) - 1):
        supply_1 = aggregated_supply[i]
        supply_2 = aggregated_supply[i + 1]
        demand_1 = aggregated_demand[i]
        demand_2 = aggregated_demand[i + 1]
        
        # Check if supply and demand intersect in this range
        if (supply_1['powerKW'] <= demand_1['powerKW'] and
            supply_2['powerKW'] >= demand_2['powerKW']):
            # Interpolate
            price_diff = supply_2['price'] - supply_1['price']
            supply_diff = supply_2['powerKW'] - supply_1['powerKW']
            demand_diff = demand_2['powerKW'] - demand_1['powerKW']
            
            # Linear interpolation
            clearing_price = supply_1['price'] + (
                (demand_1['powerKW'] - supply_1['powerKW']) /
                (supply_diff - demand_diff)
            ) * price_diff
            
            clearing_quantity = supply_1['powerKW'] + (
                (clearing_price - supply_1['price']) / price_diff
            ) * supply_diff
            
            break
    
    return {
        "clearingPrice": clearing_price,
        "clearingQuantityKW": clearing_quantity
    }
```

---

### 5.3 Economic Disaggregation

**Pattern**: Distribute setpoints to individual resources

```python
def economic_disaggregation(clearing_price, resource_bid_curves):
    """
    Disaggregate clearing price to individual resource setpoints.
    
    Steps:
    1. For each resource, find setpoint at clearing price
    2. Interpolate if needed
    3. Apply constraints
    4. Return setpoints
    """
    setpoints = {}
    
    for resource_era, bid_curve in resource_bid_curves.items():
        # Find setpoint at clearing price
        setpoint = interpolate_bid_curve(bid_curve, clearing_price)
        
        # Apply constraints
        constraints = resource_bid_curves[resource_era].get('constraints', {})
        setpoint = apply_constraints(setpoint, constraints)
        
        setpoints[resource_era] = {
            "setpointKW": setpoint,
            "clearingPrice": clearing_price
        }
    
    return setpoints
```

---

## 6. Translation Toil Assessment

### 6.1 Overall Assessment

| Protocol | Integration Complexity | Translation Toil | Notes |
|----------|------------------------|-----------------|-------|
| **OCPI** | Low | ✅ **Low** | Direct field mappings, simple unit conversions |
| **OCPP** | Low | ✅ **Low** | Unit conversion (kW ↔ Amperes), structured mappings |
| **IEEE 2030.5** | Medium | ✅ **Low** | Percentage calculations, bitmap decoding |

**Overall Assessment**: ✅ **Low Translation Toil**

All three protocols integrate cleanly with Beckn building blocks. The coordination layer provides a thin glue that enables interoperability without significant translation overhead.

---

### 6.2 Translation Complexity Breakdown

**OCPI**:
- ✅ ERA mapping: Direct string mapping
- ✅ Catalogue: Field mapping with unit conversion
- ✅ Tariff → Bid curve: Simple price conversion
- ✅ CDR → Settlement: Structured field mapping

**OCPP**:
- ✅ Setpoint → SetChargingProfile: kW to Amperes conversion
- ✅ MeterValues → Telemetry: Unit conversion (W → kW, Wh → kWh)
- ✅ Status → Availability: Direct enum mapping
- ✅ Capabilities → Bid curve: Simple construction

**IEEE 2030.5**:
- ✅ EndDeviceList → Resources: Bitmap to enum mapping
- ✅ DERCapability → Bid curve: Simple construction
- ✅ Setpoint → DERControl: Percentage calculation
- ✅ MeterReading → Telemetry: Unit conversion
- ✅ Grid topology: Custom mapping (not in spec)

---

### 6.3 Reusability of Protocol Enums

**Key Principle**: Reuse protocol enums, don't reinvent them.

**OCPI Enums Reused**:
- Connector standards: `IEC_62196_T2_COMBO` → `CCS2`
- Power types: `AC_3_PHASE`, `DC`
- Connector formats: `SOCKET`, `CABLE`

**OCPP Enums Reused**:
- Connector status: `Available`, `Charging`, `Unavailable`
- Measurands: `Energy.Active.Import.Register`, `Power.Active.Import`

**IEEE 2030.5 Enums Reused**:
- Device categories: Bitmap values
- Control modes: `opModFixedW`, `opModTargetW`
- Flow directions: `1` (Forward), `2` (Reverse)

**Translation Toil Reduction**: ✅ **Significant** - Reusing enums eliminates translation overhead.

---

## 7. Summary

### 7.1 Key Integration Patterns

1. **ERA Mapping**: Direct string mapping from protocol IDs to ERAs
2. **Bid Curve Construction**: Simple algorithms from device capabilities or tariffs
3. **Setpoint Translation**: Unit conversion (kW ↔ Amperes, percentage calculations)
4. **Telemetry Mapping**: Structured field mapping with unit conversion
5. **Settlement Mapping**: Structured field mapping from protocol records

### 7.2 Translation Toil Summary

- **OCPI**: ✅ Low - Direct mappings, simple conversions
- **OCPP**: ✅ Low - Unit conversions, structured mappings
- **IEEE 2030.5**: ✅ Low - Percentage calculations, bitmap decoding

**Overall**: ✅ **Low Translation Toil** - All protocols integrate cleanly with minimal overhead.

### 7.3 Best Practices

1. **Reuse Protocol Enums**: Don't reinvent connector types, power types, etc.
2. **Maintain Unit Consistency**: Convert units at protocol boundaries
3. **Preserve Protocol Semantics**: Map protocol concepts to Beckn attributes accurately
4. **Handle Edge Cases**: Account for missing fields, null values, etc.
5. **Cache Protocol Data**: Reduce API calls by caching device capabilities

---

**Status**: Complete  
**Next Action**: Design JSON-LD schemas for extensions (Phase 2)

