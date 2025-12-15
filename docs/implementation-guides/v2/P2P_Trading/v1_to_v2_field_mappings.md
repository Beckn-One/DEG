# Field Mapping Reference between Beckn 1.0 and 2.0 protocols and P2P trading implementation <!-- omit from toc -->

## Table of Contents  <!-- omit from toc -->
- [1. v1 to v2 Field Mapping](#1-v1-to-v2-field-mapping)
- [2. Meter ID Format Migration](#2-meter-id-format-migration)
- [3. Integration Patterns](#3-integration-patterns)
  - [3.1. Attaching Attributes to Core Objects](#31-attaching-attributes-to-core-objects)
  - [3.2. JSON-LD Context Usage](#32-json-ld-context-usage)
  - [3.3. Discovery Filtering](#33-discovery-filtering)
- [4. Best Practices](#4-best-practices)
  - [4.1. Discovery Optimization](#41-discovery-optimization)
  - [4.2. Meter ID Handling](#42-meter-id-handling)
  - [4.3. Settlement Cycle Management](#43-settlement-cycle-management)
  - [4.4. Meter Readings](#44-meter-readings)
  - [4.5. Telemetry Data](#45-telemetry-data)
  - [4.6. Error Handling](#46-error-handling)
- [5. Migration from v1](#5-migration-from-v1)
  - [5.1. Key Changes](#51-key-changes)
  - [5.2. Migration Checklist](#52-migration-checklist)
  - [5.3. Example Migration](#53-example-migration)
- [6. Key Differences from v1](#6-key-differences-from-v1)
      - [6.0.0.1. Discover/Search Request](#6001-discoversearch-request)
      - [6.0.0.2. Item Attributes](#6002-item-attributes)
      - [6.0.0.3. Order Attributes](#6003-order-attributes)
      - [6.0.0.4. Fulfillment Stops](#6004-fulfillment-stops)


# 1. v1 to v2 Field Mapping

| v1 Location                 | v2 Location                      | Notes                 |
| --------------------------- | -------------------------------- | --------------------- |
| `Item.attributes.*`         | `Item.itemAttributes.*`          | Attribute path change |
| `Offer.attributes.*`        | `Offer.offerAttributes.*`        | Attribute path change |
| `Order.attributes.*`        | `Order.orderAttributes.*`        | Attribute path change |
| `Fulfillment.attributes.*`  | `Fulfillment.attributes.*`       | No change             |
| `der://meter/{id}`          | `{id}` (IEEE mRID)               | Format change         |
| `Tag.value` (energy source) | `itemAttributes.sourceType`      | Direct attribute      |
| `Tag.value` (settlement)    | `offerAttributes.settlementType` | Direct attribute      |

# 2. Meter ID Format Migration

**v1 Format**: `der://pge.meter/100200300`  
**v2 Format**: `100200300` (IEEE 2030.5 mRID)

**Migration Rule**: Extract the numeric ID from the `der://` URI.


# 3. Integration Patterns

## 3.1. Attaching Attributes to Core Objects

**Item with EnergyResource**:
```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/context.jsonld",
  "@type": "beckn:Item",
  "beckn:id": "energy-resource-solar-001",
  "beckn:descriptor": {
    "@type": "beckn:Descriptor",
    "schema:name": "Solar Energy - 30.5 kWh"
  },
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "deliveryMode": "GRID_INJECTION",
    "meterId": "100200300"
  }
}
```

**Offer with EnergyTradeOffer**:
```json
{
  "@type": "beckn:Offer",
  "beckn:id": "offer-energy-001",
  "beckn:offerAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyTradeOffer/v0.2/context.jsonld",
    "@type": "EnergyTradeOffer",
    "pricingModel": "PER_KWH",
    "settlementType": "DAILY"
  }
}
```

**Order with EnergyTradeContract**:
```json
{
  "@type": "beckn:Order",
  "beckn:id": "order-energy-001",
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyTradeContract/v0.2/context.jsonld",
    "@type": "EnergyTradeContract",
    "contractStatus": "ACTIVE",
    "sourceMeterId": "100200300",
    "targetMeterId": "98765456"
  }
}
```

**Fulfillment with EnergyTradeDelivery**:
```json
{
  "@type": "beckn:Fulfillment",
  "beckn:id": "fulfillment-energy-001",
  "beckn:attributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyTradeDelivery/v0.2/context.jsonld",
    "@type": "EnergyTradeDelivery",
    "deliveryStatus": "IN_PROGRESS",
    "meterReadings": [...]
  }
}
```

## 3.2. JSON-LD Context Usage

All attribute bundles include `@context` and `@type`:
- `@context`: Points to the context.jsonld file for the attribute bundle
- `@type`: The schema type (EnergyResource, EnergyTradeOffer, etc.)

## 3.3. Discovery Filtering

Use JSONPath filters to search by energy attributes:

```json
{
  "filters": {
    "type": "jsonpath",
    "expression": "$[?(@.itemAttributes.sourceType == 'SOLAR' && @.itemAttributes.deliveryMode == 'GRID_INJECTION' && @.itemAttributes.availableQuantity >= 10.0)]"
  }
}
```

---

# 4. Best Practices

## 4.1. Discovery Optimization

- **Index Key Fields**: Index `itemAttributes.sourceType`, `itemAttributes.deliveryMode`, `itemAttributes.meterId`, `itemAttributes.availableQuantity`
- **Use JSONPath Filters**: Leverage JSONPath for complex filtering
- **Minimal Fields**: Return minimal fields in list/search APIs (see profile.json)

## 4.2. Meter ID Handling

- **Use IEEE mRID Format**: Always use plain identifier (e.g., `"100200300"`), not `der://` format
- **PII Treatment**: Treat meter IDs as PII - do not index, redact in logs, encrypt at rest
- **Discovery**: Meter IDs enable meter-based discovery (provider names not required)

## 4.3. Settlement Cycle Management

- **Initialize on Confirm**: Create settlement cycle when order is confirmed
- **Update on Delivery**: Link deliveries to settlement cycles via `settlementCycleId`
- **Status Tracking**: Track settlement cycle status (PENDING → SETTLED → FAILED)
- **Amount Calculation**: Calculate settlement amount based on delivered quantity and pricing

## 4.4. Meter Readings

- **Regular Updates**: Update meter readings during delivery (every 15-30 minutes)
- **Energy Flow Calculation**: Calculate `energyFlow` as difference between readings
- **Source and Target**: Track both source and target meter readings
- **Timestamp Accuracy**: Use accurate timestamps (ISO 8601 format)

## 4.5. Telemetry Data

- **Metric Selection**: Include relevant metrics (ENERGY, POWER, VOLTAGE, CURRENT, FREQUENCY)
- **Unit Codes**: Use correct unit codes (KWH, KW, VLT, AMP, HZ)
- **Update Frequency**: Update telemetry every 5-15 minutes during active delivery
- **Data Retention**: Retain telemetry data for billing and audit purposes

## 4.6. Error Handling

- **Validation Errors**: Validate all required fields before processing
- **Meter ID Format**: Validate meter IDs are IEEE mRID format
- **Quantity Validation**: Ensure quantities are within min/max limits
- **Time Window Validation**: Validate production windows and validity windows

---

# 5. Migration from v1

## 5.1. Key Changes

1. **Attribute Paths**: Change `attributes.*` to `itemAttributes.*`, `offerAttributes.*`, `orderAttributes.*`
2. **Meter Format**: Convert `der://meter/{id}` to `{id}` (IEEE mRID)
3. **Tag Values**: Convert `Tag.value` to direct attribute fields
4. **JSON-LD**: Add `@context` and `@type` to all attribute objects

## 5.2. Migration Checklist

- Update attribute paths (`attributes.*` → `itemAttributes.*`, etc.)
- Convert meter IDs from `der://` format to IEEE mRID
- Replace `Tag.value` with direct attribute fields
- Add JSON-LD context to all attribute objects
- Update discovery filters to use new attribute paths
- Update validation logic for new schema structure
- Test all transaction flows
- Update documentation

## 5.3. Example Migration

**v1 Format**:
```json
{
  "Item": {
    "attributes": {
      "sourceType": "SOLAR",
      "meterId": "der://pge.meter/100200300"
    }
  },
  "Tag": {
    "value": "SOLAR"
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Item",
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "meterId": "100200300"
  }
}
```


# 6. Key Differences from v1

| Aspect                 | v1 (Layer2)         | v2 (Composable)              |
| ---------------------- | ------------------- | ---------------------------- |
| **Schema Extension**   | `allOf` in paths    | Composable attribute bundles |
| **Attribute Location** | `Item.attributes.*` | `Item.itemAttributes.*`      |
| **Meter Format**       | `der://meter/{id}`  | IEEE 2030.5 mRID `{id}`      |
| **JSON-LD**            | Not used            | Full JSON-LD support         |
| **Modularity**         | Monolithic          | Modular bundles              |


For developers familiar with v1, here's a quick mapping guide:

#### 6.0.0.1. Discover/Search Request

**v1 Format**:
```json
{
  "message": {
    "intent": {
      "item": {
        "quantity": {
          "selected": {
            "measure": {
              "value": "10",
              "unit": "kWH"
            }
          }
        }
      },
      "fulfillment": {
        "stops": [{
          "type": "end",
          "location": {
            "address": "der://uppcl.meter/98765456"
          },
          "time": {
            "range": {
              "start": "2024-10-04T10:00:00",
              "end": "2024-10-04T18:00:00"
            }
          }
        }]
      }
    }
  }
}
```

**v2 Format** (No intent object - uses JSONPath filters):
```json
{
  "message": {
    "text_search": "solar energy grid injection",
    "filters": {
      "type": "jsonpath",
      "expression": "$[?(@.itemAttributes.sourceType == 'SOLAR' && @.itemAttributes.deliveryMode == 'GRID_INJECTION' && @.itemAttributes.availableQuantity >= 10.0 && @.itemAttributes.productionWindow.start <= '2024-10-04T10:00:00Z' && @.itemAttributes.productionWindow.end >= '2024-10-04T18:00:00Z')]"
    }
  }
}
```

**Changes**:
- ❌ **Removed**: `intent` object is not supported in v2 discover API
- ✅ **Quantity**: v1 `intent.item.quantity.selected.measure.value` → v2 `filters.expression` with `availableQuantity >= 10.0`
- ✅ **Time Range**: v1 `intent.fulfillment.stops[].time.range` → v2 `filters.expression` with `productionWindow.start <= '...' && productionWindow.end >= '...'`
- ✅ **All Parameters**: Expressed via JSONPath filters in v2

#### 6.0.0.2. Item Attributes

**v1 Format**:
```json
{
  "Item": {
    "attributes": {
      "sourceType": "SOLAR",
      "meterId": "der://meter/100200300",
      "availableQuantity": 30.5
    }
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Item",
  "beckn:itemAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyResource/v0.2/context.jsonld",
    "@type": "EnergyResource",
    "sourceType": "SOLAR",
    "meterId": "100200300",
    "availableQuantity": 30.5
  }
}
```

**Changes**:
- ⚠️ Path: `Item.attributes.*` → `beckn:itemAttributes.*`
- ⚠️ Meter format: `der://meter/100200300` → `100200300`
- ➕ Add `@context` and `@type` for JSON-LD

#### 6.0.0.3. Order Attributes

**v1 Format**:
```json
{
  "Order": {
    "attributes": {
      "sourceMeterId": "der://pge.meter/100200300",
      "targetMeterId": "der://ssf.meter/98765456",
      "contractStatus": "ACTIVE"
    }
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Order",
  "beckn:orderAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EnergyTradeContract/v0.2/context.jsonld",
    "@type": "EnergyTradeContract",
    "sourceMeterId": "100200300",
    "targetMeterId": "98765456",
    "contractStatus": "ACTIVE"
  }
}
```

**Changes**:
- ⚠️ Path: `Order.attributes.*` → `beckn:orderAttributes.*`
- ⚠️ Meter format: `der://pge.meter/100200300` → `100200300`
- ➕ Add `@context` and `@type` for JSON-LD

#### 6.0.0.4. Fulfillment Stops

**v1 Format**:
```json
{
  "Fulfillment": {
    "stops": [{
      "type": "start",
      "location": {
        "address": "der://uppcl.meter/92982739"
      }
    }, {
      "type": "end",
      "location": {
        "address": "der://uppcl.meter/98765456"
      }
    }]
  }
}
```

**v2 Format**:
```json
{
  "@type": "beckn:Fulfillment",
  "beckn:stops": [{
    "@type": "beckn:Stop",
    "beckn:type": "START",
    "beckn:location": {
      "@type": "beckn:Location",
      "beckn:address": "92982739"
    }
  }, {
    "@type": "beckn:Stop",
    "beckn:type": "END",
    "beckn:location": {
      "@type": "beckn:Location",
      "beckn:address": "98765456"
    }
  }]
}
```

**Changes**:
- ⚠️ Meter format: `der://uppcl.meter/92982739` → `92982739`
- ⚠️ Type case: `"start"` → `"START"`, `"end"` → `"END"`
- ➕ Add `@type` for JSON-LD

