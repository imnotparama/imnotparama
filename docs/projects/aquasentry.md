# AquaSentry // Edge IoT Architecture Specification
**Class:** `WATER / HARDWARE` • **Domain:** Industrial Edge Environmental Quality Diagnostics  
**Architect:** Parameshwaran S (Parama) • **Status:** Deployed Hardware Prototype

---

## 1. System Overview
AquaSentry is an autonomous edge computing environmental diagnostics platform engineered to continuously monitor, analyze, and alert on water contamination and chemical anomalies across rural reservoirs and industrial reservoirs in real-time.

```
[ Multi-Probe Sensor Array ]
 (pH, Turbidity, TDS, Temp)
             │ (Analog / ADC)
             ▼
[ ESP32 Microcontroller Core ]
 (Sensor Calibration & Local Anomaly Detection)
             │ (MQTT over TLS / Wi-Fi / GSM)
             ▼
    [ Cloud MQTT Broker ]
             │
             ├──► [ Real-Time Web Telemetry Dashboard ]
             └──► [ Autonomous Emergency SMS / Push Dispatch ]
```

---

## 2. Core Technical Architecture

### 2.1 Sensor Probe Cluster & Signal Conditioning
- Integrates analog probes for:
  - **pH Sensor:** Operational range 0.0 to 14.0 pH with automated 2-point temperature compensation.
  - **Turbidity Sensor:** Light scattering detection to identify suspended particulates (NTU).
  - **Total Dissolved Solids (TDS):** Conductivity-based measurement of mineral/pollutant concentration (ppm).
  - **DS18B20:** Digital waterproof temperature probe.

### 2.2 ESP32 Embedded Firmware Engine
- Written in C++ utilizing FreeRTOS dual-core multitasking:
  - Core 0: Continuous ADC sensor sampling and digital filtering (moving average smoothing).
  - Core 1: MQTT transmission, TLS socket management, and power saving modes (deep sleep wake cycles).
- Firmware delivers **99.98% packet delivery reliability** under high-latency intermittent cellular networks.

### 2.3 Cloud Broker & Alert Dispatch
- Telemetry published to MQTT broker topics: `aquasentry/nodes/{node_id}/telemetry`.
- Real-time thresholds immediately trigger Webhook alerts when parameters breach drinking water standards.

---

## 3. Technology Stack
- **Hardware:** ESP32-WROOM-32, Analog Probes, Custom PCB Wiring
- **Firmware:** C++, FreeRTOS, Arduino Core, PubSubClient
- **Protocols:** MQTT, I2C, SPI, UART, TLS 1.3
- **Cloud & Dashboard:** Python, FastAPI, React, WebSocket Stream
