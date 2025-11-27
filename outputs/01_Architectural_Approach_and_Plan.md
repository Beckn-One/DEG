# Architectural Approach and Plan
## Extending Beckn Building Blocks for Decentralized Energy Exchange

**Version:** 1.0  
**Date:** December 2024  
**Author:** Architecture Analysis

---

## Executive Summary

This document outlines the approach and plan for extending Beckn Protocol building blocks to enable decentralized energy exchange across multiple use cases (EV charging, demand flexibility, P2P trading, VPP coordination). The goal is to create a **thin glue layer** that provides simplicity, performance, practicality, and future adaptability while allowing use cases to emerge naturally from foundational primitives.

**Core Principle**: The simplest network that gets the job done is most likely to be adopted at scale.

---

## 1. Understanding the Current State

### 1.1 Architecture Foundation (Six Primitives)

The DEG architecture is built on six core primitives:

1. **Energy Resource**: Physical/logical entities (solar, batteries, EVs, transformers, meters)
2. **Energy Resource Address (ERA)**: Unique identifiers enabling discovery and addressability
3. **Energy Credentials**: Verifiable claims (certifications, ownership, capabilities)
4. **Energy Intent**: Consumer demand expressions (discover, select)
5. **Energy Catalogue**: Provider supply expressions (on_discover, offers)
6. **Energy Contract**: Formalized agreements (confirm → on_confirm)

**Key Insight**: The cycle of **intent matched with catalogue, forming a contract** is the fundamental interaction loop.

### 1.2 Current Beckn Protocol Building Blocks

From analysis of existing implementations:

**Core Beckn v2 Actions**:
- `discover` / `on_discover`: Discovery and catalogue matching
- `select` / `on_select`: Selection and quote generation
- `init` / `on_init`: Initialization and terms negotiation
- `confirm` / `on_confirm`: Contract formation
- `update` / `on_update`: Contract modification during fulfillment
- `status` / `on_status`: Status queries
- `track` / `on_track`: Real-time tracking
- `cancel` / `on_cancel`: Cancellation
- `rating` / `on_rating`: Post-fulfillment feedback
- `support` / `on_support`: Support requests

**JSON-LD Attribute Slots**:
- `itemAttributes`: Resource/service attributes
- `offerAttributes`: Pricing and commercial terms
- `orderAttributes`: Order-specific attributes
- `fulfillmentAttributes`: Fulfillment-specific attributes
- `providerAttributes`: Provider-specific attributes

### 1.3 Existing Use Case Implementations

**EV Charging (v0.8)**:
- Uses `itemAttributes` for EVSE specifications (connectorType, maxPowerKW, etc.)
- Uses `offerAttributes` for pricing models (per-kWh, time-based slots)
- Uses `fulfillmentAttributes` for session management (reservation, charging status)
- Well-defined flow from discovery to settlement

**P2P Trading (v0.2)**:
- Uses `itemAttributes` for energy resource specs (sourceType, deliveryMode, meterId)
- Uses `offerAttributes` for trading terms (pricingModel, settlementType, wheelingCharges)
- Uses `orderAttributes` for contract details (EnergyTradeContract)
- Uses `fulfillmentAttributes` for delivery tracking (EnergyTradeDelivery)

### 1.4 Agentic Coordination Architecture

From `agentic_coordination_arch.md`:
- **Bid Curve Model**: Price/power pairs expressing opportunity cost
- **Market Clearing**: Aggregation of bid curves, price discovery, economic disaggregation
- **Locational Pricing**: Grid nodes signal congestion adders
- **Protocol Integration**: OCPI (roaming), OCPP (station control), IEEE 2030.5 (DER control)
- **Three-Layer Model**: Coordination (Beckn/DEG) ↔ Protocol (OCPI/OCPP/IEEE 2030.5) ↔ Physical (Devices/Grid)

---

## 2. Analysis Approach

### 2.1 Gap Analysis Framework

I will analyze gaps across three dimensions:

#### A. **Functional Gaps**
- What use cases cannot be expressed with current building blocks?
- What energy-specific concepts are missing?
- What coordination patterns need support?

