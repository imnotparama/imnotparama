"""
SVG Renderer Module
===================
Renders the Pokemon battle scene as an SVG with CSS animations.

All animations use CSS @keyframes - no JavaScript, no SMIL.
GitHub blocks JS in README SVGs, so CSS-only is mandatory.

Design:
  - Dark theme (#0D1117 background)
  - Green accent (#00ff66)
  - Pokemon official artwork embedded as base64
  - HP bar as segmented pips (contribution graph = enemy HP)
  - Battle-style layout with VS divider
  - Heavy CSS animations for a living battle feel
"""

from datetime import datetime, timezone

from pokemon_data import (
    MAX_CONTRIBUTIONS,
    HP_BAR_SEGMENTS,
    PLAYER_MAX_HP,
    get_sprite_url,
    get_attack_name,
)


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0D1117",
    "border": "#30363D",
    "accent": "#00ff66",
    "text": "#C9D1D9",
    "text_dim": "#8B949E",
    "hp_full": "#00ff66",
    "hp_mid": "#FFC107",
    "hp_low": "#FF4444",
    "hp_empty": "#21262D",
    "player_hp": "#3B82F6",
    "exp_bar": "#8B5CF6",
    "flash": "#FFFF00",
}


def _hp_color(ratio: float) -> str:
    if ratio > 0.5:
        return COLORS["hp_full"]
    elif ratio > 0.25:
        return COLORS["hp_mid"]
    return COLORS["hp_low"]


# ---------------------------------------------------------------------------
# CSS Styles & Animations
# ---------------------------------------------------------------------------
CSS = """<style>
    text { font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif; }

    /* Lightning flash across entire scene */
    @keyframes flash {
      0%,100% { opacity:0 }
      4% { opacity:0.85 }
      8% { opacity:0.05 }
      12% { opacity:0.8 }
      16% { opacity:0 }
    }
    .flash { animation: flash 5s ease-in-out infinite; }

    /* Enemy HP bar pulsing glow */
    @keyframes hpGlow {
      0%,100% { filter: brightness(1) drop-shadow(0 0 2px currentColor); }
      50% { filter: brightness(1.4) drop-shadow(0 0 8px currentColor); }
    }
    .hp-glow { animation: hpGlow 1.8s ease-in-out infinite; }

    /* Attack text pulsing */
    @keyframes attackPulse {
      0%,100% { opacity:0.7; transform:scale(1); }
      50% { opacity:1; transform:scale(1.05); }
    }
    .attack-pulse { animation: attackPulse 1.5s ease-in-out infinite; transform-origin: center; }

    /* Enemy blink when hit */
    @keyframes enemyBlink {
      0%,88%,100% { opacity:1; }
      90% { opacity:0.2; }
      92% { opacity:1; }
      94% { opacity:0.3; }
      96% { opacity:1; }
    }
    .enemy-blink { animation: enemyBlink 4s ease-in-out infinite; }

    /* Player idle float */
    @keyframes playerFloat {
      0%,100% { transform:translateY(0); }
      50% { transform:translateY(-4px); }
    }
    .player-float { animation: playerFloat 2.5s ease-in-out infinite; }

    /* Title text flicker */
    @keyframes titleFlicker {
      0%,90%,100% { opacity:1; }
      92% { opacity:0.3; }
      94% { opacity:1; }
      96% { opacity:0.5; }
      98% { opacity:1; }
    }
    .title-flicker { animation: titleFlicker 3s ease-in-out infinite; }

    /* EXP bar glow */
    @keyframes expGlow {
      0%,100% { opacity:0.6; }
      50% { opacity:1; }
    }
    .exp-glow { animation: expGlow 2s ease-in-out infinite; }

    /* VS text bounce */
    @keyframes vsBounce {
      0%,100% { transform:scale(1); opacity:0.8; }
      50% { transform:scale(1.15); opacity:1; }
    }
    .vs-bounce { animation: vsBounce 2s ease-in-out infinite; transform-origin: center; }

    /* Floating particles - 6 unique paths */
    @keyframes p1 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.7} 100%{transform:translate(-30px,-45px);opacity:0} }
    @keyframes p2 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.6} 100%{transform:translate(35px,-40px);opacity:0} }
    @keyframes p3 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.5} 100%{transform:translate(-20px,-50px);opacity:0} }
    @keyframes p4 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.5} 100%{transform:translate(25px,-35px);opacity:0} }
    @keyframes p5 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.6} 100%{transform:translate(-15px,-55px);opacity:0} }
    @keyframes p6 { 0%{transform:translate(0,0);opacity:0} 8%{opacity:0.4} 100%{transform:translate(40px,-30px);opacity:0} }
    .p1{animation:p1 3s ease-out infinite} .p2{animation:p2 3.5s ease-out .4s infinite}
    .p3{animation:p3 4s ease-out .8s infinite} .p4{animation:p4 3.2s ease-out 1.2s infinite}
    .p5{animation:p5 3.8s ease-out .6s infinite} .p6{animation:p6 3.3s ease-out 1s infinite}

    /* Screen shake for damage */
    @keyframes shake {
      0%,100% { transform:translate(0,0); }
      10% { transform:translate(-2px,1px); }
      20% { transform:translate(2px,-1px); }
      30% { transform:translate(-1px,2px); }
      40% { transform:translate(1px,-2px); }
      50% { transform:translate(0,0); }
    }
    .shake { animation: shake 0.5s ease-in-out; }

    /* Damage number float up */
    @keyframes dmgFloat {
      0% { opacity:1; transform:translateY(0); }
      100% { opacity:0; transform:translateY(-25px); }
    }
    .dmg-float { animation: dmgFloat 2s ease-out infinite; }

    /* HP bar drain shimmer */
    @keyframes hpShimmer {
      0% { transform:translateX(-100%); }
      100% { transform:translateX(200%); }
    }

    /* Core spin */
    @keyframes coreSpin {
      0% { transform:rotate(0deg); }
      100% { transform:rotate(360deg); }
    }
    .core-spin { animation: coreSpin 8s linear infinite; transform-origin: 290px 445px; }

    /* Stat number count-up glow */
    @keyframes statGlow {
      0%,100% { text-shadow:0 0 4px currentColor; }
      50% { text-shadow:0 0 12px currentColor; }
    }
    .stat-glow { animation: statGlow 3s ease-in-out infinite; }
</style>"""


