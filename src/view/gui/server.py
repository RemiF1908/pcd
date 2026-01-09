import sys
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List
import asyncio
from pydantic import BaseModel
from src.model.entity_factory import EntityFactory
import json
import pathlib

# --- GESTION DES IMPORTS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.observers.Observer import Observer
from src.simulation import Simulation
from src.commands.importDungeon import importDungeon

# --- WEBSOCKETS ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class DungeonObserver(Observer):
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    def update(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'get_running_loop' fails if no loop is running
            loop = None

        if loop and loop.is_running():
            loop.create_task(self.manager.broadcast("dungeon_updated"))
        else:
            print("No running event loop to schedule broadcast")

# --- CONTEXTE GLOBAL ---
# Stocke uniquement le donjon à afficher
class GuiContext:
    dungeon = None
    input_handler = None
    simulation = None
    game_controller = None

context = GuiContext()
app = FastAPI()

class PlaceEntityRequest(BaseModel):
    type_entity: str
    x: int
    y: int

class SaveDungeonRequest(BaseModel):
    filename: str
    campaign_progress: list = []

# --- ENDPOINTS ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Just keep connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/dungeon")
async def get_dungeon():
    """Renvoie l'état statique du donjon (Grille, Murs, Pièges, Entrée, Sortie)."""
    if not context.dungeon:
        return JSONResponse({"error": "Aucun donjon chargé"}, status_code=500)

    # Utiliser toujours le donjon de la simulation pour être sûr d'être synchro
    dng = context.simulation.dungeon if context.simulation and context.simulation.dungeon else context.dungeon
    
    print(f"API Dungeon: Using dungeon from simulation, Level: {context.simulation.level.difficulty if context.simulation and context.simulation.level else 'unknown'}")

    # Log pour voir le contenu de la première ligne avant sérialisation
    if dng.grid and len(dng.grid) > 0:
        print(f"First row of dungeon grid before serialization:")
        for c, cell in enumerate(dng.grid[0]):
            entity_info = f"entity={cell.entity}, type={getattr(cell.entity, 'type', 'None') if cell.entity else 'None'}"
            print(f"  Cell [0][{c}]: {entity_info}")

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
            
            # Log pour la position où on a placé la bombe (2, 0)
            if r == 0 and c == 2:
                print(f"Cell at ({r}, {c}) in serialization: entity_type = {entity_type}")
        serialized_grid.append(row_data)

    hero_positions = []
    if context.simulation and context.simulation.heroes:
        try:
            for hero in context.simulation.heroes:
                if hero.isAlive and hero.coord:
                    hero_positions.append({"x": hero.coord[1], "y": hero.coord[0]})
        except:
            pass

    return JSONResponse({
        "rows": dng.dimension[0],
        "cols": dng.dimension[1],
        "grid": serialized_grid,
        "heros": hero_positions
    })

@app.post("/api/place_entity/")
async def place_entity(request: PlaceEntityRequest):
    if not context.input_handler:
        return JSONResponse({"entity_placed": "true"})

    # Log pour vérifier quel donjon est utilisé
    print(f"Placing entity at ({request.y}, {request.x}) on dungeon level: {context.simulation.level.difficulty if context.simulation and context.simulation.level else 'unknown'}")

    # Le modèle attend les coordonnées en (row, col), ce qui correspond à (y, x)
    # venant du front-end.
    match request.type_entity:
        case "trap":
            context.input_handler.place_trap((request.y, request.x))
        case "wall":
            context.input_handler.place_wall((request.y, request.x))
        case "dragon":
            context.input_handler.place_dragon((request.y, request.x), orientation="U")
        case "bombe":
            context.input_handler.place_bombe((request.y, request.x))
        case "floor":
            context.input_handler.remove_entity((request.y, request.x))

    return JSONResponse({"entity_placed": "true"})

@app.get("/api/dungeon_data")
async def get_dungeon_data():
    if not context.simulation:
        return JSONResponse({"error": "Aucune simulation chargée"}, status_code=500)

    prices = {
        "trap": EntityFactory.create_trap().cost,
        "dragon": EntityFactory.create_dragon().cost,
        "bombe": EntityFactory.create_bombe().cost,
        "wall": EntityFactory.create_wall().cost,
        "floor": 0
    }

    return JSONResponse({
        "money": context.simulation.current_budget,
        "prices": prices,
        "level": context.simulation.level.difficulty if context.simulation.level else 1
    })



@app.get("/api/next_level/")
async def next_level():
    if not context.input_handler:
        return JSONResponse({"next_level_change": "false"})

    # 1. On demande à l'handler de charger le niveau suivant
    # (Cela modifie self.simulation à l'intérieur de input_handler)
    context.input_handler.load_next_level()
    
    # 2. CORRECTION CRITIQUE : On met à jour les références du serveur
    # pour qu'elles pointent vers la NOUVELLE simulation créée par l'handler
    context.simulation = context.input_handler.simulation
    context.dungeon = context.input_handler.dungeon
    
    # 3. CORRECTION IMPORTANTE : Réattacher l'Observer WebSocket
    # La nouvelle simulation est toute neuve, elle n'a pas d'observer.
    # Si on ne fait pas ça, le serveur ne préviendra plus le frontend des mises à jour.
    observer = DungeonObserver(manager)
    context.simulation.attach(observer)
    
    print(f">>> Passage au niveau suivant. Difficulté: {context.simulation.level.difficulty}")
    
    return JSONResponse({"next_level_change": "true"})

@app.get("/api/start_simulation/")
async def start_simulation():
    if not context.input_handler:
        return JSONResponse({"simulation_started": "false"})

    context.input_handler.start_wave()
    
    return JSONResponse({"simulation_started": "true"})

@app.post("/api/reset_simulation")
async def reset_simulation():
    if not context.simulation:
        return JSONResponse({"error": "Aucune simulation chargée"}, status_code=500)
    
    try:
        # Réinitialiser la simulation
        context.simulation.reset()
        context.simulation.isSimStarted = False
        
        # Remettre les héros à leur position de départ et désactivés
        if context.simulation.heroes and context.simulation.dungeon:
            for hero in context.simulation.heroes:
                hero.coord = context.simulation.dungeon.entry
                hero.isAlive = False
                hero.stepsTaken = 0
        # Notifier les observers et forcer un broadcast websocket
        try:
            context.simulation.notify()
            # manager.broadcast est async - on l'attend pour garantir l'envoi
            await manager.broadcast("dungeon_updated")
        except Exception:
            # Ne pas empêcher la réponse en cas d'erreur de notification
            pass

        return JSONResponse({"simulation_reset": "true"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/save_dungeon")
async def save_dungeon(request: SaveDungeonRequest):
    if not context.dungeon:
        return JSONResponse({"error": "Aucun donjon chargé"}, status_code=500)
    
    if not context.game_controller:
        return JSONResponse({"error": "Game controller non disponible"}, status_code=500)
    
    try:
        from src.commands.exportDungeon import exportDungeon
        
        # Créer la commande d'export avec le filename et la progression de campagne
        command = exportDungeon(context.dungeon, request.filename, request.campaign_progress)
        command.execute(context.game_controller)
        
        return JSONResponse({"saved": "true", "filename": request.filename})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/move_hero")
async def move_hero():
    if not context.simulation:
        return JSONResponse({"error": "Aucune simulation chargée"}, status_code=500)
    
    try:
        result = context.simulation.step()
        return JSONResponse({"hero_moved": "true", "result": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/import_dungeon")
async def api_import_dungeon():
    """Appelle uniquement `context.input_handler.import_dungeon()`.

    Ce endpoint ne prend aucun payload et délègue l'import à
    l'`InputHandler` côté serveur (méthode `import_dungeon`).
    """
    if not context.input_handler:
        return JSONResponse({"error": "Aucun input_handler configuré"}, status_code=500)

    try:
        # N'exécute que la méthode publique de l'input handler.
        context.input_handler.import_dungeon()
        
        # Mettre à jour le contexte global avec le nouveau donjon
        context.dungeon = context.simulation.dungeon
        
        # Broadcast WebSocket pour forcer le client à rafraîchir
        await manager.broadcast("dungeon_updated")
        
        return JSONResponse({"imported": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- FICHIERS STATIQUES ---
static_path = os.path.join(current_dir, "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

# --- FONCTION DE LANCEMENT ---
def run_server(dungeon_instance, input_handler, simulation):
    """
    Configure le contexte avec le donjon fourni et lance le serveur.
    """
    context.dungeon = dungeon_instance
    context.input_handler = input_handler
    context.simulation = simulation
    context.game_controller = input_handler.invoker.game_controller if input_handler and input_handler.invoker else None
    
    dungeon_observer = DungeonObserver(manager)
    simulation.attach(dungeon_observer)

    print(f"🚀 Serveur GUI lancé sur http://127.0.0.1:8000")
    print(f"Donjon de taille {dungeon_instance.dimension} chargé.")
    
    # Lancement d'Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    print("Ce fichier ne doit pas être lancé directement.")
    print("Utilisez 'python tests/test_simulation_server.py'.")