#### B. **Structural Gaps**
- Are current attribute slots sufficient?
- Do we need new actions or modify existing ones?
- Are there missing primitives in the six-primitive model?

#### C. **Integration Gaps**
- How well do current blocks integrate with OCPI/OCPP/IEEE 2030.5?
- What protocol translation patterns are needed?
- Are there missing abstraction layers?

### 2.2 Use Case Analysis

For each use case, I will map:

1. **Current Implementation**: How it's done today (EV charging, P2P trading)
2. **Emergent Pattern**: What common pattern emerges?
3. **Building Block Requirements**: What Beckn blocks are needed?
4. **Protocol Integration**: How it maps to OCPI/OCPP/IEEE 2030.5
5. **Sequence Flow**: Step-by-step interaction diagram

**Use Cases to Analyze**:
- Smart EV charging (home, destination, en-route)
- Rate-based EV charging (time-of-use, demand response)
- Demand flexibility (load shifting, peak shaving)
- Peer-to-peer energy trading
- VPP coordination (neighborhood, city, regional)
- Grid services (frequency regulation, voltage support)

### 2.3 Simplicity Assessment

For each proposed building block extension, I will evaluate:

1. **Simplicity**: Can a developer understand it in < 5 minutes?
2. **Composability**: Does it combine naturally with existing blocks?
3. **Emergent Complexity**: Does combining blocks create useful patterns?
4. **Protocol Fit**: Does it reduce or increase translation toil?

---

## 3. Proposed Building Block Extensions

### 3.1 Potential Extensions (To Be Validated)

Based on initial analysis, these extensions may be needed:

#### A. **Bid Curve Expression**
**Purpose**: Enable objective-driven, price/power-based coordination

**Where**: 
- `itemAttributes.bidCurve`: For resources expressing capability
- `offerAttributes.bidCurve`: For offers with dynamic pricing
- `orderAttributes.bidCurve`: For contracts with market-based terms

**Rationale**: 
- Enables agentic coordination without dictating commands
- Natural fit for market clearing and economic disaggregation
- Works across all use cases (EV charging, P2P, demand flexibility)

**Simplicity Check**: 
- Single concept: price/power pairs
- Composable with existing pricing models
- Emergent: enables market mechanisms

#### B. **Locational Pricing Signals**
**Purpose**: Enable congestion-aware routing and pricing

**Where**:
- `itemAttributes.locationalPriceAdder`: For grid nodes (transformers, substations)
- `offerAttributes.locationalPriceAdder`: For offers with location-based pricing
- New attribute slot: `gridAttributes` for grid-specific metadata?

**Rationale**:
- Enables natural congestion management
- Supports grid-aware routing
- Reduces need for centralized grid control

**Simplicity Check**:
- Simple: base price + adder
- Composable: can be layered (national → state → city → neighborhood)
- Emergent: enables congestion-aware markets

#### C. **Objective Expression**
**Purpose**: Enable resources to express objectives rather than fixed commands

**Where**:
- `itemAttributes.objectives`: For resources expressing goals
- `orderAttributes.objectives`: For contracts with objective-based fulfillment

**Rationale**:
- Enables agentic behavior
- Supports bid curve construction
- Allows sub-networks to optimize locally

**Simplicity Check**:
- Simple: structured objectives (target, deadline, constraints)
- Composable: can combine with bid curves
- Emergent: enables autonomous coordination

#### D. **Meter Data Integration**
**Purpose**: Enable trusted meter readings for settlement

**Where**:
- `fulfillmentAttributes.meterReadings`: For delivery attestation
- `orderAttributes.meteringAuthority`: For settlement data sources
- New attribute slot: `settlementAttributes`?

**Rationale**:
- Required for P2P trading and demand flexibility
- Enables multi-party revenue flows
- Supports unambiguous billing

**Simplicity Check**:
- Simple: meter reading structure
- Composable: can reference external meter data
- Emergent: enables automated settlement

#### E. **External Signal References**
**Purpose**: Enable contracts to reference trusted external signals (prices, forecasts)

