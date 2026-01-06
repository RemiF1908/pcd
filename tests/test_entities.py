from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.entity import Entity


def test_floor_and_wall_and_trap_behaviour():
    floor = Floor()
    wall = Wall()
    trap = Trap(damage=7)

    c_floor = Cell((0, 0), floor)
    assert c_floor.is_walkable()
    assert not c_floor.is_dangerous()
    assert c_floor.get_damage() == 0

    c_wall = Cell((0, 1), wall)
    assert not c_wall.is_walkable()
    assert not c_wall.is_dangerous()
    assert c_wall.get_damage() == 0

    c_trap = Cell((1, 0), trap)
    assert c_trap.is_walkable()
    assert c_trap.is_dangerous()
    assert c_trap.get_damage() == 7


def test_entity_display_polymorphism():
    """Test des méthodes polymorphiques get_display_char() et get_color_id()."""
    floor = Floor()
    wall = Wall()
    trap = Trap(damage=10)

    # Vérifier que chaque entité retourne le bon caractère
    assert floor.get_display_char() == "."
    assert wall.get_display_char() == "#"
    assert trap.get_display_char() == "^"

    # Vérifier que chaque entité retourne un ID de couleur valide (int)
    assert isinstance(floor.get_color_id(), int)
    assert isinstance(wall.get_color_id(), int)
    assert isinstance(trap.get_color_id(), int)

    # Vérifier les couleurs spécifiques (paires curses)
    assert floor.get_color_id() == 1  # Paire 1 : Floor (blanc/gris)
    assert wall.get_color_id() == 2   # Paire 2 : Wall (blanc brillant)
    assert trap.get_color_id() == 3   # Paire 3 : Trap (rouge)


def test_entities_inherit_from_entity():
    """Vérifie que toutes les entités héritent bien de Entity."""
    floor = Floor()
    wall = Wall()
    trap = Trap()

    assert isinstance(floor, Entity)
    assert isinstance(wall, Entity)
    assert isinstance(trap, Entity)


def test_entity_abstract_methods_exist():
    """Vérifie que les méthodes abstraites sont bien définies."""
    # Ces méthodes doivent exister sur toutes les entités
    for entity_cls in [Floor, Wall, Trap]:
        entity = entity_cls() if entity_cls != Trap else entity_cls(damage=5)
        
        # Vérifier que les méthodes existent et sont appelables
        assert hasattr(entity, "get_display_char")
        assert hasattr(entity, "get_color_id")
        assert callable(entity.get_display_char)
        assert callable(entity.get_color_id)
        
        # Vérifier les types de retour
        assert isinstance(entity.get_display_char(), str)
        assert len(entity.get_display_char()) == 1  # Un seul caractère
        assert isinstance(entity.get_color_id(), int)


