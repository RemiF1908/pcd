"""
Script d'exemple simplifié pour tester le système de campagne avec LevelController.

Usage:
    python3 example_simple_campaign.py
"""

from src.model.campaign_manager import CampaignManager
from src.controller.level_controller import LevelController
from src.controller.game_controller import GameController
from src.simulation import Simulation
from src.model.level import Level
from src.model.level import LevelBuilder
from unittest.mock import MagicMock


def main():
    """Exemple simplifié d'utilisation du système de campagne avec LevelController."""

    print("=== Système de Campagne - Exemple avec LevelController ===\n")

    # Initialisation des contrôleurs
    simulation = Simulation(level=Level())
    level_controller = LevelController("campaign.json")
    game_controller = GameController(MagicMock(), simulation)

    # Charger la campagne
    campaign_info = level_controller.get_campaign_info()
    print(f"📜 Campagne: {campaign_info.get('name', 'Sans nom')}")
    print(f"   {campaign_info.get('description', '')}\n")

    # Boucle sur les niveaux
    level_count = 0
    while True:
        level_config = level_controller.get_current_level()
        if not level_config:
            print("🎉 Campagne terminée !")
            break

        level_count += 1
        print(f"--- Niveau {level_count}: {level_config['name']} ---")
        print(f"   Difficulté: {level_config['difficulty']}")
        print(f"   Budget: {level_controller.get_level_budget()}")
        print(f"   Héros: {len(level_controller.get_level_heroes_config())}")
        print(f"   Donjon: {level_controller.get_level_dungeon_file()}.json")

        # Créer le niveau avec LevelBuilder
        dungeon_file = level_controller.get_level_dungeon_file()
        if not dungeon_file:
            print("   ❌ Erreur: pas de fichier de donjon")
            break

        imported_dungeon = game_controller.import_dungeon(dungeon_file)
        if not imported_dungeon:
            print("   ❌ Erreur lors du chargement du donjon")
            break

        builder = LevelBuilder()
        builder.set_dungeon(imported_dungeon)
        builder.set_budget(level_controller.get_level_budget())
        builder.set_difficulty(level_controller.get_level_difficulty())

        for hero_config in level_controller.get_level_heroes_config():
            pv = hero_config.get("pv", 100)
            strategy = hero_config.get("strategy", "random")
            builder.add_hero(pv=pv, strategy=strategy, coord=imported_dungeon.entry)

        level = builder.build()
        game_controller.setup_level(level)

        print(f"   ✅ Donjon chargé: {simulation.dungeon.dimension[0]}x{simulation.dungeon.dimension[1]}")
        print(f"   ✅ Héros initialisés: {len(simulation.heroes)}")

        # Simuler une victoire (tous les héros tués)
        wave_result = {
            "heroesKilled": len(level_controller.get_level_heroes_config()),
            "heroesSurvived": 0,
            "construction_cost": 50,
            "score": 8000,
            "turns": 15
        }

        print(f"\n   Résultat simulé:")
        print(f"   - Héros tués: {wave_result['heroesKilled']}")
        print(f"   - Héros survivants: {wave_result['heroesSurvived']}")
        print(f"   - Score: {wave_result['score']}")

        # Vérifier la victoire
        if level_controller.check_win_condition(wave_result):
            print("   ✅ Niveau réussi !\n")

            # Vérifier s'il y a un niveau suivant
            if not level_controller.has_more_levels():
                print("🏆 Tous les niveaux terminés !")
                break

            level_controller.advance_to_next_level()
        else:
            print("   ❌ Niveau échoué.\n")
            break


if __name__ == "__main__":
    main()
