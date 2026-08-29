#!/usr/bin/env python3
"""
Sprite Downloader
=================
Downloads Pokemon sprites from PokeAPI and converts them to base64 data URIs.
Saves the mapping to a JSON file for the renderer to use.

Usage:
  python scripts/download_sprites.py
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

# All Pokemon sprites needed
SPRITES_TO_DOWNLOAD = {
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
    "gardevoir-mega": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/282-mega.png",
    # Player default
    "pikachu": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
    # Enemies
    "gengar": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png",
    "dragonite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/149.png",
    "tyranitar": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/248.png",
    "lucario": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/448.png",
    "rayquaza": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/384.png",
    "mewtwo": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
}


def download_and_convert(species, url):
    """Download a sprite and convert to base64 data URI."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pokemon-sprite-downloader"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"  [WARN] Failed to download {species}: {e}")
        return None


def main():
    print("Downloading Pokemon sprites...")
    output_path = os.path.join(os.path.dirname(__file__), "sprite_data.json")
    sprites = {}

    for species, url in SPRITES_TO_DOWNLOAD.items():
        data_uri = download_and_convert(species, url)
        if data_uri:
            sprites[species] = data_uri
            print(f"  OK {species}")
        else:
            print(f"  FAIL {species}")

    with open(output_path, "w") as f:
        json.dump(sprites, f)

    print(f"\nSaved {len(sprites)} sprites to {output_path}")


if __name__ == "__main__":
    main()
