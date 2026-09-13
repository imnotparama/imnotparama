"""
Pokemon Data Module
===================
Defines Pokemon species, evolution chains, enemy rosters, and sprite URLs.
All visual assets come from PokeAPI (https://pokeapi.co/).

Customization:
  - Add new Pokemon to SPRITES dict
  - Define custom evolution chains in EVOLUTION_CHAINS
  - Adjust ENEMY_ROSTER for weekly rotations
"""

from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Player Pokemon - Evolution Chains
# ---------------------------------------------------------------------------
# Each chain is ordered from base form to final evolution.
# The player's Pokemon evolves based on total contributions.

EVOLUTION_CHAINS = [
    ["bulbasaur", "ivysaur", "venusaur", "venusaur-mega"],
    ["charmander", "charmeleon", "charizard", "charizard-mega-x"],
    ["squirtle", "wartortle", "blastoise", "blastoise-mega"],
    ["eevee", "vaporeon", "jolteon", "flareon"],
    ["ralts", "kirlia", "gardevoir", "gardevoir-mega"],
]

# Evolution thresholds (total contributions in the last year)
# Index 0 = base form, index 1 = first evolution, etc.
EVOLUTION_THRESHOLDS = [0, 100, 300, 700]

# Starting chain index (which starter evolution line)
DEFAULT_CHAIN_INDEX = 0  # Grass starter (Bulbasaur line)

# ---------------------------------------------------------------------------
# Enemy Pokemon - Weekly Rotation
# ---------------------------------------------------------------------------
# 7 enemies that rotate daily (one per day of the week)

ENEMY_ROSTER = [
    "gengar",
    "charizard",
    "dragonite",
    "tyranitar",
    "lucario",
    "rayquaza",
    "mewtwo",
]

ENEMY_LEVELS = {
    "gengar": 42,
    "charizard": 45,
    "dragonite": 50,
    "tyranitar": 48,
    "lucario": 43,
    "rayquaza": 70,
    "mewtwo": 80,
    "ho-oh": 72,
    "lugia": 78,
}

# ---------------------------------------------------------------------------
# Enemy Type Effectiveness (for attack text flavor)
# ---------------------------------------------------------------------------
ENEMY_TYPES = {
    "gengar": "Ghost/Poison",
    "charizard": "Fire/Flying",
    "dragonite": "Dragon/Flying",
    "tyranitar": "Rock/Dark",
    "lucario": "Fighting/Steel",
    "rayquaza": "Dragon/Flying",
    "mewtwo": "Psychic",
    "ho-oh": "Fire/Flying",
    "lugia": "Psychic/Flying",
}

# ---------------------------------------------------------------------------
# Boss Tier System - the raid never ends
# ---------------------------------------------------------------------------
# Every commit milestone the trainer crosses summons a NEW boss with a
# bigger max-HP pool. The arena never goes stale, no matter how active
# the trainer becomes.

BOSS_TIERS = [
    {"threshold": 0,    "max_hp": 500,   "title": "ROOKIE RAID"},
    {"threshold": 500,  "max_hp": 1000,  "title": "ELITE RAID"},
    {"threshold": 1500, "max_hp": 2000,  "title": "CHAMPION RAID"},
    {"threshold": 3000, "max_hp": 3500,  "title": "MEGA RAID"},
    {"threshold": 5000, "max_hp": 6000,  "title": "LEGEND RAID"},
]

# Signature species-specific attacks (checked before type-based lookup)
SPECIES_ATTACKS = {
    "ho-oh": "Sacred Fire \U0001F525",
    "lugia": "Aeroblast \U0001F32A",
}

# Legendary raids that only appear on weekends
WEEKEND_RAIDS = {5: "ho-oh", 6: "lugia"}  # 5=Saturday, 6=Sunday

# Player Pokemon default type (overridden by evolution)
PLAYER_TYPE_DEFAULT = "Electric"

PLAYER_TYPES = {
    "bulbasaur": "Grass/Poison",
    "ivysaur": "Grass/Poison",
    "venusaur": "Grass/Poison",
    "venusaur-mega": "Grass/Poison",
    "charmander": "Fire",
    "charmeleon": "Fire",
    "charizard": "Fire/Flying",
    "charizard-mega-x": "Fire/Dragon",
    "squirtle": "Water",
    "wartortle": "Water",
    "blastoise": "Water",
    "blastoise-mega": "Water",
    "eevee": "Normal",
    "vaporeon": "Water",
    "jolteon": "Electric",
    "flareon": "Fire",
    "ralts": "Psychic/Fairy",
    "kirlia": "Psychic/Fairy",
    "gardevoir": "Psychic/Fairy",
    "gardevoir-mega": "Psychic/Fairy",
    "pikachu": "Electric",
}

# ---------------------------------------------------------------------------
# Sprite URLs (PokeAPI official artwork)
# ---------------------------------------------------------------------------
SPRITES = {
    # Player evolutions - Grass
    "bulbasaur": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png",
    "ivysaur": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/2.png",
    "venusaur": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/3.png",
    "venusaur-mega": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/3-mega.png",
    # Player evolutions - Fire
    "charmander": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png",
    "charmeleon": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/5.png",
    "charizard": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png",
    "charizard-mega-x": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6-mega-x.png",
    # Player evolutions - Water
    "squirtle": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png",
    "wartortle": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/8.png",
    "blastoise": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9.png",
    "blastoise-mega": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9-mega.png",
    # Player evolutions - Eevee
    "eevee": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png",
    "vaporeon": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/134.png",
    "jolteon": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/135.png",
    "flareon": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/136.png",
    # Player evolutions - Ralts
    "ralts": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/280.png",
    "kirlia": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/281.png",
    "gardevoir": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/282.png",
    "gardevoir-mega": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/282.png",
    # Player default
    "pikachu": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
    # Enemies
    "gengar": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png",
    "charizard": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png",
    "dragonite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/149.png",
    "tyranitar": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/248.png",
    "lucario": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/448.png",
    "rayquaza": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/384.png",
    "mewtwo": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
    "ho-oh": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png",
    "lugia": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png",
}

