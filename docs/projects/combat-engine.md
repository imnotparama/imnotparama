# Autonomous Combat Engine // Serverless Telemetry Pipeline
**Class:** `DRAGON / CI-CD` • **Domain:** Serverless Pixel Simulation & Real-Time SVG Telemetry  
**Architect:** Parameshwaran S (Parama) • **Status:** Autonomous Production Pipeline

---

## 1. System Overview
The Autonomous Combat Engine is a fully autonomous serverless SVG generation pipeline that transforms continuous GitHub developer commit velocity into real-time procedural raid encounters. The pipeline executes without external servers or databases, operating completely via scheduled GitHub Actions workflows and vector SVG rendering logic.

```
[ Developer GitHub Commit Activity ]
                 │
                 ▼ (Scheduled GitHub Actions Cron - Every 6 Hours)
     [ GitHub GraphQL & Events API ]
   (Exact 365-Day Contribution Telemetry)
                 │
                 ▼
      [ Python Vector Rendering Core ]
   (Tier Scaling, HP Calculations & Sprite Base64 Packing)
                 │
                 ├──► [ Output: pokemon.svg (Live Battle Scene) ]
                 └──► [ Output: profile.svg (Full Profile Interface) ]
```

---

## 2. Core Technical Architecture

### 2.1 Serverless Data Ingestion
- Authenticates securely via ephemeral `${{ secrets.GITHUB_TOKEN }}` to fetch granular contribution counts across 365 calendar days via GitHub's GraphQL API.
- Computes exact strike power inflicted against the active raid boss, ensuring that every git commit directly impacts the live visual scene.

### 2.2 Procedural Raid Boss Rotation & Scaling
- Rotates encounter rosters on a two-week parity cycle across elite tiers:
  - Weekdays: *Gengar, Charizard, Dragonite, Tyranitar, Lucario, Rayquaza, Mewtwo*.
  - Legendary Weekends: *Ho-Oh (Saturday)* and *Lugia (Sunday)* with unique golden radial auras.
- Implements an infinite tier-scaling state machine (*Rookie ➔ Elite ➔ Champion ➔ Mega ➔ Legend*). When commit volume exceeds 500 strikes, the raid boss ascends to a higher tier with scaled HP pools.

### 2.3 Vector SVG Optimization & Animation
- Pixel-perfect retro Gen-V sprites embedded directly as lightweight base64 payloads to eliminate external image hosting dependencies.
- CSS3 keyframe animations generate fluid lightning flashes, idle player floating, and HP gauge degradation without executing client-side JavaScript.
- Enforces strict XML compliance and retina supersampling with `image-rendering: pixelated`.

---

## 3. Technology Stack
- **Engine Core:** Python 3.11, ElementTree, Base64 Encoding
- **API Ingestion:** GitHub GraphQL API v4, Requests
- **CI/CD Automation:** GitHub Actions (Cron schedule: `0 */6 * * *`)
- **Render Format:** Scalable Vector Graphics (SVG), CSS3 Animations
