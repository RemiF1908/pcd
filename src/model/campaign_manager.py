"""Gestionnaire de campagne simplifié pour charger des niveaux."""

import json
import os
from typing import Optional, List
from .level import Level, LevelBuilder
from .dungeon import Dungeon


class Campaign:
    """Gère le chargement des niveaux depuis campaign.json et la progression."""

    def __init__(self, campaign_json_path: str = "campaign.json"):
        self.campaign_json_path = campaign_json_path
        self._data = None
        self._current_level_num = 0
        self._completed_levels: List[int] = []
        self._load_campaign_data()

    def _load_campaign_data(self) -> None:
        """Charge les données de la campagne depuis le fichier JSON."""
        if not os.path.exists(self.campaign_json_path):
            return

        with open(self.campaign_json_path, "r") as f:
            self._data = json.load(f)

    def _get_level_config(self, level_num: int) -> Optional[dict]:
        """Retourne la configuration d'un niveau par son numéro."""
        if not self._data:
            return None

        for level in self._data.get("levels", []):
            if level.get("id") == level_num:
                return level
        return None

    def _load_dungeon(self, dungeon_file: str) -> Optional[Dungeon]:
        """Charge un donjon depuis un fichier JSON."""
        dungeon_path = f"./save/{dungeon_file}.json"
        
        if not os.path.exists(dungeon_path):
            return None

        from ..commands.importDungeon import importDungeon
        
        cmd = importDungeon(dungeon_file)
        cmd.execute(None)
        return cmd.result

    def load_level(self, level_num: int) -> Optional[Level]:
        """Charge un niveau par son numéro et retourne un objet Level."""
        config = self._get_level_config(level_num)
        if not config:
            return None

        dungeon_file = config.get("dungeon_file")
        if not dungeon_file:
            return None

        dungeon = self._load_dungeon(dungeon_file)
        if not dungeon:
            return None

        builder = LevelBuilder()
        builder.set_dungeon(dungeon)
        builder.set_budget(config.get("budget", 100))
        builder.set_difficulty(config.get("difficulty", 1))

        for hero_config in config.get("heroes", []):
            pv = hero_config.get("pv", 100)
            strategy = hero_config.get("strategy", "random")
            builder.add_hero(pv=pv, strategy=strategy)

        self._current_level_num = level_num
        return builder.build()

    def load_next_level(self) -> Optional[Level]:
        """Charge le niveau suivant à partir du niveau actuel."""
        return self.load_level(self._current_level_num + 1)

    def complete_level(self, level_num: int) -> None:
        """Marque un niveau comme complété."""
        if level_num not in self._completed_levels:
            self._completed_levels.append(level_num)

    def is_completed(self, level_num: int) -> bool:
        """Vérifie si un niveau est complété."""
        return level_num in self._completed_levels

    def get_completed_levels(self) -> List[int]:
        """Retourne la liste des niveaux complétés."""
        return self._completed_levels.copy()

    def reset(self) -> None:
        """Réinitialise la progression de la campagne."""
        self._current_level_num = 0
        self._completed_levels = []

    def get_campaign_info(self) -> dict:
        """Retourne les informations générales de la campagne."""
        if not self._data:
            return {}
        return self._data.get("campaign", {})