**Where**:
- `offerAttributes.externalSignals`: For offers referencing market prices
- `orderAttributes.externalSignals`: For contracts with external dependencies
- `fulfillmentAttributes.externalSignals`: For fulfillment with external triggers

**Rationale**:
- Enables integration with wholesale markets
- Supports forecast-based trading
- Reduces toil in protocol translation

**Simplicity Check**:
- Simple: reference to external signal source
- Composable: can combine multiple signals
- Emergent: enables market integration

#### F. **Multi-Party Revenue Flows**
**Purpose**: Enable unambiguous billing with multiple parties (aggregator, customer, government, grid operator)

**Where**:
- `orderAttributes.revenueFlows`: For contracts with multi-party settlement
- `fulfillmentAttributes.revenueFlows`: For fulfillment with revenue distribution
- New attribute slot: `settlementAttributes`?

**Rationale**:
- Required for complex energy contracts
- Enables transparent revenue sharing
- Supports regulatory compliance

**Simplicity Check**:
- Simple: array of revenue flow entries
- Composable: can combine with meter data
- Emergent: enables complex settlements

### 3.2 New Actions (If Needed)

**Potential New Actions**:
- `aggregate` / `on_aggregate`: For bid curve aggregation
- `clear` / `on_clear`: For market clearing
- `disaggregate` / `on_disaggregate`: For economic disaggregation
- `forecast` / `on_forecast`: For forecast sharing

**Assessment**: 
- **Risk**: Adding actions increases complexity
- **Alternative**: Use existing actions with new attribute structures
- **Decision**: Validate if existing actions are sufficient

---

## 4. Implementation Plan

### 4.1 Phase 1: Analysis and Documentation (Week 1-2)

**Deliverables**:

1. **Building Block Extension Analysis** (`outputs/02_Building_Block_Extensions.md`)
   - Gap analysis for each use case
   - Proposed extensions with rationale
   - Simplicity assessment
   - Protocol integration patterns

2. **Use Case Sequence Diagrams** (`outputs/03_Use_Case_Sequence_Diagrams.md`)
   - Mermaid diagrams for each use case:
     - Smart EV charging (home, destination, en-route)
     - Rate-based EV charging
     - Demand flexibility
     - P2P trading
     - VPP coordination
     - Grid services
   - Each diagram shows:
     - Beckn actions
     - Attribute slot usage
     - Protocol integration points
     - Bid curve flows (if applicable)

3. **Protocol Integration Patterns** (`outputs/04_Protocol_Integration_Patterns.md`)
   - OCPI integration patterns
   - OCPP integration patterns
   - IEEE 2030.5 integration patterns
   - Translation toil assessment

### 4.2 Phase 2: Schema Design (Week 3-4)

**Deliverables**:

1. **Schema Extension Specifications** (`outputs/05_Schema_Extensions.md`)
   - JSON-LD context extensions
   - Vocabulary definitions
   - Attribute slot structures
   - Example JSON schemas

2. **Example Messages** (`outputs/examples/`)
   - Complete message flows for each use case
   - Bid curve examples
   - Locational pricing examples
   - Multi-party settlement examples
   - External signal reference examples

### 4.3 Phase 3: Validation and Refinement (Week 5)

**Deliverables**:

1. **Simplicity Validation** (`outputs/06_Simplicity_Validation.md`)
   - Developer comprehension assessment
   - Composability verification
   - Emergent pattern documentation

2. **Protocol Translation Assessment** (`outputs/07_Protocol_Translation_Assessment.md`)
   - Translation complexity analysis
   - Toil reduction verification
   - Integration pattern validation

---

## 5. Key Questions to Answer

### 5.1 Building Block Questions

1. **Do we need new Beckn actions, or can we extend attribute slots?**
   - Hypothesis: Attribute slots are sufficient; no new actions needed
   - Validation: Check if bid curve aggregation can be done via existing actions

2. **Are the six primitives sufficient, or do we need more?**
   - Hypothesis: Six primitives are sufficient; extensions are in attribute slots
   - Validation: Check if all use cases can be expressed

3. **How do bid curves fit into existing Beckn patterns?**
   - Hypothesis: Bid curves are a special case of offer pricing
   - Validation: Map bid curves to `offerAttributes` structure

