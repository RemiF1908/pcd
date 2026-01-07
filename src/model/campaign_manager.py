"""Gestionnaire de campagne pour la progression par niveaux."""

import json
import os
from typing import Dict, List, Optional


class CampaignManager:
    """Gère le chargement et la progression d'une campagne de niveaux."""

    def __init__(self, campaign_json_path: str):
        self.campaign_json_path = campaign_json_path
        self.campaign_data: Optional[Dict] = None
        self.current_level_index: int = 0
        self.completed_levels: List[int] = []

    def load_campaign(self) -> bool:
        if not os.path.exists(self.campaign_json_path):
            return False

        with open(self.campaign_json_path, "r") as f:
            self.campaign_data = json.load(f)

        return True

    def get_levels(self) -> List[Dict]:
        """Retourne la liste des niveaux de la campagne."""
        if not self.campaign_data:
            return []
        return self.campaign_data.get("levels", [])

    def get_current_level(self) -> Optional[Dict]:
        """Retourne la configuration du niveau actuel."""
        levels = self.get_levels()
        if self.current_level_index < len(levels):
            return levels[self.current_level_index]
        return None

    def get_level_by_id(self, level_id: int) -> Optional[Dict]:
        """Retourne la configuration d'un niveau par son ID."""
        for level in self.get_levels():
            if level.get("id") == level_id:
                return level
        return None

    def complete_level(self, level_id: int) -> None:
        """Marque un niveau comme complété."""
        if level_id not in self.completed_levels:
            self.completed_levels.append(level_id)

    def advance_to_next_level(self) -> Optional[Dict]:
        """Passe au niveau suivant et retourne sa configuration."""
        levels = self.get_levels()
        self.current_level_index += 1

        if self.current_level_index < len(levels):
            return levels[self.current_level_index]
        return None

    def check_win_condition(self, wave_result: Dict, level_config: Dict) -> bool:
        """Vérifie si les conditions de victoire sont remplies pour un niveau."""
        heroes_survived = wave_result.get("heroesSurvived", 0)
        return heroes_survived == 0

    def has_more_levels(self) -> bool:
        """Vérifie s'il reste des niveaux à jouer."""
        levels = self.get_levels()
        return self.current_level_index < len(levels) - 1

    def reset_progress(self) -> None:
        """Réinitialise la progression de la campagne."""
        self.current_level_index = 0
        self.completed_levels = []

    def get_campaign_info(self) -> Dict:
        """Retourne les informations générales de la campagne.Dictionnaire avec le nom et la description de la campagne.
        """
        if not self.campaign_data:
            return {}
        return self.campaign_data.get("campaign", {})
