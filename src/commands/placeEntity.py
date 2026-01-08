from .Command import Command


class placeEntity(Command):
    def __init__(self, dungeon, entity, position: tuple, simulation):
        self.dungeon = dungeon
        self.entity = entity
        self.position = position
        self.simulation = simulation

    def execute(self, game_controller):
        if not(self.simulation.isSimStarted):
            self.dungeon.place_entity(self.entity, self.position)
