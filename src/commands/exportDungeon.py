from .Command import Command

class exportDungeon(Command) :
    
    def execute(self, dungeon, filepath):
        with open(self.filepath, 'w') as file:
            file.write(dungeon.serialize())
        print(f"Dungeon exported to {filepath}")