# Compute–Energy Convergence in a DEG World

## Overview

**Goal:** Optimise AI training workloads to align with real-time grid flexibility, carbon intensity, and cost signals — through agentic coordination between a Compute Agent (CompFlex) and a Grid Agent (GridFlexAgent).

**Character:** Leena Jones, Data Centre Energy Manager at ComputeCloud.ai

---

## Phase 1: Discovery

### System Context:
ComputeCloud's scheduling agent (CompFlex) models all compute clusters — tracking power draw, time flexibility, and carbon budget.

At 8:00 AM, CompFlex sends a Beckn search request.

### GridFlexAgent Response:
- **10:00–14:00** → 80% renewable mix (optimal window)
- **14:00–18:00** → High grid load, £0.03/kWh higher price

CompFlex also queries Manchester and finds a cleaner energy window at 2 PM with a 75% renewable mix and lower price (£0.092/kWh).

### Actionable Outcomes:
- Identify low-carbon and low-cost windows across multiple grid zones
- Compare and plan compute distribution accordingly
- Prepare workload split between Cambridge (morning slot) and Manchester (afternoon slot)

---

## Phase 2: Ordering

### Actions:
CompFlex places two Beckn orders to align workloads with grid conditions.

**Order 1:**
```
area: "Cambridge-East"
time: "10:00–14:00"
intent: "AI training batch A"
compute_load: 1.2 MW
metadata: { GPU_hours, energy_draw, carbon_target }
```

**Order 2:**
```
area: "Manchester"
time: "14:00–18:00"
intent: "AI training batch B"
compute_load: 1.2 MW
metadata: { GPU_hours, energy_draw, carbon_target }
```

### Negotiation:
- GridFlexAgent confirms availability and capacity for both orders
- Orders are logged against the grid carbon index dataset for validation and audit

### Actionable Outcomes:
- Secure compute schedules tied to verified low-carbon energy slots
- Ensure each order includes carbon and flexibility metadata for settlement

---

## Phase 3: Fulfilment

### Execution Flow:

#### 10:00 AM:
- Batch A starts in Cambridge under Order 1
- Active load: 1.2 MW, mapped to Beckn Order ID
- Grid mix: 80% renewable, average cost £0.102/kWh

#### 2:00 PM:
**GridFlexAgent issues event for Cambridge:**
> "Grid stress rising; renewable share dropping to 45%; spot price up £0.03/kWh."

**CompFlex response:**
- Pauses non-critical AI training tasks (~300 kW) in Cambridge
- Redirects those workloads to Manchester, which already has an active slot (Order 2)
- Manchester now handles 1.5 MW total load (1.2 MW planned + 0.3 MW shifted)
- Local battery storage in Cambridge discharges 150 kW to maintain stability

### System Coordination:
Dashboards (ComputeCloud + Grid) update in real time:
- **Cambridge Load:** 900 kW active after shift
- **Manchester Load:** 1.5 MW active
- **Flexibility Shift:** 300 kW moved cross-city
- Cost and carbon data auto-synced to Beckn order IDs

### Actionable Outcomes:
- Dynamic response to grid stress in under 5 minutes
- Avoided high-cost energy (£0.03/kWh × 6 hours × 1 MW-equivalent = £180 saved)
- Maintained service continuity using distributed energy and flexible compute migration
- Prevented ~0.25 tonnes CO₂ emissions by shifting to a cleaner grid

---

## Phase 4: Post-Fulfilment

### Settlement & Audit:

**CompFlex generates and publishes:**
- Energy use logs (per data centre)
- Carbon emissions report (before vs. after shift)
- Cost savings summary

**GridFlex Agent:**
- Validates demand shift through premise-level metering
- Beckn transaction lifecycle closes with verified incentives for the 300 kW flexibility delivered to the grid

### Final Outcomes:
- ✅ 12% reduction in energy cost for the training job
- ✅ 18% lower carbon footprint
- ✅ Verified 300 kW flexibility provided to the grid during a stress event
