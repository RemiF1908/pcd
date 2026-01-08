
import unittest
from unittest.mock import MagicMock, patch
from src.view.input_handler import InputHandler

class TestInputHandler(unittest.TestCase):

    def setUp(self):
        # Création de mocks pour les dépendances
        self.mock_tui_view = MagicMock()
        self.mock_invoker = MagicMock()
        
        # Initialisation de l'InputHandler avec les mocks
        self.input_handler = InputHandler(self.mock_tui_view, self.mock_invoker)

    def test_move_cursor_up(self):
        # Simuler un état initial du curseur
        self.mock_tui_view.cursor_pos = (5, 5)
        self.mock_tui_view.dimension = (10, 10)
        
        # Appeler la méthode à tester
        self.input_handler.move_cursor_up()
        
        # Vérifier que la position du curseur a été mise à jour correctement
        self.assertEqual(self.mock_tui_view.cursor_pos, (4, 5))

    def test_quit(self):
        # Mettre l'état 'running' à True initialement
        self.mock_tui_view.running = True
        
        # Appeler la méthode pour quitter
        self.input_handler.quit()
        
        # Vérifier que l'état 'running' est passé à False
        self.assertFalse(self.mock_tui_view.running)

    @patch('src.view.tui.input_handler.startWave')
    def test_start_wave(self, mock_start_wave):
        # Appeler la méthode pour démarrer une vague
        self.input_handler.start_wave()
        
        # Vérifier qu'une commande a été poussée et exécutée
        self.mock_invoker.push_command.assert_called_once()
        self.mock_invoker.execute.assert_called_once()
        # Vérifier que la commande startWave a été instanciée
        mock_start_wave.assert_called_once_with(self.mock_tui_view.simulation)

    @patch('src.view.tui.input_handler.placeEntity')
    @patch('src.view.tui.input_handler.EntityFactory.create_trap')
    def test_place_trap(self, mock_create_trap, mock_place_entity):
        # Simuler la position du curseur
        self.mock_tui_view.cursor_pos = (2, 2)
        
        # Appeler la méthode pour placer un piège
        self.input_handler.place_trap()
        
        # Vérifier que la factory a été appelée
        mock_create_trap.assert_called_once_with(damage=10)
        
        # Vérifier que la commande pour placer l'entité a été appelée
        self.mock_invoker.push_command.assert_called_once()
        self.mock_invoker.execute.assert_called_once()
        mock_place_entity.assert_called_once()

if __name__ == '__main__':
    unittest.main()