4. **Can locational pricing be expressed without new primitives?**
   - Hypothesis: Locational pricing is an attribute of items/offers
   - Validation: Check if grid nodes can be expressed as Energy Resources

### 5.2 Use Case Questions

1. **Can demand flexibility emerge from EV charging patterns?**
   - Hypothesis: Yes, via bid curves and objective expression
   - Validation: Map demand flexibility flow to EV charging flow

2. **Can P2P trading use the same building blocks as EV charging?**
   - Hypothesis: Yes, with different attribute values
   - Validation: Compare attribute structures

3. **Can VPP coordination use the same primitives?**
   - Hypothesis: Yes, via aggregation of bid curves
   - Validation: Map VPP flow to individual resource flows

### 5.3 Protocol Integration Questions

1. **How do we minimize translation toil for OCPI/OCPP/IEEE 2030.5?**
   - Hypothesis: Reuse enums and structures from protocols
   - Validation: Map protocol structures to attribute slots

2. **Can external signals (market prices) be referenced without tight coupling?**
   - Hypothesis: Yes, via external signal references
   - Validation: Design reference structure

3. **How do we support multi-party revenue flows?**
   - Hypothesis: Via `settlementAttributes` or `orderAttributes.revenueFlows`
   - Validation: Design revenue flow structure

---

## 6. Success Criteria

### 6.1 Simplicity

- ✅ Each building block can be understood in < 5 minutes
- ✅ Developer can compose blocks without extensive documentation
- ✅ Emergent patterns are intuitive

### 6.2 Composability

- ✅ Use cases emerge naturally from block combinations
- ✅ No special cases or exceptions
- ✅ Consistent patterns across use cases

### 6.3 Protocol Integration

- ✅ Translation toil is minimal (< 10% overhead)
- ✅ Protocol enums are reused, not reinvented
- ✅ External interfaces (market prices) are encapsulated

### 6.4 Practicality

- ✅ Real-world use cases are supported
- ✅ Performance is acceptable (< 1s for market clearing)
- ✅ Scalability is demonstrated (neighborhood → city → national)

---

## 7. Next Steps

1. **Review this plan with stakeholders** (you)
2. **Begin Phase 1 analysis** (gap analysis, use case mapping)
3. **Create sequence diagrams** for each use case
4. **Design schema extensions** based on analysis
5. **Validate simplicity and composability**
6. **Iterate based on feedback**

---

## 8. Open Questions - RESOLVED

1. **Bid Curve Aggregation**: ✅ **New action required** - existing actions cannot do it
2. **Market Clearing**: ✅ **Contract-based pattern** - prices discovered at synchronous confirmation stage, not at offer time. Market clearing agent acts as BPP, participants as BAPs.
3. **Grid Nodes as Resources**: ✅ **Yes** - transformers can be Energy Resources if they fit the pattern. They're owned by grid operator, can set locational price adders, and command offsets for flat plateaus.
4. **Forecast Sharing**: ✅ **Separate catalog item or out-of-band** - can be shared separately to DERs
5. **Settlement Attributes**: ✅ **Extend `orderAttributes`** - add `settlement.revenueFlows` and `settlement.settlementReport` sections (see gap analysis for details)

---

## Appendix: Reference Documents

- [DEG Architecture](../architecture/README.md)
- [Energy Resource](../architecture/Energy%20resource.md)
- [Energy Intent](../architecture/Energy%20intent.md)
- [Energy Catalogue](../architecture/Energy%20catalogue.md)
- [Energy Contract](../architecture/Energy%20contract.md)
- [Agentic Coordination Architecture](../ref_docs/agentic_coordination_arch.md)
- [EV Charging Implementation Guide](../docs/implementation-guides/v2/EV_Charging_V0.8-draft.md)
- [P2P Trading Implementation Guide](../docs/implementation-guides/v2/P2P_Trading/P2P_Trading_implementation_guide_DRAFT.md)

---

**Status**: Draft for Review  
**Next Action**: Await feedback, then proceed with Phase 1 analysis

