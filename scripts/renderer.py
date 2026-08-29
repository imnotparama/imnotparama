"""
SVG Renderer Module
===================
Renders the Pokemon battle scene as an SVG with CSS animations.

All animations use CSS @keyframes - no JavaScript, no SMIL.
GitHub blocks JS in README SVGs, so CSS-only is mandatory.

Design:
  - Dark theme (#0D1117 background)
  - Green accent (#00ff66)
  - Pokemon official artwork from PokeAPI
  - HP bar as segmented pips (contribution graph = enemy HP)
  - Battle-style layout with VS divider
"""

from datetime import datetime, timezone
from typing import Optional

from pokemon_data import (
    SPRITES,
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
    "bg_light": "#161B22",
    "bg_card": "#0D1117",
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
    "divider": "#30363D",
    "flash": "#FFFF00",
}


def _hp_color(ratio: float) -> str:
    """Return HP bar color based on remaining HP ratio."""
    if ratio > 0.5:
        return COLORS["hp_full"]
    elif ratio > 0.25:
        return COLORS["hp_mid"]
    return COLORS["hp_low"]


def _escape_xml(text: str) -> str:
    """Escape special characters for XML/SVG content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ---------------------------------------------------------------------------
# CSS Styles
# ---------------------------------------------------------------------------
def _build_css() -> str:
    """Build all CSS @keyframes and styles for the battle scene."""
    return """<style>
    /* === Global === */
    text { font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif; }

    /* === Lightning Flash === */
    @keyframes lightningFlash {
      0%   { opacity: 0; }
      5%   { opacity: 0.9; }
      10%  { opacity: 0.1; }
      15%  { opacity: 0.85; }
      20%  { opacity: 0; }
      100% { opacity: 0; }
    }
    .flash { animation: lightningFlash 4s ease-in-out infinite; }

    /* === HP Bar Glow === */
    @keyframes hpGlow {
      0%, 100% { filter: brightness(1) drop-shadow(0 0 2px currentColor); }
      50%      { filter: brightness(1.3) drop-shadow(0 0 6px currentColor); }
    }
    .hp-glow { animation: hpGlow 2.5s ease-in-out infinite; }

    /* === Attack Pulse === */
    @keyframes attackPulse {
      0%, 100% { opacity: 0.8; }
      50%      { opacity: 1; }
    }
    .attack-pulse { animation: attackPulse 1.8s ease-in-out infinite; }

    /* === Enemy Blink === */
    @keyframes enemyBlink {
      0%, 90%, 100% { opacity: 1; }
      95%           { opacity: 0.3; }
    }
    .enemy-blink { animation: enemyBlink 5s ease-in-out infinite; }

    /* === Player Float === */
    @keyframes playerFloat {
      0%, 100% { transform: translateY(0); }
      50%      { transform: translateY(-3px); }
    }
    .player-float { animation: playerFloat 3s ease-in-out infinite; }

    /* === Text Flicker === */
    @keyframes textFlicker {
      0%, 100% { opacity: 1; }
      92%      { opacity: 1; }
      93%      { opacity: 0.4; }
      94%      { opacity: 1; }
      96%      { opacity: 0.6; }
      97%      { opacity: 1; }
    }
    .text-flicker { animation: textFlicker 4s ease-in-out infinite; }

    /* === Exp Bar Glow === */
    @keyframes expGlow {
      0%, 100% { opacity: 0.7; }
      50%      { opacity: 1; }
    }
    .exp-glow { animation: expGlow 2s ease-in-out infinite; }

    /* === Particle Float === */
    @keyframes particleFloat1 {
      0%   { transform: translate(0, 0); opacity: 0; }
      10%  { opacity: 0.8; }
      90%  { opacity: 0.3; }
      100% { transform: translate(-25px, -35px); opacity: 0; }
    }
    @keyframes particleFloat2 {
      0%   { transform: translate(0, 0); opacity: 0; }
      10%  { opacity: 0.7; }
      90%  { opacity: 0.2; }
      100% { transform: translate(30px, -28px); opacity: 0; }
    }
    @keyframes particleFloat3 {
      0%   { transform: translate(0, 0); opacity: 0; }
      10%  { opacity: 0.6; }
      90%  { opacity: 0.2; }
      100% { transform: translate(-18px, -40px); opacity: 0; }
    }
    @keyframes particleFloat4 {
      0%   { transform: translate(0, 0); opacity: 0; }
      10%  { opacity: 0.5; }
      90%  { opacity: 0.15; }
      100% { transform: translate(22px, -32px); opacity: 0; }
    }
    .p1 { animation: particleFloat1 3.0s ease-out infinite; }
    .p2 { animation: particleFloat2 3.5s ease-out 0.5s infinite; }
    .p3 { animation: particleFloat3 4.0s ease-out 1.0s infinite; }
    .p4 { animation: particleFloat4 3.2s ease-out 1.5s infinite; }
    .p5 { animation: particleFloat1 3.8s ease-out 0.8s infinite; }
    .p6 { animation: particleFloat2 3.3s ease-out 1.2s infinite; }
    </style>"""


# ---------------------------------------------------------------------------
# SVG Building Blocks
# ---------------------------------------------------------------------------

def _build_svg_header(width: int = 580, height: int = 480) -> str:
    """SVG opening tag with dimensions and XMLNS."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">"""


def _build_background(width: int = 580, height: int = 480) -> str:
    """Background with subtle scanline texture and accent border."""
    return f"""
    <!-- Background -->
    <rect width="{width}" height="{height}" rx="10" ry="10" fill="{COLORS['bg']}"/>

    <!-- Subtle grid pattern -->
    <defs>
      <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{COLORS['border']}" stroke-width="0.3" opacity="0.25"/>
      </pattern>
    </defs>
    <rect width="{width}" height="{height}" rx="10" ry="10" fill="url(#grid)"/>

    <!-- Top accent line -->
    <rect x="12" y="1" width="{width - 24}" height="2" rx="1" fill="{COLORS['accent']}" opacity="0.7"/>

    <!-- Corner accents -->
    <circle cx="16" cy="8" r="3" fill="{COLORS['accent']}" opacity="0.5"/>
    <circle cx="{width - 16}" cy="8" r="3" fill="{COLORS['accent']}" opacity="0.5"/>
    """


def _build_lightning_flash(width: int = 580, height: int = 480) -> str:
    """Animated lightning flash overlay that plays periodically."""
    return f"""
    <!-- Lightning Flash Effect -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="10" ry="10"
          fill="{COLORS['flash']}" opacity="0" class="flash" pointer-events="none"/>
    """


def _build_header_text() -> str:
    """The 'Wild Pokemon Appeared!' header."""
    return f"""
    <!-- Header -->
    <text x="290" y="35" text-anchor="middle"
          font-size="16" font-weight="bold" fill="{COLORS['accent']}"
          class="text-flicker">
      Wild Pokemon Appeared!
    </text>
    """


def _build_enemy_section(species: str, level: int, hp_ratio: float) -> str:
    """
    Enemy Pokemon sprite, name, level, and HP bar.

    Args:
        species: Enemy Pokemon species name
        level: Enemy Pokemon level
        hp_ratio: HP remaining as 0.0-1.0 ratio
    """
    sprite_url = get_sprite_url(species)
    display_name = species.replace("-", " ").title()
    hp_color = _hp_color(hp_ratio)
    filled = max(0, round(hp_ratio * HP_BAR_SEGMENTS))
    hp_text = f"{filled * (MAX_CONTRIBUTIONS // HP_BAR_SEGMENTS)}/{MAX_CONTRIBUTIONS}"

    # Build HP pips
    pips = []
    pip_start_x = 210
    pip_y = 63
    pip_size = 13
    pip_gap = 2

    for i in range(HP_BAR_SEGMENTS):
        x = pip_start_x + i * (pip_size + pip_gap)
        if i < filled:
            pips.append(
                f'<rect x="{x}" y="{pip_y}" width="{pip_size}" height="{pip_size - 2}" '
                f'rx="2" fill="{hp_color}" class="hp-glow"/>'
            )
        else:
            pips.append(
                f'<rect x="{x}" y="{pip_y}" width="{pip_size}" height="{pip_size - 2}" '
                f'rx="2" fill="{COLORS["hp_empty"]}"/>'
            )

    pips_str = "\n      ".join(pips)

    return f"""
    <!-- Enemy Section -->
    <g class="enemy-blink">
      <image x="25" y="50" width="130" height="130" href="{sprite_url}"
             preserveAspectRatio="xMidYMid meet"/>
    </g>
    <text x="170" y="68" font-size="18" font-weight="bold" fill="{COLORS['text']}">
      {display_name}
    </text>
    <text x="{170 + len(display_name) * 11 + 5}" y="68"
          font-size="14" fill="{COLORS['text_dim']}">
       Lv.{level}
    </text>
    <text x="170" y="82" font-size="11" fill="{COLORS['text_dim']}">
      HP {hp_text}
    </text>
    <g>
      {pips_str}
    </g>
    """


def _build_vs_divider() -> str:
    """The VS divider between enemy and player sections."""
    return f"""
    <!-- VS Divider -->
    <line x1="290" y1="110" x2="290" y2="135"
          stroke="{COLORS['divider']}" stroke-width="1" opacity="0.5"/>
    <text x="290" y="155" text-anchor="middle" font-size="22" font-weight="bold"
          fill="{COLORS['accent']}" class="attack-pulse" opacity="0.9">
      VS
    </text>
    <line x1="290" y1="165" x2="290" y2="180"
          stroke="{COLORS['divider']}" stroke-width="1" opacity="0.5"/>
    """


def _build_player_section(
    species: str,
    level: int,
    total_contributions: int,
    commit_count: int,
) -> str:
    """
    Player Pokemon sprite, name, level, HP bar, attack, and stats.

    Args:
        species: Player Pokemon species name
        level: Player level
        total_contributions: Total contributions in the last year
        commit_count: Commits today
    """
    sprite_url = get_sprite_url(species)
    display_name = species.replace("-", " ").title()
    hp_color = COLORS["player_hp"]
    player_hp = min(total_contributions, PLAYER_MAX_HP)
    hp_filled = max(1, round((player_hp / PLAYER_MAX_HP) * HP_BAR_SEGMENTS))

    # Determine type for attack name
    from pokemon_data import PLAYER_TYPES
    poke_type = PLAYER_TYPES.get(species, "Electric")
    attack = get_attack_name(poke_type)

    # HP bar pips
    pips = []
    pip_start_x = 210
    pip_y = 215
    pip_size = 13
    pip_gap = 2

    for i in range(HP_BAR_SEGMENTS):
        x = pip_start_x + i * (pip_size + pip_gap)
        if i < hp_filled:
            pips.append(
                f'<rect x="{x}" y="{pip_y}" width="{pip_size}" height="{pip_size - 2}" '
                f'rx="2" fill="{hp_color}" class="hp-glow"/>'
            )
        else:
            pips.append(
                f'<rect x="{x}" y="{pip_y}" width="{pip_size}" height="{pip_size - 2}" '
                f'rx="2" fill="{COLORS["hp_empty"]}"/>'
            )

    pips_str = "\n      ".join(pips)

    # Exp bar (progress to next evolution)
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

    exp_bar_width = 160
    exp_filled_width = max(0, int(exp_pct * exp_bar_width))

    return f"""
    <!-- Player Section -->
    <g class="player-float">
      <image x="25" y="195" width="130" height="130" href="{sprite_url}"
             preserveAspectRatio="xMidYMid meet"/>
    </g>
    <text x="170" y="212" font-size="18" font-weight="bold" fill="{COLORS['text']}">
      {display_name}
    </text>
    <text x="{170 + len(display_name) * 11 + 5}" y="212"
          font-size="14" fill="{COLORS['text_dim']}">
       Lv.{level}
    </text>
    <text x="170" y="228" font-size="11" fill="{COLORS['text_dim']}">
      HP {player_hp}/{PLAYER_MAX_HP}
    </text>
    <g>
      {pips_str}
    </g>

    <!-- Attack -->
    <text x="170" y="265" font-size="12" fill="{COLORS['text_dim']}">
      Last Attack:
    </text>
    <text x="170" y="282" font-size="15" font-weight="bold" fill="{COLORS['accent']}" class="attack-pulse">
      {attack}
    </text>

    <!-- Exp Bar -->
    <text x="170" y="305" font-size="10" fill="{COLORS['text_dim']}">
      EXP to next evolution
    </text>
    <rect x="170" y="312" width="{exp_bar_width}" height="6" rx="3" fill="{COLORS['hp_empty']}"/>
    <rect x="170" y="312" width="{exp_filled_width}" height="6" rx="3"
          fill="{COLORS['exp_bar']}" class="exp-glow"/>
    """


def _build_stats_section(
    total_contributions: int,
    commit_count: int,
    repos_count: int,
    username: str,
) -> str:
    """Bottom stats bar with commit count, repos, and username."""
    return f"""
    <!-- Stats Section -->
    <rect x="15" y="340" width="550" height="1" fill="{COLORS['border']}" opacity="0.4"/>

    <!-- Commits Today -->
    <text x="30" y="370" font-size="12" fill="{COLORS['text_dim']}">
      Commits Today
    </text>
    <text x="30" y="392" font-size="26" font-weight="bold" fill="{COLORS['accent']}">
      {commit_count}
    </text>

    <!-- Total Contributions -->
    <text x="180" y="370" font-size="12" fill="{COLORS['text_dim']}">
      Total (365d)
    </text>
    <text x="180" y="392" font-size="26" font-weight="bold" fill="{COLORS['text']}">
      {total_contributions}
    </text>

    <!-- Repos -->
    <text x="340" y="370" font-size="12" fill="{COLORS['text_dim']}">
      Repos
    </text>
    <text x="340" y="392" font-size="26" font-weight="bold" fill="{COLORS['text']}">
      {repos_count}
    </text>

    <!-- Username -->
    <text x="550" y="392" text-anchor="end" font-size="14" font-weight="bold"
          fill="{COLORS['accent']}" opacity="0.6">
      @{username}
    </text>
    """


def _build_pokeball_divider() -> str:
    """Small Pokeball icon as a decorative divider."""
    return f"""
    <!-- Pokeball Divider -->
    <circle cx="290" cy="415" r="8" fill="none" stroke="{COLORS['text_dim']}" stroke-width="1.5" opacity="0.4"/>
    <line x1="282" y1="415" x2="298" y2="415" stroke="{COLORS['text_dim']}" stroke-width="1.5" opacity="0.4"/>
    <circle cx="290" cy="415" r="2.5" fill="{COLORS['text_dim']}" opacity="0.5"/>
    """


def _build_footer() -> str:
    """Footer text and timestamp."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""
    <!-- Footer -->
    <text x="290" y="445" text-anchor="middle" font-size="9" fill="{COLORS['text_dim']}" opacity="0.5">
      Pokemon Battle Profile | Updated {now}
    </text>
    """


def _build_particles(num: int = 6) -> str:
    """
    Floating particle effects for ambiance.

    Small colored circles that float upward and fade out.
    """
    colors = [COLORS["accent"], COLORS["player_hp"], COLORS["exp_bar"], COLORS["hp_mid"]]
    particles = []
    positions = [
        (25, 120), (540, 100), (290, 350),
        (80, 400), (500, 380), (200, 440),
    ]

    for i in range(min(num, len(positions))):
        x, y = positions[i]
        color = colors[i % len(colors)]
        size = 2.0 + (i % 3) * 0.5
        particles.append(
            f'<circle cx="{x}" cy="{y}" r="{size}" fill="{color}" '
            f'opacity="0" class="p{i + 1}"/>'
        )

    return "\n    ".join(particles)


# ---------------------------------------------------------------------------
# Main Render Function
# ---------------------------------------------------------------------------

def render_battle_svg(
    enemy_species: str,
    enemy_level: int,
    player_species: str,
    player_level: int,
    total_contributions: int,
    contributions_today: int,
    repos_count: int,
    username: str,
    output_path: str = "output/pokemon.svg",
) -> str:
    """
    Render the complete Pokemon battle scene SVG.

    This is the main entry point for the renderer. It assembles all
    visual components into a single SVG file with CSS animations.

    Args:
        enemy_species: Enemy Pokemon species (e.g., "gengar")
        enemy_level: Enemy Pokemon level
        player_species: Player Pokemon species (e.g., "venusaur")
        player_level: Player level
        total_contributions: Total contributions in the last year
        contributions_today: Contributions made today
        repos_count: Number of public repos
        username: GitHub username
        output_path: Path to write the SVG file

    Returns:
        The rendered SVG content as a string
    """
    width = 580
    height = 480

    # Calculate enemy HP ratio from contributions
    # More contributions = less enemy HP (you're beating them!)
    hp_ratio = max(0, 1.0 - (total_contributions / MAX_CONTRIBUTIONS))
    hp_ratio = round(hp_ratio, 2)

    # Build the SVG
    parts = [
        _build_svg_header(width, height),
        _build_css(),
        _build_background(width, height),
        _build_lightning_flash(width, height),
        _build_header_text(),
        _build_enemy_section(enemy_species, enemy_level, hp_ratio),
        _build_vs_divider(),
        _build_player_section(
            player_species,
            player_level,
            total_contributions,
            contributions_today,
        ),
        _build_stats_section(
            total_contributions,
            contributions_today,
            repos_count,
            username,
        ),
        _build_pokeball_divider(),
        _build_footer(),
        _build_particles(),
        "</svg>",
    ]

    svg_content = "\n".join(parts)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"  SVG written to {output_path}")
    return svg_content