# ---------------------------------------------------------------------------
# SVG Building Blocks
# ---------------------------------------------------------------------------

def _build_background(w=580, h=520):
    return f"""
    <defs>
      <linearGradient id="pokedexChassis" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#E51B24"/>
        <stop offset="60%" stop-color="#C60813"/>
        <stop offset="100%" stop-color="#8B0007"/>
      </linearGradient>
      <linearGradient id="lensGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#00F0FF"/>
        <stop offset="60%" stop-color="#0080FF"/>
        <stop offset="100%" stop-color="#002288"/>
      </linearGradient>
      <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
        <path d="M 30 0 L 0 0 0 30" fill="none" stroke="{COLORS['border']}" stroke-width="0.3" opacity="0.18"/>
      </pattern>
      <linearGradient id="hpShimmerGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="white" stop-opacity="0"/>
        <stop offset="50%" stop-color="white" stop-opacity="0.15"/>
        <stop offset="100%" stop-color="white" stop-opacity="0"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>

    <!-- Outer Pokédex Chassis -->
    <rect width="{w}" height="{h}" rx="14" fill="url(#pokedexChassis)" stroke="#5A0005" stroke-width="2"/>

    <!-- Top Hardware Sensors -->
    <!-- Blue Scanner Lens -->
    <circle cx="34" cy="24" r="16" fill="#D9DFE5" stroke="#888F96" stroke-width="1.5"/>
    <circle cx="34" cy="24" r="12" fill="url(#lensGrad)" filter="url(#glow)"/>
    <ellipse cx="31" cy="21" rx="4" ry="2.5" fill="white" opacity="0.8" transform="rotate(-30 31 21)"/>

    <!-- Tri-Color LEDs -->
    <circle cx="64" cy="16" r="4.5" fill="#FF1744" stroke="#8B0007" stroke-width="0.8"/>
    <circle cx="63" cy="15" r="1.5" fill="white" opacity="0.7"/>
    <circle cx="78" cy="16" r="4.5" fill="#FFEA00" stroke="#8B7B00" stroke-width="0.8"/>
    <circle cx="77" cy="15" r="1.5" fill="white" opacity="0.7"/>
    <circle cx="92" cy="16" r="4.5" fill="#00E676" stroke="#00662A" stroke-width="0.8"/>
    <circle cx="91" cy="15" r="1.5" fill="white" opacity="0.7"/>

    <!-- Top Model Stamp -->
    <rect x="{w-145}" y="12" width="130" height="18" rx="4" fill="#600006" stroke="#8B0007" stroke-width="1"/>
    <text x="{w-80}" y="24" text-anchor="middle" font-size="9" font-family="'Fira Code',monospace" font-weight="bold" fill="#FFA3A8" letter-spacing="1">DEX COMBAT // v4.2</text>

    <!-- Inner LCD Screen Bezel -->
    <rect x="14" y="44" width="{w-28}" height="{h-58}" rx="10" fill="#D9DFE5" stroke="#9DA3A8" stroke-width="1.5"/>
    
    <!-- LCD Arena Screen -->
    <rect x="22" y="52" width="{w-44}" height="{h-74}" rx="6" fill="{COLORS['bg']}" stroke="#001824" stroke-width="2"/>
    <rect x="22" y="52" width="{w-44}" height="{h-74}" rx="6" fill="url(#grid)"/>

    <!-- Corner Screws -->
    <circle cx="20" cy="50" r="2.5" fill="#888F96"/>
    <circle cx="{w-20}" cy="50" r="2.5" fill="#888F96"/>
    <circle cx="20" cy="{h-18}" r="2.5" fill="#888F96"/>
    <circle cx="{w-20}" cy="{h-18}" r="2.5" fill="#888F96"/>
    """


