from .Command import Command


class resetDungeon(Command):
    """Commande pour réinitialiser le donjon.

    Note:
        - On accepte un paramètre `simulation` optionnel. Si fourni, la commande
          calcule le montant total des entités placées (coûts) et le rajoute au
          `current_budget` de la simulation (refund), puis réinitialise le donjon.
        - Le paramètre optionnel permet de garder la compatibilité avec les
          tests/unitaires qui instancient `resetDungeon(dungeon)`.
    """

    def __init__(self, dungeon, simulation=None):
        self.dungeon = dungeon
        self.simulation = simulation

    def execute(self, game_controller) -> None:
        """Exécute la commande de réinitialisation du donjon.

        Si une simulation est fournie, on rembourse le coût des entités
        non-floor qui ont un attribut `cost` strictement positif.
        """
        # Si on a une simulation, calculer le remboursement
        if self.simulation is not None:
            refund = 0
            try:
                # Importer Floor localement pour éviter les éventuels imports circulaires
                from src.model.floor import Floor

                for row in self.dungeon.grid:
                    for cell in row:
                        ent = cell.entity
                        if ent is None:
                            continue
                        # Ne pas rembourser le sol
                        if isinstance(ent, Floor):
                            continue
                        # Si l'entité possède un coût, l'ajouter au remboursement
                        ent_cost = getattr(ent, "cost", 0)
                        if isinstance(ent_cost, (int, float)) and ent_cost > 0:
                            refund += ent_cost
            except Exception:
                # En cas d'erreur (import, attribut manquant...), on ignore le remboursement
                refund = 0

            if refund:
                # Ajoute le remboursement au budget courant
                try:
                    self.simulation.current_budget += refund
                except Exception:
                    # Si la simulation ne possède pas l'attribut, on ignore
                    pass

        # Enfin, réinitialiser le donjon
        self.dungeon.reset()