# ---------------------------------------------------------------------------
# Battle Configuration
# ---------------------------------------------------------------------------
MAX_CONTRIBUTIONS = 500          # Full HP bar at this count
HP_BAR_SEGMENTS = 20             # Number of HP pips in the bar
PLAYER_MAX_HP = 100              # Player's max HP (display only)

# ---------------------------------------------------------------------------
# Attack Names (flavor text)
# ---------------------------------------------------------------------------
ATTACKS = {
    "Electric": "Thunderbolt ⚡",
    "Grass/Poison": "Solar Beam 🌿",
    "Fire/Flying": "Flamethrower 🔥",
    "Fire/Dragon": "Dragon Claw 🔥",
    "Fire": "Flamethrower 🔥",
    "Water": "Hydro Pump 💧",
    "Normal": "Body Slam 💫",
    "Psychic/Fairy": "Psychic 💜",
    "Dragon/Flying": "Dragon Pulse 🐉",
}

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_player_pokemon(total_contributions: int, chain_index: int = DEFAULT_CHAIN_INDEX) -> str:
    """
    Determine the player's current Pokemon based on total contributions
    and which evolution chain they're on.

    Args:
        total_contributions: Total contributions in the last 365 days
        chain_index: Which evolution chain (0=Grass, 1=Fire, etc.)

    Returns:
        Pokemon species name (e.g., "venusaur")
    """
    chain = EVOLUTION_CHAINS[chain_index % len(EVOLUTION_CHAINS)]
    pokemon = chain[0]

    for i, threshold in enumerate(EVOLUTION_THRESHOLDS):
        if total_contributions >= threshold:
            pokemon = chain[min(i, len(chain) - 1)]

    return pokemon


def get_player_level(total_contributions: int) -> int:
    """
    Calculate player level based on total contributions.
    Scale: 0 contributions = Lv.5, 500+ = Lv.100

    Args:
        total_contributions: Total contributions in the last 365 days

    Returns:
        Integer level between 5 and 100
    """
    if total_contributions <= 0:
        return 5
    level = min(5 + int(total_contributions * 95 / MAX_CONTRIBUTIONS), 100)
    return max(5, level)


def get_enemy_pokemon(day_of_week: int, day_of_year: int = None) -> str:
    """
    Select the enemy Pokemon. Weekends summon exclusive legendary raids
    (Ho-Oh on Saturday, Lugia on Sunday). Weekdays rotate through the full
    7-species roster on a two-week parity cycle so every boss stays visible
    even though weekends are reserved.

    Args:
        day_of_week: 0=Monday, 6=Sunday
        day_of_year: Optional day-of-year override for deterministic tests

    Returns:
        Enemy Pokemon species name
    """
    weekend = WEEKEND_RAIDS.get(day_of_week)
    if weekend:
        return weekend

    if day_of_year is None:
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    week_parity = (day_of_year // 7) % 2
    return ENEMY_ROSTER[(day_of_week + 7 * week_parity) % len(ENEMY_ROSTER)]


def get_boss_tier(total_contributions: int) -> dict:
    """
    Resolve the active boss tier for the trainer's lifetime commit count.
    Higher tiers summon bosses with bigger max-HP pools, so the HP bar
    never flatlines at zero.

    Args:
        total_contributions: Total contributions in the last 365 days

    Returns:
        Dict with keys: threshold, max_hp, title
    """
    tier = BOSS_TIERS[0]
    for t in BOSS_TIERS:
        if total_contributions >= t["threshold"]:
            tier = t
    return tier


def is_weekend_raid(day_of_week: int) -> bool:
    """True when the given weekday summons a legendary weekend raid boss."""
    return day_of_week in WEEKEND_RAIDS


_sprite_cache = None


def _load_sprite_cache():
    """Load base64 sprite data from sprite_data.json (downloaded by download_sprites.py)."""
    global _sprite_cache
    if _sprite_cache is not None:
        return _sprite_cache

    import json as _json
    import os as _os

    data_path = _os.path.join(_os.path.dirname(__file__), "sprite_data.json")
    try:
        with open(data_path, "r") as f:
            _sprite_cache = _json.load(f)
    except FileNotFoundError:
        print("  [WARN] sprite_data.json not found, using URLs")
        _sprite_cache = {}
    return _sprite_cache


def get_sprite_url(species: str) -> str:
    """
    Get the Pokemon sprite. Returns base64 data URI if available,
    otherwise falls back to the PokeAPI URL.

    Args:
        species: Pokemon species name

    Returns:
        Base64 data URI or URL to the Pokemon's sprite image
    """
    cache = _load_sprite_cache()
    if species in cache:
        return cache[species]
    # Fallback to base form if mega not available
    if "-mega" in species:
        base = species.split("-")[0]
        if base in cache:
            return cache[base]
    return cache.get("pikachu", SPRITES.get(species, SPRITES["pikachu"]))


def get_attack_name(pokemon_type: str, species: str = "") -> str:
    """
    Get a themed attack name. Signature species attacks take priority,
    then type-based lookup.

    Args:
        pokemon_type: Pokemon type string (e.g., "Electric")
        species: Optional species name for signature moves (e.g., "ho-oh")

    Returns:
        Attack name with emoji
    """
    if species and species in SPECIES_ATTACKS:
        return SPECIES_ATTACKS[species]
    return ATTACKS.get(pokemon_type, "Tackle 💫")
