from __future__ import annotations

import logging
import re

from .main import client, images

logger = logging.getLogger(__name__)


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
        image_url = images.get(match.lower())
        if image_url:
            await message.channel.send(image_url)
        else:
            logger.warning("Image '%s' non trouvée.", match)
            # await message.channel.send(f"Image '{match}' non trouvée.")
