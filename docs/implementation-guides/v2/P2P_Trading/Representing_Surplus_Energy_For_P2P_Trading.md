# Representing Surplus Energy in a Peer to Peer Energy Trading Ecosystem

### Using schema.org, CIM, and deg:WheelingChargeSpecification

---

## 1. Purpose and Scope

This document specifies how to represent surplus electrical energy, offered by a prosumer into a peer-to-peer (P2P) energy trading ecosystem, using:

* **schema.org** for commercial semantics (offers, prices, quantities, time).
* **IEC CIM** for electrical coverage (which grid / trading zone a transaction belongs to).
* A **custom `deg:` namespace** to:

  * Link offers to CIM grid regions (`deg:electricalCoverage`).
  * Represent wheeling charges as a first-class price component (`deg:WheelingChargeSpecification`).

Scope:

* Conceptual model of surplus energy in P2P trading.
* Mapping of domain concepts (prosumer, surplus energy, time windows, price, electrical coverage, wheeling) to the schemas above.
* Canonical JSON-LD representation pattern that:

  * Works for simple and complex cases (single vs multiple windows).
  * Encodes grid-relevant temporal constraints (day-ahead, cut-off).
  * Is protocol-agnostic and embeddable in other APIs (e.g., Beckn).

Out of scope:

* Settlement, clearing, and billing internals.
* Blockchain tokenization / smart contracts.
* Detailed grid operation (dispatch, balancing algorithms).

---

## 2. Conceptual View of Surplus Energy in P2P Trading

### 2.1 Prosumer

A **prosumer** is an energy consumer who also produces energy (e.g., rooftop solar):

* Generates behind-the-meter energy.
* Sometimes has generation that exceeds their own load.
* Can offer the surplus to peers in the same electrical system.

### 2.2 Surplus Energy

**Surplus energy** is the portion of generated energy that:

* Is not needed for self-consumption in a given time window.
* Can be injected into the grid and traded.
* Is constrained by:

  * **Quantity** (kWh available).
  * **Time** (when it can be delivered).
  * **Electrical coverage** (which grid / DISCOM / zone).
  * **Commercial terms** (price, taxes, wheeling).

### 2.3 P2P Energy Trade

In a P2P trading setting:

* Prosumers publish **offers** describing surplus energy they are willing to sell.
* Consumers (or their agents) discover these offers and place orders.
* The grid operator uses aggregated offers and trades for planning and scheduling within its **CIM-modelled regions**.

### 2.4 Time as a First-Class Constraint

Time is central:

* Grid operators may require **day-ahead** (or intra-day) commitments.
* Each offer has:

  * A **delivery window**: when energy can flow.
  * An **order cut-off**: latest time by which the trade must be agreed.
* There may be multiple windows per day, each with:

  * Different available quantity.
  * Different price.
  * Different cut-off.

### 2.5 Price and Cost Components

The visible “price per kWh” can bundle:

* Pure **energy component**.
* **Wheeling / network use-of-system** charges.
* **Taxes** (VAT/GST).
* Other regulatory components.

We need:

* Explicit price composition for machines (for mapping to CIM charges).
* A single “total price per kWh” for UX and simple clients.

---

## 3. Representation Approach

### 3.1 Schemas in Play

* **schema.org**

  * `AggregateOffer`, `Offer`, `Product`
  * `QuantitativeValue`
  * `PriceSpecification`, `UnitPriceSpecification`, `CompoundPriceSpecification`

* **IEC CIM** (conceptual; identifiers and classes reused in JSON-LD)

  * `cim:GeographicalRegion`
  * `cim:SubGeographicalRegion`
  * plus underlying tariff/charge models in backend (not fully exposed here).

* **deg namespace** (custom)

  * `deg:electricalCoverage` – link from Offer/AggregateOffer/Trade to CIM region.
  * `deg:WheelingChargeSpecification` – subclass of `schema:UnitPriceSpecification` representing wheeling/network charges.
  * Optional helper properties (e.g., tariff references, CIM mapping).

### 3.2 Design Principles

1. **Single canonical pattern**

   * Top-level: `AggregateOffer`.
   * Inside: one or more `Offer` objects, one per time window.

2. **Separation of concerns**

   * Commercial semantics → schema.org.
   * Electrical coverage → CIM (`GeographicalRegion`/`SubGeographicalRegion`).
   * Cross-links and wheeling specialization → `deg:`.

