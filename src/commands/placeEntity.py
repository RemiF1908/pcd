from .Command import Command

class placeEntity(Command) :
    
    def execute(self, dungeon, entity, position : tuple):
        dungeon.place_entity(entity, position)
            