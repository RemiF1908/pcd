import sys
import os

# --- SETUP PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

# Imports du Modèle
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor_creator import FloorCreator
from src.model.wall_creator import WallCreator
from src.model.trap_creator import TrapCreator

# Import du Serveur (la Vue)
from src.view.gui.server import run_server

def create_simulation_dungeon():
    """Crée un donjon statique avec des obstacles pour tester l'affichage."""
    rows, cols = (5,5)
    
    # 1. Création de la grille
    grid = [[Cell((r, c), FloorCreator().build()) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon((rows, cols), grid, (4, 1), (0, 2))
    
    # 2. Ajout d'obstacles (Le L de murs)
    walls = [(2,0),(2,3)]
    for r, c in walls:
        dungeon.place_entity(WallCreator().build(), (r, c))
    
    # 3. Ajout de pièges (sur le chemin direct)
    traps = [(2,1),(2,2),(3,2)]
    for r, c in traps:
        dungeon.place_entity(TrapCreator().build(), (r, c))
    return dungeon

if __name__ == "__main__":
    # A. Création du donjon
    my_dungeon = create_simulation_dungeon()
    
    # B. Injection du donjon dans le serveur et lancement
    run_server(my_dungeon)