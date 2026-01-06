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

	@abstractmethod
	def get_display_char(self) -> str:
		"""Retourne le caractère à afficher pour cette entité dans le TUI.

		Chaque entité concrète doit implémenter cette méthode.
		Exemples : '.' pour Floor, '#' pour Wall, '^' pour Trap.
		"""

	@abstractmethod
	def get_color_id(self) -> int:
		"""Retourne l'identifiant de la paire de couleur curses pour l'affichage.

		Conventions (à respecter dans l'initialisation curses) :
		  1 = Floor (blanc/gris)
		  2 = Wall (blanc brillant)
		  3 = Trap (rouge)
		  4 = Monster (magenta)
		  5 = Entrance (vert)
		  6 = Exit (cyan)
		  7 = Hero (jaune)
		"""

	def __repr__(self) -> str:  
		try:
			return f"{self.__class__.__name__}({self.type})"
		except Exception:
			return f"{self.__class__.__name__}()"

