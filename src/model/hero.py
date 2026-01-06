class Hero : 
    def __init__(self, pv_total, strategy : str, coord = None, isAlive=False):
        self.pv_total = pv_total
        self.pv_cur = pv_total
        self.coord = coord
        self.isAlive = isAlive
        self.reachedGoal = False
        self.stepsTaken = 0
        self.path = None
        self.strategy = None

    def awake(self) : 
        self.isAlive = True

    def getHero_coord(self) : 
        return self.coord

    def take_damage(self, damage : int) :
        self.pv_cur -= damage
        if self.pv_cur <= 0 :
            self.isAlive = False
            self.pv_cur = 0
    
    def move(self, new_coord : tuple) :
        self.coord = new_coord


    def getMove(self) -> tuple : 
        return self.path[self.stepsTaken]

    def update(self, dungeon) :
        entity = dungeon.get_cell(self.coord).entity
        self.take_damage(entity.damage)

    