# PawPal AI // System Architecture Specification
**Class:** `PSYCHIC / NEURAL` • **Domain:** Multi-Modal Pet Healthcare Diagnostics  
**Architect:** Parameshwaran S (Parama) • **Status:** Active Production Prototype

---

## 1. System Overview
PawPal AI is an intelligent computer vision and multimodal diagnostic triage pipeline designed to empower pet owners with immediate preliminary health assessments, automated dietary planning, and interactive 3D anatomical visualization of pet conditions.

```
[ User Mobile Camera / Upload ]
                │
                ▼
      [ Computer Vision Ingestion ]
      (Resolution Normalization & Feature Extraction)
                │
                ▼
   [ Google Gemini Vision API Gateway ]
   (Contextual Prompt Engineering & Multi-Modal Diagnostics)
                │
                ├──► [ Preliminary Triage & Symptom Assessment ]
                ├──► [ Autonomous Dietary Formulation ]
                └──► [ Three.js WebGL 3D Anatomical Mapping ]
```

---

## 2. Core Technical Architecture

### 2.1 Multimodal Ingestion Pipeline
- Processes high-resolution canine/feline images through an automated preprocessing pipeline (OpenCV) to normalize color channels, white balance, and zoom on symptomatic areas (skin, eyes, limbs).
- Packages image payloads into optimized base64 byte streams for the Gemini Vision API gateway.

### 2.2 Neural Inference Engine
- Employs tailored veterinary system prompts that enforce structured JSON output:
  - Symptom identification and severity tier (Mild, Moderate, Critical).
  - Recommended first-aid measures.
  - Contraindicated foods and suggested nutritional regimen.
- Latency: **Sub-50ms** end-to-end inference across Google Cloud infrastructure.

### 2.3 Interactive 3D Anatomy Mapping
- Utilizes **Three.js** to render a real-time, rotatable 3D anatomical model of a canine/feline skeleton and muscular structure.
- Dynamically highlights affected body zones in glowing neon shaders based on the Gemini triage response.

---

## 3. Technology Stack
- **AI & Vision:** Google Gemini API (Multimodal), OpenCV, Python 3.11
- **Backend API:** Flask / FastAPI, Gunicorn, RESTful endpoints
- **Interactive UI:** Three.js (WebGL), React.js, TailwindCSS
- **Deployment:** Docker, Google Cloud Run
