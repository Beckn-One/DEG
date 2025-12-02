# Energy Policy as Code

## Overview

Machine-readable representations of policies, rules, and constraints that govern energy transactions and system operations. Unlike traditional policy documents written in natural language, Policy as Code expresses rules in structured formats (JSON, YAML, XML) that systems can parse and validate against.

## Why Policy as Code Matters

Traditional energy policies exist as human-readable documents—regulatory frameworks, tariff schedules, interconnection agreements—creating challenges in decentralized markets:
- Manual interpretation leads to inconsistent enforcement
- Policy changes require code updates and redeployment
- Difficult to verify compliance automatically
- Complex for stakeholders to understand applicability

Policy as Code solves this by providing structured, standardized formats that enable automated policy interpretation, consistent application, transparent verification, and dynamic updates without changing application code.

## Types of Policies

### Regulatory and Compliance
- Grid interconnection rules (export limits, voltage requirements)
- Renewable energy mandates (RPO percentages, net metering caps)
- Consumer protection policies (maximum pricing, cancellation rules)

### Operational
- Demand response program rules (eligibility, triggers, compensation)
- Dynamic pricing policies (time-of-use tariffs, surge pricing)
- Priority and allocation rules (emergency curtailment, queue management)

### Business and Commercial
- Service level agreements (uptime guarantees, penalties)
- Payment and settlement policies (accepted methods, credit limits)
- Platform policies (finder fees, transaction limits, geographic boundaries)

## Policy Application Points

**Discovery Phase**
- Filter catalogues based on geographic restrictions, credential requirements, eligibility criteria
- Example: "Consumer must have commercial vehicle credential to see fleet charging catalogues"

**Selection Phase**
- Validate selections against quantity limits, compatibility checks, time constraints
- Example: "Reservation quantity must be within charger's min/max power range"

**Contract Formation Phase**
- Authorize contract initialization based on payment validation, SLA acceptance, compliance
- Example: "Transaction rejected if buyer's payment credential is expired"

**Fulfillment Phase**
- Govern real-time resource behavior with power limits, emergency curtailment, priority dispatch
- Example: "Solar export capped at 5kW per grid interconnection policy"

## Policy Composition and Hierarchy

Complex policies can be composed from simpler components and organized hierarchically:

```
National Grid Code (Base Policy)
  ↓
State Renewable Energy Policy (Extends/Refines)
  ↓
Utility Interconnection Policy (Further Constraints)
  ↓
Platform-Specific Rules (Additional Requirements)
```

## Practical Examples (in draft)

### Idle Fee Policy (EV Charging)
```json
{
  "policyId": "idle-fee-standard",
  "policyType": "fee-calculation",
  "parameters": {
    "gracePeriodMinutes": 10,
    "feePerMinute": {"currency": "INR", "value": 2.0},
    "applicableAfter": "charging-complete"
  }
}
```

### Prosumer Export Limit (P2P Trading)
```json
{
  "policyId": "prosumer-export-limit",
  "policyType": "authorization",
  "conditions": {
    "all": [
      {"field": "prosumer.gridConnection.netMeteringEnabled", "operator": "equals", "value": true},
      {"field": "exportQuantity", "operator": "lessThanOrEqual", "valueFrom": "prosumer.gridConnection.exportLimitKW"},
      {"field": "prosumer.credentials.interconnectionApproval.valid", "operator": "equals", "value": true}
    ]
  },
  "effect": "allow"
}
```

### RPO Compliance (Renewable Mandate)
```json
{
  "policyId": "state-rpo-2024",
  "policyType": "compliance",
  "parameters": {
    "renewablePercentage": 21.5,
    "applicableYear": 2024,
    "enforcementLevel": "state",
    "penaltyPerUnit": {"currency": "INR", "value": 2.0}
  }
}
```

## Summary

Energy Policy as Code transforms regulatory rules, operational constraints, and business logic from human-readable documents into structured, machine-readable representations. By providing a standardized format for expressing policies, Policy as Code enables systems to consistently interpret and apply rules, making decentralized energy markets trustworthy, compliant, and efficient at scale.

From grid interconnection limits to dynamic pricing schedules, from renewable energy mandates to platform fee structures—policies define the guardrails within which all energy transactions occur. Representing these policies in machine-readable formats is essential for the India Energy Stack to function as an open, interoperable ecosystem.
