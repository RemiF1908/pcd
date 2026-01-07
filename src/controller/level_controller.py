"""Contrôleur de niveau pour gérer les campagnes et la progression."""

from typing import Optional, Dict
from ..model.campaign_manager import CampaignManager
from ..model.dungeon import Dungeon


class LevelController:
    """Gere le niveau et la progression dans une campagne de donjons.
    
    se base sur CampaignManager pour le chargement et la gestion des niveaux."""
    def __init__(self, campaign_json_path: Optional[str] = None):
        """Initialise le contrôleur de niveau. """
        self.campaign_manager: Optional[CampaignManager] = None
        if campaign_json_path:
            self.load_campaign(campaign_json_path)

    def load_campaign(self, campaign_json_path: str) -> bool:
        """Charge une campagne depuis un fichier JSON. """
        self.campaign_manager = CampaignManager(campaign_json_path)
        return self.campaign_manager.load_campaign()

    def get_levels(self) -> list:
        """Retourne la liste des niveaux de la campagne. """
        if not self.campaign_manager:
            return []
        return self.campaign_manager.get_levels()

    def get_current_level(self) -> Optional[Dict]:
        """Retourne la configuration du niveau actuel.  """
        if not self.campaign_manager:
            return None
        return self.campaign_manager.get_current_level()

    def get_level_by_id(self, level_id: int) -> Optional[Dict]:
        """Retourne la configuration d'un niveau par son ID. """
        if not self.campaign_manager:
            return None
        return self.campaign_manager.get_level_by_id(level_id)

    def get_campaign_info(self) -> Dict:
        """Retourne les informations générales de la campagne. """
        if not self.campaign_manager:
            return {}
        return self.campaign_manager.get_campaign_info()

    def get_level_dungeon_file(self, level_id: Optional[int] = None) -> Optional[str]:
        """Retourne le nom du fichier de donjon pour un niveau.  """
        if not self.campaign_manager:
            return None

        if level_id is None:
            level_config = self.campaign_manager.get_current_level()
        else:
            level_config = self.campaign_manager.get_level_by_id(level_id)

        if not level_config:
            return None

        return level_config.get("dungeon_file")

    def get_level_heroes_config(self, level_id: Optional[int] = None) -> list:
        """Retourne la configuration des héros pour un niveau.  """
        if not self.campaign_manager:
            return []

        if level_id is None:
            level_config = self.campaign_manager.get_current_level()
        else:
            level_config = self.campaign_manager.get_level_by_id(level_id)

        if not level_config:
            return []

        return level_config.get("heroes", [])

    def get_level_budget(self, level_id: Optional[int] = None) -> int:
        """Retourne le budget pour un niveau.  """
        if not self.campaign_manager:
            return 100

        if level_id is None:
            level_config = self.campaign_manager.get_current_level()
        else:
            level_config = self.campaign_manager.get_level_by_id(level_id)

        if not level_config:
            return 100

        return level_config.get("budget", 100)

    def get_level_difficulty(self, level_id: Optional[int] = None) -> int:
        """Retourne la difficulté pour un niveau. """
        if not self.campaign_manager:
            return 1

        if level_id is None:
            level_config = self.campaign_manager.get_current_level()
        else:
            level_config = self.campaign_manager.get_level_by_id(level_id)

        if not level_config:
            return 1

        return level_config.get("difficulty", 1)

    def check_win_condition(self, wave_result: Dict, level_config: Optional[Dict] = None) -> bool:
        """Vérifie si les conditions de victoire sont remplies pour un niveau.  """
        if not self.campaign_manager:
            return False

        if level_config is None:
            level_config = self.campaign_manager.get_current_level()

        if not level_config:
            return False

        won = self.campaign_manager.check_win_condition(wave_result, level_config)
        if won:
            level_id = level_config.get("id")
            if level_id is not None:
                self.campaign_manager.complete_level(level_id)

        return won

    def advance_to_next_level(self) -> Optional[Dict]:
        """Passe au niveau suivant et retourne sa configuration.Configuration du niveau suivant ou None si fin de campagne.
        """
        if not self.campaign_manager:
            return None
        return self.campaign_manager.advance_to_next_level()

    def has_more_levels(self) -> bool:
        """Vérifie s'il reste des niveaux à jouer.True s'il reste des niveaux, False sinon.
        """
        if not self.campaign_manager:
            return False
        return self.campaign_manager.has_more_levels()

    def reset_progress(self) -> None:
        """Réinitialise la progression de la campagne."""
        if self.campaign_manager:
            self.campaign_manager.reset_progress()

    def get_completed_levels(self) -> list:
        """Retourne la liste des niveaux complétés. """
        if not self.campaign_manager:
            return []
        return self.campaign_manager.completed_levels.copy()

    def is_level_completed(self, level_id: int) -> bool:
        """Vérifie si un niveau est complété."""
        if not self.campaign_manager:
            return False
        return level_id in self.campaign_manager.completed_levels
