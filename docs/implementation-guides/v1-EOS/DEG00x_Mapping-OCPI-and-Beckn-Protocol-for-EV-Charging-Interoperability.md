# DEG00x: Mapping OCPI and Beckn Protocol for EV Charging Interoperability

## Request for Comments \- Status : DRAFT

[Authors](#authors)

[Reviewers](#reviewers)

[Overview](#overview)

[Why Beckn ↔ OCPI Mapping Benefits the EV Charging Ecosystem](#why-beckn-↔-ocpi-mapping-benefits-the-ev-charging-ecosystem)

[Terminology](#terminology)

[Adapter Implementation Recommendation](#adapter-implementation-recommendation)

[Caching Strategy](#caching-strategy)

[Recommendations:](#recommendations)

[Adapter Responsibilities](#adapter-responsibilities)

[Error Handling](#error-handling)

[Authorization](#authorization)

[Recommended Architectures](#recommended-architecture)

[Architecture 1: EV Charger as Beckn Item (Resource)](#ev-charger-as-beckn-item-resource)

[Architecture 2: Energy as Beckn Item, EV Charger as "Vehicle"](#heading=hipnceh7wbgt)

[Schema Mapping](#schema-mapping)

[1\. Catalog Discovery](#1-catalog-discovery)

[2\. Price Negotiation / Agreement](#2-price-negotiation--agreement)

[3\. Terms Agreement  (Billing, Fulfillment, Payment)](#3-terms-agreement-billing-fulfillment-payment)

[4\. Order Confirmation](#4-order-confirmation)

[5\. Order Update / Charging Start](#5-order-update--charging-start)

[6\. Track (Real-time Charging Tracking)](#6-track-real-time-charging-tracking)

[7\. Order Update / Charging Stop & Final CDR](#7-order-update--charging-stop--final-cdr)

[8\. Order Cancellation](#8-order-cancellation)

[9\. Status / on\_status \- Informational Updates](#9-status--on_status---informational-updates)

[10\. Rating & Support](#10-rating--support)

[Example Implementation](#example-implementation)

[1\. Discovery](#1-discovery)

[1.1 search Request (BAP → BPP)](#11-search-request-bap--bpp)

[1.2. OCPI Adapter Processing (inside BPP)](#12-ocpi-adapter-processing-inside-bpp)

[1.3. on\_search Response (BPP → BAP)](#13-on_search-response-bpp--bap)

[1.4 Adapter Recommendations for search/on\_search](#14-adapter-recommendations-for-searchon_search)

[2\. Select / on\_select Workflow](#2-select--on_select-workflow)

[2.1. select Request (BAP → BPP)](#21-select-request-bap--bpp)

[2.2. OCPI Adapter Processing (inside BPP)](#22-ocpi-adapter-processing-inside-bpp)

[2.3. on\_select Response (BPP → BAP)](#23-on_select-response-bpp--bap)

[2.4 Adapter Recommendations for select/on\_select](#24-adapter-recommendations-for-selecton_select)

[3\. Init / On\_init Workflow](#3-init--on_init-workflow)

[3.1. init Request (BAP → BPP)](#31-init-request-bap--bpp)

[{](#{)

[3.2. OCPI Adapter Processing (inside BPP)](#32-ocpi-adapter-processing-inside-bpp)

[3.3. on\_init Response (BPP → BAP)](#33-on_init-response-bpp--bap)

[3.4. Adapter Recommendations for init/on\_init](#34-adapter-recommendations-for-inititon_init)

[4\. Confirm / on\_confirm Workflow](#4-confirm--on_confirm-workflow)

[4.1. confirm Request (BAP → BPP)](#41-confirm-request-bap--bpp)

[4.2. OCPI Adapter Processing (inside BPP)](#42-ocpi-adapter-processing-inside-bpp)

[4.3. on\_confirm Response (BPP → BAP)](#43-on_confirm-response-bpp--bap)

[4.4. Adapter Recommendations for confirm/on\_confirm](#44-adapter-recommendations-for-confirmon_confirm)

[5\. Update / On\_update flows (Charging Start)](#5-update--on_update-flows-charging-start)

[5.1. update Request (BAP → BPP)](#51-update-request-bap--bpp)

[5.2. OCPI Adapter Processing (inside BPP)](#52-ocpi-adapter-processing-inside-bpp)

[5.3. on\_update Response (BPP → BAP)](#53-on_update-response-bpp--bap)

[5.4. Adapter Recommendations for update/on\_update](#54-adapter-recommendations-for-updateon_update)

[6\. Track / on\_track Flows (Charging session)](#6-track--on_track-flows-charging-session)

[6.1. track Request (BAP → BPP)](#61-track-request-bap--bpp)

[6.2. OCPI Adapter Processing (inside the BPP)](#62-ocpi-adapter-processing-inside-the-bpp)

[6.3. on\_track Response (BPP → BAP)](#63-on_track-response-bpp--bap)

[6.4. Adapter Recommendations for track/on\_track](#64-adapter-recommendations-for-trackon_track)

[7\. Update / On\_update Flows (End of charging session)](#7-update--on_update-flows-end-of-charging-session)

[7.1. update Request (BAP → BPP)](#71-update-request-bap--bpp)

[7.2. OCPI Adapter Processing (inside BPP)](#72-ocpi-adapter-processing-inside-bpp)

[7.3. on\_update Response (BPP → BAP)](#73-on_update-response-bpp--bap)

[7.4 Adapter Recommendations for Stopping & Finalizing Payment](#74-adapter-recommendations-for-stopping--finalizing-payment)

[8\. Asynchronous on\_update \- When charging terms change on an active order](#8-asynchronous-on_update---when-charging-terms-change-on-an-active-order)

[8.1. Triggering Events](#81-triggering-events)

[8.2. Fulfillment State Schema](#82-fulfillment-state-schema)

[8.3. Example: Time-of-Day Tariff Change Mid-Session](#83-example-time-of-day-tariff-change-mid-session)

[8.4. Adapter Recommendations](#84-adapter-recommendations)

[9\. Status / on\_status flows (Informational updates)](#9-status--on_status-flows-informational-updates)

[9.1. status Request (BAP → BPP)](#91-status-request-bap--bpp)

[9.2 Adapter Processing](#92-adapter-processing)

[9.3. on\_status Response (BPP → BAP)](#93-on_status-response-bpp--bap)

[9.4 Unsolicited on\_status Calls from BPP](#94-unsolicited-on_status-calls-from-bpp)

[9.5 Triggering Status Codes (Informational Only)](#95-triggering-status-codes-informational-only)

[9.6. Example: Station-Side Pause (SUSPENDED\_EVSE)](#96-example-station-side-pause-suspended_evse)

[9.7 Recommendations for Unsolicited on\_status](#97-recommendations-for-unsolicited-on_status)

[10\. Cancel / on\_cancel flows](#10-cancel--on_cancel-flows)

[10.1. cancel Request (BAP → BPP)](#101-cancel-request-bap--bpp)

[10.2 Adapter Processing](#102-adapter-processing)

[10.3. on\_cancel Response (BPP → BAP)](#103-on_cancel-response-bpp--bap)

[10.4 Unsolicited on\_cancel Calls from BPP](#104-unsolicited-on_cancel-calls-from-bpp)

[Triggering Scenarios](#triggering-scenarios)

[Example: Charger Hardware Failure](#example-charger-hardware-failure)

[10.5 Adapter Recommendations](#105-adapter-recommendations)

[11\. Rating / on\_rating flows](#11-rating--on_rating-flows)

[11.1. rating Request (BAP → BPP)](#111-rating-request-bap--bpp)

[11.2 Adapter Processing](#112-adapter-processing)

[11.3. on\_rating Response (BPP → BAP)](#113-on_rating-response-bpp--bap)

[11.4. Unsolicited on\_rating Calls from BPP](#114-unsolicited-on_rating-calls-from-bpp)

[11.5 Adapter Recommendations](#115-adapter-recommendations)

[12\. Support / on\_support flows](#12-support--on_support-flows)

[12.1. support Request (BAP → BPP)](#121-support-request-bap--bpp)

[Adapter Processing](#adapter-processing)

[12.2. on\_support Response (BPP → BAP)](#122-on_support-response-bpp--bap)

[12.3. Unsolicited on\_support Calls from BPP](#123-unsolicited-on_support-calls-from-bpp)

[Triggering Scenarios](#triggering-scenarios-1)

[Example: Proactive Support Notification](#example-proactive-support-notification)

[12.4 Adapter Recommendations for support/on\_support](#124-adapter-recommendations-for-supporton_support)

[Conclusion](#conclusion)

# 

# **Authors**

| Name | Title / Affiliation |
| :---- | :---- |
| Ravi Prakash | Head, Architecture and Technology Ecosystem; Volunteer at Beckn Open Collective |

# **Reviewers**

| Name | Title / Affiliation |
| :---- | :---- |
| Pramod Varma | Chief Architect, Beckn Labs; Volunteer at Beckn Open Collective |
| Sujith Nair | CEO, Beckn Labs; Volunteer at Beckn Open Collective |

# **Overview**

This RFC specifies a detailed schema mapping between the Beckn Protocol and OCPI (Open Charge Point Interface). It describes how a Beckn Provider Platform (BPP) can implement an adapter layer to translate Beckn protocol calls into OCPI requests and responses, enabling seamless interoperability between Beckn-enabled Digital Energy Grids (DEG) and OCPI-compliant EV charging infrastructure.

Note: The specifications in this document are compatible with Beckn Protocol Version 1.0

# **Why Beckn ↔ OCPI Mapping Benefits the EV Charging Ecosystem**

Integrating Beckn’s open marketplace protocol with the OCPI standard yields substantial advantages for all participants:

1. **Seamless Roaming Across Networks**

   * **Interoperability**: Beckn abstracts the nuances of individual CPO APIs, while OCPI provides a common language for charger discovery, booking, and billing. Together they enable EV drivers to roam effortlessly across diverse charging networks without multiple apps or credentials.

   * **Network Expansion**: BAPs and BPPs can onboard new CPOs faster, simply by implementing the adapter, rather than re-engineering for every proprietary API.

2. **Decoupled, Future-Proof Architecture**

   * **Stateless Core**: Beckn’s request-response pattern ensures state is carried in messages rather than in servers, reducing coupling. The OCPI adapter layer can evolve (e.g., v2.3, v3.0) transparently, without impacting BAPs.

   * **Modular Enhancements**: New OCPI modules—such as for reservation, roaming, or tariffs—can be adopted incrementally within the same Beckn flows.

3. **Consistent User Experience**

   * **Unified Catalogs**: Users see a single, harmonized catalog of chargers, prices, and availability, regardless of the underlying OCPI implementation.

   * **Predictable Workflows**: A standardized Beckn workflow (search→select→init→confirm→update) delivers consistent UI and error-handling patterns, even when CPOs differ.

4. **Operational Efficiency for Service Providers**

   * **Shared Infrastructure**: BPPs can operate a single adapter to serve multiple BAPs and CPOs, leveraging common caching, logging, and monitoring tooling.

   * **Reduced Integration Overhead**: Rather than building and maintaining custom integrations for each partner, teams implement one Beckn-to-OCPI bridge.

5. **Accelerated Innovation**

   * **Open Ecosystem**: By lowering technical barriers, new mobility services—such as dynamic pricing, bundled energy services, or sustainability credits—can be prototyped on the Beckn layer, while OCPI continues to handle low-level charging operations.

   * **Data-Driven Insights**: Unified telemetry (via Beckn’s status/update hooks) and standardized CDRs (via OCPI) enable cross-network analytics for grid optimization and user behavior.

6. **Regulatory and Business Alignment**

   * **Compliance Ready**: OCPI’s built-in support for token authorization, CDRs, and tariffs helps meet regional regulations, while Beckn’s marketplace model aligns with emerging policies on energy markets and interoperability mandates.

   * **New Revenue Streams**: Service providers can package value-added offerings (e.g., loyalty programs, maintenance services) on top of the Beckn marketplace, leveraging the charging data delivered via OCPI.

By bridging Beckn’s flexible, stateless marketplace with OCPI’s rich, charging-specific APIs, the ecosystem gains the best of both worlds: **rapid integration**, **scalable operations**, and a **seamless experience** for EV drivers, platform operators, and charging point owners alike.

# **Terminology**

| Term | Definition |
| :---- | :---- |
| **Beckn** | An open, decentralized protocol for interoperable commerce and services, defining a stateless messaging pattern (search, select, init, confirm, update, status, cancel, rating, support) between Buyer Application Platforms (BAPs) and Provider Platforms (BPPs). |
| **BAP** | Buyer Application Platform: the app or service that initiates Beckn calls on behalf of the end user (e.g., an EV charging app that searches for chargers and places orders). |
| **BPP** | Beckn Provider Platform: the backend service that implements Beckn endpoints, translates requests into OCPI (or other provider-specific APIs), and responds with the required Beckn messages. |
| **CPO** | Charging Point Operator: the entity that owns or operates EV charging stations and exposes their infrastructure via OCPI APIs. |
| **OCPI** | Open Charge Point Interface: a standardized protocol for communication between CPOs and e-Mobility Service Providers (EMSPs), covering modules such as Locations, Tariffs, Tokens, Sessions, Commands, and CDRs. |
| **EVSE** | Electric Vehicle Supply Equipment: the physical charging unit identified by an `evse.uid` in OCPI, and mapped to `item.id` in Beckn. |
| **SessionStatus** | Enumeration of OCPI session states (`RESERVATION`, `PENDING`, `ACTIVE`, `SUSPENDED_EVSE`, `SUSPENDED_EV`, `FINISHING`, `COMPLETED`, `INVALID`) that map directly to Beckn fulfillment states. |
| **CDR** | Charge Detail Record: the record returned by OCPI’s CDR module summarizing a completed charging session, including total energy consumed and cost. |
| **XInput** | Beckn’s schema for extended form inputs (`Form` object) when additional information is required to confirm an order or collect feedback (`feedback_form`). |
| **Fulfillment** | Beckn object describing how an order will be rendered or delivered; for charging, it encapsulates EVSE location, time window, and state. |
| **Payment Terms** | The Beckn `payments` array detailing settlement terms: who collects payment (`collected_by`), payment URL or parameters, timing (`type`), and status. |
| **Unsolicited Callbacks** | Beckn messages (`on_status`, `on_update`, `on_cancel`, `on_rating`, `on_support`) pushed by the BPP without a prior request, to inform the BAP of state changes, contractual updates, cancellations, feedback invitations, or support engagement. |

# **Adapter Implementation Recommendation**

## Caching Strategy

The adapter does **not require synchronous OCPI calls** for every Beckn request.

## Recommendations:

1. Cache static data (`locations`, `tariffs`) periodically (every 10-15 mins).  
2. Real-time data (`EVSE status`, `sessions`) can be polled at frequent intervals (e.g., every 30 seconds to 1 minute).

## Adapter Responsibilities

1. Periodically poll OCPI endpoints (`locations`, `tariffs`) to populate cache.  
2. On Beckn `search` call, fetch data directly from cache.  
3. On Beckn `init` or `confirm` calls, translate immediately to OCPI's `/tokens`.  
4. Map Beckn `status` and `billing` calls to OCPI’s `/sessions` and `/cdrs`.

## Error Handling

Implement robust logging and retries when OCPI APIs are temporarily unavailable.

## Authorization

Manage token-based authorization transparently between Beckn & OCPI, ensuring user consent.

# **Recommended Architecture**

## **EV Charger** as Beckn Item (Resource)

In this approach, the EV charger is the primary Beckn catalog `item`.

**Example JSON (Beckn item):**

```json
{
  "id": "IN*BCN*E001",
  "descriptor": {
    "name": "EV Charger #1",
    "code": "load"
  },
  "tags": [
    {"descriptor":{"code":"connector_standard"}, "value":"IEC_62196_T2"},
    {"descriptor":{"code":"power_type"}, "value":"AC_3_PHASE"}
  ],
  "price": {"currency": "INR", "value": "18"},
  "fulfillment_ids": ["fulfillment-001"]
}
```

**Advantages:**

* Clear visibility into individual EVSEs.  
* Easier tariff association and user understanding.

# 

# **Implementation Guide : Architecture 1**

# Schema Mapping

Below is a detailed mapping between **Beckn** protocol objects and **OCPI** APIs/fields. This ensures that each Beckn message field can be populated from—or translated into—the corresponding OCPI data.

## 1\. Catalog Discovery

| Beckn Field | OCPI Source | Notes |
| :---- | :---- | :---- |
| `providers[].id` | `party_id` domain | e.g. `cpo1.com` |
| `providers[].descriptor.name` | CPO party name | From OCPI Credentials module |
| `providers[].locations[].id` | `location.id` | OCPI Location UID |
| `providers[].locations[].descriptor.name` | `location.name` | Human‐readable station name |
| `providers[].locations[].gps` | `location.coordinates` | `"lat,lon"` |
| `providers[].locations[].address.full` | `location.address` | Concatenate street, city, postal\_code |
| `providers[].items[].id` | `evse.uid` | OCPI EVSE UID |
| `providers[].items[].descriptor.name` | `"EV Charger #"+index` or `evse.display_name` | Fallback to generic naming if absent |
| `providers[].items[].descriptor.code` | `"load"` | Static code for charging |
| `providers[].items[].tags[].list.value` | connector\_standard, power\_type, status | From OCPI EVSE fields & `location.status` |
| `providers[].items[].price.value` | `tariff.energy €/kWh` × unit conversion | Match Beckn `currency`: `"INR/kWh"` |
| `providers[].fulfillments[].id` | Generated Beckn UUID per location | Maps to OCPI Location/EVSE combination |
| `providers[].fulfillments[].type` | `"CHARGING"` | Static |
| `providers[].fulfillments[].stops[].location.gps` | `location.coordinates` | Same as catalog |
| `providers[].fulfillments[].stops[].time.range` | `location.evse.hours` or `00:00:00–23:59:59` | OCPI Opening Hours |

## 2\. Price Negotiation / Agreement

| Beckn Field | OCPI Source | Notes |
| :---- | :---- | :---- |
| `order.provider.id` | `party_id` | Echoed |
| `order.items[].id` | `evse.uid` | Echoed |
| `order.fulfillments[].location.id` | `location.id` | Echoed |
| `quote.id` | UUID | Generated by BPP |
| `quote.price.value` | `tariff.energy * assumed_kWh + service_fee` | Service fee is proprietary |
| `quote.price.currency` | `"INR/kWh"` | Use per‐unit currency |
| `quote.breakup[].item.id` | `evse.uid` | Reference item |
| `quote.breakup[].title` | e.g. `"Energy (5 kWh @ ₹18.00/kWh)"` | Human description |
| `quote.breakup[].price.value` | Component cost (energy or fees) | Aggregates match total price |
| `quote.ttl` | Duration (e.g. `"PT15M"`) | Validity of this quote |

## 3\. Terms Agreement  (Billing, Fulfillment, Payment)

| Beckn Field | OCPI Source | Notes |
| :---- | :---- | :---- |
| `order.billing` | BAP‐provided string | Beckn schema; not from OCPI |
| `payments[].id` | UUID | Generated by BPP |
| `payments[].collected_by` | `"bpp"` | BPP decides collection |
| `payments[].url` | BPP payment gateway URL | Contains `$transaction_id` & `$amount` |
| `payments[].params.transaction_id` | `transaction_id` | Echoed |
| `payments[].params.amount` | `quote.price.value` | Initial amount |
| `payments[].params.currency` | `"INR"` | Static |
| `payments[].type` | `"PRE-FULFILLMENT"` | Pre‐charging payment |
| `payments[].status` | `"NOT-PAID"` | BPP sets initial status |
| `payments[].time.timestamp` | Timestamp before `confirm` | BPP‐generated |

## 4\. Order Confirmation

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| `order.auth.token.uid` | BAP‐provided token UID | e.g. RFID UID |
| OCPI `POST /tokens/{country}/{party}/{uid}/authorize` | OCPI authorize endpoint | Returns `authorization_id` |
| `on_confirm.auth_token` | `authorization_id` | Echoed into Beckn |
| `fulfillments[].state.descriptor.code` | `"PENDING"` (OCPI SessionStatus.PENDING) | Session requested, not yet charging |
| `fulfillments[].state.updated_at` | TC generated timestamp |  |
| `fulfillments[].state.updated_by` | BPP ID |  |

## 5\. Order Update / Charging Start

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| `update.auth_token` | Beckn echo |  |
| OCPI `POST /commands { "command":"START_SESSION", authorization_id, ... }` | Starts session | Returns `session_id` |
| `on_update.fulfillments[].state.descriptor.code` | `"ACTIVE"` (SessionStatus.ACTIVE) | Charging in progress |
| `on_update.fulfillments[].state.*` | Timestamp & BPP ID |  |

## 6\. Track (Real-time Charging Tracking)

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| `track.order_id` | Beckn echo |  |
| OCPI `GET /sessions/{session_id}` | Fetch status |  |
| `on_track.tracking.id` | `"TRACK-"+session_id` | Unique tracking ref |
| `on_track.tracking.url` | BPP tracking URL |  |
| `on_track.tracking.status` | `"active"` / `"inactive"` | Map SessionStatus.ACTIVE→active; else inactive |

## 7\. Order Update / Charging Stop & Final CDR

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| OCPI `POST /commands {"command":"STOP_SESSION", session_id,...}` | Stop charging |  |
| OCPI `GET /cdrs/{session_id}` | Fetch final CDR | Contains `total_cost` & `total_energy` |
| `on_update.fulfillments[].state.descriptor.code` | `"COMPLETED"` (SessionStatus.COMPLETED) |  |
| `on_update.payments[].params.amount` | CDR.`total_cost` \+ fixed fees | BPP‐recalculated final amount |
| `on_update.payments[].type` | `"POST-FULFILLMENT"` |  |
| `on_update.payments[].time.timestamp` | CDR fetch timestamp |  |

## 8\. Order Cancellation

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| `cancel.order_id` | Beckn echo |  |
| `cancel.cancellation_reason_id` | Option ID | e.g. `"user_request"`, `"hardware_failure"` |
| `on_cancel.order.status` | `"CANCELLED"` |  |
| `on_cancel.cancellation` | `{ reason_id, descriptor, updated_at, updated_by }` |  |
| OCPI `STOP_SESSION` \+ `GET /cdrs/…` | If partial usage, calculate refund/fee |  |

## 9\. Status / on\_status \- Informational Updates

| Beckn Field | OCPI API | Notes |
| :---- | :---- | :---- |
| `status.order_id` | Beckn echo |  |
| OCPI `GET /sessions/{session_id}` | Fetch current session status |  |
| `on_status.fulfillments[].state` | `{ descriptor:{code,name}, updated_at, updated_by }` | For `RESERVATION`, `PENDING`, `ACTIVE`, `SUSPENDED_*`, `FINISHING` |

## 10\. Rating & Support

| Beckn Field | OCPI / Internal | Notes |
| :---- | :---- | :---- |
| `rating.ratings[]` | Stored in BPP feedback store |  |
| `on_rating.feedback_form` | XInput (Form URL, mime\_type, submission\_id) | Per BECKN-007 spec |
| `support.support` | BPP CRM ticket (ref\_id, phone, email, url) |  |
| `on_support.support` | Echoed support details |  |

# 

# Example Implementation

Use the below link to view the sequence diagram for a typical EV charging workflow using **Architecture 1**

[https://www.mermaidchart.com/app/projects/f64e3e47-bd99-40a4-ad82-10e78efe3196/diagrams/858c8256-3392-4b3d-a752-63b3e14ab35f/version/v0.1/edit](https://www.mermaidchart.com/app/projects/f64e3e47-bd99-40a4-ad82-10e78efe3196/diagrams/858c8256-3392-4b3d-a752-63b3e14ab35f/version/v0.1/edit) 

## **1\. Discovery**

### 1.1 `search` Request (BAP → BPP)

```json
{
  "context": {
    "domain": "deg",
    "action": "search",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "search-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:00:00Z"
  },
  "message": {
    "intent": {
      "item": {
        "descriptor": {
          "code": "load",
          "name": "EV Charger"
        }
      },
      "fulfillment": {
        "type": "CHARGING",
        "stops": [
          {
            "location": {
              "gps": "28.6304,77.2177",
              "circle": {
                "radius": {
                  "value": "5",
                  "unit": "km"
                }
              }
            }
          }
        ]
      }
    }
  }
}
```

### 1.2. OCPI Adapter Processing (inside BPP)

1. **Cache Freshness Check**  
     
   * If cached data \> 10 min old, fetch fresh OCPI data:

```http
GET /ocpi/2.2/locations?country_code=IN&party_id=BCN
GET /ocpi/2.2/tariffs?country_code=IN&party_id=BCN
```

`GET /ocpi/2.2/locations?country_code=IN&party_id=BCN`

`Request Headers:` 

```json
{    
  "X-Request-ID": "1234567890"    "X-Correlation-ID": "9876543210",    "Authorization": "Token ZGM2MDE3"
}
```

`Request Payload`  
`None`

`Response Headers:`

```json
{
  "date": "Thu, 14 Aug 2025 09:34:00 GMT",
  "content-type": "application/json",
  "vary": "Accept-Encoding",
  "link": "",
  "x-total-count": "2",
  "x-limit": "20",
  "x-request-id": "1234567890",
  "x-correlation-id": "9876543210",
  "ocpi-to-party-id": "INS",
  "ocpi-to-country-code": "IN",
  "ocpi-from-party-id": "THP",
  "ocpi-from-country-code": "IN"
}
```

`Response Payload:`

```json
{
  "data": [
    {
      "name": "Thunder Test CS",
      "coordinates": {
        "latitude": "28.5503906",
        "longitude": "77.2584309"
      },
      "city": "Delhi",
      "state": "Delhi",
      "country_code": "IN",
      "party_id": "THP",
      "id": "HrKNUxJ9Ara6AL6PaUlF",
      "publish": true,
      "address": "Test",
      "country": "IND",
      "time_zone": "Asia/Kolkata",
      "last_updated": "2025-08-01T11:27:05.768Z",
      "evses": [
        {
          "physical_reference": "Test QR Code - T",
          "uid": "v5bXyAlSr8G6lvUAN1A_1",
          "evse_id": "v5bXyAlSr8G6lvUAN1A_1",
          "status": "UNKNOWN",
          "connectors": [
            {
              "id": "1",
              "standard": "IEC_62196_T2",
              "format": "CABLE",
              "power_type": "AC_3_PHASE",
              "max_voltage": 100,
              "max_amperage": 150,
              "max_electric_power": 15000,
              "tariff_ids": [
                "dz2SXdIDJDfNjsPfw"
              ],
              "last_updated": "2024-12-09T08:43:21.791Z"
            }
          ],
          "last_updated": "2024-12-09T08:43:21.791Z"
        },
        {
          "physical_reference": "Test QR Code - T",
          "uid": "v5bXyAlSr8G6lvUAN1A_2",
          "evse_id": "v5bXyAlSr8G6lvUAN1A_2",
          "status": "UNKNOWN",
          "connectors": [
            {
              "id": "1",
              "standard": "IEC_62196_T2",
              "format": "CABLE",
              "power_type": "AC_3_PHASE",
              "max_voltage": 415,
              "max_amperage": 32,
              "max_electric_power": 20000,
              "tariff_ids": [
                "dz2SXdIDJDfNjsPfw"
              ],
              "last_updated": "2024-12-09T08:43:21.792Z"
            }
          ],
          "last_updated": "2024-12-09T08:43:21.792Z"
        },
        {
          "physical_reference": "Testing",
          "uid": "af7c3MVQklXwBshPj8_2",
          "evse_id": "af7c3MVQklXwBshPj8_2",
          "status": "UNKNOWN",
          "connectors": [
            {
              "id": "1",
              "standard": "IEC_60309_2_three_16",
              "format": "SOCKET",
              "power_type": "AC_1_PHASE",
              "max_voltage": 230,
              "max_amperage": 15,
              "max_electric_power": 3300,
              "tariff_ids": [
                "ajcx2DQt07uERmEqprnQ"
              ],
              "last_updated": "2025-07-30T14:35:12.040Z"
            }
          ],
          "last_updated": "2025-07-30T14:35:12.040Z"
        },
        {
          "physical_reference": "Testing",
          "uid": "af7c3MVQklXwBshPj8_1",
          "evse_id": "af7c3MVQklXwBshPj8_1",
          "status": "UNKNOWN",
          "connectors": [
            {
              "id": "1",
              "standard": "DOMESTIC_D",
              "format": "SOCKET",
              "power_type": "AC_1_PHASE",
              "max_voltage": 230,
              "max_amperage": 15,
              "max_electric_power": 3300,
              "tariff_ids": [
                "ajcx2DQt07uERmEqprnQ"
              ],
              "last_updated": "2025-07-17T10:54:21.512Z"
            }
          ],
          "last_updated": "2025-07-17T10:54:21.512Z"
        },
        {
          "physical_reference": "Thunder+ Test CP",
          "uid": "tLAj42jrr0dYtDqdqTDK_1",
          "evse_id": "tLAj42jrr0dYtDqdqTDK_1",
          "status": "AVAILABLE",
          "connectors": [
            {
              "id": "1",
              "standard": "IEC_62196_T2",
              "format": "SOCKET",
              "power_type": "AC_3_PHASE",
              "max_voltage": 415,
              "max_amperage": 16,
              "max_electric_power": 10000,
              "tariff_ids": [
                "ajcx2DQt07uERmEqprnQ"
              ],
              "last_updated": "2025-08-01T11:25:10.732Z"
            }
          ],
          "last_updated": "2025-08-01T11:25:10.732Z"
        },
        {
          "physical_reference": "Thunder+ Test CP",
          "uid": "tLAj42jrr0dYtDqdqTDK_2",
          "evse_id": "tLAj42jrr0dYtDqdqTDK_2",
          "status": "AVAILABLE",
          "connectors": [
            {
              "id": "1",
              "standard": "DOMESTIC_D",
              "format": "SOCKET",
              "power_type": "AC_1_PHASE",
              "max_voltage": 230,
              "max_amperage": 15,
              "max_electric_power": 3300,
              "tariff_ids": [
                "ajcx2DQt07uERmEqprnQ"
              ],
              "last_updated": "2025-08-01T11:27:26.168Z"
            }
          ],
          "last_updated": "2025-08-01T11:27:26.168Z"
        }
      ],
      "opening_times": {
        "twentyfourseven": true
      },
      "operator": {
        "name": "Thunder Plus",
        "website": "https://www.thunderplus.io/"
      }
    }
  ],
  "status_code": 1000,
  "status_message": "Success",
  "timestamp": "2025-08-14T09:58:05.069Z"
}

```

`GET /ocpi/2.2/tariffs?offset=0&limit=20`

`Request Headers:` 

```json
{
"X-Request-ID": "8046203538"    "X-Correlation-ID": "4036910083",    "Authorization": "Token ZGM2MDE3"
}
```

`Request Payload`  
`None`

`Response Headers:`

```json
{
  "date": "Thu, 14 Aug 2025 09:34:00 GMT",
  "content-type": "application/json",
  "vary": "Accept-Encoding",
  "link": "",
  "x-total-count": "2",
  "x-limit": "20",
  "x-request-id": "8046203538",
  "x-correlation-id": "4036910083",
  "ocpi-to-party-id": "INS",
  "ocpi-to-country-code": "IN",
  "ocpi-from-party-id": "THP",
  "ocpi-from-country-code": "IN"
}

```

`Response Body:`

```json
{
  "data": [
    {
      "country_code": "IN",
      "party_id": "THP",
      "id": "dz2SXdIDJDfNjsPfw",
      "currency": "INR",
      "elements": [
        {
          "price_components": [
            {
              "type": "ENERGY",
              "price": 12,
              "step_size": 1,
              "vat": 5
            }
          ]
        }
      ],
      "last_updated": "2024-12-10T06:53:43.315Z",
      "start_date_time": "2024-05-20T03:30:43.825Z",
      "end_date_time": "2024-05-20T06:30:43.825Z"
    },
    {
      "country_code": "IN",
      "party_id": "THP",
      "id": "ajcx2DQt07uERmEqprnQ",
      "currency": "INR",
      "elements": [
        {
          "price_components": [
            {
              "type": "ENERGY",
              "price": 20,
              "step_size": 1,
              "vat": 18
            }
          ]
        }
      ],
      "last_updated": "2024-12-09T08:43:21.913Z",
      "start_date_time": "2024-01-17T07:25:05.990Z",
      "end_date_time": "2024-01-17T07:25:05.990Z"
    }
  ],
  "status_code": 1000,
  "status_message": "Success",
  "timestamp": "2025-08-14T09:34:00.363Z"
}

```

1. **Geospatial Filtering**  
     
   * From cached OCPI locations, select those within 5 km of 28.6304,77.2177 (Haversine).

   

3. **Map OCPI → Beckn** For each matching location & its EVSEs:  
     
   * **provider.id** ← OCPI `party_id` domain (`cpo1.com`)  
   * **locations\[\]** ← OCPI `location.id`, `location.name`, `coordinates` → `gps`, `address.full`  
   * **items\[\]** ← OCPI `evse_id`, name `"EV Charger #n"`, code `"load"`, **tags** ← group under one descriptor `"Charger Description"` with a `list` of `{ descriptor.code: connector_standard|power_type|status, value }`  
   * **price** ← map from OCPI `tariffs` entry for that `tariff_id`  
   * **fulfillments\[\]** ← use location coordinates & opening hours as `stops` with time ranges

   

4. **Compose Beckn `on_search`**

### 1.3. `on_search` Response (BPP → BAP)

```json
{
  "context": {
    "domain": "deg",
    "action": "on_search",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "abcdef12-5678-1234-abcd-abcdef987654",
    "timestamp": "2025-07-30T12:00:02Z"
  },
  "message": {
    "catalog": {
      "providers": [
        {
          "id": "cpo1.com",
          "descriptor": {
            "name": "CPO 1"
          },
          "locations": [
            {
              "id": "LOC-DELHI-001",
              "descriptor": {
                "name": "BlueCharge Connaught Place Station"
              },
              "gps": "28.6304,77.2177",
              "address": {
                "full": "Connaught Place, New Delhi"
              }
            }
          ],
          "items": [
            {
              "id": "IN*BCN*E001",
              "descriptor": {
                "name": "EV Charger #1 (AC Fast Charger)",
                "code": "load"
              },
              "tags": [
                {
                  "descriptor": {
                    "name": "Charger Description"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "connector_standard"
                      },
                      "value": "IEC_62196_T2"
                    },
                    {
                      "descriptor": {
                        "code": "power_type"
                      },
                      "value": "AC_3_PHASE"
                    },
                    {
                      "descriptor": {
                        "code": "status"
                      },
                      "value": "AVAILABLE"
                    }
                  ]
                }
              ],
              "price": {
                "currency": "INR/kWh",
                "value": "18.00"
              },
              "fulfillment_ids": [
                "fulfillment-001"
              ]
            },
            {
              "id": "IN*BCN*E002",
              "descriptor": {
                "name": "EV Charger #2 (DC Ultra Fast Charger)",
                "code": "load"
              },
              "tags": [
                {
                  "descriptor": {
                    "name": "Charger Description"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "code": "connector_standard"
                      },
                      "value": "IEC_62196_CCS2"
                    },
                    {
                      "descriptor": {
                        "code": "power_type"
                      },
                      "value": "DC"
                    },
                    {
                      "descriptor": {
                        "code": "status"
                      },
                      "value": "AVAILABLE"
                    }
                  ]
                }
              ],
              "price": {
                "currency": "INR/kWh",
                "value": "25.00"
              },
              "fulfillment_ids": [
                "fulfillment-002"
              ]
            }
          ],
          "fulfillments": [
            {
              "id": "fulfillment-001",
              "type": "CHARGING",
              "stops": [
                {
                  "location": {
                    "gps": "28.6304,77.2177",
                    "address": {
                      "full": "Connaught Place, New Delhi"
                    }
                  },
                  "time": {
                    "range": {
                      "start": "00:00:00",
                      "end": "23:59:59"
                    }
                  }
                }
              ]
            },
            {
              "id": "fulfillment-002",
              "type": "CHARGING",
              "stops": [
                {
                  "location": {
                    "gps": "28.6310,77.2200",
                    "address": {
                      "full": "Barakhamba Road, New Delhi"
                    }
                  },
                  "time": {
                    "range": {
                      "start": "00:00:00",
                      "end": "23:59:59"
                    }
                  }
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

### 1.4 Adapter Recommendations for `search`/`on_search`

1. **Stateless Handling**  
     
   * No session state is stored. Each `search` must include all needed intent parameters; `on_search` must echo the full `context.transaction_id` and catalog.

   

2. **OCPI Data Caching**  
     
   * Cache `/ocpi/2.2/locations` and `/ocpi/2.2/tariffs` for \~10 minutes.  
   * On cache expiry or miss, fetch fresh data before mapping.

   

3. **Geospatial Filtering**  
     
   * Use Haversine algorithm on cached coordinates to select EVSEs within the requested radius.

   

4. **Schema Mapping**  
     
   * **Locations** → `providers[].locations[]`  
   * **EVSEs** → `providers[].items[]` with proper `descriptor.code`, grouped `tags`  
   * **Tariffs** → `item.price`  
   * **Opening hours** → `fulfillments[].stops[].time.range`

   

5. **Error Handling & Fallbacks**  
     
   * If OCPI endpoints fail, return last-known-good cache with an added warning `tag`, or return a Beckn error with `error.code` and `error.message`.

   

6. **Logging & Metrics**  
     
   * Log adapter calls, latencies, and success rates for `/locations` and `/tariffs` to monitor performance.

With this, your BPP adapter will efficiently bridge Beckn’s `search`/`on_search` with OCPI’s discovery APIs—fully stateless, standards-compliant, and performant.

## **2\. Select / on\_select Workflow**

### 2.1. `select` Request (BAP → BPP)

```json
{
  "context": {
    "domain": "deg",
    "action": "select",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "select-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:01:00Z"
  },
  "message": {
    "order": {
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "location": { "id": "LOC-DELHI-001" }
        }
      ]
    }
  }
}
```

### 2.2. OCPI Adapter Processing (inside BPP)

1. **Fetch latest tariff**

```
GET https://api.cpo1.com/ocpi/2.2/tariffs?country_code=IN&party_id=BCN
→ rate = ₹18.00 per kWh
```

2. **Check EVSE availability**

```
GET https://api.cpo1.com/ocpi/2.2/locations/LOC-DELHI-001
→ status = AVAILABLE
```

3. **Calculate quote**  
     
   * Assume a standard session of 5 kWh  
   * Energy cost: 5 kWh × ₹18.00/kWh \= ₹90.00  
   * Service fee: ₹10.00  
   * **Total quoted price**: ₹100.00  
   * **Quote TTL**: 15 minutes (`"PT15M"`)

### 2.3. `on_select` Response (BPP → BAP)

```json
{
  "context": {
    "domain": "deg",
    "action": "on_select",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onselect-eeee-ffff-gggg-hhhh",
    "timestamp": "2025-07-30T12:01:02Z"
  },
  "message": {
    "order": {
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "location": { "id": "LOC-DELHI-001" }
        }
      ],
      "quote": {
        "id": "b1a38a2d-4f5e-6a7b-8c9d-0e1f2a3b4c5d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      }
    }
  }
}
```

### 2.4 Adapter Recommendations for `select`/`on_select`

1. **Stateless Echo**  
     
   * Mirror `provider`, `items`, and `fulfillments` exactly from the `select` request into `on_select`.

   

2. **Tariff Caching & Revalidation**  
     
   * Cache OCPI `/tariffs` for \~10 minutes.  
   * Always re-fetch on `select` if cache expired.

   

3. **Availability Check**  
     
   * GET `/ocpi/2.2/locations/{location_id}` to confirm `AVAILABLE`.

   

4. **Quote Construction**  
     
   * Use per-unit currency `INR/kWh` in all `price.currency` fields.  
   * Include a unique `quote.id`, full `breakup` referencing item IDs, and a `ttl`.

   

5. **Error Handling & Fallbacks**  
     
   * On OCPI failure, return a Beckn error or last-known-good data with a warning tag.

   

6. **Logging & Monitoring**  
     
   * Instrument OCPI interactions (latency, success/fail) for SLA compliance.

## **3\. Init / On\_init Workflow**

### 3.1. `init` Request (BAP → BPP)

```json
{
  "context": {
    "domain": "deg",
    "action": "init",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "init-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:02:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      }
    }
  }
}
```

### 3.2. OCPI Adapter Processing (inside BPP)

Between receiving the **`init`** request and sending **`on_init`**, the BPP adapter must perform the following OCPI operations and internal computations:

1. **Re-fetch Tariffs**

```
GET /ocpi/2.2/tariffs?country_code=IN&party_id=BCN
Authorization: Token {cpo_api_token}
```

   • Ensure you have the latest per-kWh rate before quoting.

   

2. **Re-check Availability**

```
GET /ocpi/2.2/locations/LOC-DELHI-001
Authorization: Token {cpo_api_token}
```

   • Confirm the EVSE status is still `AVAILABLE`.

   

3. **Re-calculate Quote**  
     
   * Use the agreed energy amount (or standard assumed usage) and current tariff:

```
energy_cost = tariff_rate × kWh
total_quote = energy_cost + service_fee
```

4. **Compute Payment Terms**  
     
   * Generate a new `payments[0].id` (e.g. based on transaction\_id)  
   * Set:

```json
{
  "collected_by": "bpp",
  "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
  "params": {
    "transaction_id": "<transaction_id>",
    "amount": "<total_quote>",
    "currency": "INR"
  },
  "type": "PRE-FULFILLMENT",
  "status": "NOT-PAID",
  "time": { "timestamp": "<pre-init timestamp>" }
}
```

5. **Map Fulfillment State → OCPI `SessionStatus.RESERVATION`**  
     
   * Since charging has not yet started, set:

```json
"fulfillments[0].state": {
  "descriptor": { "code": "RESERVATION", "name": "Reservation Confirmed" },
  "updated_at": "<now>",
  "updated_by": "<bpp_id>"
}
```

6. **Error Handling**  
     
   * If any OCPI call fails, immediately return a Beckn error response with an appropriate `error.code` and `error.message`, rather than proceeding to `on_init`.

This processing block ensures the BPP’s `on_init` response is both **stateless** (echoing the original init fields) and **OCPI-validated** (using live tariff and availability data).

### 3.3. `on_init` Response (BPP → BAP)

```json
{
  "context": {
    "domain": "deg",
    "action": "on_init",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "oninit-ffff-eeee-dddd-cccc",
    "timestamp": "2025-07-30T12:02:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "rateable": true,
          "tracking": true,
          "state": "RESERVATION",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "100.00",
            "currency": "INR"
          },
          "type": "PRE-FULFILLMENT",
          "status": "NOT-PAID",
          "time": { "timestamp": "2025-07-30T14:59:00Z" },
          "tags": []
        }
      ]
    }
  }
}
```

### 3.4. Adapter Recommendations for `init`/`on_init`

1. **Stateless Echo**  
     
   * Echo all `order` fields from `init` into `on_init`, including `fulfillments`, `quote`, and `billing`.

   

2. **OCPI Validation**  
     
   * **Tariffs:** Re-fetch `/ocpi/2.2/tariffs` for the latest rate.  
   * **Availability:** Re-GET `/ocpi/2.2/locations/{location_id}` to ensure the EVSE is still `AVAILABLE`.

   

3. **Fulfillment State Mapping**  
     
   * Use OCPI’s `SessionStatus.RESERVATION` immediately after `init` to indicate a booked session .

   

4. **Payments Array**  
     
   * Construct `payments` per the Payment schema, with `collected_by: "bpp"`, a parameterized `url`, and correct `params`.

   

5. **Quote Compliance**  
     
   * Ensure `quote.price.currency` is `"INR/kWh"` and breakup entries reference the correct item IDs.  
   * Include a UUID `quote.id` and a sensible `ttl` (e.g., `"PT15M"`).

   

6. **Caching Strategy**  
     
   * Cache OCPI `/locations` & `/tariffs` for \~10 minutes; on expiry, fetch fresh data.

   

7. **Error Handling**  
     
   * If any OCPI call fails, return a Beckn error with a clear `error.code`/`error.message`.  
   * Optionally fall back to last-known-good cache with a warning tag.

   

8. **Logging & Monitoring**  
     
   * Log OCPI interactions (requests, responses, latencies, errors) for audit and SLA monitoring.

## **4\. Confirm / on\_confirm Workflow**

### 4.1. `confirm` Request (BAP → BPP)

```json
{
  "context": {
    "domain": "deg",
    "action": "confirm",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "confirm-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:03:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "100.00",
            "currency": "INR"
          },
          "type": "PRE-FULFILLMENT",
          "status": "NOT-PAID",
          "time": { "timestamp": "2025-07-30T14:59:00Z" },
          "tags": []
        }
      ],
      "auth": {
        "token": {
          "uid": "GCN12345678",
          "type": "RFID",
          "contract_id": "GCN-IND-00001"
        }
      }
    }
  }
}
```

### 4.2. OCPI Adapter Processing (inside BPP)

1. **Authorize Token via OCPI**

```
POST https://api.cpo1.com/ocpi/2.2/tokens/IN/BCN/authorize
Authorization: Token {cpo_api_token}
Content-Type: application/json

{
  "token": {
    "uid": "GCN12345678",
    "type": "RFID",
    "contract_id": "GCN-IND-00001"
  }
}
```

   * **Response:**

```json
{
  "status_code": 1000,
  "data": {
    "authorization_id": "AUTH-GCN-20250730-001",
    "evse_uid": "IN*BCN*E001",
    "connector_id": "1"
  }
}
```

2. **Final Availability Check**

```
GET https://api.cpo1.com/ocpi/2.2/locations/LOC-DELHI-001
→ status = AVAILABLE
```

3. **Persist Order**  
     
   * Save order with all echoed fields, plus `"auth_token": "AUTH-GCN-20250730-001"`.  
   * Set `fulfillments[0].state = "PENDING"` (OCPI SessionStatus.PENDING).

### 4.3. `on_confirm` Response (BPP → BAP)

```json
{
  "context": {
    "domain": "deg",
    "action": "on_confirm",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onconfirm-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:03:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "rateable": true,
          "tracking": true,
          "state": "PENDING",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "100.00",
            "currency": "INR"
          },
          "type": "PRE-FULFILLMENT",
          "status": "NOT-PAID",
          "time": { "timestamp": "2025-07-30T14:59:00Z" },
          "tags": []
        }
      ],
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 4.4. Adapter Recommendations for `confirm`/`on_confirm`

1. **Stateless Echo**  
     
   * Mirror all `order` fields from `confirm` in `on_confirm`, including `provider`, `items`, `fulfillments`, `quote`, `billing`, and `payments`.

   

2. **OCPI Token Authorization**  
     
   * Call `/ocpi/2.2/tokens/{country}/{party}/{uid}/authorize` with the provided `auth.token`.  
   * Extract `authorization_id` and map it as `auth_token` in response.

   

3. **Final Availability Check**  
     
   * GET `/ocpi/2.2/locations/{location_id}` to ensure the EVSE remains `AVAILABLE`.

   

4. **Fulfillment State Mapping**  
     
   * Use OCPI’s `SessionStatus.PENDING` immediately after confirm to signal “session requested, not yet charging.”

   

5. **Error Handling**  
     
   * If token auth or availability check fails, return a Beckn error with `error.code`/`error.message`.  
   * Do not proceed to charging commands on failure.

   

6. **Logging & Monitoring**  
     
   * Log the OCPI `/authorize` and `/locations` calls for traceability and SLA monitoring.

## **5\. Update / On\_update flows (Charging Start)**

### 5.1. `update` Request (BAP → BPP)

```json
{
  "context": {
    "domain": "deg",
    "action": "update",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "update-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:04:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 5.2. OCPI Adapter Processing (inside BPP)

1. **Start Charging Session**

```
POST https://api.cpo1.com/ocpi/2.2/commands
Authorization: Token {cpo_api_token}
Content-Type: application/json

{
  "command": "START_SESSION",
  "authorization_id": "AUTH-GCN-20250730-001",
  "location_id": "LOC-DELHI-001",
  "evse_uid": "IN*BCN*E001",
  "connector_id": "1"
}
```

   * **Response:**

```json
{
  "status_code": 1000,
  "data": {
    "session_id": "SESSION-9876543210"
  }
}
```

2. **Persist Session**  
     
   * Store `"session_id": "SESSION-9876543210"` in order record.  
   * Set `fulfillments[0].state = "ACTIVE"` (OCPI’s SessionStatus.ACTIVE).

### 5.3. `on_update` Response (BPP → BAP)

```json
{
  "context": {
    "domain": "deg",
    "action": "on_update",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onupdate-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:04:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "rateable": true,
          "tracking": true,
          "state": "ACTIVE",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 5.4. Adapter Recommendations for `update`/`on_update`

1. **Stateless Echo**  
     
   * Echo `order.id` and any relevant fields (e.g., `auth_token`) from `update` into `on_update`.

   

2. **OCPI START\_SESSION Command**  
     
   * Call `/ocpi/2.2/commands` with `"command": "START_SESSION"` and the `authorization_id`.  
   * Extract `session_id` to track the charging session.

   

3. **Fulfillment State Mapping**  
     
   * Map Beckn’s `fulfillment.state` to OCPI’s `SessionStatus.ACTIVE` to indicate charging in progress.

   

4. **Persist Session ID**  
     
   * Store the returned `session_id` for use in tracking and billing.

   

5. **Error Handling**  
     
   * If the OCPI command fails, return a Beckn error with `error.code`/`error.message` and do *not* send `on_update`.

   

6. **Logging & Monitoring**  
     
   * Log the OCPI command request/response and measure latency to ensure SLA compliance.

## 6\. Track / on\_track Flows (Charging session)

### 6.1. `track` Request (BAP → BPP)

```json
POST /track
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "track",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "track-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:05:00Z"
  },
  "message": {
    "order_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 6.2. OCPI Adapter Processing (inside the BPP)

1. **Lookup Session**  
     
   * Retrieve stored `session_id` (e.g., `"SESSION-9876543210"`) using `order_id`.

   

2. **Fetch Real-Time Status**

```
GET https://api.cpo1.com/ocpi/2.2/sessions/SESSION-9876543210
Authorization: Token {cpo_api_token}
```

   * **Response** provides:  
       
     * `status`: one of OCPI’s `SessionStatus` (e.g. `"ACTIVE"`)

   

3. **Map OCPI → Tracking Schema**  
     
   * **tracking.id** ← `"TRACK-" + session_id`  
   * **tracking.url** ← `"https://track.bluechargenet-aggregator.io/session/" + session_id`  
   * **tracking.status** ← `"active"` if OCPI `status == "ACTIVE"`, otherwise `"inactive"`

### 6.3. `on_track` Response (BPP → BAP)

```json
POST /on_track
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_track",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "ontrack-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:05:02Z"
  },
  "message": {
    "tracking": {
      "id": "TRACK-SESSION-9876543210",
      "url": "https://track.bluechargenet-aggregator.io/session/SESSION-9876543210",
      "status": "active"
    }
  }
}
```

### 6.4. Adapter Recommendations for `track`/`on_track`

1. **Stateless Operation**  
     
   * Use only `order_id` to look up `session_id`; do not store per-call state.

   

2. **OCPI Session Polling**  
     
   * Call `/ocpi/2.2/sessions/{session_id}` to retrieve live `status`.

   

3. **Tracking Schema Compliance**  
     
   * Populate only `tracking.id`, `tracking.url`, and `tracking.status`—omit `location` for fixed chargers.

   

4. **Status Mapping**  
     
   * OCPI `SessionStatus.ACTIVE` → `"active"`, all other statuses → `"inactive"`.

   

5. **Error Handling**  
     
   * If session lookup or OCPI call fails, return an `on_track` containing an `error` object with a Beckn `error.code` and `error.message`.

   

6. **Throttling & Caching**  
     
   * Throttle OCPI session calls (e.g., max once per 15 s) and cache recent results briefly to smooth bursts.

   

7. **Logging & Monitoring**  
     
   * Log tracking requests and OCPI interactions for SLA and debugging.

## **7\. Update / On\_update Flows (End of charging session)**

### 7.1. `update` Request (BAP → BPP)

```json
POST /update
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "update",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "update-stop-1111-2222-3333-4444",
    "timestamp": "2025-07-30T16:00:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 7.2. OCPI Adapter Processing (inside BPP)

1. **Stop Charging Session**

```
POST https://api.cpo1.com/ocpi/2.2/commands
Authorization: Token {cpo_api_token}
Content-Type: application/json

{
  "command": "STOP_SESSION",
  "session_id": "SESSION-9876543210",
  "authorization_id": "AUTH-GCN-20250730-001",
  "location_id": "LOC-DELHI-001",
  "evse_uid": "IN*BCN*E001",
  "connector_id": "1"
}
```

   → `status_code: 1000`

   

2. **Retrieve Final CDR**

```
GET https://api.cpo1.com/ocpi/2.2/cdrs/SESSION-9876543210
Authorization: Token {cpo_api_token}
```

   **Response data**:

```json
{
  "status_code": 1000,
  "data": {
    "cdr": {
      "id": "CDR-SESSION-9876543210",
      "session_id": "SESSION-9876543210",
      "start_date_time": "2025-07-30T15:00:00Z",
      "end_date_time": "2025-07-30T16:00:00Z",
      "total_energy": 4.5,
      "total_cost": 81.00,
      "currency": "INR"
    }
  }
}
```

3. **Compute Final Amount**  
     
   * **Energy cost:** ₹81.00  
   * **Service fee:** ₹10.00  
   * **Total due:** ₹91.00

   

4. **Persist Updates**  
     
   * Update `fulfillments[0].state = "COMPLETED"` (OCPI `SessionStatus.COMPLETED`).  
       
   * Update `payments[0]`:  
       
     * `type` → `"POST-FULFILLMENT"`  
     * `params.amount` → `"91.00"`  
     * `status` → `"NOT-PAID"`  
     * `time.timestamp` → `"2025-07-30T16:00:01Z"`

### 7.3. `on_update` Response (BPP → BAP)

```json
POST /on_update
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_update",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onupdate-stop-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T16:00:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "rateable": true,
          "tracking": true,
          "state": "COMPLETED",
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "91.00",
            "currency": "INR"
          },
          "type": "POST-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T16:00:01Z"
          },
          "tags": []
        }
      ]
    }
  }
}
```

### 7.4 Adapter Recommendations for Stopping & Finalizing Payment

1. **Stateless Echo**  
     
   * Echo all relevant `order.id`, `fulfillments`, and `payments` fields from the internal state into `on_update`.

   

2. **OCPI STOP\_SESSION Command**  
     
   * Call `/ocpi/2.2/commands` with `"command": "STOP_SESSION"`, the `session_id`, and `authorization_id`.

   

3. **Fetch Final CDR**  
     
   * GET `/ocpi/2.2/cdrs/{session_id}` to obtain `total_energy` and `total_cost`.

   

4. **Payment Recalculation**  
     
   * Combine `total_cost` with any fixed fees to compute the final amount.  
       
   * Update the existing `payments[0]` entry:  
       
     * Change `type` to `"POST-FULFILLMENT"`.  
     * Set `params.amount` to the newly calculated total.  
     * Update `time.timestamp` to now.

   

5. **Fulfillment State Mapping**  
     
   * Map to OCPI’s `SessionStatus.COMPLETED` → `"COMPLETED"` in Beckn.

   

6. **Error Handling**  
     
   * If any OCPI call (stop, CDR fetch) fails, return a Beckn error with `error.code` and `error.message`.  
   * Do not send `on_update` if the stop command itself fails.

   

7. **Logging & Monitoring**  
     
   * Log all OCPI STOP\_SESSION and CDR calls along with latencies and statuses for SLA compliance.

## **8\. Asynchronous on\_update \- When charging terms change on an active order**

When the BPP detects a change that **alters the agreed-upon payment terms** (but does **not** cancel the order), it must send an unsolicited `on_update` with the new `quote` and `payments`. These updates occur **without** a BAP-initiated action.

### 8.1. Triggering Events

The BPP should push an unsolicited `on_update` **only** when one of these events occurs **and** the payment terms change:

* **Time-of-Day Tariff Change** (off-peak → peak)  
* **Dynamic Grid Pricing / Demand Response**  
* **Promotional or Loyalty Discount Redeemed**  
* **Vehicle Pre-conditioning Add-On**  
* **Connector Swap / Power Level Upgrade**  
* **Local Tax or Fee Update**  
* **Network Congestion Credit**  
* **Partial Session Extension**

Intermediate state changes (e.g. `PENDING`, `ACTIVE`, `SUSPENDED_*`, `FINISHING`) that **do not** affect payment go via `on_status`, **not** `on_update`.

### 8.2. Fulfillment State Schema

```
state:
  descriptor:
    $ref: "./Descriptor.yaml"
  updated_at:
    type: string
    format: date-time
  updated_by:
    type: string
    description: ID of entity which changed the state
```

### 

### 8.3. Example: Time-of-Day Tariff Change Mid-Session

At **16:00**, peak rates kick in; the remaining 2 kWh is now ₹25/kWh instead of ₹18/kWh.

```json
POST /on_update
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_update",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onupdate-tod-tariff-161000",
    "timestamp": "2025-07-30T16:00:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "ACTIVE",
              "name": "Charging In Progress"
            },
            "updated_at": "2025-07-30T16:00:00Z",
            "updated_by": "bluechargenet-aggregator.io"
          },
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "112.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (3 kWh @ ₹18.00/kWh)",
            "price": { "currency": "INR/kWh", "value": "54.00" }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (2 kWh @ ₹25.00/kWh)",
            "price": { "currency": "INR/kWh", "value": "50.00" }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": { "currency": "INR/kWh", "value": "8.00" }
          }
        ],
        "ttl": "PT10M"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "112.00",
            "currency": "INR"
          },
          "type": "ON-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T16:00:00Z"
          },
          "tags": []
        }
      ]
    }
  }
}
```

### 8.4. Adapter Recommendations

1. **Detect Only Term-Altering Events**  
     
   * Monitor OCPI or business logic for the eight scenarios above.

   

2. **Stateless Echo**  
     
   * Echo `order.id`, `fulfillments[].id`, and unchanged fields; update only `state`, `quote`, `payments`.

   

3. **Quote Recalculation**  
     
   * Assign a new `quote.ttl` (shorter, e.g. 10 min) to reflect the freshness requirement.

   

4. **Payment Terms Update**  
     
   * Change `payments[0].type` to `ON-FULFILLMENT` when charging is ongoing.

   

5. **Idempotency**  
     
   * Use unique `message_id` per event and debounce identical term updates.

   

6. **Error Handling**  
     
   * If recalculation fails, send `on_update` with `error` and leave previous terms intact.

   

7. **Logging**  
     
   * Record each asynchronous `on_update` for audit and SLA verification.

## 

## **9\. Status / on\_status flows (Informational updates)**

### 9.1. `status` Request (BAP → BPP)

```json
POST /status
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "status",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "status-1111-2222-3333-4444",
    "timestamp": "2025-07-30T12:06:00Z"
  },
  "message": {
    "order_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 9.2 Adapter Processing

1. **Lookup Order & Session**  
     
   * Retrieve full order record and associated `session_id` for `order_id`.

   

2. **Fetch OCPI Session Status**

```
GET https://api.cpo1.com/ocpi/2.2/sessions/SESSION-9876543210
Authorization: Token {cpo_api_token}
```

3. **Map OCPI → Beckn Fulfillment State**  
     
   * Build the `state` object per Fulfillment State schema.

### 9.3. `on_status` Response (BPP → BAP)

```json
POST /on_status
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_status",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onstatus-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:06:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "rateable": true,
          "tracking": true,
          "state": {
            "descriptor": {
              "code": "ACTIVE",
              "name": "Charging In Progress"
            },
            "updated_at": "2025-07-30T12:06:02Z",
            "updated_by": "bluechargenet-aggregator.io"
          },
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "100.00",
            "currency": "INR"
          },
          "type": "PRE-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T14:59:00Z"
          },
          "tags": []
        }
      ],
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 9.4 Unsolicited `on_status` Calls from BPP

The BPP should also **push** `on_status` whenever **informational** OCPI session statuses change, **without** a prior `status` request. These updates keep the BAP in sync with charger state but do **not** affect payment terms.

### 9.5 Triggering Status Codes (Informational Only)

* `RESERVATION`  
* `PENDING`  
* `ACTIVE`  
* `SUSPENDED_EVSE`  
* `SUSPENDED_EV`  
* `FINISHING`

**Note:** Do **not** send unsolicited `on_status` for `COMPLETED` or `INVALID`—those are handled by `on_update` (or `on_cancel` for invalid sessions).

### 9.6. Example: Station-Side Pause (`SUSPENDED_EVSE`)

```json
POST /on_status
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_status",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onstatus-pause-152500",
    "timestamp": "2025-07-30T15:25:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "SUSPENDED_EVSE",
              "name": "Charging Paused by Station"
            },
            "updated_at": "2025-07-30T15:25:00Z",
            "updated_by": "bluechargenet-aggregator.io"
          },
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "quote": {
        "id": "82a8f741-9bd3-4c9e-8c2d-1e2b3a4f5c6d",
        "price": {
          "currency": "INR/kWh",
          "value": "100.00"
        },
        "breakup": [
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Energy (5 kWh @ ₹18.00/kWh)",
            "price": {
              "currency": "INR/kWh",
              "value": "90.00"
            }
          },
          {
            "item": { "id": "IN*BCN*E001" },
            "title": "Service Fee",
            "price": {
              "currency": "INR/kWh",
              "value": "10.00"
            }
          }
        ],
        "ttl": "PT15M"
      },
      "billing": {
        "name": "Ravi Kumar",
        "organization": {
          "descriptor": { "name": "GreenCharge Pvt Ltd" }
        },
        "address": "Apartment 123, MG Road, Bengaluru, Karnataka, 560001, India",
        "state": { "name": "Karnataka" },
        "city": { "name": "Bengaluru" },
        "email": "ravi.kumar@greencharge.com",
        "phone": "+918765432100",
        "time": { "timestamp": "2025-07-30T12:02:00Z" },
        "tax_id": "GSTIN29ABCDE1234F1Z5"
      },
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/pay?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "100.00",
            "currency": "INR"
          },
          "type": "PRE-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T14:59:00Z"
          },
          "tags": []
        }
      ],
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 9.7 Recommendations for Unsolicited `on_status`

1. **Detect Informational Statuses**  
     
   * Watch for OCPI statuses: `RESERVATION`, `PENDING`, `ACTIVE`, `SUSPENDED_EVSE`, `SUSPENDED_EV`, `FINISHING`.

   

2. **Stateless Echo**  
     
   * Send full `order` object with only the updated `fulfillment.state`.

   

3. **Debounce & Idempotency**  
     
   * Only push when the state actually changes; include unique `message_id`.

   

4. **Error Handling**  
     
   * Do not push on transient fetch errors.

   

5. **Monitoring**  
     
   * Log every unsolicited `on_status` event for audit and SLA tracking.

## 

## 10\. Cancel / on\_cancel flows

### 10.1. `cancel` Request (BAP → BPP)

```json
POST /cancel
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "cancel",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "cancel-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T12:10:00Z"
  },
  "message": {
    "order_id": "123e4567-e89b-12d3-a456-426614174000",
    "cancellation_reason_id": "user_request",
    "descriptor": {
      "code": "USER_CANCELLED",
      "name": "User Requested Cancellation"
    }
  }
}
```

### 10.2 Adapter Processing

1. **Lookup Order & Session**  
     
   * Retrieve the order and any active `session_id`.

   

2. **Terminate OCPI Session (if exists)**

```
POST /ocpi/2.2/commands
{
  "command": "STOP_SESSION",
  "session_id": "SESSION-9876543210",
  "authorization_id": "AUTH-GCN-20250730-001",
  "location_id": "LOC-DELHI-001",
  "evse_uid": "IN*BCN*E001",
  "connector_id": "1"
}
```

3. **Fetch Final CDR (if partially charged)**

```
GET /ocpi/2.2/cdrs/SESSION-9876543210
```

4. **Compute Any Refund or Fees**  
     
   * E.g., if 2 kWh consumed → ₹36 \+ ₹10 fee \= ₹46 due; refund remainder.

   

5. **Update Order Status**  
     
   * `order.status` → `"CANCELLED"`  
   * `order.cancellation` → `{ reason_id, descriptor, time, updated_by }`  
   * `payments` → adjust `params.amount` and `status` per refund logic.

### 10.3. `on_cancel` Response (BPP → BAP)

```json
POST /on_cancel
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_cancel",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "oncancel-eeee-ffff-gggg-hhhh",
    "timestamp": "2025-07-30T12:10:02Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "CANCELLED",
      "cancellation": {
        "reason_id": "user_request",
        "descriptor": {
          "code": "USER_CANCELLED",
          "name": "User Requested Cancellation"
        },
        "updated_at": "2025-07-30T12:10:02Z",
        "updated_by": "bluechargenet-aggregator.io"
      },
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "INVALID",
              "name": "Session Cancelled"
            },
            "updated_at": "2025-07-30T12:10:02Z",
            "updated_by": "bluechargenet-aggregator.io"
          },
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "https://payments.bluechargenet-aggregator.io/refund?transaction_id=$transaction_id&amount=$amount",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "46.00",
            "currency": "INR"
          },
          "type": "POST-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T12:10:02Z"
          },
          "tags": []
        }
      ],
      "auth_token": "AUTH-GCN-20250730-001"
    }
  }
}
```

### 10.4 Unsolicited `on_cancel` Calls from BPP

The BPP should **push** an unsolicited `on_cancel` when the order must be cancelled **by the provider** due to external events:

### Triggering Scenarios

* **Charger Hardware Failure** Station reports EVSE offline or faulty → no session possible.  
* **Connector Incompatibility** Vehicle cannot connect to the charger standard → session invalid.  
* **Payment Timeout** User fails to pay before `quote.ttl` expires.  
* **No-Show at Reservation** User does not arrive or start a session within the reserved window.  
* **Station Closure / Maintenance** CPO closes a station unexpectedly or for emergency work.  
* **Regulatory / Grid Emergency Shutdown** Grid operator forces charging halt.

### Example: Charger Hardware Failure

```json
POST /on_cancel
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_cancel",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "oncancel-async-failure-2222-3333-4444",
    "timestamp": "2025-07-30T15:10:00Z"
  },
  "message": {
    "order": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "CANCELLED",
      "cancellation": {
        "reason_id": "hardware_failure",
        "descriptor": {
          "code": "CHARGER_HW_FAIL",
          "name": "Charger Hardware Failure"
        },
        "updated_at": "2025-07-30T15:10:00Z",
        "updated_by": "bluechargenet-aggregator.io"
      },
      "provider": { "id": "cpo1.com" },
      "items": [
        { "id": "IN*BCN*E001" }
      ],
      "fulfillments": [
        {
          "id": "fulfillment-001",
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "INVALID",
              "name": "Session Invalidated"
            },
            "updated_at": "2025-07-30T15:10:00Z",
            "updated_by": "bluechargenet-aggregator.io"
          },
          "stops": [
            {
              "location": { "id": "LOC-DELHI-001" },
              "time": {
                "range": {
                  "start": "2025-07-30T15:00:00Z",
                  "end":   "2025-07-30T16:00:00Z"
                }
              }
            }
          ]
        }
      ],
      "payments": [
        {
          "id": "payment-123e4567-e89b-12d3-a456-426614174000",
          "collected_by": "bpp",
          "url": "",
          "params": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "amount": "0.00",
            "currency": "INR"
          },
          "type": "POST-FULFILLMENT",
          "status": "NOT-PAID",
          "time": {
            "timestamp": "2025-07-30T15:10:00Z"
          },
          "tags": []
        }
      ]
    }
  }
}
```

### 10.5 Adapter Recommendations

1. **Detect Cancellation Conditions**  
     
   * Monitor OCPI error codes or internal health checks for charger availability and session invalidations.

   

2. **Stateless Echo**  
     
   * Always include the full `order` object in `on_cancel`, updating only `status`, `cancellation`, `fulfillment.state`, and `payments`.

   

3. **Cancellation Reasons**  
     
   * Use clear `cancellation_reason_id` values (e.g., `hardware_failure`, `no_show`, `payment_timeout`) with matching descriptors.

   

4. **Payment Handling**  
     
   * If no charge incurred, set `payments[0].params.amount = "0.00"` and leave `url` empty, indicating offline/no payment required.

   

5. **Idempotency & Debounce**  
     
   * Ensure a single `on_cancel` per order; use unique `message_id`.

   

6. **Logging**  
     
   * Record all unsolicited cancellations and their triggers for audit and compliance.

## **11\. Rating / on\_rating flows**

### 11.1. `rating` Request (BAP → BPP)

```
POST /rating
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "rating",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "rating-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T17:00:00Z"
  },
  "message": {
    "ratings": [
      {
        "rating_category": "Fulfillment",
        "id": "fulfillment-001",
        "value": "5"
      },
      {
        "rating_category": "Support",
        "id": "agent-007",
        "value": "4"
      }
    ]
  }
}
```

### 11.2 Adapter Processing

1. **Persist Ratings**  
     
   * Store each rating (`rating_category`, `id`, `value`) in BPP’s feedback store.

   

2. **Determine Feedback Form Need**  
     
   * If additional qualitative input is required, prepare an **XInput** object (per BECKN-007) to solicit it; otherwise, omit or return an empty XInput.

### 11.3. `on_rating` Response (BPP → BAP)

```
POST /on_rating
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_rating",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onrating-eeee-ffff-gggg-hhhh",
    "timestamp": "2025-07-30T17:00:02Z"
  },
  "message": {
    "feedback_form": {
      "form": {
        "url": "https://api.bluechargenet-aggregator.io/v1/feedback/forms/123e4567-e89b-12d3-a456-426614174999",
        "mime_type": "application/xml",
        "submission_id": "9f8a7b6c-5d4e-3f2a-1b0c-9d8e7f6a5b4c"
      },
      "required": true
    }
  }
}
```

* If no further feedback is required, return:

```json
"feedback_form": {}
```

### 11.4. Unsolicited `on_rating` Calls from BPP

The BPP may proactively invite richer feedback once the order is `COMPLETED`, by pushing an unsolicited `on_rating` with an XInput form:

```
POST /on_rating
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_rating",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onrating-async-1111-2222-3333-4444",
    "timestamp": "2025-07-30T16:10:00Z"
  },
  "message": {
    "feedback_form": {
      "form": {
        "url": "https://api.bluechargenet-aggregator.io/v1/feedback/forms/abcdef12-3456-7890-abcd-ef1234567890",
        "mime_type": "text/html",
        "submission_id": "abcdef12-3456-7890-abcd-ef1234567890"
      },
      "required": false
    }
  }
}
```

### 11.5 Adapter Recommendations

1. **Stateless Echo**  
     
   * Always include full `context` in `on_rating`; the BPP cannot assume prior state.

   

2. **XInput Compliance**  
     
   * Use the XInput schema:

```
feedback_form:
  form:
    url: <uri>
    mime_type: <text/html|application/xml>
    submission_id: <uuid>
  required: <boolean>
```

3. **Conditional Prompting**  
     
   * Send an empty object if no further feedback is needed.

   

4. **Unsolicited Invitations**  
     
   * After order `COMPLETED`, optionally issue an unsolicited `on_rating` to request more detailed feedback.

   

5. **Idempotency**  
     
   * Debounce invites so each order gets at most one proactive feedback request; use unique `message_id`.

   

6. **Error Handling**  
     
   * If preparing or persisting the form fails, respond with an `error` object in `on_rating`.

   

7. **Monitoring**  
     
   * Track submission rates, form loads, and completion rates for continuous improvement.

## **12\. Support / on\_support flows**

### 12.1. `support` Request (BAP → BPP)

```
POST /support
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "support",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "support-aaaa-bbbb-cccc-dddd",
    "timestamp": "2025-07-30T17:30:00Z"
  },
  "message": {
    "support": {
      "callback_phone": "+911234567890",
      "email": "ravi.kumar@bookmycharger.com"
    }
  }
}
```

### Adapter Processing

1. **Ticket Creation**  
     
   * Create a support ticket in the BPP’s CRM, linking it to `transaction_id`.  
   * Use `message.support.callback_phone` / `email` to schedule a callback or email response.

   

2. **Prepare Support Details**  
     
   * Assign a `ref_id` for the ticket.  
   * Determine support contact channels: phone, email, and self-service URL.

### 12.2. `on_support` Response (BPP → BAP)

```
POST /on_support
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_support",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onsupport-eeee-ffff-gggg-hhhh",
    "timestamp": "2025-07-30T17:30:02Z"
  },
  "message": {
    "support": {
      "ref_id": "SUP-20250730-001",
      "phone": "1800123456",
      "email": "support@bluechargenet-aggregator.io",
      "url": "https://support.bluechargenet-aggregator.io/ticket/SUP-20250730-001"
    }
  }
}
```

* **`ref_id`**: Unique support ticket identifier  
* **`phone`**: Toll-free line for immediate help  
* **`email`**: Support inbox for follow-up  
* **`url`**: Web portal to view ticket status and chat

### 12.3. Unsolicited `on_support` Calls from BPP

The BPP may **proactively** notify the BAP that support is engaged when certain **critical events** occur (without a prior `/support` call):

### Triggering Scenarios

* **Charger Hardware Failure**  
* **Billing Dispute Raised**  
* **Session Invalidated**  
* **Emergency Station Shutdown**

### Example: Proactive Support Notification

```
POST /on_support
Content-Type: application/json

{
  "context": {
    "domain": "deg",
    "action": "on_support",
    "version": "1.0.0",
    "bap_id": "bookmycharger.com",
    "bap_uri": "https://api.bookmycharger.com/v1",
    "bpp_id": "bluechargenet-aggregator.io",
    "bpp_uri": "https://api.bluechargenet-aggregator.io/v1",
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "message_id": "onsupport-async-2222-3333-4444",
    "timestamp": "2025-07-30T15:10:00Z"
  },
  "message": {
    "support": {
      "ref_id": "SUP-20250730-002",
      "phone": "1800123456",
      "email": "support@bluechargenet-aggregator.io",
      "url": "https://support.bluechargenet-aggregator.io/ticket/SUP-20250730-002"
    }
  }
}
```

### 12.4 Adapter Recommendations for `support`/`on_support`

1. **Stateless Echo**  
     
   * Always echo full `context` and include a complete `support` object.

   

2. **Support Ticketing**  
     
   * Integrate with BPP’s CRM or ticketing system; generate and return `ref_id`.

   

3. **Proactive Alerts**  
     
   * On critical failures (hardware, billing, invalid session), send an unsolicited `on_support`.

   

4. **Idempotency**  
     
   * Ensure each support ticket triggers at most one unsolicited `on_support` per `transaction_id`.

   

5. **Error Handling**  
     
   * If support creation fails, respond with `error` in lieu of `support`.

   

6. **Monitoring**  
     
   * Track support requests and notifications to meet SLA and response-time targets.

# **Conclusion**

This RFC has detailed a comprehensive, Beckn-first integration strategy for EV charging, mapping each Beckn protocol step (`search` → `on_search`, `select` → `on_select`, `init` → `on_init`, `confirm` → `on_confirm`, `update`/`track`/`cancel`/`rating`/`support` and their callbacks) to the corresponding OCPI APIs. Key takeaways include:

* **Stateless Architecture**  
   Each Beckn request includes all necessary context; every response echoes the full order (or relevant object), ensuring the BPP does not need to maintain session state between calls.

* **Schema Compliance**  
   We have aligned Beckn objects (`Quote`, `Fulfillment`, `Payment`, `State`, `Tracking`, `Support`, etc.) with OCPI’s modules (`Locations`, `Tariffs`, `Tokens`, `Sessions`, `CDRs`, `Commands`), preserving standardized codes and formats.

* **Adapter Best Practices**

  * **Caching & Revalidation:** Cache OCPI data (locations, tariffs) for a short TTL, re-fetching on expiry or critical steps.  
  * **Error Handling:** Translate OCPI failures into Beckn error responses with clear codes/messages.  
  * **Idempotency & Debounce:** Use unique `message_id`s and only push unsolicited callbacks for meaningful state or contract changes.  
  * **Logging & Monitoring:** Instrument all OCPI interactions and unsolicited callbacks for SLA tracking and debugging.

* **Asynchronous Callbacks**

  * **`on_status`** for informative charger states that do not affect billing.  
  * **`on_update`** for contract-altering events (final CDR, tariff changes, add-ons).  
  * **`on_cancel`** when sessions are invalidated or aborted.  
  * **`on_rating`** and **`on_support`** to close the loop on feedback and customer care.

By following this RFC, a BPP can reliably translate Beckn marketplace calls into OCPI operations and back, offering seamless roaming across diverse CPO networks while maintaining Beckn’s core principles of statelessness, interoperability, and clear separation of informational vs. contractual updates.

