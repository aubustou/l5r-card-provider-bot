from __future__ import annotations

import logging
import re
from io import BytesIO

import discord

from .main import client, image_database, image_folder

logger = logging.getLogger(__name__)

breakpoint()


@client.event
async def on_ready():
    logger.info("Bot connecté en tant que %s", client.user)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Regex pour trouver le format [[nom de l'image]]
    pattern = r"\[\[(.*?)\]\]"
    matches = re.findall(pattern, message.content)

    for match in matches:
        if card := image_database.get(match):
            image_path = image_folder / next(card["images"]["0"].values())
            image_data = BytesIO(image_path.read_bytes())
            await message.channel.send(
                file=discord.File(image_data, filename=f"{match}.jpg")
            )
        else:
            logger.warning("Image '%s' non trouvée.", match)
            # await message.channel.send(f"Image '{match}' non trouvée.")
