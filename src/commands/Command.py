from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self, game_controller):
        pass
