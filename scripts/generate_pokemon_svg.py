#!/usr/bin/env python3
"""
Pokemon SVG Generator
=====================
Main script that orchestrates the generation of the Pokemon battle SVG.

Workflow:
  1. Fetch contribution data from GitHub API
  2. Determine player and enemy Pokemon
  3. Calculate levels and HP
  4. Render the battle scene SVG

Usage:
  python scripts/generate_pokemon_svg.py

Environment Variables:
  GITHUB_USERNAME  - GitHub username (default: imnotparama)
  GITHUB_TOKEN     - Optional GitHub token for higher API rate limits
  OUTPUT_PATH      - Output path for the SVG (default: pokemon.svg)
"""

import os
import sys
import random
from datetime import datetime, timezone

# Ensure scripts directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_api import get_contribution_data
from pokemon_data import (
    get_player_pokemon,
    get_player_level,
    get_enemy_pokemon,
    DEFAULT_CHAIN_INDEX,
)
from renderer import render_battle_svg


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "imnotparama")
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "pokemon.svg")


def main():
    """Main entry point for the Pokemon SVG generator."""
    print("=" * 50)
    print("  Pokemon Battle SVG Generator")
    print("=" * 50)

    # Step 1: Fetch contribution data
    print("\n[1/4] Fetching GitHub data...")
    contrib_data = get_contribution_data(GITHUB_USERNAME)
    total = contrib_data["total_contributions"]
    today = contrib_data["contributions_today"]
    repos = contrib_data["repos_count"]

    # Step 2: Determine Pokemon
    print("\n[2/4] Selecting Pokemon...")
    player_species = get_player_pokemon(total, DEFAULT_CHAIN_INDEX)
    player_level = get_player_level(total)

    # Enemy rotates by day of week (Monday=0, Sunday=6)
    day_of_week = datetime.now(timezone.utc).weekday()
    enemy_species = get_enemy_pokemon(day_of_week)

    # Add a tiny bit of randomness to enemy level
    from pokemon_data import ENEMY_LEVELS
    base_level = ENEMY_LEVELS.get(enemy_species, 45)
    enemy_level = base_level + random.randint(-2, 2)

    print(f"  Player: {player_species.title()} Lv.{player_level}")
    print(f"  Enemy:  {enemy_species.title()} Lv.{enemy_level}")
    print(f"  Enemy HP ratio: {max(0, 1.0 - (total / 500)):.1%}")

    # Step 3: Calculate stats
    print("\n[3/4] Calculating battle stats...")
    hp_remaining = max(0, 500 - total)
    print(f"  Enemy HP remaining: {hp_remaining}/500")
    print(f"  Player EXP: {total} total contributions")

    # Step 4: Render SVG
    print("\n[4/4] Rendering battle scene...")
    render_battle_svg(
        enemy_species=enemy_species,
        enemy_level=enemy_level,
        player_species=player_species,
        player_level=player_level,
        total_contributions=total,
        contributions_today=today,
        repos_count=repos,
        username=GITHUB_USERNAME,
        output_path=OUTPUT_PATH,
    )

    print("\n" + "=" * 50)
    print("  Done! SVG generated successfully.")
    print(f"  Output: {OUTPUT_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()
