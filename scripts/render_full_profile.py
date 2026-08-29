#!/usr/bin/env python3
"""
Full Profile SVG Generator
==========================
Generates the ENTIRE GitHub profile as a single animated Pokemon game interface.
Everything - About Me, Tech Stack, Projects, Stats - lives inside one SVG
with CSS animations. No JavaScript, no SMIL.

The profile becomes a Pokemon game menu screen.
"""

import os
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_api import get_contribution_data
from pokemon_data import (
    get_player_pokemon,
    get_player_level,
    get_enemy_pokemon,
    get_sprite_url,
    get_attack_name,
    PLAYER_TYPES,
    EVOLUTION_THRESHOLDS,
    MAX_CONTRIBUTIONS,
    HP_BAR_SEGMENTS,
    PLAYER_MAX_HP,
    DEFAULT_CHAIN_INDEX,
    ENEMY_LEVELS,
)


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
C = {
    "bg": "#0D1117",
    "card": "#161B22",
    "border": "#30363D",
    "accent": "#00ff66",
    "text": "#C9D1D9",
    "dim": "#8B949E",
    "hp": "#00ff66",
    "hp_mid": "#FFC107",
    "hp_low": "#FF4444",
    "empty": "#21262D",
    "blue": "#3B82F6",
    "purple": "#8B5CF6",
    "red": "#FF4444",
    "yellow": "#FFC107",
}


def hp_color(r):
    if r > 0.5: return C["hp"]
    if r > 0.25: return C["hp_mid"]
    return C["hp_low"]


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = """<style>
text{font-family:'Segoe UI','SF Pro Display',-apple-system,sans-serif}

/* Flash */
@keyframes fl{0%,100%{opacity:0}4%{opacity:.8}8%{opacity:.05}12%{opacity:.75}16%{opacity:0}}
.fl{animation:fl 6s ease-in-out infinite}

/* HP glow */
@keyframes hg{0%,100%{filter:brightness(1) drop-shadow(0 0 2px currentColor)}50%{filter:brightness(1.4) drop-shadow(0 0 8px currentColor)}}
.hg{animation:hg 1.8s ease-in-out infinite}

/* Attack pulse */
@keyframes ap{0%,100%{opacity:.7;transform:scale(1)}50%{opacity:1;transform:scale(1.06)}}
.ap{animation:ap 1.5s ease-in-out infinite;transform-origin:center}

/* Enemy blink */
@keyframes eb{0%,87%,100%{opacity:1}89%{opacity:.15}91%{opacity:1}93%{opacity:.25}95%{opacity:1}}
.eb{animation:eb 4s ease-in-out infinite}

/* Player float */
@keyframes pf{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.pf{animation:pf 2.5s ease-in-out infinite}

/* Title flicker */
@keyframes tf{0%,89%,100%{opacity:1}91%{opacity:.25}93%{opacity:1}95%{opacity:.4}97%{opacity:1}}
.tf{animation:tf 3s ease-in-out infinite}

/* EXP glow */
@keyframes eg{0%,100%{opacity:.5}50%{opacity:1}}
.eg{animation:eg 2s ease-in-out infinite}

/* VS bounce */
@keyframes vb{0%,100%{transform:scale(1);opacity:.8}50%{transform:scale(1.15);opacity:1}}
.vb{animation:vb 2s ease-in-out infinite;transform-origin:center}

/* Floating particles */
@keyframes a1{0%{transform:translate(0,0);opacity:0}8%{opacity:.7}100%{transform:translate(-30px,-50px);opacity:0}}
@keyframes a2{0%{transform:translate(0,0);opacity:0}8%{opacity:.6}100%{transform:translate(35px,-45px);opacity:0}}
@keyframes a3{0%{transform:translate(0,0);opacity:0}8%{opacity:.5}100%{transform:translate(-20px,-55px);opacity:0}}
@keyframes a4{0%{transform:translate(0,0);opacity:0}8%{opacity:.5}100%{transform:translate(25px,-40px);opacity:0}}
@keyframes a5{0%{transform:translate(0,0);opacity:0}8%{opacity:.6}100%{transform:translate(-15px,-60px);opacity:0}}
@keyframes a6{0%{transform:translate(0,0);opacity:0}8%{opacity:.4}100%{transform:translate(40px,-35px);opacity:0}}
.pt1{animation:a1 3s ease-out infinite}
.pt2{animation:a2 3.5s ease-out .4s infinite}
.pt3{animation:a3 4s ease-out .8s infinite}
.pt4{animation:a4 3.2s ease-out 1.2s infinite}
.pt5{animation:a5 3.8s ease-out .6s infinite}
.pt6{animation:a6 3.3s ease-out 1s infinite}

/* Damage float */
@keyframes df{0%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(-30px)}}
.df{animation:df 2.5s ease-out infinite}

/* Pokeball spin */
@keyframes ps{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
.ps{animation:ps 10s linear infinite;transform-origin:center}

/* Stat glow */
@keyframes sg{0%,100%{text-shadow:0 0 4px currentColor}50%{text-shadow:0 0 14px currentColor}}
.sg{animation:sg 3s ease-in-out infinite}

/* Section reveal */
@keyframes sr{0%{opacity:0;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}
.sr{animation:sr .6s ease-out forwards;opacity:0}
.sr1{animation-delay:.1s} .sr2{animation-delay:.2s} .sr3{animation-delay:.3s}
.sr4{animation-delay:.4s} .sr5{animation-delay:.5s} .sr6{animation-delay:.6s}

/* Scanline overlay */
@keyframes scan{0%{transform:translateY(-100%)}100%{transform:translateY(100%)}}
.scanline{animation:scan 8s linear infinite;opacity:.03}

/* Border pulse */
@keyframes bp{0%,100%{stroke-opacity:.3}50%{stroke-opacity:.7}}
.bp{animation:bp 4s ease-in-out infinite}

/* Typing cursor */
@keyframes cursor{0%,100%{opacity:1}50%{opacity:0}}
.cursor{animation:cursor 1s step-end infinite}
</style>"""


