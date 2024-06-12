from __future__ import annotations

import argparse
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TypedDict

import discord

CONF_PATH = Path.home() / ".l5r_bot" / "config.json"

logger = logging.getLogger(__name__)

client: discord.Client
image_folder: Path
image_database: CardDict


def init_conf() -> dict[str, str]:
    CONF_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CONF_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONF_PATH}")

    config = json.loads(CONF_PATH.read_text())
    if "token" not in config:
        raise KeyError("Token not found in configuration file")

    return config


class Card(TypedDict, total=False):
    id: str
    name: str
    type: str
    rarity: str
    edition: str
    image: str
    legal: str
    text: str
    cost: str
    focus: str
    images: dict[str, Path]


class CardDict(dict[str, Card]):
    def __setitem__(self, key: str, value: Card) -> None:
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str) -> Card:
        return super().__getitem__(key.lower())

    def get(self, key: str, default: Card | None = None) -> Card | None:
        return super().get(key.lower(), default)


def load_xml_database(path: Path) -> dict[str, Card]:
    """Load the L5R Oracle XML database into a dictionary of dictionaries.

    <cards version="2023/12/26 Onyx Oracle Edition">	<!--"Oct 4, 2015 Kamisasori no Kaisho (Complete), Nov 28, 2017 Kolat 1.3.4">-->
        <card id="AD092" type="strategy">
                <name>A Chance Meeting</name>
                <rarity>u</rarity>
                <edition>AD</edition><image edition="AD">images/cards/AD/AD092.jpg</image>
                <legal>open</legal>
                <text><![CDATA[<b>Battle:</b> One of your Personalities in this battle challenges an opposing Personality. If the challenged Personality refuses the challenge, that personality becomes dishonored, and all of his or her Followers bow. If the challenged Personality accepts the challenge, the duel's winner gains Honor equal to the number of cards focused by both players, and the loser is destroyed.]]></text>
                <cost>0</cost>
                <focus>3</focus>
        </card>
        <card id="AD081" type="region">
                <name>Akodo Fields</name>
                <rarity>u</rarity>
                <edition>AD</edition><image edition="AD">images/cards/AD/AD081.jpg</image>
                <legal>open</legal>
                <legal>jade</legal>
                <text><![CDATA[<B>Limited:</B> Target one of your Followers in play and pay Gold equal to the Follower's Force. For the rest of the game, the Follower is Elite, contributes its Force to its army's total during the Resolution Segment of battle even if its Personality is bowed, and is immune to Fear.]]></text>
        </card>
    """

    with path.open() as f:
        tree = ET.parse(f)

    root = tree.getroot()
    cards = root.findall("card")

    card_dict: dict[str, Card] = CardDict()
    for card in cards:
        name = card.find("name").text
        card_id = card.attrib["id"]
        rarity = card.find("rarity")
        card_dict[name] = {
            "id": card_id,
            "name": name,
            "type": card.attrib["type"],
            "images": {
                x.attrib["edition"]: Path(x.text) for x in card.findall("image")
            },
            "text": card.find("text").text,
            "rarity": (
                rarity.text if rarity is not None else "c"
            ),  # Common if rarity is not specified
        }

    return card_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database_path", type=Path, help="Chemin du fichier XML contenant les données"
    )
    parser.add_argument(
        "image_folder", type=Path, help="Chemin du dossier contenant les images"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    global client, image_folder, image_database

    # Intents pour lire les messages
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    image_folder = args.image_folder
    image_database = load_xml_database(args.database_path)

    config = init_conf()

    from . import api  # noqa: F401

    client.run(config["token"])


if __name__ == "__main__":
    main()