def _build_flash(w=580, h=520):
    return f"""
    <rect x="22" y="52" width="{w-44}" height="{h-74}" rx="6" fill="{COLORS['flash']}" opacity="0" class="flash" pointer-events="none"/>
    """


def _build_header():
    return f"""
    <text x="290" y="74" text-anchor="middle" font-size="15" font-weight="bold" fill="{COLORS['accent']}" class="title-flicker" filter="url(#glow)">
      ⚔️ RAID BOSS ENCOUNTER DETECTED
    </text>
    """


def _build_enemy(species, level, hp_ratio):
    sprite = get_sprite_url(species)
    name = species.replace("-", " ").title()
    color = _hp_color(hp_ratio)
    filled = max(0, round(hp_ratio * HP_BAR_SEGMENTS))
    hp_val = filled * (MAX_CONTRIBUTIONS // HP_BAR_SEGMENTS)
    hp_text = f"{hp_val}/{MAX_CONTRIBUTIONS}"

    pips = []
    for i in range(HP_BAR_SEGMENTS):
        x = 210 + i * 15
        fill = color if i < filled else COLORS["hp_empty"]
        cls = ' class="hp-glow"' if i < filled else ""
        pips.append(f'<rect x="{x}" y="80" width="13" height="11" rx="2" fill="{fill}"{cls}/>')

    return f"""
    <!-- Enemy -->
    <g class="enemy-blink">
      <image x="30" y="55" width="140" height="140" href="{sprite}" preserveAspectRatio="xMidYMid meet"/>
    </g>
    <text x="180" y="82" font-size="19" font-weight="bold" fill="{COLORS['text']}">{name}</text>
    <text x="{185 + len(name) * 11}" y="82" font-size="14" fill="{COLORS['text_dim']}"> Lv.{level}</text>
    <text x="180" y="97" font-size="11" fill="{COLORS['text_dim']}">HP {hp_text}</text>
    {"".join(pips)}
    <!-- Damage indicator -->
    <text x="100" y="75" font-size="14" font-weight="bold" fill="{COLORS['hp_low']}" class="dmg-float" opacity="0.8">-1</text>
    """


def _build_vs():
    return f"""
    <line x1="290" y1="120" x2="290" y2="155" stroke="{COLORS['border']}" stroke-width="1" opacity="0.4"/>
    <text x="290" y="180" text-anchor="middle" font-size="26" font-weight="bold" fill="{COLORS['accent']}" class="vs-bounce" filter="url(#glow)">VS</text>
    <line x1="290" y1="190" x2="290" y2="210" stroke="{COLORS['border']}" stroke-width="1" opacity="0.4"/>
    """


def _build_player(species, level, total_contributions):
    sprite = get_sprite_url(species)
    name = species.replace("-", " ").title()
    player_hp = min(total_contributions, PLAYER_MAX_HP)
    filled = max(1, round((player_hp / PLAYER_MAX_HP) * HP_BAR_SEGMENTS))

    from pokemon_data import PLAYER_TYPES
    poke_type = PLAYER_TYPES.get(species, "Electric")
    attack = get_attack_name(poke_type)

    pips = []
    for i in range(HP_BAR_SEGMENTS):
        x = 210 + i * 15
        fill = COLORS["player_hp"] if i < filled else COLORS["hp_empty"]
        cls = ' class="hp-glow"' if i < filled else ""
        pips.append(f'<rect x="{x}" y="232" width="13" height="11" rx="2" fill="{fill}"{cls}/>')

    from pokemon_data import EVOLUTION_THRESHOLDS
    exp_pct = 0
    for i, threshold in enumerate(EVOLUTION_THRESHOLDS):
        if total_contributions < threshold:
            if i > 0:
                prev = EVOLUTION_THRESHOLDS[i - 1]
                exp_pct = (total_contributions - prev) / (threshold - prev)
            break
    else:
        exp_pct = 1.0

    exp_w = int(exp_pct * 160)

    return f"""
    <!-- Player -->
    <g class="player-float">
      <image x="30" y="210" width="140" height="140" href="{sprite}" preserveAspectRatio="xMidYMid meet"/>
    </g>
    <text x="180" y="228" font-size="19" font-weight="bold" fill="{COLORS['text']}">{name}</text>
    <text x="{185 + len(name) * 11}" y="228" font-size="14" fill="{COLORS['text_dim']}"> Lv.{level}</text>
    <text x="180" y="245" font-size="11" fill="{COLORS['text_dim']}">HP {player_hp}/{PLAYER_MAX_HP}</text>
    {"".join(pips)}

    <!-- Attack -->
    <text x="180" y="278" font-size="12" fill="{COLORS['text_dim']}">Last Strike:</text>
    <text x="180" y="298" font-size="16" font-weight="bold" fill="{COLORS['accent']}" class="attack-pulse" filter="url(#glow)">{attack}</text>

    <!-- EXP Bar -->
    <text x="180" y="322" font-size="10" fill="{COLORS['text_dim']}">EXP to next tier</text>
    <rect x="180" y="330" width="160" height="7" rx="3.5" fill="{COLORS['hp_empty']}"/>
    <rect x="180" y="330" width="{exp_w}" height="7" rx="3.5" fill="{COLORS['exp_bar']}" class="exp-glow"/>
    """


def _build_stats(total, today, repos, username):
    return f"""
    <rect x="18" y="365" width="544" height="1" fill="{COLORS['border']}" opacity="0.3"/>

    <text x="35" y="392" font-size="11" fill="{COLORS['text_dim']}">Commits Today</text>
    <text x="35" y="416" font-size="28" font-weight="bold" fill="{COLORS['accent']}" class="stat-glow">{today}</text>

    <text x="185" y="392" font-size="11" fill="{COLORS['text_dim']}">Total (365d)</text>
    <text x="185" y="416" font-size="28" font-weight="bold" fill="{COLORS['text']}" class="stat-glow">{total}</text>

    <text x="340" y="392" font-size="11" fill="{COLORS['text_dim']}">Repos</text>
    <text x="340" y="416" font-size="28" font-weight="bold" fill="{COLORS['text']}" class="stat-glow">{repos}</text>

    <text x="545" y="416" text-anchor="end" font-size="14" font-weight="bold" fill="{COLORS['accent']}" opacity="0.5">@{username}</text>
    """


def _build_pokeball():
    return f"""
    <g class="core-spin">
      <polygon points="290,437 297,445 290,453 283,445" fill="none" stroke="{COLORS['accent']}" stroke-width="1.5" opacity="0.6"/>
      <circle cx="290" cy="445" r="2.5" fill="{COLORS['accent']}" opacity="0.8"/>
    </g>
    """


def _build_footer():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""
    <text x="290" y="498" text-anchor="middle" font-size="9" fill="{COLORS['text_dim']}" opacity="0.4">
      Live Combat Simulation Engine | Updated {now}
    </text>
    """


def _build_particles():
    particles = [
        (30, 130, COLORS["accent"]),
        (550, 110, COLORS["player_hp"]),
        (290, 370, COLORS["exp_bar"]),
        (90, 420, COLORS["hp_mid"]),
        (510, 400, COLORS["accent"]),
        (200, 460, COLORS["player_hp"]),
    ]
    parts = []
    for i, (x, y, c) in enumerate(particles):
        r = 2 + (i % 3) * 0.5
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="0" class="p{i+1}"/>')
    return "\n    ".join(parts)


# ---------------------------------------------------------------------------
# Main Render
# ---------------------------------------------------------------------------

def render_battle_svg(
    enemy_species, enemy_level,
    player_species, player_level,
    total_contributions, contributions_today,
    repos_count, username,
    output_path="pokemon.svg",
):
    """Render the complete battle scene SVG."""
    w, h = 580, 540
    hp_ratio = round(max(0, 1.0 - (total_contributions / MAX_CONTRIBUTIONS)), 2)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        CSS,
        _build_background(w, h),
        _build_flash(w, h),
        _build_header(),
        _build_enemy(enemy_species, enemy_level, hp_ratio),
        _build_vs(),
        _build_player(player_species, player_level, total_contributions),
        _build_stats(total_contributions, contributions_today, repos_count, username),
        _build_pokeball(),
        _build_footer(),
        _build_particles(),
        "</svg>",
    ]

    svg = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  SVG written to {output_path}")
    return svg
