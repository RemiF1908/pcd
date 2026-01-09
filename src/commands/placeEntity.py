from .Command import Command


class placeEntity(Command):
    def __init__(self, dungeon, entity, position: tuple, simulation):
        self.dungeon = dungeon
        self.entity = entity
        self.position = position
        self.simulation = simulation

    def execute(self, game_controller):
        if not (self.simulation.isSimStarted):
            # Si une entité existe déjà à cet emplacement (et n'est pas un Floor),
            # rembourser son coût avant de tenter de placer la nouvelle entité.
            try:
                from ..model.floor import Floor
            except Exception:
                # Import local fallback
                from src.model.floor import Floor

            try:
                cell = self.dungeon.get_cell(self.position)
                existing = getattr(cell, "entity", None)
            except Exception:
                existing = None

            if existing is not None and not isinstance(existing, Floor):
                prev_cost = getattr(existing, "cost", 0)
                if isinstance(prev_cost, (int, float)) and prev_cost > 0:
                    try:
                        self.simulation.current_budget += prev_cost
                    except Exception:
                        # Si la simulation n'expose pas current_budget, on ignore
                        pass

            # Maintenant vérifier le budget pour la nouvelle entité
            if self.entity.cost <= self.simulation.current_budget:
                self.simulation.current_budget -= self.entity.cost
                self.dungeon.place_entity(self.entity, self.position)
