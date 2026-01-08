import sys
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List
import asyncio

# --- GESTION DES IMPORTS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.observers.Observer import Observer
from src.simulation import Simulation

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
    simulation: Simulation = None

context = GuiContext()
app = FastAPI()

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

    hero_positions = []
    if context.simulation:
        hero_positions = [{"x": pos[1], "y": pos[0]} for pos in context.simulation.get_all_hero_positions()]

    return JSONResponse({
        "rows": dng.dimension[0],
        "cols": dng.dimension[1],
        "grid": serialized_grid,
        "heros": hero_positions
    })

@app.get("/api/place_entity/")
async def place_entity(type_entity: str, x: int, y: int):
    if not context.input_handler:
        return JSONResponse({"entity_placed": "true"})

    match type_entity:
        case "trap":
            context.input_handler.place_trap((x, y))
        case "wall":
            context.input_handler.place_wall((x, y))
        case "dragon":
            context.input_handler.place_dragon((x, y))
        case "bombe":
            context.input_handler.place_bombe((x, y))

    return JSONResponse({"entity_placed": "true"})



@app.get("/api/start_simulation/")
async def start_simulation():
    if not context.input_handler:
        return JSONResponse({"simulation_started": "false"})

    context.input_handler.start_wave()
    
    return JSONResponse({"simulation_started": "true"})




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
    
    dungeon_observer = DungeonObserver(manager)
    simulation.attach(dungeon_observer)

    print(f"🚀 Serveur GUI lancé sur http://127.0.0.1:8000")
    print(f"Donjon de taille {dungeon_instance.dimension} chargé.")
    
    # Lancement d'Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    print("Ce fichier ne doit pas être lancé directement.")
    print("Utilisez 'python tests/test_simulation_server.py'.")