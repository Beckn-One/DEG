# RFC: Implementation Guide for Demand Flexibility Programs using Beckn Protocol

**RFC Number:** BECKN-DF-001  
**Category:** Informational  
**Status:** Draft  
**Version:** 0.1.0  
**Date:** 2025-08-18  
**Updated:** 2025-08-28  
**Authors:** Rajaneesh Kumar  
**Reviewers:** Ravi Prakash  
**Supersedes:** None  
**Keywords:** Demand Flexibility, Electricity Grid, Energy Management, Beckn Protocol, Distribution Companies, Commercial Consumers, Residential Consumers, Retail Consumers  

## Copyright Notice
This work is licensed under Creative Commons Attribution-ShareAlike 4.0 International License

## Status of This Memo
This document is a draft RFC for implementation guidance on using Beckn Protocol for Demand Flexibility programs. It provides comprehensive guidance for energy utilities and commercial consumers implementing demand response and flexibility solutions. The specification is ready for community review and pilot implementations.

## Abstract

This RFC presents a paradigm shift in electricity grid management by leveraging the Beckn Protocol's distributed commerce architecture for Demand Flexibility (DF) programs. Rather than traditional top-down utility control, this approach creates a **marketplace for grid flexibility** where consumers become active participants in grid stability through automated discovery, subscription-based participation, and performance-based compensation. 

