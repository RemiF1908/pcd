from __future__ import annotations

from abc import ABC, abstractmethod

from .entity import Entity


class EntityCreator(ABC):
    """Interface pour tous les ."""

    @abstractmethod
    def factory_method(self) -> Entity:
        """Méthode de fabrique qui retourne une nouvelle instance d'Entity.

        Les sous-classes concrètes doivent implémenter cette méthode pour créer
        le type d'entité approprié.
        """
        pass

    def build(self) -> Entity:
        """Méthode de construction par défaut utilisant l'entité créée.

        Returns:
            Instance d'Entity créée par factory_method().
        """
        return self.factory_method()
