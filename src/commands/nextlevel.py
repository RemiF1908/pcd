from .Command import Command


class nextLevel(Command):
    def __init__(self, campaign, simulation):
        """
        Initialise la commande pour passer au niveau suivant.
        """
        self.campaign = campaign
        self.simulation = simulation
        self.result = None

    def execute(self, game_controller=None):
        """
        Exécute l'action de passer au niveau suivant.
        """
        if self.simulation.allHeroesDead:
            if self.campaign:
                current_level_num = self.campaign._current_level_num
                next_level_instance = self.campaign.load_next_level()

                if next_level_instance:
                    self.campaign.complete_level(current_level_num)

                    self.simulation.level = next_level_instance
                    self.simulation.dungeon = next_level_instance.dungeon
                    self.simulation.heroes = next_level_instance.heroes
                    self.simulation.current_budget = next_level_instance.budget_tot
                    self.simulation.totalscore += self.simulation.score
                    self.simulation.reset()

                    self.result = next_level_instance
                else:
                    self.result = None