3. **Time-aware and grid-aware offers**

   * Time windows and cut-offs encoded on each `Offer`.
   * Electrical coverage encoded once on the `AggregateOffer` via CIM.

4. **Explicit multi-component pricing**

   * Use `CompoundPriceSpecification` with `priceComponent` list:

     * Energy component (`UnitPriceSpecification`).
     * Wheeling component (`deg:WheelingChargeSpecification`).
     * Additional components if needed.

---

## 4. Core Information Model

### 4.1 Main Concepts and Mappings

| Concept                                | Primary Type / Property                                                     | Supporting Types / Notes                            |
| -------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------- |
| Prosumer                               | `schema:Person` / `schema:Organization`                                     | Can be mapped to CIM `UsagePoint` in backend        |
| Surplus energy product                 | `schema:Product`                                                            | With `additionalProperty` for energySource, surplus |
| Single tradable time window            | `schema:Offer`                                                              | With time, quantity, price                          |
| Group of related offers (same product) | `schema:AggregateOffer`                                                     | Holds an array of `offers`                          |
| Energy quantity                        | `schema:QuantitativeValue` (`value`, `unitCode="KWH"`)                      | UN/CEFACT unit codes                                |
| Energy price component                 | `schema:UnitPriceSpecification`                                             | Per-kWh base energy price                           |
| Wheeling price component               | `deg:WheelingChargeSpecification` (⊂ `UnitPriceSpecification`)              | Per-kWh network / wheeling charge                   |
| Combined price                         | `schema:CompoundPriceSpecification` + `schema:priceComponent`               | Sum of components                                   |
| Tax inclusion flag                     | `schema:UnitPriceSpecification.valueAddedTaxIncluded`                       | On the combined or individual components            |
| Product attributes (solar, surplus)    | `schema:Product.additionalProperty` (`schema:PropertyValue`)                | e.g., energySource=solar, surplus=true              |
| Electrical coverage                    | `deg:electricalCoverage` → `cim:GeographicalRegion`/`SubGeographicalRegion` | Binds offer to a DISCOM / zone                      |
| Availability window                    | `schema:Offer.availabilityStarts` / `availabilityEnds`                      | ISO 8601 timestamps with TZ                         |
| Order cut-off                          | `schema:Offer.validThrough`                                                 | Must be < `availabilityStarts`                      |

### 4.2 Default Pattern

* **Top-level object**: `AggregateOffer`
* Common attributes:

  * `offeredBy` – the prosumer.
  * `itemOffered` – the surplus energy `Product`.
  * `deg:electricalCoverage` – CIM region / sub-region URI.
* **Inside `offers[]`**:

  * Each `Offer` = one tradable time window + associated price + constraints.

---

## 5. Domain Concepts → Schemas

### 5.1 Prosumer

Simple person:

```json
{
  "@type": "Person",
  "@id": "urn:person:prosumer-123",
  "name": "Prosumer 123"
}
```

Organization (e.g., a housing society):

```json
{
  "@type": "Organization",
  "@id": "urn:org:prosumer-housing-society-1",
  "name": "Green Heights Housing Society"
}
```

### 5.2 Surplus Energy Product

```json
{
  "@type": "Product",
  "@id": "urn:product:surplus-solar-energy",
  "name": "Surplus solar electrical energy",
  "description": "Prosumer surplus solar electricity available for local P2P sale",
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "energySource",
      "value": "solar"
    },
    {
      "@type": "PropertyValue",
      "name": "surplus",
      "value": "true"
    }
  ]
}
```

### 5.3 Energy Quantity

```json
{
  "@type": "QuantitativeValue",
  "value": 10,
  "unitCode": "KWH"
}
```

### 5.4 Electrical Coverage via CIM

Define once in your grid model (conceptually CIM; shown here as JSON-LD-style):

```json
{
  "@id": "urn:cim:grid:IN-KA-BESCOM",
  "@type": "cim:GeographicalRegion",
  "cim:IdentifiedObject.name": "BESCOM service territory",
  "cim:IdentifiedObject.mRID": "IN-KA-BESCOM"
}
```

Optional P2P trading sub-zone:

```json
{
  "@id": "urn:cim:subgrid:IN-KA-BESCOM-P2P-01",
  "@type": "cim:SubGeographicalRegion",
  "cim:IdentifiedObject.name": "BESCOM P2P Zone 01",
  "cim:IdentifiedObject.mRID": "IN-KA-BESCOM-P2P-01",
  "cim:SubGeographicalRegion.Region": {
    "@id": "urn:cim:grid:IN-KA-BESCOM"
  }
}
```

