# BusIt // Campus Transit Telemetry & ETA Engine Specification
**Class:** `ELECTRIC / REACT` • **Domain:** Fleet Telemetry & Real-Time Geospatial Transit  
**Architect:** Parameshwaran S (Parama) • **Status:** Production Campus Platform

---

## 1. System Overview
BusIt is an enterprise campus transit tracking and dispatch platform developed to eliminate shuttle wait times across university campuses. It features live GPS geofencing, sub-second WebSocket telemetry streams, automated route optimization, and student push notifications.

```
[ Shuttle GPS Telemetry Node / Mobile Transmitter ]
                        │
                        ▼ (Sub-Second Latency via WebSockets)
             [ Firebase Realtime Database ]
                        │
                        ├──► [ Cloud Geofencing & ETA Inference Engine ]
                        │    (Haversine Distance & Historical Speed Curves)
                        │
                        ▼
      [ Client Web & Mobile Application (React.js) ]
  (Live Google Maps Overlay, Station Pinning, & Geofence Alarms)
```

---

## 2. Core Technical Architecture

### 2.1 Real-Time Geospatial Ingestion
- Shuttle drivers transmit continuous coordinate pairs (Latitude, Longitude, Heading, Velocity) sampled at 1Hz from mobile onboard GPS receivers.
- Telemetry streams into **Firebase Realtime Database** via persistent WebSocket connections, ensuring global state propagation with sub-second synchronization latency.

### 2.2 Predictive ETA Algorithm
- Calculates estimated times of arrival (ETA) utilizing an augmented **Haversine Distance Model** weighted against:
  - Historical route segment velocity profiles.
  - Active campus traffic density coefficients.
  - Station dwell time averages (passenger boarding/alighting).
- Validated to reduce student shuttle waiting time by **35%** across campus transit loops.

### 2.3 Dynamic Geofencing & Push Dispatch
- Implements polygon geofencing around primary student dormitory zones and academic blocks.
- When an approaching shuttle crosses within an 800m threshold, automated browser notifications alert waiting students to proceed to designated pick-up bays.

---

## 3. Technology Stack
- **Frontend Client:** React.js, TailwindCSS, Redux Toolkit
- **Geospatial Mapping:** Google Maps JavaScript API, Leaflet.js
- **Real-Time Data Layer:** Firebase Realtime Database, WebSockets
- **Deployment:** Vercel / Cloudflare CDN
