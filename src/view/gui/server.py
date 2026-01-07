import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# --- GESTION DES IMPORTS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# --- CONTEXTE GLOBAL ---
# Stocke uniquement le donjon à afficher
class GuiContext:
    dungeon = None

context = GuiContext()
app = FastAPI()

# --- ENDPOINTS ---
@app.get("/api/dungeon")
async def get_dungeon():
    """Renvoie l'état statique du donjon (Grille, Murs, Pièges, Entrée, Sortie)."""
    if not context.dungeon:
        return JSONResponse({"error": "Aucun donjon chargé"}, status_code=500)

    dng = context.dungeon

    # Sérialisation de la grille
    serialized_grid = []
    for r, row in enumerate(dng.grid):
        row_data = []
        for c, cell in enumerate(row):
            # Type par défaut
            entity_type = cell.entity.type if cell.entity else "FLOOR"
            
            # Surcharge pour l'affichage visuel (Départ / Arrivée)
            if (r, c) == dng.entry:
                entity_type = "START"
            elif (r, c) == dng.exit:
                entity_type = "EXIT"
            
            row_data.append({
                "x": c, 
                "y": r, 
                "type": entity_type
            })
        serialized_grid.append(row_data)

    return JSONResponse({
        "rows": dng.dimension[0],
        "cols": dng.dimension[1],
        "grid": serialized_grid
    })

# --- FICHIERS STATIQUES ---
static_path = os.path.join(current_dir, "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

# --- FONCTION DE LANCEMENT ---
def run_server(dungeon_instance):
    """
    Configure le contexte avec le donjon fourni et lance le serveur.
    """
    context.dungeon = dungeon_instance
    
    print(f"🚀 Serveur GUI lancé sur http://127.0.0.1:8000")
    print(f"Donjon de taille {dungeon_instance.dimension} chargé.")
    
    # Lancement d'Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    print("Ce fichier ne doit pas être lancé directement.")
    print("Utilisez 'python tests/test_simulation_server.py'.")