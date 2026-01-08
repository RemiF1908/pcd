from .Observer import Observer

class DamageObserver(Observer) : 
    def __init__(self):
        self.totaldamage = 0
        self.lastdamage = None

    def update(self, damage : int) : 
        self.lastdamage = damage
        #print(f"Hero took {damage} damage")
        self.totaldamage += damage

    def getTotalDmg(self) :
        return self.totaldamage