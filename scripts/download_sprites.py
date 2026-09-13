#!/usr/bin/env python3
"""
Sprite Downloader
=================
Downloads Pokemon sprites from PokeAPI and converts them to base64 data URIs.
Saves the mapping to a JSON file for the renderer to use.

Strategy:
  1. Try the Gen-V animated pixel GIF (~2-8 KB) - perfect retro feel, tiny weight
  2. Fall back to the static pixel sprite (~1-3 KB)
  3. Fall back to the official artwork PNG (~50-250 KB, last resort)

Usage:
  python scripts/download_sprites.py
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

# All Pokemon needed, mapped to their PokeAPI national dex ID
SPRITE_IDS = {
    # Player evolutions - Grass
    "bulbasaur": 1, "ivysaur": 2, "venusaur": 3, "venusaur-mega": 3,
    # Player evolutions - Fire
    "charmander": 4, "charmeleon": 5, "charizard": 6, "charizard-mega-x": 6,
    # Player evolutions - Water
    "squirtle": 7, "wartortle": 8, "blastoise": 9, "blastoise-mega": 9,
    # Player evolutions - Eevee
    "eevee": 133, "vaporeon": 134, "jolteon": 135, "flareon": 136,
    # Player evolutions - Ralts
    "ralts": 280, "kirlia": 281, "gardevoir": 282, "gardevoir-mega": 282,
    # Player default
    "pikachu": 25,
    # Enemies (weekday roster)
    "gengar": 94, "charizard": 6, "dragonite": 149, "tyranitar": 248,
    "lucario": 448, "rayquaza": 384, "mewtwo": 150,
    # Enemies (weekend legendary raids)
    "ho-oh": 250, "lugia": 249,
}

ANIMATED_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    "sprites/pokemon/versions/generation-v/black-white/animated/{id}.gif"
)
STATIC_PIXEL_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    "sprites/pokemon/{id}.png"
)
OFFICIAL_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    "sprites/pokemon/other/official-artwork/{id}.png"
)


def _fetch(url: str):
    """Fetch URL bytes, returning None on any failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pokemon-sprite-downloader"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"    miss ({e.__class__.__name__})")
        return None


def download_and_convert(species: str, dex_id: int):
    """Download the smallest good-looking sprite tier and return a data URI."""
    # Tier 1: animated pixel GIF (best retro look, tiny)
    for label, url in (
        ("animated", ANIMATED_URL.format(id=dex_id)),
        ("pixel", STATIC_PIXEL_URL.format(id=dex_id)),
        ("artwork", OFFICIAL_ARTWORK_URL.format(id=dex_id)),
    ):
        data = _fetch(url)
        if not data:
            continue
        mime = "image/gif" if url.endswith(".gif") else "image/png"
        b64 = base64.b64encode(data).decode("ascii")
        kb = len(data) / 1024
        print(f"  OK {species} [{label}] {kb:.1f} KB")
        return f"data:{mime};base64,{b64}"
    return None


def main():
    print("Downloading Pokemon pixel sprites...")
    output_path = os.path.join(os.path.dirname(__file__), "sprite_data.json")
    sprites = {}
    failures = []

    for species, dex_id in SPRITE_IDS.items():
        data_uri = download_and_convert(species, dex_id)
        if data_uri:
            sprites[species] = data_uri
        else:
            failures.append(species)
            print(f"  FAIL {species}")

    with open(output_path, "w") as f:
        json.dump(sprites, f)

    total_kb = sum(len(v) for v in sprites.values()) / 1024 * 0.75  # b64 overhead approx
    print(f"\nSaved {len(sprites)} sprites to {output_path} (~{total_kb:.0f} KB base64)")
    if failures:
        print(f"[WARN] Missing sprites: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