def build_svg(username, contrib_data, enemy_species, enemy_level,
              player_species, player_level, total, today, repos):
    """Build the entire profile as one animated SVG."""

    hp_ratio = round(max(0, 1.0 - (total / MAX_CONTRIBUTIONS)), 2)
    hp_filled = max(0, round(hp_ratio * HP_BAR_SEGMENTS))
    hp_val = hp_filled * (MAX_CONTRIBUTIONS // HP_BAR_SEGMENTS)
    player_hp = min(total, PLAYER_MAX_HP)
    p_filled = max(1, round((player_hp / PLAYER_MAX_HP) * HP_BAR_SEGMENTS))

    poke_type = PLAYER_TYPES.get(player_species, "Electric")
    attack = get_attack_name(poke_type)

    enemy_sprite = get_sprite_url(enemy_species)
    player_sprite = get_sprite_url(player_species)
    enemy_name = enemy_species.replace("-", " ").title()
    player_name = player_species.replace("-", " ").title()

    # EXP bar
    exp_pct = 0
    for i, th in enumerate(EVOLUTION_THRESHOLDS):
        if total < th:
            if i > 0:
                exp_pct = (total - EVOLUTION_THRESHOLDS[i-1]) / (th - EVOLUTION_THRESHOLDS[i-1])
            break
    else:
        exp_pct = 1.0
    exp_w = int(exp_pct * 160)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build HP pip strings
    enemy_pips = []
    for i in range(HP_BAR_SEGMENTS):
        x = 220 + i * 15
        fill = hp_color(hp_ratio) if i < hp_filled else C["empty"]
        cls = ' class="hg"' if i < hp_filled else ""
        enemy_pips.append(f'<rect x="{x}" y="118" width="13" height="11" rx="2" fill="{fill}"{cls}/>')

    player_pips = []
    for i in range(HP_BAR_SEGMENTS):
        x = 220 + i * 15
        fill = C["blue"] if i < p_filled else C["empty"]
        cls = ' class="hg"' if i < p_filled else ""
        player_pips.append(f'<rect x="{x}" y="270" width="13" height="11" rx="2" fill="{fill}"{cls}/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 1350" width="600" height="1350">
{CSS}

<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{C['border']}" stroke-width=".3" opacity=".15"/>
  </pattern>
  <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{C['accent']}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{C['accent']}" stop-opacity=".15"/>
    <stop offset="100%" stop-color="{C['accent']}" stop-opacity="0"/>
  </linearGradient>
  <filter id="sh"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>

<!-- BG -->
<rect width="600" height="1350" rx="12" fill="{C['bg']}"/>
<rect width="600" height="1350" rx="12" fill="url(#grid)"/>
<rect x="14" y="2" width="572" height="2.5" rx="1" fill="{C['accent']}" opacity=".5"/>
<circle cx="18" cy="10" r="3" fill="{C['accent']}" opacity=".35"/>
<circle cx="582" cy="10" r="3" fill="{C['accent']}" opacity=".35"/>

<!-- Scanline effect -->
<rect width="600" height="40" fill="white" class="scanline" pointer-events="none"/>

<!-- Flash overlay -->
<rect width="600" height="1350" rx="12" fill="{C['yellow']}" opacity="0" class="fl" pointer-events="none"/>

<!-- ===================== HEADER ===================== -->
<text x="300" y="50" text-anchor="middle" font-size="22" font-weight="bold" fill="{C['accent']}" class="tf" filter="url(#sh)">
  ⚔️ RAID BOSS ENCOUNTER
</text>
<text x="300" y="72" text-anchor="middle" font-size="12" fill="{C['dim']}">
  Real-time GitHub commit telemetry fuels combat strikes
</text>

<!-- ===================== BATTLE SCENE ===================== -->
<!-- Enemy -->
<g class="eb">
  <image x="30" y="82" width="150" height="150" href="{enemy_sprite}" preserveAspectRatio="xMidYMid meet"/>
</g>
<text x="190" y="110" font-size="20" font-weight="bold" fill="{C['text']}">{enemy_name}</text>
<text x="{195 + len(enemy_name) * 12}" y="110" font-size="14" fill="{C['dim']}"> Lv.{enemy_level}</text>
<text x="190" y="128" font-size="11" fill="{C['dim']}">HP {hp_val}/{MAX_CONTRIBUTIONS}</text>
{"".join(enemy_pips)}

<!-- Damage float -->
<text x="105" y="100" font-size="16" font-weight="bold" fill="{C['hp_low']}" class="df" opacity=".9">-1</text>

<!-- VS -->
<line x1="300" y1="155" x2="300" y2="185" stroke="{C['border']}" stroke-width="1" opacity=".35"/>
<text x="300" y="210" text-anchor="middle" font-size="28" font-weight="bold" fill="{C['accent']}" class="vb" filter="url(#sh)">VS</text>
<line x1="300" y1="220" x2="300" y2="240" stroke="{C['border']}" stroke-width="1" opacity=".35"/>

<!-- Player -->
<g class="pf">
  <image x="30" y="240" width="150" height="150" href="{player_sprite}" preserveAspectRatio="xMidYMid meet"/>
</g>
<text x="190" y="260" font-size="20" font-weight="bold" fill="{C['text']}">{player_name}</text>
<text x="{195 + len(player_name) * 12}" y="260" font-size="14" fill="{C['dim']}"> Lv.{player_level}</text>
<text x="190" y="278" font-size="11" fill="{C['dim']}">HP {player_hp}/{PLAYER_MAX_HP}</text>
{"".join(player_pips)}

<!-- Attack -->
<text x="190" y="312" font-size="12" fill="{C['dim']}">Last Attack:</text>
<text x="190" y="334" font-size="17" font-weight="bold" fill="{C['accent']}" class="ap" filter="url(#sh)">{attack}</text>

<!-- EXP -->
<text x="190" y="360" font-size="10" fill="{C['dim']}">EXP to next tier</text>
<rect x="190" y="368" width="160" height="7" rx="3.5" fill="{C['empty']}"/>
<rect x="190" y="368" width="{exp_w}" height="7" rx="3.5" fill="{C['purple']}" class="eg"/>

<!-- ===================== STATS BAR ===================== -->
<rect x="20" y="405" width="560" height="1" fill="{C['border']}" opacity=".3"/>

<text x="50" y="430" font-size="11" fill="{C['dim']}">Commits Today</text>
<text x="50" y="458" font-size="30" font-weight="bold" fill="{C['accent']}" class="sg">{today}</text>

<text x="200" y="430" font-size="11" fill="{C['dim']}">Total (365d)</text>
<text x="200" y="458" font-size="30" font-weight="bold" fill="{C['text']}" class="sg">{total}</text>

<text x="360" y="430" font-size="11" fill="{C['dim']}">Repos</text>
<text x="360" y="458" font-size="30" font-weight="bold" fill="{C['text']}" class="sg">{repos}</text>

<text x="560" y="458" text-anchor="end" font-size="14" font-weight="bold" fill="{C['accent']}" opacity=".45">@{username}</text>

<!-- ===================== DIVIDER ===================== -->
<g class="ps">
  <polygon points="300,482 308,490 300,498 292,490" fill="none" stroke="{C['accent']}" stroke-width="1.5" opacity=".5"/>
  <circle cx="300" cy="490" r="2.5" fill="{C['accent']}" opacity=".7"/>
</g>

<!-- ===================== ABOUT ME ===================== -->
<text x="30" y="540" font-size="18" font-weight="bold" fill="{C['accent']}" class="sr sr1">
  About Me
</text>
<rect x="30" y="548" width="60" height="2" rx="1" fill="{C['accent']}" opacity=".4" class="sr sr1"/>

<text x="30" y="575" font-size="12" fill="{C['text']}" class="sr sr2">
  Engineering student passionate about AI, Data Science, and Full Stack Dev.
</text>
<text x="30" y="595" font-size="12" fill="{C['text']}" class="sr sr2">
  Building products beyond classroom projects - from AI assistants to web apps.
</text>

<text x="30" y="625" font-size="11" fill="{C['dim']}" class="sr sr2">Currently focusing on:</text>
<text x="30" y="645" font-size="12" fill="{C['text']}" class="sr sr3">  Artificial Intelligence</text>
<text x="30" y="663" font-size="12" fill="{C['text']}" class="sr sr3">  Data Science &amp; Machine Learning</text>
<text x="30" y="681" font-size="12" fill="{C['text']}" class="sr sr3">  Full Stack Web Development</text>
<text x="30" y="699" font-size="12" fill="{C['text']}" class="sr sr3">  Open Source &amp; Hackathons</text>

<!-- ===================== TECH STACK ===================== -->
<text x="30" y="740" font-size="18" font-weight="bold" fill="{C['accent']}" class="sr sr3">
  Tech Stack
</text>
<rect x="30" y="748" width="60" height="2" rx="1" fill="{C['accent']}" opacity=".4" class="sr sr3"/>

<text x="30" y="775" font-size="11" fill="{C['dim']}">Languages</text>
<text x="30" y="795" font-size="12" fill="{C['text']}" class="sr sr4">Python  JavaScript  TypeScript  SQL  C</text>

<text x="30" y="820" font-size="11" fill="{C['dim']}">Frontend</text>
<text x="30" y="840" font-size="12" fill="{C['text']}" class="sr sr4">React  Next.js  HTML5  CSS3  TailwindCSS</text>

<text x="30" y="865" font-size="11" fill="{C['dim']}">Backend</text>
<text x="30" y="885" font-size="12" fill="{C['text']}" class="sr sr4">Django  Flask  Node.js</text>

<text x="30" y="910" font-size="11" fill="{C['dim']}">AI &amp; Data Science</text>
<text x="30" y="930" font-size="12" fill="{C['text']}" class="sr sr4">Pandas  NumPy  Scikit Learn  OpenCV</text>

<text x="30" y="955" font-size="11" fill="{C['dim']}">Tools</text>
<text x="30" y="975" font-size="12" fill="{C['text']}" class="sr sr4">Git  GitHub  Linux  VS Code</text>

<!-- ===================== PROJECTS ===================== -->
<text x="30" y="1015" font-size="18" font-weight="bold" fill="{C['accent']}" class="sr sr5">
  Featured Projects
</text>
<rect x="30" y="1023" width="60" height="2" rx="1" fill="{C['accent']}" opacity=".4" class="sr sr5"/>

<!-- Project 1 -->
<rect x="30" y="1040" width="540" height="55" rx="8" fill="{C['card']}" stroke="{C['border']}" stroke-width="1" opacity=".8"/>
<text x="50" y="1060" font-size="13" font-weight="bold" fill="{C['accent']}" class="sr sr5">PawPal AI</text>
<text x="50" y="1078" font-size="11" fill="{C['text']}">AI-powered pet health tracking &amp; symptom analysis</text>
<text x="50" y="1092" font-size="10" fill="{C['dim']}">Python  Gemini AI  Flask  Three.js</text>

<!-- Project 2 -->
<rect x="30" y="1105" width="540" height="55" rx="8" fill="{C['card']}" stroke="{C['border']}" stroke-width="1" opacity=".8"/>
<text x="50" y="1125" font-size="13" font-weight="bold" fill="{C['accent']}" class="sr sr5">Smart Parking System</text>
<text x="50" y="1143" font-size="11" fill="{C['text']}">Full-stack parking management with analytics</text>
<text x="50" y="1157" font-size="10" fill="{C['dim']}">Django  MySQL  JavaScript</text>

<!-- Project 3 -->
<rect x="30" y="1170" width="540" height="55" rx="8" fill="{C['card']}" stroke="{C['border']}" stroke-width="1" opacity=".8"/>
<text x="50" y="1190" font-size="13" font-weight="bold" fill="{C['accent']}" class="sr sr5">BusIt</text>
<text x="50" y="1208" font-size="11" fill="{C['text']}">Smart college bus tracking with live GPS &amp; ETA</text>
<text x="50" y="1222" font-size="10" fill="{C['dim']}">React  Firebase  Google Maps</text>

<!-- Project 4 -->
<rect x="30" y="1235" width="540" height="55" rx="8" fill="{C['card']}" stroke="{C['border']}" stroke-width="1" opacity=".8"/>
<text x="50" y="1255" font-size="13" font-weight="bold" fill="{C['accent']}" class="sr sr5">AquaSentry</text>
<text x="50" y="1273" font-size="11" fill="{C['text']}">IoT water quality monitoring for rural regions</text>
<text x="50" y="1287" font-size="10" fill="{C['dim']}">ESP32  Sensors  AI  IoT</text>

<!-- ===================== FOOTER ===================== -->
<rect x="20" y="1310" width="560" height="1" fill="{C['border']}" opacity=".25"/>
<text x="300" y="1335" text-anchor="middle" font-size="10" fill="{C['dim']}" opacity=".4">
  Live Combat Telemetry HUD | Updated {now}
</text>

<!-- Particles -->
<circle cx="30" cy="200" r="2.5" fill="{C['accent']}" opacity="0" class="pt1"/>
<circle cx="570" cy="180" r="2" fill="{C['blue']}" opacity="0" class="pt2"/>
<circle cx="300" cy="500" r="3" fill="{C['purple']}" opacity="0" class="pt3"/>
<circle cx="80" cy="1000" r="2" fill="{C['yellow']}" opacity="0" class="pt4"/>
<circle cx="520" cy="950" r="2.5" fill="{C['accent']}" opacity="0" class="pt5"/>
<circle cx="200" cy="1300" r="2" fill="{C['blue']}" opacity="0" class="pt6"/>
<circle cx="450" cy="400" r="1.5" fill="{C['hp_low']}" opacity="0" class="pt1"/>
<circle cx="150" cy="750" r="2" fill="{C['accent']}" opacity="0" class="pt3"/>

</svg>"""

    return svg


def main():
    username = os.environ.get("GITHUB_USERNAME", "imnotparama")
    output_path = os.environ.get("OUTPUT_PATH", "profile.svg")

    print("=" * 50)
    print("  Full Profile SVG Generator")
    print("=" * 50)

    # Fetch data
    print("\n[1/3] Fetching GitHub data...")
    data = get_contribution_data(username)
    total = data["total_contributions"]
    today = data["contributions_today"]
    repos = data["repos_count"]

    # Pokemon selection
    print("\n[2/3] Selecting Pokemon...")
    player = get_player_pokemon(total, DEFAULT_CHAIN_INDEX)
    player_lv = get_player_level(total)
    from datetime import datetime, timezone
    day = datetime.now(timezone.utc).weekday()
    enemy = get_enemy_pokemon(day)
    import random
    enemy_lv = ENEMY_LEVELS.get(enemy, 45) + random.randint(-2, 2)

    print(f"  Player: {player.title()} Lv.{player_lv}")
    print(f"  Enemy:  {enemy.title()} Lv.{enemy_lv}")

    # Generate
    print("\n[3/3] Rendering full profile SVG...")
    svg = build_svg(username, data, enemy, enemy_lv, player, player_lv, total, today, repos)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Written to {output_path}")
    print(f"  Size: {len(svg):,} bytes")
    print("\nDone!")


if __name__ == "__main__":
    main()