Offers will reference this using `deg:electricalCoverage`.

### 5.5 Price and Cost Components (with WheelingChargeSpecification)

We use:

* `CompoundPriceSpecification` as the container.
* `UnitPriceSpecification` for the **energy** component.
* `deg:WheelingChargeSpecification` (a subclass of `UnitPriceSpecification`) for the **wheeling** component.

Context snippet (for clarity):

```json
{
  "@context": [
    "https://schema.org",
    {
      "deg": "https://example.org/deg#",
      "WheelingChargeSpecification": "deg:WheelingChargeSpecification"
    }
  ]
}
```

Example price:

```json
"priceSpecification": {
  "@type": "CompoundPriceSpecification",
  "priceComponent": [
    {
      "@type": "UnitPriceSpecification",
      "name": "Energy component",
      "price": 3.5,
      "priceCurrency": "INR",
      "unitCode": "KWH",
      "valueAddedTaxIncluded": true
    },
    {
      "@type": [
        "UnitPriceSpecification",
        "WheelingChargeSpecification"
      ],
      "name": "Wheeling charge",
      "price": 1.5,
      "priceCurrency": "INR",
      "unitCode": "KWH",
      "valueAddedTaxIncluded": true,
      "chargeScope": "distribution",
      "tariffReference": "IN-KA-BESCOM-P2P-2025-SCHED-5",
      "isMandatory": true,
      "underlyingCimChargeType": "urn:cim:ChargeType:IN-KA-BESCOM:WHEELING-DIST"
    }
  ]
}
```

Machines can:

* Compute total price per kWh = 3.5 + 1.5 = 5.0 INR/kWh.
* Map the wheeling component directly to a CIM `ChargeType` for settlement.

---

## 6. Base Case: Single Surplus Energy Offer

We recommend using `AggregateOffer` even for a single time window, for consistency.

### 6.1 Example: Single Window, Single Prosumer

```json
{
  "@context": [
    "https://schema.org",
    {
      "cim": "http://www.iec.ch/TC57/CIM#",
      "deg": "https://example.org/deg#",
      "WheelingChargeSpecification": "deg:WheelingChargeSpecification"
    }
  ],
  "@type": "AggregateOffer",
  "@id": "urn:aggregate-offer:prosumer-123-solar-2025-11-24",

  "offeredBy": {
    "@type": "Person",
    "@id": "urn:person:prosumer-123",
    "name": "Prosumer 123"
  },

  "itemOffered": {
    "@type": "Product",
    "@id": "urn:product:surplus-solar-energy",
    "name": "Surplus solar electrical energy",
    "description": "Prosumer surplus solar electricity available for local P2P sale",
    "additionalProperty": [
      {
        "@type": "PropertyValue",
        "name": "energySource",
        "value": "solar"
      },
      {
        "@type": "PropertyValue",
        "name": "surplus",
        "value": "true"
      }
    ]
  },

  "deg:electricalCoverage": {
    "@id": "urn:cim:subgrid:IN-KA-BESCOM-P2P-01",
    "@type": "cim:SubGeographicalRegion"
  },

  "offers": [
    {
      "@type": "Offer",
      "@id": "urn:offer:prosumer-123-solar-2025-11-24-slot-1",

      "eligibleQuantity": {
        "@type": "QuantitativeValue",
        "value": 10,
        "unitCode": "KWH"
      },

      "priceSpecification": {
        "@type": "CompoundPriceSpecification",
        "priceComponent": [
          {
            "@type": "UnitPriceSpecification",
            "name": "Energy component",
            "price": 3.5,
            "priceCurrency": "INR",
            "unitCode": "KWH",
            "valueAddedTaxIncluded": true
          },
          {
            "@type": [
              "UnitPriceSpecification",
              "WheelingChargeSpecification"
            ],
            "name": "Wheeling charge",
            "price": 1.5,
            "priceCurrency": "INR",
            "unitCode": "KWH",
            "valueAddedTaxIncluded": true,
            "chargeScope": "distribution",
            "isMandatory": true,
            "tariffReference": "IN-KA-BESCOM-P2P-2025-SCHED-5",
            "underlyingCimChargeType": "urn:cim:ChargeType:IN-KA-BESCOM:WHEELING-DIST"
          }
        ]
      },

      "availabilityStarts": "2025-11-24T14:00:00+05:30",
      "availabilityEnds":   "2025-11-24T18:00:00+05:30",
      "validThrough":       "2025-11-23T18:00:00+05:30"
    }
  ]
}
```