The architecture transforms electricity demand from a passive consumption model to an active grid resource, enabling utilities to harness distributed flexibility at scale while providing all consumer types—from residential households to large industrial facilities—with revenue opportunities. This marketplace-driven approach addresses the growing complexity of modern grids—renewable intermittency, peak demand challenges, and infrastructure constraints—through coordinated, incentive-aligned participation rather than emergency load shedding.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Conventions and Terminology](#2-conventions-and-terminology)
3. [Background and Context](#3-background-and-context)
4. [Implementation Guide](#4-implementation-guide)
5. [Best Practices](#5-best-practices)
6. [IANA Considerations](#6-iana-considerations)
7. [Examples](#7-examples)
8. [References](#8-references)
9. [Appendix](#9-appendix)

## 1. Introduction

### 1.1 Purpose

This RFC provides implementation guidance for deploying Demand Flexibility (DF) programs using the Beckn Protocol. It specifically addresses how energy utilities can implement demand response programs that enable all types of consumers—residential, commercial, and industrial—to participate in grid flexibility services while receiving economic incentives for their participation.

### 1.2 Scope

This document covers:
- Architecture patterns for DF program implementation using Beckn Protocol
- Discovery and subscription mechanisms for DF programs
- Event-based demand response coordination
- Incentive calculation and distribution
- Security and privacy considerations for energy data
- Integration with existing utility systems

This document does not cover:
- Detailed power grid engineering specifications
- Regulatory compliance beyond technical implementation
- Hardware specifications for smart meters or control systems

### 1.3 Target Audience

- **Energy Utilities**: Implementing demand flexibility programs across all customer segments
- **Residential Consumers**: Households participating in DF programs through smart devices and energy management systems
- **Commercial/Industrial Consumers**: Businesses and facilities participating in DF programs
- **Aggregators**: Third-party service providers managing DF participation for multiple consumers
- **Technology Integrators**: Building Beckn-based energy solutions
- **Policymakers**: Understanding technical implementation options
- **Developers**: Implementing energy management applications

### 1.4 Prerequisites

Readers should have:
- **Basic understanding of Beckn Protocol concepts and APIs**
  - [Beckn Protocol Specification v1.1.0](https://github.com/beckn/protocol-specifications)
  - [Beckn Protocol Developer Documentation](https://developers.becknprotocol.io/)
  - [Generic Implementation Guide](https://github.com/beckn/missions/blob/main/Generic-Implementation-Guide/generic_implementation_guide.md)
- **Knowledge of electricity grid operations and demand response**
  - [Grid Modernization and Smart Grid - US Department of Energy](https://www.energy.gov/oe/grid-modernization-and-smart-grid)
  - [IEEE Power & Energy Society](https://www.ieee-pes.org/)
  - [Electric Power Research Institute (EPRI)](https://www.epri.com/)
  - [Demand Flexibility - Lawrence Berkeley National Laboratory](https://buildings.lbl.gov/demand-flexibility)
- **Familiarity with JSON schema and RESTful APIs**
  - [JSON Schema Specification](https://json-schema.org/)
  - [RESTful API Design Guidelines](https://restfulapi.net/)
  - [OpenAPI Specification](https://swagger.io/specification/)
- **Understanding of electricity market structures**
  - [Energy Markets 101 - International Energy Agency](https://www.iea.org/)
  - [Smart Grid and Demand Response - Lawrence Berkeley National Laboratory](https://eta.lbl.gov/)

## 2. Conventions and Terminology

**MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC 2119.

**Additional Terms:**
- **DF Program**: Demand Flexibility Program offering grid services
- **DF Event**: Specific demand response event with time-bound requirements
- **Distribution Company (DISCOM)**: Utility responsible for electricity distribution
- **Consumer**: Any electricity end-user participating in DF programs (residential, commercial, or industrial)
- **Aggregator**: Third-party entity that manages DF participation for multiple consumers
- **BAP**: Beckn Application Platform (Consumer or Aggregator in this context)
- **BPP**: Beckn Provider Platform (Utility/DISCOM in this context)
- **Load Flexibility**: Ability to adjust electricity consumption patterns
- **Incentive**: Financial or non-financial benefit for DF participation

## 3. Background and Context

### 3.1 Problem Domain

**The Grid's Growing Complexity Crisis**

Modern electricity grids face an unprecedented convergence of challenges that traditional centralized control cannot effectively address:

**Peak Demand Explosion**: Global electricity demand peaks are growing 3-4% annually, driven by electrification of transport, heating, and industrial processes. Utilities must maintain expensive "peaker" plants that operate only a few hundred hours per year but represent billions in capital costs. A single 100MW peaker plant costs $50-100 million but may only run during the hottest 50 afternoons of the year.

**The Renewable Intermittency Paradox**: While renewable energy is abundant and cheap when available, its variability creates grid management nightmares. Solar generation peaks at noon but demand peaks at 6 PM. Wind can drop from 80% to 10% capacity within hours. Grid operators need flexible resources that can respond in minutes, not the hours required for traditional power plants.

**Infrastructure at Breaking Point**: Many electricity networks operate close to capacity limits. A single transmission line failure can cascade into blackouts affecting millions. The 2003 Northeast blackout started with tree contact on a single Ohio transmission line but ultimately left 55 million people without power, demonstrating how fragile our interconnected grid has become.

**The Hidden Flexibility Goldmine**

Electricity consumers across all segments—residential, commercial, and industrial—represent an untapped reservoir of grid flexibility that collectively dwarfs most power plants:

**Commercial Buildings**: A typical shopping mall with 200 stores consumes 2-5 MW continuously. During peak demand periods, reducing HVAC load by 20% for two hours provides the same grid relief as a small power plant—without the environmental impact or capital investment.

**Manufacturing Facilities**: Industrial processes often have inherent flexibility. Aluminum smelters can modulate their load within minutes. Food processing facilities can shift energy-intensive operations to off-peak hours. A single steel mill can adjust its consumption by 50-100 MW based on production scheduling.

**Cold Storage and Data Centers**: These facilities are essentially "thermal batteries" and "computational batteries." A cold storage warehouse can pre-cool to lower temperatures when electricity is cheap, then coast on thermal inertia during peak periods. Data centers can shift non-urgent computational workloads to other locations or time periods.

**Transportation Hubs**: Bus depots, train stations, and airports have massive energy footprints with significant scheduling flexibility. Electric bus charging can be optimized around grid conditions. Airport terminals can adjust lighting, escalators, and air conditioning without impacting passenger experience.

**Residential Households**: While individual homes consume 1-5 kW on average, their collective impact is enormous. A neighborhood of 1,000 homes represents 3-5 MW of potential flexibility through smart thermostats, water heaters, electric vehicle charging, and battery storage systems. Smart home technologies enable automated participation without compromising comfort or convenience.

**Residential Aggregation**: The key to residential participation lies in aggregation—combining thousands of small, individually insignificant loads into grid-scale resources. A residential aggregator managing 50,000 homes can deliver 50-100 MW of flexibility, equivalent to a traditional power plant, but distributed across the grid and inherently more resilient.

### 3.2 Current State

Traditional demand response programs face limitations:
- **Manual Coordination**: Phone calls and emails for event notification
- **Limited Granularity**: Broad load curtailment without optimization
- **Poor Incentive Alignment**: Fixed rates not reflecting real-time value
- **Operational Complexity**: Difficult participation for smaller consumers

### 3.3 Motivation

Using Beckn Protocol for DF programs enables:
- **Automated Discovery**: Consumers can find and evaluate DF programs
- **Dynamic Participation**: Real-time event coordination and response
- **Transparent Incentives**: Clear pricing and settlement mechanisms
- **Scalable Architecture**: Support for many participants and program types
- **Interoperability**: Standard interfaces across different utilities

## 4. Implementation Guide

### 4.1 Overview

**Beckn Protocol as the Foundation for Grid Communication**

This implementation guide demonstrates how to harness the **Beckn open source protocol** as the unified communication backbone for Demand Flexibility programs. We leverage Beckn's proven distributed commerce architecture to create seamless interactions between utilities and their diverse consumer base.

The Beckn Protocol serves as our **digital lingua franca**, enabling standardized communication for:
- **Program discovery and subscription**: Utilities publishing available DF programs and consumers discovering and enrolling in suitable offerings
- **Demand signals**: Utilities broadcasting grid needs and flexibility requirements
- **Response coordination**: Consumers communicating availability, capacity, and participation decisions  
- **Event notifications**: Real-time grid event dispatch and status updates
- **Incentive flows**: Transparent performance verification and compensation processing

This approach transforms complex utility-consumer interactions into **standardized API conversations** that any participant can understand and implement, whether they're managing a single household or coordinating thousands of industrial facilities.

**Implementation Architecture: Four-Phase Orchestration**

An implementation follows a **discovery-first marketplace approach** where each phase builds upon standardized Beckn API interactions:

1. **Discovery Phase**: Consumers discover available DF programs through search APIs, finding opportunities matched to their capabilities
2. **Subscription Phase**: Enrollment in suitable programs using confirm APIs, establishing clear terms and commitments  
3. **Event Phase**: Real-time coordination of DF events via on_init (BPP to BAP) and confirm (BAP to BPP) APIs, enabling dynamic grid response
4. **Settlement Phase**: Performance verification and incentive distribution through status APIs, ensuring transparent compensation

Each phase leverages **native Beckn Protocol capabilities**—search, select, init, confirm, status, update, support, cancel, rating-adapted specifically for the energy domain while maintaining full protocol compliance and interoperability.

### 4.2 Prerequisites

Before implementation, the following infrastructure must be in place:

**For Participating Consumers:**
- **Smart Metering**: Advanced metering infrastructure (AMI) with 15-minute or hourly interval data capability
- **Controllable Devices** (recommended): Smart thermostats, automated equipment controls, or energy management systems capable of load adjustment, or manual procedures for load modification
- **Communication Infrastructure**: Reliable internet connectivity for receiving API calls and sending responses
- **Local Intelligence**: Basic automation or manual procedures to execute load reduction commands

**For Utilities/DISCOMs:**
- **Grid Operations Integration**: Existing SCADA, Energy Management Systems (EMS), and demand forecasting capabilities
- **Communication Systems**: API infrastructure capable of handling real-time message exchange with multiple participants
- **Authorization Framework**: Digital signature capabilities, participant authentication, and access control systems
- **Data Management**: Baseline calculation engines, performance measurement systems, and billing/settlement infrastructure
- **Regulatory Compliance**: Appropriate approvals for demand response programs and consumer participation frameworks

### 4.3 Configuration

#### 4.3.1 Network Architecture Setup

**The Distributed Intelligence Paradigm**

Demand Flexibility fundamentally reimagines grid operations as a **distributed intelligence network** rather than centralized command-and-control. Each participant—whether utility or consumer—operates as an autonomous agent capable of making intelligent decisions while coordinating with the broader grid ecosystem.

**Consumer Entity (BAP) - The Intelligent Edge Node:**

Think of each participating entity—whether a household, commercial building, industrial facility, or aggregator managing multiple consumers—as a "smart grid edge node" with decision-making capabilities. A BAP implementation consists of three logical components:

**1. Network-Side Interface (Beckn Protocol Communication):**
This component handles all Beckn Protocol API communications with the utility network. It processes search requests, subscription confirmations, event notifications, and status updates. This is the standard Beckn BAP endpoint that accepts BPP callbacks following the protocol specification.

**2. Decision Engine (Local Intelligence):**
This is the business logic component that makes participation decisions by considering:
  - Current operational priorities (production schedules, occupancy patterns, comfort settings, equipment maintenance)
  - Economic opportunities (electricity prices, incentive rates, demand charges, bill savings)
  - Technical constraints (equipment ramp rates, minimum run times, safety interlocks, comfort bounds)
  - Consumer preferences (participation willingness, priority loads, override capabilities)
  - Historical performance (baseline accuracy, commitment reliability, revenue optimization)

**3. Client-Side Interface (Internal Systems Integration):**
This component interfaces with the consumer's internal energy systems—home automation platforms, Building Management Systems, SCADA, IoT sensors, or aggregator platforms. It translates between "consumer language" (comfort settings, production schedules, operational constraints) and "DF program language" (load reduction commitments, baseline calculations, participation decisions).

**Note:** These are **logical components within a single BAP application**, not separate physical services. They can be implemented as modules within one software system or as separate microservices depending on the deployment architecture.

**Utility/DISCOM (BPP) - The Grid Orchestrator:**

The utility transforms from a traditional "power deliverer" to a "flexibility marketplace operator". A BPP implementation consists of three logical components:

**1. Grid Operations Interface (Internal Systems Integration):**
This component interfaces with traditional utility systems—SCADA, Energy Management Systems (EMS), Market Operations, demand forecasting, and billing systems. It translates between "grid operations language" (MW requirements, frequency deviations, transmission constraints) and "DF marketplace language" (event notifications, participant capacity, incentive calculations).

**2. DF Program Management Engine (Grid Intelligence):**
This is the business logic component that orchestrates DF programs by:
  - Monitoring grid conditions and forecasting flexibility needs
  - Managing participant portfolios and capacity tracking
  - Optimizing event dispatch across multiple participants
  - Calculating baselines, measuring performance, and processing settlements
  - Coordinating with traditional grid operations and market systems

**3. Network-Side Interface (Beckn Protocol Communication):**
This component handles all Beckn Protocol API communications with consumer BAPs. It processes search responses, subscription management, event dispatch, and status collection. This is the standard Beckn BPP endpoint that serves BAP requests following the protocol specification.

**Note:** Like BAP components, these are **logical components within a single BPP application**. The implementation can range from integrated modules within existing utility systems to standalone DF marketplace platforms depending on utility architecture and integration requirements.

**Gateway Service:**
Discovery requests flow through gateways(Beckn Gateway) that broadcast search queries to all relevant providers in the network. Gateways filter and route messages based on domain and geographic criteria.

**Registry Service:**
Each DF network or Energy network requires a registry where all participants(BAP, BPP, BG) register themselves with details such as network endpoint, domains, region of operation, public keys. The registry maintains the authoritative list of network participants and their subscription status.

Participant Registration contains:
- Unique participant identifiers across the network
- Endpoint URLs for client and network communication
- Geographic coverage and operational hours
- Subscription status and access permissions

**Recommendations for implementing the above mentioned components**

  - BAP: All BAP implementations MUST follow the relevant APIs from the Beckn [transaction](https://github.com/beckn/protocol-specifications/blob/master/api/transaction/build/transaction.yaml) and [meta](https://github.com/beckn/protocol-specifications/blob/master/api/meta/build/meta.yaml) specifications.
  - BPP: All BPP implementations MUST follow the relevant APIs from the Beckn [transaction](https://github.com/beckn/protocol-specifications/blob/master/api/transaction/build/transaction.yaml) and [meta](https://github.com/beckn/protocol-specifications/blob/master/api/meta/build/meta.yaml) specifications.
  - Beckn Gateway: The implemented gateway MUST follow the Beckn [gateway](https://github.com/beckn/protocol-specifications/blob/master/api/transaction/build/transaction.yaml) specifications.
  - Beckn Registry: The implemented registry MUST follow the Beckn [registry](https://github.com/beckn/protocol-specifications/tree/master/api/registry/build/registry.yaml) specifications.

NOTE: FIDE provides a software stack called [Beckn-ONIX](https://becknprotocol.io/beckn-onix/), for rapidly deploying and configuring a Beckn enabled network. This is just one of many ways to deploy a Beckn enabled network.

Recommendation for implementing Registry:
  - **Participant Registration**: Registry MUST allow Network Participants to register themselves with a Subscriber ID and Subscriber URL
  - **Approval Criteria**: Registry MAY have approval criteria for registrants, once the criteria are met, the registrants MAY be considered as subscribers
  - **Participant Rights**: Registry MUST allow network participants to own and have rights to modify their network roles and participant keys
  - **Access Control**: Registry MUST NOT allow a user to change other user's network participant details
  - **Detail Management**: Registry MUST allow subscribers to create and alter their details including domain, role, and location
  - **Key Management**: Registry MUST allow public keys associated with network participants to be changed
  - **Information Updates**: Registry MUST support the modification of subscriber information
  - **Lookup Services**: Registry MUST support the lookup of Subscriber information through the registry lookup endpoint
  - Here is a step by step guide for [setting up Beckn registry using Beckn-ONIX](https://github.com/beckn/beckn-onix/blob/main/docs/user_guide.md#setting-up-a-new-network---registry)
  
Recommendation for implementing Gateway:
  - **Authentication & Signing**: Gateway MUST implement signature addition with X-Gateway-Authorization header when forwarding BAP messages to BPPs
  - **Search Endpoint**: Gateway MUST implement and expose search endpoint at subscriber URL to receive search requests from BAPs
  - **Registry Integration**: Gateway MUST use lookup API to fetch relevant BPPs based on message context (domain, location, capabilities)
  - **Message Forwarding**: Gateway MUST forward signed search requests to all relevant BPPs returned by Registry lookup
  - **Caching**: Gateway SHOULD implement short-term caching to reduce Registry lookup load during peak grid events
  - **Error Handling**: Gateway MUST gracefully handle Registry lookup failures and BPP communication errors
  - Here is a step by step guide for [setting up Beckn Gateway using Beckn-ONIX](https://github.com/beckn/beckn-onix/blob/main/docs/user_guide.md#setting-up-a-gateway)

Recommendation for implementing BAPs:
  - **Transaction APIs**: 
    - BAP MUST implement the mandatory Transaction APIs (on_init, on_confirm, on_status). These APIs are required for receiving DF events and incentive details.
    - BAP MAY implement additional APIs (on_search, on_cancel, on_rating, on_support): 
      - on_search is required if a network wishes to implement DF program discovery and subscription features
      - on_cancel is required for cancellation of an existing DF program subscription
      - on_rating is required for rating existing DF programs
      - on_support is required for handling customer support requests and technical assistance
  - **Layer 2 Compliance**: BAP MUST ensure all requests/responses comply with Layer 2 configuration rules for demand-flexibility domain
  - **Context Management**: BAP MUST generate unique message_id for each interaction and maintain transaction_id across workflow stages
  - **Authentication**: BAP MUST provide on_subscribe endpoint for Registry public-key verification
  - **Error Handling**: BAP MUST gracefully handle NACK responses and implement appropriate business logic triggers
  - **Meta APIs**:
    - BAP MAY implement cancellation_reasons Meta API to receive predefined cancellation reasons from BPP
    - BAP MAY implement rating_categories Meta API to receive predefined rating categories from BPP
  - Here is a step by step guide for [setting up a BAP using Beckn-ONIX](https://github.com/beckn/beckn-onix/blob/main/docs/user_guide.md#setting-up-a-bap-beckn-adapter)

Recommendation for implementing BPPs:
  - **Transaction APIs**: 
    - BPP MUST implement the mandatory Transaction APIs (init, confirm, status). These APIs are required for sending DF events and providing incentive status updates
    - BPP MAY implement additional APIs (search, cancel, rating, support):
      - search is required if a network wishes to implement DF program discovery and subscription features
      - cancel is required for cancellation of an existing DF program subscription
      - rating is required for receiving ratings for a DF program
      - support is required for providing customer support and resolving technical issues
  - **Layer 2 Validation**: BPP MUST ensure all requests/responses comply with Layer 2 configuration rules for demand-flexibility domain
  - **Context Preservation**: BPP MUST return unaltered message_id, transaction_id, bap_id, and bap_uri in responses
  - **Authentication**: BPP MUST provide on_subscribe endpoint for Registry verification and implement Gateway proxy verification for search messages
  - **Meta APIs**: 
    - BPP MAY implement get_cancellation_reasons Meta API if it requires BAP to fetch a predefined set of cancellation reasons
    - BPP MAY implement get_rating_categories Meta API if it requires BAP to fetch a predefined set of rating categories
  - Here is a step by step guide for [setting up a BPP using Beckn-ONIX](https://github.com/beckn/beckn-onix/blob/main/docs/user_guide.md#setting-up-a-bpp-beckn-adapter)

#### 4.3.2 Security and Communication Infrastructure

**Security Infrastructure:**
- Digital signature capabilities for message authentication
- Public key management system for participant verification
- Certificate authorities for endpoint validation
- Secure storage for cryptographic keys

**Communication Infrastructure:**
- HTTPS endpoints for all network communication
- Reverse proxy configuration (typically Nginx) for routing internal services
- Load balancing for high-availability deployments
- Message queuing for asynchronous processing

**Data Management Infrastructure:**
- Real-time data collection from smart meters
- Historical data storage for baseline calculations
- Performance monitoring and reporting
- Compliance and audit trail maintenance

#### 4.3.3 Domain Configuration

**Layer 2 Configuration:**
DF networks require domain-specific configuration files that enforce network-wide rules and standards across all DF transactions. These Layer 2 configurations act as **governance mechanisms** that ensure protocol compliance, data consistency, and semantic interoperability throughout the network.

Layer 2 configurations define and enforce:
- **Schema Compliance Rules**: Mandatory field validations, data type constraints, and API payload structure requirements
- **Energy Domain Vocabularies**: Standardized taxonomies for equipment types, load categories, and flexibility services
- **Measurement Standards**: Required units (kW, kWh, Hz), precision requirements, and conversion factors
- **Baseline Methodology Enforcement**: Approved calculation methods, data requirements, and validation criteria  
- **Incentive Calculation Standards**: Compensation formulas, payment timing rules, and settlement procedures
- **Regional Grid Compliance**: Local grid codes, regulatory requirements, and operational constraints
- **Field Inclusion Policies**: Mandatory vs. optional fields for different transaction types and participant categories

These configurations are applied automatically to **every API call** within the DF network, ensuring that all participants—whether residential aggregators or industrial facilities—operate within consistent technical and business parameters while maintaining full Beckn Protocol compatibility.

#### 4.3.4 Integration Requirements

**Energy Management System Integration:**
Commercial facilities must integrate their energy management systems with the BAP client endpoint to:
- Monitor real-time energy consumption
- Control flexible loads and equipment
- Calculate available flexibility capacity
- Execute load reduction commands

**Grid Operations Integration - The Mission-Critical Interface:**
This integration represents the most technically challenging aspect of DF implementation because it bridges two fundamentally different worlds: traditional power system operations (millisecond response times, N-1 contingency planning, physical laws of power flow) and modern digital marketplaces (API calls, data validation, distributed decision-making).

Grid operators must enhance their existing Energy Management Systems (EMS) to:
- **Real-time Grid Monitoring**: Continuously assess grid frequency (typically 50 or 60 Hz with tolerances of ±0.2 Hz), transmission line loadings (percentage of thermal capacity), and reserve margins (MW of available generation above current load)
- **Predictive Analytics**: Use machine learning models to forecast system stress 15 minutes to 24 hours ahead, accounting for weather forecasts, historical patterns, and planned outages
- **Resource Optimization**: Calculate optimal DF event sizing and timing by modeling the grid impact of distributed load reductions, considering transmission constraints and voltage stability
- **Emergency Procedures**: Integrate DF resources into established grid emergency protocols, including automatic load shedding sequences and black start procedures

**The Engineering Challenge**: Traditional grid operations think in terms of "firm capacity" (guaranteed available power), but DF resources are probabilistic (dependent on participant availability and response). Grid operators must develop new reliability frameworks that account for the statistical nature of distributed flexibility while maintaining the same N-1 contingency standards required for grid stability.

### 4.4 Step-by-Step Implementation

#### 4.4.1 Step 1: Program Discovery

Consumers (residential, commercial, or through aggregators) discover available DF programs using search APIs.

**Process:**
- Consumer entity (household, business, or aggregator) sends search request to find available DF programs
- Search criteria include location, load capacity, participant type, and consumer segment
- Gateway broadcasts the search to all relevant utilities in the network
- Utilities respond with available programs matching the criteria and consumer characteristics

**Key Information Exchanged:**
- Geographic location and coverage area
- Load capacity and flexibility capabilities (individual or aggregated)
- Consumer segment (residential, commercial, industrial)
- Program types and incentive structures tailored to consumer size
- Participation requirements, terms, and minimum commitment levels

#### 4.4.2 Step 2: Program Subscription

Consumer subscribes to selected DF program (directly or through aggregator).

**Process:**
- Consumer entity selects a DF program from search results based on their capacity and preferences
- Submits subscription request with commitment details, capabilities, and participation constraints
- Utility reviews application, validates technical requirements, and confirms subscription
- Subscription becomes active with defined terms, conditions, and consumer-specific parameters

**Key Information Exchanged:**
- Maximum load reduction capacity commitment (individual household or aggregated portfolio)
- Available flexibility timeframes, notice periods, and seasonal variations
- Incentive rates and payment terms appropriate to consumer segment
- Program duration, renewal options, and opt-out procedures
- Performance requirements, penalties, and consumer protection measures

#### 4.4.3 Step 3: DF Event Notification

**The Moment of Truth: When the Grid Calls for Help**

This step represents the convergence of sophisticated grid engineering and market dynamics. Unlike traditional power plant dispatch (where utilities own and control generation resources), DF events require **negotiating with independent actors** who have their own business priorities and technical constraints.

**The Grid Operator's Decision Matrix:**
When system stress is detected, grid operators must make rapid decisions balancing multiple factors:
- **Technical Requirements**: How much load reduction is needed, where on the grid, and for how long?
- **Economic Optimization**: Which participants can deliver flexibility most cost-effectively?
- **Reliability Assurance**: What's the confidence level that participants will actually perform?
- **System Impact**: How will reduced consumption affect voltage profiles and power flows?

**Process:**
- **Grid Condition Assessment**: Operators analyze real-time data from thousands of sensors across the transmission and distribution network, identifying stress patterns that may lead to equipment overloads or frequency deviations
- **Optimization Algorithm Execution**: Advanced algorithms simultaneously solve for optimal participant selection, event timing, and incentive levels while respecting grid constraints and participant availability
- **Multi-Participant Coordination**: The system constructs event notifications for potentially hundreds of participants, each receiving customized requests based on their location, capacity, and contract terms
- **Real-time Validation**: Before sending notifications, the system validates that the proposed DF event will actually resolve the grid constraint without creating new problems elsewhere

**Key Information Exchanged:**
- **Grid Context**: Current frequency (e.g., "49.8 Hz, declining"), transmission loading percentages, and projected stress duration
- **Locational Signals**: Specific grid areas where load reduction is most valuable (transmission constraints are highly location-dependent)
- **Economic Signals**: Real-time pricing that reflects both grid need and participant availability
- **Technical Requirements**: Precise timing (including required ramp rates), duration, and any operational constraints

#### 4.4.4 Step 4: Event Participation Confirmation

Commercial consumer confirms participation in DF event.

**Process:**
- Commercial facility evaluates event requirements against operational constraints
- Determines available load reduction capacity for the event timeframe
- Commits to specific load reduction amount with confidence level
- Confirms participation with baseline and target consumption details

**Key Information Exchanged:**
- Committed load reduction amount and confidence level
- Baseline consumption and target consumption during event
- Confirmation of participation timing and constraints
- Equipment and systems to be controlled during event
- Emergency override and safety procedures

#### 4.4.5 Step 5: Performance Verification

Utility verifies actual load reduction delivered during the DF event.

**Process:**
- Utility collects real-time meter data during event period
- Compares actual consumption against calculated baseline
- Validates load reduction against commitment
- Assesses any deviations or operational constraints reported
- Calculates final performance metrics

**Key Information Exchanged:**
- Actual consumption data with timestamps
- Baseline consumption for comparison
- Load reduction achieved (kW and duration)
- Performance percentage against commitment
- Any qualifying events or exceptions

#### 4.4.6 Step 6: Incentive Settlement

Utility processes incentive payments based on verified performance.

**Process:**
- Utility calculates incentive amount based on verified performance
- Applies any adjustments for partial performance or exceptions
- Sends settlement notification with performance details
- Processes payment according to program terms
- Updates participant performance history

**Key Information Exchanged:**
- Performance verification results
- Incentive calculation breakdown
- Payment amount and timing
- Settlement status and confirmation
- Updated performance metrics for future events

### 4.5 Testing

#### 4.5.1 Test Scenarios

Key validation scenarios for DF implementation:

1. **Program Discovery Test**
   - **Test Case:** Search for DF programs with various criteria
   - **Expected Result:** Relevant programs returned with accurate details

2. **Subscription Flow Test**
   - **Test Case:** Complete subscription process for multiple programs
   - **Expected Result:** Successful enrollment with proper terms

3. **Event Response Test**
   - **Test Case:** Respond to DF events under different conditions
   - **Expected Result:** Appropriate load reduction achieved

4. **Performance Verification Test**
   - **Test Case:** Verify actual load reduction against baseline and commitments
   - **Expected Result:** Accurate measurement of delivered flexibility with proper exception handling

5. **Settlement Verification**
   - **Test Case:** Calculate and verify incentive payments
   - **Expected Result:** Accurate calculation based on actual performance

#### 4.5.2 Validation Checklist

- [ ] API endpoints respond within timeout limits
- [ ] Digital signatures validate correctly
- [ ] Load reduction targets are achievable
- [ ] Baseline calculations are accurate
- [ ] Incentive calculations match contract terms
- [ ] Data privacy requirements are met
- [ ] Emergency override procedures work

## 5. Best Practices

### 5.1 Design Principles

1. **Reliability First**: DF systems must maintain grid stability as primary objective
2. **Transparent Incentives**: Clear calculation methods and timely payments
3. **Participant Autonomy**: Consumers retain control over their participation decisions
4. **Scalable Architecture**: Support growth from pilots to system-wide deployment

### 5.2 Common Patterns

#### 5.2.1 Pattern 1: Baseline Calculation

**What is a Baseline?**
A baseline is the **financial and technical foundation** of any demand flexibility program—imagine it as the "truth serum" that determines whether participants actually delivered the grid services they promised, and consequently, whether they get paid.

Think of it like a performance athlete's personal best time. Before you can claim you ran faster, everyone needs to agree on your normal running speed. In the electricity world, before you can claim you reduced 200 kW of demand, everyone needs to agree on how much electricity you normally use.

But here's where it gets technically fascinating: electricity consumption patterns are incredibly complex. A shopping mall's "normal" consumption depends on weather (hotter = more air conditioning), day of week (weekends = different tenant operations), season (holiday shopping = higher loads), and even local events (nearby concert = parking lot lighting). Creating an accurate baseline requires sophisticated statistical analysis that accounts for all these variables.

**The Engineering Reality:** Grid operators need baselines that are forensically accurate because they're the basis for million-dollar settlements. A 1% error in baseline calculation across a 50 MW demand response portfolio could result in $50,000+ in incorrect payments annually. This is why baseline calculation isn't just math—it's engineering economics.

**Why Baselines Matter:**
Without accurate baselines, the system falls apart:
- **Fair Payment**: How do you pay someone for reducing electricity if you don't know their normal usage?
- **Gaming Prevention**: Without baselines, participants could artificially use more electricity on normal days to make their "reductions" look bigger
- **Performance Verification**: Utilities need proof that load reduction actually happened

**How Baseline Calculation Works:**
The BPP (Grid/Utility) must have a mechanism to calculate accurate baselines for all participants. One commonly used method is the "3-of-5 Average" approach, which uses historical consumption data to establish normal usage patterns.

**When to Use This Pattern:** Every demand flexibility program that pays participants based on their actual electricity reduction performance.

#### 5.2.2 Pattern 2: Graduated Response

**What is Graduated Response?**
Graduated response is like a traffic light system for electricity emergencies. Just as traffic lights have green (go normally), yellow (caution), and red (stop), the electricity grid has different levels of urgency requiring different responses.

Think of it like a hospital emergency system:
- **Green Zone**: Normal operations, no action needed
- **Yellow Zone**: Busy but manageable, voluntary help appreciated  
- **Red Zone**: Critical situation, all available help needed immediately

**Why Graduated Response is Needed:**
The electricity grid faces different levels of stress:
- **Minor Peak**: Slightly higher than normal demand (like a busy shopping day)
- **Significant Strain**: Notable supply shortage (like a hot summer afternoon when everyone uses air conditioning)
- **Emergency**: Potential blackout risk (like when a power plant unexpectedly shuts down)

Each situation requires a different level of response and offers different compensation.

**How Graduated Response Works:**

**Level 1 - Advisory (Green Light):**
- **Situation**: "We're getting busy, but manageable"
- **Request**: "Please reduce 5% of your electricity use if convenient"
- **Participation**: Voluntary - you can say no without penalty
- **Payment**: Low rate, like a "thank you" bonus
- **Example**: "We're seeing higher demand today. If you can turn off some non-essential lights, we'll give you a small credit."

**Level 2 - Warning (Yellow Light):**
- **Situation**: "We need help to maintain stability"
- **Request**: "Please reduce 15% of your electricity use"
- **Participation**: Mandatory for enrolled participants
- **Payment**: Standard rate you agreed to when you joined
- **Example**: "Grid demand is high. Please reduce HVAC load and non-critical equipment as committed."

**Level 3 - Emergency (Red Light):**
- **Situation**: "Risk of blackouts, all hands on deck"
- **Request**: "Please reduce 25% or more of your electricity use immediately"
- **Participation**: Mandatory, with penalties for non-compliance
- **Payment**: Premium rate - highest compensation
- **Example**: "Major power plant offline. Implement maximum load reduction to prevent system collapse."

**When to Use This Pattern:** When your demand flexibility program needs to handle both routine peak management (happens regularly) and genuine emergency situations (rare but critical).

### 5.3 Anti-Patterns

#### 5.3.1 Anti-Pattern 1: Over-Promising Flexibility

Committing to load reductions beyond actual capability.

**Why it's problematic:** Can compromise grid reliability and damage program credibility
**Better approach:** Conservative estimates with confidence intervals and backup plans

#### 5.3.2 Anti-Pattern 2: Ignoring Baseline Accuracy

Using inaccurate or manipulated baselines for incentive calculation.

**Why it's problematic:** Creates perverse incentives and unfair compensation
**Better approach:** Robust baseline methodologies with independent verification

### 5.4 Performance Considerations

- **Response Time**: DF events have varying notification periods depending on type - week-ahead (planned maintenance), day-ahead (weather forecasts), intraday (equipment failures), to real-time emergency response
- **Data Accuracy**: Real-time monitoring needed for verification
- **System Reliability**: 99.9% uptime requirement for critical grid services
- **Scalability**: Architecture must support hundreds of participants per utility

### 5.5 Language and Conventions

#### 5.5.1 Naming Conventions

**API Endpoints:**
- Use lowercase with hyphens for domain names: `energy:demand-flexibility`
- Action names follow Beckn standard: `search`, `confirm`, `on_init`, `on_status`
- Resource IDs use descriptive names: `df-program-subscription-001`, `load-reduction-request`

**JSON Field Naming:**
- Use snake_case for custom fields: `max_reduction_kw`, `baseline_kw`
- Follow Beckn core schema for standard fields: `transaction_id`, `message_id`, `timestamp`
- Energy-specific units clearly specified: `kW`, `kWh`, `Hz`

**Identifier Patterns:**
- Transaction IDs: `df-[action]-[sequence]` (e.g., `df-search-001`)
- Event IDs: `df-event-[YYYYMMDD]-[sequence]` (e.g., `df-event-20250818-001`)
- Participant IDs: Domain-based (e.g., `commercial-facility.example.com`)

#### 5.5.2 Data Validation Rules

**Required Fields:**
- All Beckn context fields (domain, action, version, timestamp, etc.)
- Energy-specific tags for measurement units and calculations
- Baseline and target consumption values for performance tracking

**Value Constraints:**
- Timestamps in ISO 8601 format with timezone information
- Energy measurements with appropriate units (kW, kWh, MW, MWh)
- Grid frequency in Hz with decimal precision (e.g., "49.7Hz")
- Currency codes following ISO 4217 standard

**Schema Compliance:**
- All messages must validate against Beckn Protocol core schema
- Energy domain extensions follow consistent patterns
- Custom tags documented with clear semantic meaning

**Note:** A comprehensive list of data validation rules, including field requirements, data types, and validation logic, is configured in the Layer 2 configurations (see Section 4.3.3). These configurations serve as the single source of truth for all data validation across the DF network.

#### 5.5.3 Error Handling Standards

**Error Response Format:**
- Use standard Beckn error structure in context and message fields
- Include specific error codes for DF-related failures
- Provide human-readable error descriptions for debugging

**Common Error Scenarios:**
- Insufficient load reduction capacity available
- Baseline calculation failures or disputes
- Communication timeouts during critical events
- Authorization failures for sensitive grid operations

### 5.6 Security Considerations

- **Data Privacy**: Energy consumption data requires strict privacy protection
- **Authentication**: Digital signatures and PKI for all transactions
- **Authorization**: Role-based access control for different participants
- **Audit Trail**: Complete logging of all DF events and responses

## 6. IANA Considerations

This document has no IANA actions.

## 7. Examples

This section provides comprehensive JSON examples for all Demand Flexibility API interactions. These examples follow the Beckn Protocol specification and demonstrate production-ready message formats.

### 7.1 Discovery Examples

#### 7.1.1 Program Discovery (search API)

- Consumers (residential, commercial, retail, industrial) search for available DF programs for subscription
- The example below demonstrates a comprehensive parameter set; consumers MAY use a subset of these parameters as per their requirements
- This API call is required only when consumers need to discover available DF programs for subscription
- BAPs that do not implement DF program subscription functionality MAY omit this API

Consumer searches for available DF programs: [Example](../../../../examples/demand_flexibility/1.discover/discover-request.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/1.discover/discover-request.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "search",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "transaction_id": "df-txn-1001",
    "message_id": "df-msg-2001",
    "timestamp": "2025-08-20T14:30:00+05:30",
    "ttl": "PT30S"
  },
  "message": {
    "intent": {
      "descriptor": {
        "name": "Demand flexibility Programs"
      },
      "category": {
        "descriptor": {
          "name": "demand-flexibility"
        }
      },
      "fulfillment": {
        "stops": [
          {
              "type": "end",
              "location": {
                "gps": "28.613901,77.209010",
                "address": "meter://brpl/98765456",
                "area_code": "110001"
              },
              "time": {
                "range": {
                  "start": "2025-08-26T00:00:00.000Z",
                  "end": "2025-08-26T23:59:59.999Z"
                }
              }
          }
        ]
      }
      "tags": [
        {
          "descriptor": {
            "name": "Participant Capabilities"
          },
          "list": [
            {
              "descriptor": {
                "code": "load_capacity",
                "name": "Load Reduction Capacity"
              },
              "value": "500kW"
            },
            {
              "descriptor": {
                "code": "participant_type",
                "name": "Participant Type"
              },
              "value": "commercial"
            },
            {
              "descriptor": {
                "code": "control_type",
                "name": "Load Control Method"
              },
              "value": "automated"
            }
          ]
        },
        {
          "descriptor": {
            "name": "Availability Parameters"
          },
          "list": [
            {
              "descriptor": {
                "code": "response_time",
                "name": "Response Time Capability"
              },
              "value": "15min"
            },
            {
              "descriptor": {
                "code": "availability_hours",
                "name": "Operating Hours"
              },
              "value": "09:00-18:00"
            },
            {
              "descriptor": {
                "code": "availability_days",
                "name": "Operating Days"
              },
              "value": "weekdays"
            },
            {
              "descriptor": {
                "code": "seasonal_availability",
                "name": "Seasonal Availability"
              },
              "value": "summer,winter"
            }
          ]
        },
        {
          "descriptor": {
            "name": "Event Parameters"
          },
          "list": [
            {
              "descriptor": {
                "code": "min_event_duration",
                "name": "Minimum Event Duration"
              },
              "value": "30min"
            },
            {
              "descriptor": {
                "code": "max_event_duration",
                "name": "Maximum Event Duration"
              },
              "value": "240min"
            },
            {
              "descriptor": {
                "code": "notification_type",
                "name": "Preferred Notification Type"
              },
              "value": "day_ahead"
            }
          ]
        },
        {
          "descriptor": {
            "name": "Technical Parameters"
          },
          "list": [
            {
              "descriptor": {
                "code": "load_type",
                "name": "Controllable Load Types"
              },
              "value": "hvac,lighting,process"
            }
          ]
        },
        {
          "descriptor": {
            "name": "Incentive Parameters"
          },
          "list": [
            {
              "descriptor": {
                "code": "min_incentive_rate",
                "name": "Minimum Incentive Rate"
              },
              "value": "5.00"
            },
            {
              "descriptor": {
                "code": "incentive_currency",
                "name": "Incentive Currency"
              },
              "value": "INR_per_kWh_load_reduction"
            }
          ]
        },
        {
          "descriptor": {
            "name": "Priority Parameters"
          },
          "list": [
            {
              "descriptor": {
                "code": "event_priority",
                "name": "Event Priority Level"
              },
              "value": "high,medium"
            },
            {
              "descriptor": {
                "code": "participation_mode",
                "name": "Participation Mode"
              },
              "value": "mandatory,voluntary"
            }
          ]
        }
      ]
    }
  }
}
```
</details>

**Parameter Explanation:**

**Search Criteria:**
- `descriptor.name`: Free text search for DF programs (user can enter any search terms)
- `category.descriptor.name`: Category-based search filter (user can choose specific program categories)

**Location and Timing:**
- `stops.type`: Set to "end" to indicate consumer location
- `stops.location`: Consumer's location details (REQUIRED - MAY include any combination of gps, address, or area_code as per implementor needs)
- `stops.time.range`: Time range for which DF programs are sought (OPTIONAL - can be omitted if searching for all available programs)

**Participant Capabilities:**
- `load_capacity`: Total load reduction capacity the participant can offer (used by grid to assess potential impact)
- `participant_type`: Type of participant - residential, commercial, industrial, retail (used for program eligibility filtering)
- `control_type`: Load control capabilities this consumer has - automated, manual, hybrid (used to match with program requirements)

**Availability Parameters:**
- `response_time`: How quickly participant can respond to DF events (used to match with program urgency requirements)
- `availability_hours`: Operating hours when participant can participate (used to align with event timing)
- `availability_days`: Days of the week when participation is possible (used for program scheduling)
- `seasonal_availability`: Seasons when participant is available - summer, winter, all (used for seasonal program matching)

**Event Parameters:**
- `min_event_duration`: Shortest duration participant can maintain load reduction (used to filter compatible programs)
- `max_event_duration`: Longest duration participant can sustain response (used to prevent overcommitment)
- `notification_type`: Preferred advance notice period - instant, day_ahead, week_ahead (used to match notification preferences)

**Technical Parameters:**
- `load_type`: Types of controllable loads - hvac, lighting, process, pumps that participant has (used to match with program requirements)

**Incentive Parameters:**
- `min_incentive_rate`: Minimum acceptable compensation rate (used to filter programs meeting economic requirements)
- `incentive_currency`: Expected currency and basis - INR_per_kWh_load_reduction (used to clarify compensation structure)

**Priority Parameters:**
- `event_priority`: Priority levels participant will respond to - high, medium, low (used to match with grid urgency levels)
- `participation_mode`: Participation type preference - mandatory, voluntary (used to filter program types)

#### 7.1.2 A catalog of DF programs (on_search API)

- Consumers receive a catalog of available DF programs for subscription
- The example below demonstrates a comprehensive catalog response
- This API call is required only when consumers need to discover available DF programs for subscription
- BPPs that do not implement DF program subscription functionality MAY omit this API

DISCOM returns catalog of available DF programs: [Example](../../../../examples/demand_flexibility/1.discover/on_discover-response.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/1.discover/on_discover-response.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "on_search",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "DEL"
      }
    },
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1001",
    "message_id": "df-msg-2001",
    "timestamp": "2025-08-20T14:30:00+05:30"
  },
  "message": {
    "catalog": {
      "descriptor": {
        "name": "Catalog for demand flexibility Programs"
      },
      "providers": [
        {
          "id": "brpl_df_001",
          "descriptor": {
            "name": "BRPL",
            "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
            "images": [
              {
                "url": "https://brpl.co.in/assets/logo.png"
              }
            ]
          },
          "locations": [
            {
              "id": "1",
              "city": {
                "name": "New Delhi"
              }
            }
          ],
          "fulfillments": [
            {
              "id": "f1",
              "type": "DIGITAL",
              "tags": [
                {
                  "descriptor": {
                    "code": "event_notification_delivery"
                  },
                  "list": [
                    {
                      "value": "api_push"
                    },
                    {
                      "value": "sms_alert"
                    },
                    {
                      "value": "email_notice"
                    }
                  ]
                }
              ]
            }
          ],
          "categories": [
            {
              "id": "always_available",
              "descriptor": {
                "code": "ALWAYS_AVAILABLE",
                "name": "Always Available Programs"
              }
            },
            {
              "id": "seasonal_programs",
              "descriptor": {
                "code": "SEASONAL",
                "name": "Seasonal Programs (Summer/Winter)"
              }
            },
            {
              "id": "emergency_only",
              "descriptor": {
                "code": "EMERGENCY_ONLY",
                "name": "Emergency-Only Programs"
              }
            }
          ],
          "items": [
            {
              "id": "brpl_peak_saver_001",
              "descriptor": {
                "name": "Evening Peak Saver Program",
                "short_desc": "₹5/kWh for 2-5 PM reductions (manual acceptance)",
                "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Upon manual acceptance, they can reduce usage and earn ₹5 for every kWh saved during the window.",
                "additional_desc": {
                  "url": "https://brpl.co.in/flexibility/peak-saver"
                }
              },
              "location_ids": [
                "1"
              ],
              "category_ids": [
                "seasonal_programs"
              ],
              "fulfillment_ids": [
                "f1"
              ],
              "tags": [
                {
                  "descriptor": {
                    "name": "Participant Capabilities"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "load_capacity",
                        "name": "Load Reduction Capacity"
                      },
                      "value": "100kW-1000kW"
                    },
                    {
                      "descriptor": {
                        "code": "participant_type",
                        "name": "Participant Type"
                      },
                      "value": "commercial,residential"
                    },
                    {
                      "descriptor": {
                        "code": "control_type",
                        "name": "Load Control Method"
                      },
                      "value": "manual"
                    }
                  ]
                },
                {
                  "descriptor": {
                    "name": "Availability Parameters"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "response_time",
                        "name": "Response Time Capability"
                      },
                      "value": "30min"
                    },
                    {
                      "descriptor": {
                        "code": "availability_hours",
                        "name": "Operating Hours"
                      },
                      "value": "14:00-17:00"
                    },
                    {
                      "descriptor": {
                        "code": "availability_days",
                        "name": "Operating Days"
                      },
                      "value": "weekdays"
                    },
                    {
                      "descriptor": {
                        "code": "seasonal_availability",
                        "name": "Seasonal Availability"
                      },
                      "value": "summer,monsoon"
                    }
                  ]
                },
                {
                  "descriptor": {
                    "name": "Event Parameters"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "min_event_duration",
                        "name": "Minimum Event Duration"
                      },
                      "value": "60min"
                    },
                    {
                      "descriptor": {
                        "code": "max_event_duration",
                        "name": "Maximum Event Duration"
                      },
                      "value": "180min"
                    },
                    {
                      "descriptor": {
                        "code": "notification_type",
                        "name": "Notification Type"
                      },
                      "value": "day_ahead"
                    }
                  ]
                },
                {
                  "descriptor": {
                    "name": "Incentive Parameters"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "incentive_rate",
                        "name": "Incentive Rate"
                      },
                      "value": "5.00"
                    },
                    {
                      "descriptor": {
                        "code": "incentive_currency",
                        "name": "Incentive Currency"
                      },
                      "value": "INR"
                    },
                    {
                      "descriptor": {
                        "code": "settlement_frequency",
                        "name": "Settlement Frequency"
                      },
                      "value": "monthly"
                    }
                  ]
                },
                {
                  "descriptor": {
                    "name": "Priority Parameters"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "event_priority",
                        "name": "Event Priority Level"
                      },
                      "value": "medium"
                    },
                    {
                      "descriptor": {
                        "code": "participation_mode",
                        "name": "Participation Mode"
                      },
                      "value": "voluntary"
                    },
                    {
                      "descriptor": {
                        "code": "grid_condition",
                        "name": "Grid Condition Trigger"
                      },
                      "value": "peak_demand"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```
</details>

**Response Structure Explanation:**

**Provider Information:**
- `id`: Unique identifier for the DF program provider (used for subsequent API calls)
- `descriptor.name`: Provider's display name (e.g., "BRPL")
- `descriptor.short_desc`: Brief description of provider's DF programs and coverage area
- `locations`: Geographic areas where provider operates DF programs

**Fulfillment Options:**
- `id`: Unique identifier for the fulfillment method
- `type`: Service delivery type (typically "DIGITAL" for DF programs)
- `event_notification_delivery`: Available notification methods for DF event push (api_push, sms_alert, email_notice)

**Program Categories:**
- Categories help consumers filter programs by availability commitment (always available, seasonal, emergency-only)
- Each category has a unique `id` and descriptive `code` for filtering

**Available Programs (Items):**
- `id`: Unique program identifier for subscription requests
- `descriptor.name`: Program display name
- `descriptor.short_desc`: Brief program summary including incentive rate
- `descriptor.long_desc`: Detailed program description and participation requirements
- `category_ids`: Links to applicable program categories
- `fulfillment_ids`: Links to available fulfillment methods
- `location_ids`: Links to available location objects

**Program Tags (Key Parameters):**
- **Participant Capabilities**: `load_capacity` (capacity range), `participant_type` (eligible consumer types), `control_type` (required control method)
- **Availability Parameters**: `response_time` (required response time), `availability_hours` (operating hours), `availability_days` (operating days), `seasonal_availability` (seasons)
- **Event Parameters**: `min_event_duration` and `max_event_duration` (event duration range), `notification_type` (advance notice period)
- **Incentive Parameters**: `incentive_rate` (compensation rate), `incentive_currency` (payment currency), `settlement_frequency` (payment schedule)
- **Priority Parameters**: `event_priority` (priority levels), `participation_mode` (voluntary/mandatory), `grid_condition` (triggering conditions)

This catalog structure allows consumers to evaluate and select DF programs that match their capabilities and preferences.

### 7.2 DF program subscription Examples

#### 7.2.1 DF program Subscription Request (confirm API)

- Consumers send a subscription confirmation for a selected DF program using order.type = "program_subscription"
- The example below demonstrates the subscription request structure
- This API call is required only when consumers need to subscribe to DF programs
- BAPs that do not implement DF program subscription functionality MAY omit this API

Consumer confirms subscription to a DF program: [Example](../../../../examples/demand_flexibility/2.subscription/confirm-request.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/2.subscription/confirm-request.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "confirm",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1002",
    "message_id": "df-msg-2002",
    "timestamp": "2025-08-20T14:45:00+05:30",
    "ttl": "PT30S"
  },
  "message": {
    "order": {
      "type": "program_subscription",
      "provider": {
        "id": "brpl_df_001"
      },
      "items": [
        {
          "id": "brpl_peak_saver_001"
        }
      ],
      "fulfillments": [
        {
          "id": "f1",
          "stops": [
            {
                "type": "end",
                "location": {
                  "descriptor": {
                    "name": "Gov Bus Depot, Anand Vihar",
                  },
                  "city": {
                    "code": "New-Delhi"
                  },
                  "gps": "28.613901,77.209010",
                  "area_code": "110001"
                },
                "time": {
                  "range": {
                    "start": "2025-08-26T00:00:00.000Z",
                    "end": "2025-08-26T23:59:59.999Z"
                  }
                }
            }
          ]
        }
      ]
    }
  }
}
```
</details>

**Request Structure Explanation:**

**Order Information:**
- `order.type`: Set to "program_subscription" to indicate subscription request
- `order.provider`: References the selected provider from on_search response
- `order.items`: Contains the specific DF program consumer wishes to subscribe

**Item Details:**
- `id`: Program identifier from the catalog (used to identify specific program)

**Fulfillment Method:**
- `id`: Selected fulfillment option from available options
- `stops`: Contains consumer's location and operational timeframe

This request formally commits the consumer to participate in the selected DF program.

#### 7.2.2 DF program Subscription confirmation (on_confirm API)

- BPPs send subscription acknowledgment to confirm consumer enrollment in the DF program
- The example below demonstrates the confirmation response structure
- This API call is required only when BPPs need to acknowledge DF program subscriptions
- BPPs that do not implement DF program subscription functionality MAY omit this API

DISCOM confirms consumer subscription to DF program: [Example](../../../../examples/demand_flexibility/2.subscription/on_confirm-response.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/2.subscription/on_confirm-response.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "on_confirm",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1002",
    "message_id": "df-msg-2002",
    "timestamp": "2025-08-20T14:46:00+05:30"
  },
  "message": {
    "order": {
      "type": "program_subscription",
      "id": "df-program-subscription-001",
      "provider": {
        "id": "brpl_df_001",
        "descriptor": {
          "name": "BRPL",
          "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
          "images": [
            {
              "url": "https://brpl.co.in/assets/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "brpl_peak_saver_001",
          "descriptor": {
            "name": "Evening Peak Saver Program",
            "short_desc": "₹5/kWh for 2-5 PM reductions (manual acceptance)",
            "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Upon manual acceptance, they can reduce usage and earn ₹5 for every kWh saved during the window.",
            "additional_desc": {
              "url": "https://brpl.co.in/flexibility/peak-saver"
            }
          },
          "tags": [
            {
              "descriptor": {
                "name": "Subscription Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "max_reduction_kw",
                    "name": "Maximum Reduction Capacity"
                  },
                  "value": "200"
                },
                {
                  "descriptor": {
                    "code": "notice_period_hours",
                    "name": "Notice Period"
                  },
                  "value": "2"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Participant Capabilities"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "load_capacity",
                    "name": "Load Reduction Capacity"
                  },
                  "value": "100kW-1000kW"
                },
                {
                  "descriptor": {
                    "code": "participant_type",
                    "name": "Participant Type"
                  },
                  "value": "commercial,residential"
                },
                {
                  "descriptor": {
                    "code": "control_type",
                    "name": "Load Control Method"
                  },
                  "value": "manual"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Availability Parameters"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "response_time",
                    "name": "Response Time Capability"
                  },
                  "value": "30min"
                },
                {
                  "descriptor": {
                    "code": "availability_hours",
                    "name": "Operating Hours"
                  },
                  "value": "14:00-17:00"
                },
                {
                  "descriptor": {
                    "code": "availability_days",
                    "name": "Operating Days"
                  },
                  "value": "weekdays"
                },
                {
                  "descriptor": {
                    "code": "seasonal_availability",
                    "name": "Seasonal Availability"
                  },
                  "value": "summer,monsoon"
                }
              ]
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "f1",
          "stops": [
            {
                "type": "end",
                "location": {
                  "descriptor": {
                    "name": "Gov Bus Depot, Anand Vihar",
                  },
                  "city": {
                    "code": "New-Delhi"
                  },
                  "gps": "28.613901,77.209010",
                  "area_code": "110001"
                },
                "time": {
                  "range": {
                    "start": "2025-08-26T00:00:00.000Z",
                    "end": "2025-08-26T23:59:59.999Z"
                  }
                }
            }
          ],
          "state": {
            "descriptor": {
              "code": "SUBSCRIBED"
            }
          }
        }
      ]
    }
  }
}
```
</details>

**Response Structure Explanation:**

**Subscription Confirmation:**
- `order.type`: type of the info this payload contains, in this case it is "program_subscription" type
- `order.id`: Unique identifier assigned for this particular subscription
- `order.provider`: Provider details confirming program enrollment
- `order.items`: Enrolled program details

**Enrollment Details:**
- Item details are the same as received in the on_search response, confirming the specific program that was subscribed to

**Assigned Fulfillment:**
- Fulfillment details are the same as in on_search response, but with updated state
- State changes to "SUBSCRIBED" after successful subscription, or relevant error state if subscription failed at BPP level

This response confirms successful enrollment and provides the consumer with subscription details and assigned identifiers for future reference.

### 7.3 DF Event Management Examples

#### 7.3.1 DF Event Notification (on_init API)

- BPPs initiate DF events when grid conditions require demand reduction using order.type = "event_participation"
- The example below demonstrates the event notification structure
- This API call is required for core DF functionality when BPPs need to notify consumers of DF events
- BAPs MUST implement this API

DISCOM notifies consumer of a DF event: [Example](../../../../examples/demand_flexibility/3.event/1.on_init-event-notification.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/3.event/1.on_init-event-notification.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "on_init",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1003",
    "message_id": "df-msg-2003",
    "timestamp": "2025-08-20T14:45:00+05:30"
  },
  "message": {
    "order": {
      "type": "event_participation",
      "provider": {
        "id": "brpl_df_001",
        "descriptor": {
          "name": "BRPL",
          "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
          "images": [
            {
              "url": "https://brpl.co.in/assets/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "brpl_peak_saver_001_event_001",
          "descriptor": {
            "name": "Evening Peak Saver Program - Event",
            "short_desc": "Load reduction request for 150kW during peak hours",
            "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Please reduce load by 150kW from your baseline during this event window.",
            "additional_desc": {
              "url": "https://brpl.co.in/flexibility/peak-saver"
            }
          },
          "quantity": {
            "measure": {
              "unit": "kW",
              "value": "150"
            }
          },
          "tags": [
            {
              "descriptor": {
                "name": "Event Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "subscription_id",
                    "name": "Program Subscription ID"
                  },
                  "value": "df-program-subscription-001"
                },
                {
                  "descriptor": {
                    "code": "program_id",
                    "name": "Program ID"
                  },
                  "value": "brpl_peak_saver_001"
                },
                {
                  "descriptor": {
                    "code": "priority",
                    "name": "Event Priority"
                  },
                  "value": "high"
                },
                {
                  "descriptor": {
                    "code": "grid_frequency",
                    "name": "Grid Frequency"
                  },
                  "value": "49.7Hz"
                },
                {
                  "descriptor": {
                    "code": "response_deadline",
                    "name": "Response Required By"
                  },
                  "value": "2025-08-20T15:00:00+05:30"
                },
                {
                  "descriptor": {
                    "code": "baseline_kw",
                    "name": "Calculated Baseline Load"
                  },
                  "value": "400"
                },
                {
                  "descriptor": {
                    "code": "baseline_method",
                    "name": "Baseline Calculation Method"
                  },
                  "value": "3-of-5_average"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Incentive Parameters"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "incentive_rate",
                    "name": "Incentive Rate"
                  },
                  "value": "5.00"
                },
                {
                  "descriptor": {
                    "code": "incentive_currency",
                    "name": "Incentive Currency"
                  },
                  "value": "INR"
                },
                {
                  "descriptor": {
                    "code": "incentive_type",
                    "name": "Incentive Type"
                  },
                  "value": "per_kWh_reduced"
                }
              ]
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "stops": [
            {
              "time": {
                "range": {
                  "start": "2025-08-26T00:00:00.000Z",
                  "end": "2025-08-26T23:59:59.999Z"
                }
              }
            }
          ],
          "state": {
            "descriptor": {
              "code": "REQUESTED"
            }
          }
        }
      ]
    }
  }
}
```
</details>

**Request Structure Explanation:**

**Critical API Overview:**
This API represents the core moment when grid operators request demand flexibility from consumers. It transforms grid stress into actionable consumer requests, making it the cornerstone of demand response programs.

**Event Details:**
- `order.type`: Set to "event_participation" to distinguish this from subscription requests - this is an actual event call
- `order.provider`: Grid operator/utility initiating the event, establishing accountability and trust
- `order.items`: Contains the specific DF event details that consumers must evaluate for participation

**Event Parameters (Consumer Decision Factors):**
- `items.id`: Unique event identifier enabling precise tracking across all systems and settlement processes
- `items.descriptor`: Human-readable event description including context and load reduction requirements
- `quantity.measure.value`: Specific load reduction requested from this consumer (in kW) - forms the basis of commitment and compensation
- `quantity.measure.unit`: Unit of measurement for the requested reduction (typically "kW")

**Event Details Tags:**
- `status`: Current event status - "REQUESTED" indicates the grid operator is awaiting consumer's participation decision
- `priority`: Event urgency classification (high=critical grid stress requiring immediate response, medium=economic optimization, low=voluntary participation)
- `grid_frequency`: Real-time grid frequency measurement (normal=50Hz, deviations indicate system stress requiring demand response)
- `response_deadline`: Critical deadline for consumer confirmation - enables grid operator to plan alternative actions
- `baseline_kw`: Consumer's calculated normal consumption during event period - critical for fair performance measurement
- `baseline_method`: How baseline was calculated (e.g., "3-of-5_average") - provides transparency in measurement

**Program Context Tags:**
- `subscription_id`: Links to consumer's program enrollment - ensures event is sent to eligible participants only
- `program_id`: Specific DF program triggering this event - enables program-specific response rules and compensation

**Incentive Information Tags:**
- `incentive_rate`: Compensation rate for load reduction
- `incentive_currency`: Payment currency (e.g., "INR")
- `incentive_type`: Basis for calculation (e.g., "per_kWh_reduced")

**Event Timing (Operational Coordination):**
- `fulfillments.stops.time.range`: Event start and end times - ensures synchronized response across grid
- `fulfillments.state`: Current fulfillment status of the event

**Consumer Response Requirements:**
Consumers receiving this notification must:
1. Evaluate their operational ability to provide the requested load reduction
2. Consider the event timing against their operational schedules
3. Assess the baseline calculation for accuracy
4. Respond within the specified deadline with their participation decision
5. Understand that non-response may be treated as non-participation

**Grid Operator Responsibilities:**
- Ensure baseline calculations are accurate and fair
- Provide sufficient advance notice as per program terms
- Send events only to eligible, subscribed consumers
- Include all necessary context for informed consumer decisions
- Respect consumer operational constraints and response capabilities

This notification represents a bilateral contract offer that, once accepted, creates binding obligations for both parties.

#### 7.3.2 DF Event Participation Confirmation (confirm API)

- Consumers respond to DF event notifications by confirming their participation decision using order.type = "event_participation"
- The example below demonstrates the participation confirmation structure
- This API call is required for core DF functionality when consumers respond to DF event notifications
- BPPs MUST implement this API

Consumer confirms participation in DF event: [Example](../../../../examples/demand_flexibility/3.event/confirm-event-participation.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/3.event/confirm-event-participation.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "confirm",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1003",
    "message_id": "df-msg-2004",
    "timestamp": "2025-08-20T14:50:00+05:30"
  },
  "message": {
    "order": {
      "type": "event_participation",
      "provider": {
        "id": "brpl_df_001",
        "descriptor": {
          "name": "BRPL",
          "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
          "images": [
            {
              "url": "https://brpl.co.in/assets/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "brpl_peak_saver_001_event_001",
          "descriptor": {
            "name": "Evening Peak Saver Program - Event",
            "short_desc": "Load reduction request for 150kW during peak hours",
            "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Please reduce load by 150kW from your baseline during this event window.",
            "additional_desc": {
              "url": "https://brpl.co.in/flexibility/peak-saver"
            }
          },
          "quantity": {
            "measure": {
              "unit": "kW",
              "value": "120"
            }
          },
          "tags": [
            {
              "descriptor": {
                "name": "Event Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "subscription_id",
                    "name": "Program Subscription ID"
                  },
                  "value": "df-program-subscription-001"
                },
                {
                  "descriptor": {
                    "code": "program_id",
                    "name": "Program ID"
                  },
                  "value": "brpl_peak_saver_001"
                },
                {
                  "descriptor": {
                    "code": "commitment_confidence",
                    "name": "Commitment Confidence"
                  },
                  "value": "high"
                },
                {
                  "descriptor": {
                    "code": "baseline_kw",
                    "name": "Baseline Load"
                  },
                  "value": "400"
                },
                {
                  "descriptor": {
                    "code": "target_kw",
                    "name": "Target Load"
                  },
                  "value": "280"
                }
              ]
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "stops": [
            {
              "time": {
                "range": {
                  "start": "2025-08-26T00:00:00.000Z",
                  "end": "2025-08-26T23:59:59.999Z"
                }
              }
            }
          ],
          "state": {
            "descriptor": {
              "code": "CONFIRMED"
            }
          }
        }
      ]
    }
  }
}
```
</details>

**Understanding the Event Participation Confirmation:**
**Request Structure Explanation:**

This confirm API response contains the same structure and fields as the on_init notification, with few key differences:

**Key Changes from on_init:**
- `quantity.measure.value`: Consumer's committed reduction amount (e.g., "120" kW) - this is how much the consumer promises they will reduce, may differ from the originally requested amount
- `fulfillment.state`: Changes from "REQUESTED" to "CONFIRMED" (if accepting) or "REJECTED" (if declining) indicating consumer's participation decision
- `commitment_confidence`: New tag indicating consumer's confidence level in their ability to deliver the committed reduction (e.g., "high")

**Unchanged Elements:**
- All event details, baseline information, incentive parameters, and timing remain identical to the on_init request
- Consumer confirms participation with the same event parameters provided by the grid operator

This confirmation creates a binding commitment for the consumer to reduce specified load during the DF event period.

#### 7.3.3 DF Event Participation Acknowledgement (on_confirm API)

- BPPs acknowledge consumer participation commitment and provide incentive estimates
- The example below demonstrates the acknowledgment response structure
- This API call is required for core DF functionality when BPPs need to acknowledge consumer participation decisions
- BAPs MUST implement this API

DISCOM acknowledges consumer participation in DF event: [Example](../../../../examples/demand_flexibility/3.event/on_confirm-event-acknowledgement.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/3.event/on_confirm-event-acknowledgement.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "on_confirm",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1003",
    "message_id": "df-msg-2005",
    "timestamp": "2025-08-20T14:51:00+05:30"
  },
  "message": {
    "order": {
      "id": "df-event-20250820-001",
      "type": "event_participation",
      "provider": {
        "id": "brpl_df_001",
        "descriptor": {
          "name": "BRPL",
          "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
          "images": [
            {
              "url": "https://brpl.co.in/assets/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "brpl_peak_saver_001_event_001",
          "descriptor": {
            "name": "Evening Peak Saver Program - Event",
            "short_desc": "Load reduction request for 150kW during peak hours",
            "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Please reduce load by 150kW from your baseline during this event window.",
            "additional_desc": {
              "url": "https://brpl.co.in/flexibility/peak-saver"
            }
          },
          "quantity": {
            "measure": {
              "unit": "kW",
              "value": "120"
            }
          },
          "tags": [
            {
              "descriptor": {
                "name": "Event Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "subscription_id",
                    "name": "Program Subscription ID"
                  },
                  "value": "df-program-subscription-001"
                },
                {
                  "descriptor": {
                    "code": "program_id",
                    "name": "Program ID"
                  },
                  "value": "brpl_peak_saver_001"
                },
                {
                  "descriptor": {
                    "code": "commitment_confidence",
                    "name": "Commitment Confidence"
                  },
                  "value": "high"
                },
                {
                  "descriptor": {
                    "code": "baseline_kw",
                    "name": "Baseline Load"
                  },
                  "value": "400"
                },
                {
                  "descriptor": {
                    "code": "target_kw",
                    "name": "Target Load"
                  },
                  "value": "280"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Incentive Parameters"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "incentive_rate",
                    "name": "Incentive Rate"
                  },
                  "value": "5.00"
                },
                {
                  "descriptor": {
                    "code": "incentive_currency",
                    "name": "Incentive Currency"
                  },
                  "value": "INR"
                },
                {
                  "descriptor": {
                    "code": "incentive_type",
                    "name": "Incentive Type"
                  },
                  "value": "per_kWh_reduced"
                },
                {
                  "descriptor": {
                    "code": "estimated_incentive",
                    "name": "Estimated Incentive"
                  },
                  "value": "1800.00"
                }
              ]
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "stops": [
            {
              "time": {
                "range": {
                  "start": "2025-08-26T00:00:00.000Z",
                  "end": "2025-08-26T23:59:59.999Z"
                }
              }
            }
          ],
          "state": {
            "descriptor": {
              "code": "ACCEPTED"
            }
          }
        }
      ]
    }
  }
}
```
</details>

**Understanding the Event Participation Acknowledgement:**
**Response Structure Explanation:**

This on_confirm API response contains the same structure and fields as the confirm request, with key differences:

**Key Changes from confirm:**
- `order.id`: New unique identifier is created to track this acknowledgment response
- `order.status`: BPP's response to the participation decision ("ACCEPTED" if BPP accepts consumer's commitment, or relevant status if declined)
- Additional tags may be added for incentive estimation and performance monitoring setup

**Unchanged Elements:**
- All event details, baseline information, committed reduction amount, and timing remain identical to the confirm request
- BPP acknowledges the consumer's participation decision with the same event parameters

This acknowledgment confirms that the BPP has processed the consumer's participation decision and establishes the framework for performance monitoring and incentive calculation.

### 7.4 Settlement and Monitoring Examples

#### 7.4.1 Settlement and Incentive Calculation against participation in a DF event (on_status API)

- BPPs provide performance metrics and final incentive calculations after DF event completion
- The example below demonstrates the settlement response structure
- This API call is required for core DF functionality when BPPs need to provide settlement information
- BAPs MUST implement this API

DISCOM provides settlement details and incentive calculation: [Example](../../../../examples/demand_flexibility/4.settlement/on_status-settlement.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/4.settlement/on_status-settlement.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "domain": "demand-flexibility",
    "action": "on_status",
    "version": "1.1.0",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "transaction_id": "df-txn-1003",
    "message_id": "df-msg-2006",
    "timestamp": "2025-08-26T17:30:00+05:30"
  },
  "message": {
    "order": {
      "id": "df-event-20250820-001",
      "type": "event_participation",
      "provider": {
        "id": "brpl_df_001",
        "descriptor": {
          "name": "BRPL",
          "short_desc": "BRPL Demand Flexibility Programs for Delhi NCR",
          "images": [
            {
              "url": "https://brpl.co.in/assets/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "brpl_peak_saver_001_event_001",
          "descriptor": {
            "name": "Evening Peak Saver Program - Event",
            "short_desc": "Load reduction request for 150kW during peak hours",
            "long_desc": "Users will receive app notifications during afternoon peak hours (2–5 PM). Please reduce load by 150kW from your baseline during this event window.",
            "additional_desc": {
              "url": "https://brpl.co.in/flexibility/peak-saver"
            }
          },
          "quantity": {
            "measure": {
              "unit": "kW",
              "value": "120"
            }
          },
          "tags": [
            {
              "descriptor": {
                "name": "Event Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "subscription_id",
                    "name": "Program Subscription ID"
                  },
                  "value": "df-program-subscription-001"
                },
                {
                  "descriptor": {
                    "code": "program_id",
                    "name": "Program ID"
                  },
                  "value": "brpl_peak_saver_001"
                },
                {
                  "descriptor": {
                    "code": "baseline_kw",
                    "name": "Baseline Load"
                  },
                  "value": "400"
                },
                {
                  "descriptor": {
                    "code": "target_kw",
                    "name": "Target Load"
                  },
                  "value": "280"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Performance Metrics"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "actual_avg_load",
                    "name": "Actual Average Load"
                  },
                  "value": "288"
                },
                {
                  "descriptor": {
                    "code": "load_reduction_achieved",
                    "name": "Load Reduction Achieved"
                  },
                  "value": "112"
                },
                {
                  "descriptor": {
                    "code": "performance_percentage",
                    "name": "Performance Against Commitment"
                  },
                  "value": "93.33"
                }
              ]
            },
            {
              "descriptor": {
                "name": "Settlement Details"
              },
              "list": [
                {
                  "descriptor": {
                    "code": "incentive_rate",
                    "name": "Incentive Rate"
                  },
                  "value": "5.00"
                },
                {
                  "descriptor": {
                    "code": "incentive_currency",
                    "name": "Incentive Currency"
                  },
                  "value": "INR"
                },
                {
                  "descriptor": {
                    "code": "incentive_type",
                    "name": "Incentive Type"
                  },
                  "value": "per_kWh_reduced"
                },
                {
                  "descriptor": {
                    "code": "total_reduction_kwh",
                    "name": "Total Energy Reduction"
                  },
                  "value": "336"
                },
                {
                  "descriptor": {
                    "code": "total_incentive",
                    "name": "Total Incentive Amount"
                  },
                  "value": "1680.00"
                },
                {
                  "descriptor": {
                    "code": "settlement_status",
                    "name": "Settlement Status"
                  },
                  "value": "PROCESSING"
                }
              ]
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "stops": [
            {
              "time": {
                "range": {
                  "start": "2025-08-26T00:00:00.000Z",
                  "end": "2025-08-26T23:59:59.999Z"
                }
              }
            }
          ],
          "state": {
            "descriptor": {
              "code": "COMPLETED"
            }
          }
        }
      ]
    }
  }
}
```
</details>

**Understanding the Settlement and Performance Metrics:**
**Response Structure Explanation:**

**Performance Metrics:**
- `actual_avg_load`: Measured average consumption during event period
- `load_reduction_achieved`: Calculated actual load reduction (baseline - actual)
- `performance_percentage`: Performance ratio (achieved/committed * 100)

**Settlement Calculation:**
- `total_reduction_kwh`: Total energy reduced during event period
- `incentive_rate`: Applied compensation rate per kWh reduced
- `total_incentive`: Final calculated compensation amount
- `incentive_currency`: Payment currency and denomination

**Settlement Status:**
- `settlement_status`: Payment processing status (calculated/pending/paid)
- `settlement_period`: Billing cycle when payment will be processed
- `performance_verified`: Indicates completion of performance validation

**Quality Metrics:**
- `baseline_accuracy`: Validation of baseline calculation method
- `measurement_quality`: Data quality assessment for settlement
- `compliance_status`: Adherence to program participation requirements

This status response provides comprehensive performance assessment and final incentive calculation for the completed DF event.

### 7.5 Post-Fulfillment Examples

#### 7.5.1 Cancellation (cancel API)

- Consumers can cancel their subscription to a DF program
- The example below demonstrates the cancellation request structure
- This API call is OPTIONAL for DF implementations

Consumer cancels subscription to DF program: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/1.cancel-request.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/1.cancel-request.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "cancel",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:30:00+05:30",
    "message_id": "msg-cancel-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "ttl": "PT30S",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "order_id": "df-program-subscription-001",
    "cancellation_reason_id": "user_request",
    "descriptor": {
      "name": "User Requested Cancellation",
      "short_desc": "Consumer wishes to exit the DF program"
    }
  }
}
```
</details>

#### 7.5.2 Cancellation Acknowledgement (on_cancel API)

- BPPs acknowledge the cancellation request and provide status
- The example below demonstrates the cancellation response structure
- This API call is OPTIONAL for DF implementations

DISCOM acknowledges cancellation request: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/2.on_cancel-response.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/2.on_cancel-response.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_cancel",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:31:00+05:30",
    "message_id": "msg-on-cancel-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "order": {
      "@context": "https://becknprotocol.io/schema/Order/schema-context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "df-program-subscription-001",
      "beckn:status": "CANCELLED",
      "beckn:cancellationTerms": {
        "@type": "beckn:CancellationTerms",
        "beckn:cancellationFee": {
          "schema:priceCurrency": "INR",
          "schema:price": "0.00"
        },
        "beckn:cancellationDate": "2025-08-20T14:31:00+05:30",
        "beckn:descriptor": {
          "schema:name": "Subscription Cancelled",
          "beckn:shortDesc": "Your subscription has been successfully cancelled"
        }
      }
    }
  }
}
```
</details>

#### 7.5.3 Support Request (support API)

- Consumers can request support for issues related to DF programs
- The example below demonstrates the support request structure
- This API call is OPTIONAL for DF implementations

Consumer requests support: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/3.support-request.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/3.support-request.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "support",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:30:00+05:30",
    "message_id": "msg-support-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "ttl": "PT30S",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "support": {
      "ref_id": "df-program-subscription-001",
      "ref_type": "ORDER",
      "issue": "Unable to understand baseline calculation method"
    }
  }
}
```
</details>

#### 7.5.4 Support Response (on_support API)

- BPPs provide support contact information and assistance
- The example below demonstrates the support response structure
- This API call is OPTIONAL for DF implementations

DISCOM provides support information: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/4.on_support-response.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/4.on_support-response.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_support",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:31:00+05:30",
    "message_id": "msg-on-support-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "supportInfo": {
      "beckn:phone": "1800-123-4567",
      "beckn:email": "df-support@brpl.co.in",
      "beckn:url": "https://brpl.co.in/support/demand-flexibility",
      "beckn:supportTicketURL": "https://support.brpl.co.in/create-ticket",
      "beckn:descriptor": {
        "schema:name": "BRPL Demand Flexibility Support",
        "beckn:shortDesc": "24/7 support for DF program participants"
      }
    }
  }
}
```
</details>

#### 7.5.5 Rating (rating API)

- Consumers can rate their experience with DF programs
- The example below demonstrates the rating request structure
- This API call is OPTIONAL for DF implementations

Consumer rates DF program experience: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/5.rating-request.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/5.rating-request.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "rating",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:30:00+05:30",
    "message_id": "msg-rating-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "ttl": "PT30S",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "rating": {
      "@context": "https://becknprotocol.io/schema/Rating/schema-context.jsonld",
      "@type": "beckn:RatingInput",
      "beckn:id": "df-program-subscription-001",
      "beckn:category": "FULFILLMENT",
      "beckn:value": 5,
      "beckn:feedback": "Excellent program! Clear communication and fair incentives.",
      "beckn:feedbackTags": [
        "Clear Communication",
        "Fair Incentives",
        "Easy to Participate"
      ]
    }
  }
}
```
</details>

#### 7.5.6 Rating Acknowledgement (on_rating API)

- BPPs acknowledge the rating submission
- The example below demonstrates the rating response structure
- This API call is OPTIONAL for DF implementations

DISCOM acknowledges rating: [Example](../../../../examples/demand_flexibility/5.post-fulfillment/6.on_rating-response.json)

<details>
<summary><a href="../../../../examples/demand_flexibility/5.post-fulfillment/6.on_rating-response.json">Example json :rocket:</a></summary>

```json
{
  "context": {
    "version": "2.0.0",
    "action": "on_rating",
    "domain": "beckn.one:DEG:demand-flexibility:1.0",
    "timestamp": "2025-08-20T14:31:00+05:30",
    "message_id": "msg-on-rating-df-001",
    "transaction_id": "txn-df-program-search-001",
    "bap_id": "consumer-app.example.com",
    "bap_uri": "https://consumer-app.example.com",
    "bpp_id": "brpl.co.in",
    "bpp_uri": "https://brpl.co.in",
    "schema_context": [
      "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld"
    ]
  },
  "message": {
    "ratingOutput": {
      "@context": "https://becknprotocol.io/schema/Rating/schema-context.jsonld",
      "@type": "beckn:RatingOutput",
      "beckn:ratingValue": 4.7,
      "beckn:ratingCount": 342,
      "beckn:bestRating": 5,
      "beckn:worstRating": 1,
      "beckn:descriptor": {
        "schema:name": "Thank you for your feedback!",
        "beckn:shortDesc": "Your rating helps us improve our DF programs"
      }
    }
  }
}
```
</details>

### 7.6 Future Reference Implementations

Reference implementations will be developed as part of pilot programs and early adopter deployments. These implementations will be added to this section once validated in production environments.

## 8. References

### 8.1 Normative References

- [RFC 2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997
- [RFC 8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, May 2017
- [BECKN-CORE] Beckn Protocol Core Specification v1.1.0
- [BECKN-ENERGY] Beckn Protocol Energy Domain Specification (Draft)

### 8.2 Informative References

- [DF-GLOBAL] "Demand Flexibility: A Global Perspective", International Energy Agency, 2024
- [GRID-CODES] "Electricity Grid Codes and Standards", International Electrotechnical Commission, 2023
- [IEEE-2030] IEEE Standard 2030-2011, "Guide for Smart Grid Interoperability"
- [LBL-DF] "Demand Flexibility: A Key Enabler of Electricity System Resilience", Lawrence Berkeley National Laboratory, 2024
- [DR-STANDARDS] "Demand Response Standards and Best Practices", Global Energy Council, 2023

## 9. Appendix

### 9.1 Change Log

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2025-08-18 | Initial draft with complete implementation guide |

### 9.2 Acknowledgments

- Beckn Foundation for protocol specifications and community support
- Energy industry experts who provided domain knowledge and insights
- Commercial facility operators for operational requirements input
- Technology partners for implementation feedback

### 9.3 Glossary

- **Baseline**: Historical electricity consumption pattern used to measure load reductions
- **Demand Flexibility**: Ability to adjust electricity consumption in response to grid conditions
- **Load Curtailment**: Temporary reduction in electricity consumption during specific periods
- **Peak Shaving**: Reducing electricity demand during highest consumption periods
- **Grid Frequency**: Measure of electrical supply-demand balance (typically 50 Hz or 60 Hz depending on region)
- **Distribution Company (DISCOM)**: Utility responsible for electricity distribution to end consumers

### 9.4 FAQ

**Q: How does this approach differ from traditional demand response programs?**
A: Traditional programs rely on manual coordination and phone/email communication. This Beckn-based approach enables automated discovery, subscription, and real-time event coordination with transparent incentive calculations.

**Q: What are the minimum technical requirements for participation?**
A: Participants need smart metering infrastructure, controllable loads, internet connectivity, and the ability to implement Beckn Protocol APIs or use compatible platforms.

**Q: How are baseline calculations handled to ensure fairness?**
A: The system uses standardized baseline methodologies (such as 3-of-5 average) with weather adjustments and operational corrections to ensure accurate measurement of load reductions.

**Q: What happens if a participant cannot fulfill their commitment?**
A: The system includes penalty structures for non-performance, but also recognizes that some factors (equipment failures, operational emergencies) are beyond participant control.

### 9.5 RFC Evolution and Maintenance

#### 9.5.1 Version Management

**Version Numbering:**
- **Major versions (X.0.0)**: Breaking changes to API structure or fundamental concepts
- **Minor versions (X.Y.0)**: New features, additional use cases, backward-compatible enhancements
- **Patch versions (X.Y.Z)**: Bug fixes, clarifications, documentation improvements

**Release Process:**
- Draft versions for community review and feedback
- Public comment period of minimum 30 days for major changes
- Implementation testing with reference platforms
- Final approval by maintainers and domain experts

#### 9.5.2 Community Contribution Guidelines

**How to Contribute:**
- Submit issues via GitHub for bugs, clarifications, or enhancement requests
- Propose changes through pull requests with detailed explanations
- Participate in community discussions and working group meetings
- Provide feedback from real-world implementations

**Contribution Requirements:**
- All proposals must include implementation considerations
- Changes should maintain backward compatibility when possible
- Include updated examples and test cases
- Document migration paths for breaking changes

**Review Process:**
- Technical review by energy domain experts
- Beckn Protocol compliance validation
- Community feedback integration
- Implementation feasibility assessment

#### 9.5.3 Maintenance Procedures

**Regular Maintenance:**
- Quarterly review of open issues and community feedback
- Annual alignment with Beckn Protocol core specification updates
- Bi-annual review of examples and reference implementations
- Continuous monitoring of real-world deployment experiences

**Maintenance Responsibilities:**
- **Core Authors**: Major architectural decisions and breaking changes
- **Domain Experts**: Energy industry best practices and regulatory compliance
- **Community Maintainers**: Documentation updates, example maintenance, issue triage
- **Implementation Partners**: Real-world validation and feedback

#### 9.5.4 Deprecation and Migration Policy

**Deprecation Process:**
- Minimum 12-month notice for breaking changes
- Clear migration paths and tools provided
- Support for legacy versions during transition period
- Documentation of deprecated features and alternatives

**Migration Support:**
- Step-by-step migration guides for each major version
- Automated migration tools where possible
- Community support channels for implementation questions
- Reference implementations for new versions

### 9.6 Troubleshooting

#### 9.6.1 Issue 1: API Response Timeouts

**Symptoms:** DF event notifications not received within expected timeframe
**Cause:** Network connectivity issues or overloaded servers during peak events
**Solution:** Implement retry mechanisms with exponential backoff and backup communication channels

#### 9.6.2 Issue 2: Baseline Calculation Discrepancies

**Symptoms:** Disputed incentive payments due to baseline disagreements
**Cause:** Different calculation methods or data sources between utility and participant
**Solution:** Use standardized calculation APIs with shared data sources and transparent audit logs

#### 9.6.3 Issue 3: Schema Validation Failures

**Symptoms:** Messages rejected due to schema validation errors
**Cause:** Incorrect field names, missing required fields, or invalid data formats
**Solution:** Implement comprehensive validation testing, use schema validation tools, maintain updated field documentation

#### 9.6.4 Issue 4: Performance Measurement Disputes

**Symptoms:** Disagreements about actual load reduction achieved during events
**Cause:** Different measurement methodologies, data synchronization issues, or equipment failures
**Solution:** Establish standardized measurement protocols, implement real-time data reconciliation, maintain audit trails for all measurements

---

**Note:** This RFC provides comprehensive guidance for implementing Demand Flexibility programs using Beckn Protocol. Implementations should be carefully adapted to specific regulatory and operational requirements in different jurisdictions. Feedback from initial implementations will help evolve this specification. 