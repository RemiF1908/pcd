from src.model.dungeon import Dungeon
from src.model.level import Level
from simulation import Simulation
from src.controller.game_controller import GameController

donjon = Dungeon(dimension=(10, 10), grid=[], entry=(0, 0), exit=(9, 9))
level = Level(dungeon=donjon, budget_tot=200, difficulty=3)

simu = Simulation(dungeon=donjon, budget_tot=level.budget_tot, nb_heroes=level.nb_heroes, heroes=level.heroes)

gc = GameController(interface=0, simulation=simu)