Semantics:

* Prosumer 123 offers 10 kWh surplus solar energy.
* Electrical coverage: CIM SubGeographicalRegion `IN-KA-BESCOM-P2P-01`.
* Delivery window: 14:00–18:00, 24-Nov-2025.
* Order cut-off: 18:00, 23-Nov-2025 (day-ahead).
* Price:

  * 3.5 INR/kWh energy.
  * 1.5 INR/kWh wheeling (mandatory, mapped to CIM tariff).
  * Total: 5 INR/kWh (tax-inclusive in both components).

---

## 7. Multi-Window and Time-of-Day Pricing

To support multiple availability windows, add multiple `Offer` entries in the same `AggregateOffer`. The `deg:electricalCoverage` and `itemOffered` remain shared.

### 7.1 Example: Multiple Slots (simplified)

```json
{
  "@context": [
    "https://schema.org",
    {
      "cim": "http://www.iec.ch/TC57/CIM#",
      "deg": "https://example.org/deg#",
      "WheelingChargeSpecification": "deg:WheelingChargeSpecification"
    }
  ],
  "@type": "AggregateOffer",
  "@id": "urn:aggregate-offer:prosumer-123-solar-2025-11-24",

  "offeredBy": { "@type": "Person", "@id": "urn:person:prosumer-123", "name": "Prosumer 123" },

  "itemOffered": { /* same Product as before */ },

  "deg:electricalCoverage": {
    "@id": "urn:cim:subgrid:IN-KA-BESCOM-P2P-01",
    "@type": "cim:SubGeographicalRegion"
  },

  "offers": [
    {
      "@type": "Offer",
      "@id": "urn:offer:prosumer-123-solar-2025-11-24-slot-1",
      "eligibleQuantity": { "@type": "QuantitativeValue", "value": 5, "unitCode": "KWH" },
      "priceSpecification": {
        "@type": "CompoundPriceSpecification",
        "priceComponent": [
          {
            "@type": "UnitPriceSpecification",
            "name": "Energy component",
            "price": 3.0,
            "priceCurrency": "INR",
            "unitCode": "KWH"
          },
          {
            "@type": [ "UnitPriceSpecification", "WheelingChargeSpecification" ],
            "name": "Wheeling charge",
            "price": 1.5,
            "priceCurrency": "INR",
            "unitCode": "KWH"
          }
        ]
      },
      "availabilityStarts": "2025-11-24T10:00:00+05:30",
      "availabilityEnds":   "2025-11-24T12:00:00+05:30",
      "validThrough":       "2025-11-23T18:00:00+05:30"
    },
    {
      "@type": "Offer",
      "@id": "urn:offer:prosumer-123-solar-2025-11-24-slot-2",
      "eligibleQuantity": { "@type": "QuantitativeValue", "value": 3, "unitCode": "KWH" },
      "priceSpecification": {
        "@type": "CompoundPriceSpecification",
        "priceComponent": [
          {
            "@type": "UnitPriceSpecification",
            "name": "Energy component",
            "price": 3.5,
            "priceCurrency": "INR",
            "unitCode": "KWH"
          },
          {
            "@type": [ "UnitPriceSpecification", "WheelingChargeSpecification" ],
            "name": "Wheeling charge",
            "price": 1.5,
            "priceCurrency": "INR",
            "unitCode": "KWH"
          }
        ]
      },
      "availabilityStarts": "2025-11-24T14:00:00+05:30",
      "availabilityEnds":   "2025-11-24T16:00:00+05:30",
      "validThrough":       "2025-11-23T18:00:00+05:30"
    }
  ]
}
```

Notes:

* Both slots share the same wheeling structure; only the **energy component price** changes by time-of-day.
* Matching engines can choose:

  * Earliest slot.
  * Cheapest slot (energy price) for a given consumer’s timeframe.

---

## 8. Electrical Coverage and Grid Planning (CIM Layer)

The `deg:electricalCoverage` link provides:

* A concrete anchor into the **CIM network model**:

  * `cim:GeographicalRegion` for the DISCOM’s overall service territory.
  * `cim:SubGeographicalRegion` for P2P trading zones, feeder groups, etc.
* A join key between:

  * P2P Offers/Trades in JSON-LD.
  * EMS/DMS / market / planning tools in the utility backend.

