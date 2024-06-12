from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import discord

CONF_PATH = Path.home() / ".l5r_bot" / "config.json"

logger = logging.getLogger(__name__)

client: discord.Client


def init_conf() -> dict[str, str]:
    CONF_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CONF_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONF_PATH}")

    return json.loads(CONF_PATH.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database-path", help="Chemin du fichier XML contenant les données"
    )
    parser.add_argument("image-folder", help="Chemin du dossier contenant les images")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    global client

    # Intents pour lire les messages
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    images = args.image_folder

    config = init_conf()

    # Remplacez 'YOUR_BOT_TOKEN' par le token de votre bot
    client.run(config["token"])


if __name__ == "__main__":
    main()
