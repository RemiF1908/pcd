"""Entities abstraites du donjon.

Cette module contient la classe abstraite `Entity` qui sert de contrat
pour toutes les entités placées dans une `Cell` (floor, wall, trap, monster...).

Les classes concrètes doivent implémenter au minimum :
- la propriété `type` (str)
- la propriété `passable` (bool) indiquant si un héros peut marcher dessus
- la propriété `damage` (int) indiquant les dégâts infligés par la case

Les méthodes de sérialisation n'étant pas utilisées dans le projet, elles
ne sont pas exigées ici.

On utilise le module `abc` pour déclarer les méthodes abstraites.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Entity(ABC):
	"""Contrat abstrait pour une entité placée dans une case.

	Exemples d'implémentations : Floor, Wall, Trap, Monster.
	"""

	@property
	@abstractmethod
	def type(self) -> str:
		"""Type de l'entité (ex: 'FLOOR', 'WALL', 'TRAP', 'MONSTER')."""

	@property
	def passable(self) -> bool:
		"""Indique si la case est franchissable par un héros.

		Par défaut, on considère que l'entité est franchissable. Les murs
		ou obstacles doivent redéfinir cette propriété en False.
		"""
		return True

	@property
	def damage(self) -> int:
		"""Dégâts infligés par l'entité si applicable (pièges/monstres).

		Valeur par défaut 0 pour les entités non dangereuses.
		"""
		return 0

	@property
	def attack_power(self) -> int:
		"""Puissance d'attaque (pour les monstres)."""
		return 0

	def __repr__(self) -> str:  
		try:
			return f"{self.__class__.__name__}({self.type})"
		except Exception:
			return f"{self.__class__.__name__}()"

