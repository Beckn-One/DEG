# Architecture

## Introduction

The Digital Energy Grid (DEG) is built on a decentralized, open architecture that enables seamless interactions between diverse energy stakeholders - from individual consumers and distributed energy resources (DERs) to utilities, aggregators, and service providers. At its core, DEG provides a standardized framework for energy transactions, data exchange, and service delivery across a fragmented ecosystem.

As energy markets evolve toward decentralization, the proliferation of small-scale producers (rooftop solar, community batteries), distributed resources (EVs, smart appliances), and new energy services creates a pressing need for interoperability. Traditional centralized systems struggle to accommodate this complexity, leading to siloed networks, proprietary platforms, and limited consumer choice.

DEG addresses these challenges through a set of fundamental primitives that work together to create a universal language for energy interactions - enabling discovery, negotiation, contracting, and fulfillment across any compliant platform or network.

## The Six Core Primitives

The DEG architecture is built on six fundamental primitives that together enable trustworthy, efficient energy transactions:

### 1. [Energy Resource](./Energy%20resource.md)
Physical or logical entities in the energy ecosystem - including generation assets (solar panels, wind turbines, VPPs), storage systems (batteries), consumption devices (EVs, appliances), infrastructure (transformers, meters), and service providers. Energy resources can act as consumers, providers, or both (prosumers), depending on the context and transaction.

### 2. [Energy Resource Address (ERA)](./Energy%20resource%20address.md)
A globally or locally unique digital identifier assigned to any energy resource, enabling seamless addressability and discovery. ERAs function like internet domain names, allowing systems to uniformly recognize and interact with energy resources across platforms and contexts.

### 3. [Energy Credentials](./Energy%20credentials.md)
Digital attestations tied to Energy Resource Addresses that provide verifiable claims about resources - such as green energy certification, ownership status, maintenance logs, subsidy eligibility, and transaction history. Credentials establish trust in decentralized energy markets where traditional audit mechanisms are cost-prohibitive.

### 4. [Energy Intent](./Energy%20intent.md) (also called Energy Objective)
A digital expression of what an actor values - goals, preferences, and constraints. Intents guide optimization: actors accept EnergyOffers, participate in contracts, or update offer curves to maximize their expressed values. Used in `discover` calls to find matching contracts.

### 5. [Energy Offer](./Energy%20catalogue.md)
The core Beckn primitive representing contract participation opportunities. Published in `offerAttributes`, offers specify open roles (BUYER, SELLER, PROSUMER, MARKET_CLEARING_AGENT, etc.) that participants can assume. Offers reference EnergyContracts that define computational billing logic.

### 6. [Energy Contract](./Energy%20contract.md)
A computational, role-based agreement that specifies how billing flows are computed from input signals (prices, meter readings, telemetry). Contracts form when roles are filled and participants provide required inputs. Contracts transform external signals into net-zero revenue flows between parties.

## How the Primitives Work Together

The DEG primitives form a cohesive interaction model:

```
         Energy Resources
                ↓
        Assigned ERAs
                ↓
        Carry Credentials
           ↙         ↘
    Express         Publish
    Intents         Offers
    (Values)    (Open Roles)
       ↓                ↓
       └────(Match)─────┘
                ↓
         Energy Contract
    (Roles Filled, Signals Connected)
                ↓
         Contract Execution
    (Fulfillment, Compute Billing from Signals)
```

**The Transaction Cycle:**

1. **Resources are identified**: Every participating entity (consumer, producer, prosumer, device, service) has an Energy Resource Address (ERA)
2. **Trust is established**: Energy Credentials verify claims about resources (capacity, certification, ownership)
3. **Values are expressed**: Resources express Energy Intents (objectives) - what they value
4. **Offers are published**: Providers publish Energy Offers with open roles in contracts
5. **Matching occurs**: Intents guide selection of offers; participants assume roles
6. **Contracts are formed**: When roles are filled and inputs provided, Energy Contracts are confirmed
7. **Fulfillment happens**: Energy is delivered according to contract terms
8. **Billing is computed**: Contracts transform signals (prices, meter readings) into revenue flows & quality of service metrics.

This cycle - **intent guides offer selection, roles fill contracts, contracts are connected to the trusted signals/telemetry which drives revenue flows** - is the fundamental interaction loop in the Digital Energy Grid.

A single Energy Resource can simultaneously express intents (as a consumer) and publish catalogues (as a provider). For example, a home with rooftop solar and battery storage might publish a catalogue selling excess solar energy while expressing an intent to buy grid power during peak demand hours.

## Real-World Application

These primitives map to practical energy scenarios:

**EV Charging Example:**
- **Energy Resource**: Charging station (EVSE), Electric vehicle, EV user
- **ERA**: Unique identifier for each resource
- **Credentials**: CPO verification, charger safety certification
- **Intent**: "Value: Charge 20 kWh by 9 PM, prefer solar, max ₹18/kWh"
- **Offer**: CPO publishes offer with open BUYER role, fixed price contract
- **Contract**: User assumes BUYER role; contract computes billing from meter readings

**P2P Energy Trading Example:**
- **Energy Resource**: Rooftop solar, Home battery, Prosumer household
- **ERA**: Unique identifiers for resources
- **Credentials**: Green energy certification, grid connection approval
- **Intent**: "Value: Find the lowest price for 10kwh of renewable local energy between 2-4 PM"
- **Offer**: Prosumer publishes offer with open BUYER role, offer curve contract
- **Contract**: Market clears; contract computes billing from clearing price × cleared power

## Navigation

Explore each primitive in detail:

- [Energy Resource](./Energy%20resource.md) - Understanding energy ecosystem entities
- [Energy Resource Address](./Energy%20resource%20address.md) - Digital addressing for energy
- [Energy Credentials](./Energy%20credentials.md) - Establishing trust and verification
- [Energy Intent](./Energy%20intent.md) - Expressing what actors value (objectives)
- [Energy Offer](./Energy%20catalogue.md) - Contract participation opportunities (core Beckn primitive)
- [Energy Contract](./Energy%20contract.md) - Computational, role-based agreements

For implementation examples, see:
- [EV Charging Implementation Guide](../docs/implementation-guides/v2/EV_Charging_V0.8-draft.md)
- [P2P Energy Trading Implementation Guide](../docs/implementation-guides/v2/P2P_Trading) (coming soon)