Operationally:

* When validating a trade:

  * Buyer and seller must be in compatible CIM regions (same grid or allowed pair).
* When planning day-ahead schedules:

  * Aggregate offers per `cim:SubGeographicalRegion`.
  * Cross-check against network constraints (lines, transformers) in CIM.

This keeps:

* **schema.org** focused on market semantics.
* **CIM** focused on physical and market topology.
* `deg:electricalCoverage` as the glue.

---

## 9. Price Semantics with WheelingChargeSpecification

### 9.1 Components

Each `Offer.priceSpecification`:

* MUST be a `CompoundPriceSpecification` when you need explicit decomposition.
* SHOULD have at least:

  * One **energy** `UnitPriceSpecification`.
  * One **wheeling** `deg:WheelingChargeSpecification` (if network charges are present).

### 9.2 Total Price for UX

User interfaces can:

* Show only the total rate:

  * Sum of `price` across all `priceComponent` entries (per kWh).
* Optionally expand:

  * “Energy: 3.5 INR/kWh”
  * “Wheeling: 1.5 INR/kWh”
  * “Total: 5.0 INR/kWh (taxes included)”

### 9.3 Mapping to CIM Tariffs and Charges

Back-office systems:

* Interpret each `WheelingChargeSpecification` via:

  * `underlyingCimChargeType` (a URI / identifier of the relevant CIM `ChargeType` / tariff element).
  * `tariffReference` for legal tariff documents or regulatory schedules.

This ensures:

* What the prosumer publishes in P2P offers is **consistent** with the DISCOM’s tariff model.
* Regulatory compliance and settlement calculations remain traceable back to the underlying tariff.

---

## 10. Validation Rules and Constraints

Recommended checks:

* **AggregateOffer level**

  * `offeredBy` present and valid (`Person` or `Organization`).
  * `itemOffered` present and of type `Product`.
  * `deg:electricalCoverage` points to a known CIM region/sub-region.

* **Offer level**

  * `eligibleQuantity.value > 0`, `unitCode = "KWH"` or equivalent.
  * `availabilityStarts < availabilityEnds`.
  * `validThrough < availabilityStarts`.
  * `priceSpecification.@type` includes `CompoundPriceSpecification`.
  * `priceSpecification.priceComponent`:

    * Contains at least one energy `UnitPriceSpecification`.
    * Optionally contains one or more `WheelingChargeSpecification` components.

* **Temporal rules (day-ahead example)**

  * `availabilityStarts - validThrough >= 24 hours` (configurable per market rule).

* **CIM coherence**

  * `deg:electricalCoverage` references a region/sub-region that exists in the current CIM model and is consistent with buyers’ and sellers’ connection points.

---

## 11. Discovery and Filtering

Market participants and AI agents can:

* Filter by **electrical coverage**:

  * `deg:electricalCoverage = urn:cim:subgrid:IN-KA-BESCOM-P2P-01`
* Filter by **energy attributes**:

  * `energySource = solar`, `surplus = true`.
* Filter by **time**:

  * Offers overlapping a desired delivery interval.
* Filter by **price**:

  * Total price per kWh or individual components (e.g., min energy component, fixed wheeling component).
* Sort by:

  * Cheapest total rate.
  * Highest share of renewables.
  * Earliest availability.

Because this is JSON-LD, all of the above can be done:

* Via JSONPath / JMESPath in non-RDF systems.
* Via SPARQL / graph queries in RDF-aware systems.

---

## 12. Extensibility

The model is intentionally minimal but extensible:

* **Product level (`schema:Product.additionalProperty`)**

  * Tariff category.
  * Meter type and phase.
  * Certifiability for carbon credits.

* **Price level (`schema:CompoundPriceSpecification.priceComponent`)**

  * Additional price components:

    * System operation fees.
    * Congestion surcharges.
    * Environmental/REC components.

* **deg namespace**

  * Additional specializations of `PriceSpecification` beyond wheeling.
  * Contract identifiers, settlement rules, or dispute-resolution clauses.

* **CIM integration**

  * Links from offers/trades to:

    * Buyer and seller `UsagePoint`s.
    * Specific network elements (feeders, transformers) if you need very granular constraints.

This combination—schema.org, CIM, and the `deg:` extensions—provides a concrete, interoperable way to represent surplus energy offers in a P2P ecosystem that is both **grid-aware** and **market-aware**, while remaining implementation-agnostic and future-proof.
