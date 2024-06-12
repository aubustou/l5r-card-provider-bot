from __future__ import annotations

import logging
import re
from io import BytesIO

import discord

from .main import client, image_database, image_folder

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

    files: list[discord.File] = []

    for match in matches:
        # match could be <image name> or <image name|edition>
        if len(match := match.split("|")) == 2:
            match, edition = match
        else:
            edition = None

        if card := image_database.get(match):
            if edition:
                if not (found_image := card["images"].get(edition)):
                    logger.warning(
                        "Image '%s' non trouvée pour l'édition '%s'.", match, edition
                    )
                    continue
            else:
                found_image = next(iter(card["images"].values()))

            if not (image_path := next(image_folder.rglob(found_image.name), None)):
                logger.warning("Image '%s' non trouvée.", match)
                continue

            image_data = BytesIO(image_path.read_bytes())
            files.append(discord.File(image_data, filename=f"{match}.jpg"))
        else:
            logger.warning("Image '%s' non trouvée.", match)
            # await message.channel.send(f"Image '{match}' non trouvée.")

    if files:
        await message.channel.send(files=files)
