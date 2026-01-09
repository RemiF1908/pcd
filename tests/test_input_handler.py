
import unittest
from unittest.mock import MagicMock, patch
from src.view.input_handler import InputHandler

class TestInputHandler(unittest.TestCase):

    def setUp(self):
        # Création de mocks pour les dépendances
        self.mock_simulation = MagicMock()
        self.mock_dungeon = MagicMock()
        self.mock_invoker = MagicMock()
        self.mock_campaign = MagicMock()
        
        # Initialisation de l'InputHandler avec les mocks
        self.input_handler = InputHandler(
            self.mock_simulation, self.mock_dungeon, self.mock_invoker, self.mock_campaign
        )

    @patch('src.view.input_handler.startWave')
    def test_start_wave(self, mock_start_wave):
        # Appeler la méthode pour démarrer une vague
        self.input_handler.start_wave()
        
        # Vérifier qu'une commande a été poussée et exécutée
        self.mock_invoker.push_command.assert_called_once()
        self.mock_invoker.execute.assert_called_once()
        # Vérifier que la commande startWave a été instanciée
        mock_start_wave.assert_called_once_with(self.mock_simulation)

    @patch('src.view.input_handler.placeEntity')
    @patch('src.view.input_handler.EntityFactory.create_trap')
    def test_place_trap(self, mock_create_trap, mock_place_entity):
        # Appeler la méthode pour placer un piège
        self.input_handler.place_trap((2, 2))
        
        # Vérifier que la factory a été appelée
        mock_create_trap.assert_called_once_with(damage=10)
        
        # Vérifier que la commande pour placer l'entité a été appelée
        self.mock_invoker.push_command.assert_called_once()
        self.mock_invoker.execute.assert_called_once()
        mock_place_entity.assert_called_once()

if __name__ == '__main__':
    unittest.main()
