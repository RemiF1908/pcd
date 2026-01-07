from .Command import Command


class placeEntity(Command):
    def __init__(self, dungeon, entity, position: tuple):
        self.dungeon = dungeon
        self.entity = entity
        self.position = position

    def execute(self, game_controller):
        self.dungeon.place_entity(self.entity, self.position)
