"""Tests for pathfinding strategies."""

import pytest
from src.model.path_strategies import (
    PathStrategy,
    ShortestPathStrategy,
    SafestPathStrategy,
    PathStrategyFactory
)
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.entity_factory import EntityFactory


def create_simple_dungeon():
    """Create a simple 3x3 dungeon with no obstacles."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(2, 2))
    return dungeon


def create_dungeon_with_traps():
    """Create a dungeon with traps on the shortest path."""
    rows, cols = 5, 5
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(4, 4))
    
    # Place traps along the diagonal (shortest path)
    dungeon.place_entity(EntityFactory.create_trap(damage=10), (1, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=10), (2, 2))
    dungeon.place_entity(EntityFactory.create_trap(damage=10), (3, 3))
    
    return dungeon


def create_dungeon_with_walls():
    """Create a dungeon with walls forcing path around traps."""
    rows, cols = 5, 5
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(4, 4))
    
    # Create a wall in the middle
    for c in range(1, 4):
        dungeon.place_entity(EntityFactory.create_wall(), (2, c))
    
    # Place traps on the left path
    dungeon.place_entity(EntityFactory.create_trap(damage=20), (1, 0))
    dungeon.place_entity(EntityFactory.create_trap(damage=20), (3, 0))
    
    # Place smaller traps on the right path
    dungeon.place_entity(EntityFactory.create_trap(damage=5), (1, 4))
    dungeon.place_entity(EntityFactory.create_trap(damage=5), (3, 4))
    
    return dungeon


def calculate_path_damage(dungeon, path):
    """Calculate total damage a hero would take on a path."""
    total_damage = 0
    for coord in path:
        cell = dungeon.get_cell(coord)
        if cell.entity:
            total_damage += cell.entity.damage
    return total_damage


class TestShortestPathStrategy:
    """Tests for ShortestPathStrategy (A* ignoring traps)."""
    
    def test_find_path_simple(self):
        """Test finding shortest path in simple dungeon."""
        dungeon = create_simple_dungeon()
        strategy = ShortestPathStrategy()
        start = (0, 0)
        goal = (2, 2)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        assert len(path) == 5  # Manhattan distance is 4, +1 for start
    
    def test_find_path_with_traps(self):
        """Test that shortest path goes through traps."""
        dungeon = create_dungeon_with_traps()
        strategy = ShortestPathStrategy()
        start = (0, 0)
        goal = (4, 4)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path is not None
        assert len(path) == 9  # Manhattan distance
        assert path[0] == start
        assert path[-1] == goal
    
    def test_find_path_with_walls(self):
        """Test finding path around walls."""
        dungeon = create_dungeon_with_walls()
        strategy = ShortestPathStrategy()
        start = (0, 0)
        goal = (4, 4)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        
        # Verify path doesn't go through walls
        for coord in path:
            cell = dungeon.get_cell(coord)
            assert cell.is_walkable()
    
    def test_find_path_start_equals_goal(self):
        """Test path when start equals goal."""
        dungeon = create_simple_dungeon()
        strategy = ShortestPathStrategy()
        start = goal = (1, 1)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path == [start]
    
    def test_find_path_no_path_exists(self):
        """Test when no path exists (blocked by walls)."""
        rows, cols = 3, 3
        grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
        dungeon = Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(2, 2))
        
        # Block the path completely
        dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
        dungeon.place_entity(EntityFactory.create_wall(), (1, 0))
        dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
        
        strategy = ShortestPathStrategy()
        start = (0, 0)
        goal = (2, 2)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path == []


class TestSafestPathStrategy:
    """Tests for SafestPathStrategy (minimizing damage)."""
    
    def test_find_path_simple(self):
        """Test finding path in simple dungeon with no traps."""
        dungeon = create_simple_dungeon()
        strategy = SafestPathStrategy()
        start = (0, 0)
        goal = (2, 2)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        assert len(path) == 5
    
    def test_find_path_with_traps(self):
        """Test that safest path avoids traps when possible."""
        dungeon = create_dungeon_with_walls()
        strategy = SafestPathStrategy()
        start = (0, 0)
        goal = (4, 4)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        
        damage = calculate_path_damage(dungeon, path)
        
        # The path should have minimal damage (right side has 5+5=10 damage)
        assert damage <= 10
    
    def test_find_path_minimizes_damage(self):
        """Test that safest path actually minimizes damage."""
        dungeon = create_dungeon_with_walls()
        
        # Compare both strategies
        shortest_strategy = ShortestPathStrategy()
        safest_strategy = SafestPathStrategy()
        
        start = (0, 0)
        goal = (4, 4)
        
        shortest_path = shortest_strategy.find_path(dungeon, start, goal)
        safest_path = safest_strategy.find_path(dungeon, start, goal)
        
        shortest_damage = calculate_path_damage(dungeon, shortest_path)
        safest_damage = calculate_path_damage(dungeon, safest_path)
        
        # Safest path should have less or equal damage
        assert safest_damage <= shortest_damage
    
    def test_find_path_start_equals_goal(self):
        """Test path when start equals goal."""
        dungeon = create_simple_dungeon()
        strategy = SafestPathStrategy()
        start = goal = (1, 1)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path == [start]
    
    def test_find_path_no_path_exists(self):
        """Test when no path exists (blocked by walls)."""
        rows, cols = 3, 3
        grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
        dungeon = Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(2, 2))
        
        dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
        dungeon.place_entity(EntityFactory.create_wall(), (1, 0))
        dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
        
        strategy = SafestPathStrategy()
        start = (0, 0)
        goal = (2, 2)
        
        path = strategy.find_path(dungeon, start, goal)
        
        assert path == []


class TestPathStrategyFactory:
    """Tests for PathStrategyFactory."""
    
    def test_create_shortest_strategy(self):
        """Test creating shortest path strategy."""
        strategy = PathStrategyFactory.create("shortest")
        
        assert isinstance(strategy, ShortestPathStrategy)
        assert isinstance(strategy, PathStrategy)
    
    def test_create_safest_strategy(self):
        """Test creating safest path strategy."""
        strategy = PathStrategyFactory.create("safest")
        
        assert isinstance(strategy, SafestPathStrategy)
        assert isinstance(strategy, PathStrategy)
    
    def test_create_case_insensitive(self):
        """Test that strategy names are case insensitive."""
        shortest = PathStrategyFactory.create("SHORTEST")
        safest = PathStrategyFactory.create("Safest")
        
        assert isinstance(shortest, ShortestPathStrategy)
        assert isinstance(safest, SafestPathStrategy)
    
    def test_create_unknown_strategy(self):
        """Test that unknown strategy raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PathStrategyFactory.create("unknown")
        
        assert "Unknown strategy" in str(exc_info.value)
    
    def test_register_custom_strategy(self):
        """Test registering a custom strategy."""
        class CustomStrategy(PathStrategy):
            def find_path(self, dungeon, start, goal):
                return [start, goal]
        
        PathStrategyFactory.register_strategy("custom", CustomStrategy)
        strategy = PathStrategyFactory.create("custom")
        
        assert isinstance(strategy, CustomStrategy)
    
    def test_register_invalid_strategy(self):
        """Test that registering invalid strategy raises TypeError."""
        class NotAStrategy:
            pass
        
        with pytest.raises(TypeError):
            PathStrategyFactory.register_strategy("invalid", NotAStrategy)


class TestStrategyIntegration:
    """Integration tests for path strategies with heroes and levels."""
    
    def test_hero_compute_path_shortest(self):
        """Test hero computing path with shortest strategy."""
        from src.model.hero import Hero
        
        dungeon = create_dungeon_with_traps()
        hero = Hero(pv_total=100, strategy="shortest", coord=(0, 0))
        
        hero.compute_path(dungeon, (0, 0), (4, 4))
        
        assert hero.path is not None
        assert len(hero.path) > 0
        assert hero.path[0] == (0, 0)
        assert hero.path[-1] == (4, 4)
    
    def test_hero_compute_path_safest(self):
        """Test hero computing path with safest strategy."""
        from src.model.hero import Hero
        
        dungeon = create_dungeon_with_walls()
        hero = Hero(pv_total=100, strategy="safest", coord=(0, 0))
        
        hero.compute_path(dungeon, (0, 0), (4, 4))
        
        assert hero.path is not None
        assert len(hero.path) > 0
        assert hero.path[0] == (0, 0)
        assert hero.path[-1] == (4, 4)
        
        damage = calculate_path_damage(dungeon, hero.path)
        assert damage <= 10  # Should take the right path with less damage
    
    def test_level_build_creates_paths(self):
        """Test that level builder computes paths for heroes."""
        from src.model.level import LevelBuilder
        
        dungeon = create_dungeon_with_traps()
        
        level = (LevelBuilder()
            .set_dungeon(dungeon)
            .add_hero(pv=100, strategy="shortest")
            .add_hero(pv=100, strategy="safest")
            .build())
        
        assert len(level.heroes) == 2
        
        # Both heroes should have paths computed
        for hero in level.heroes:
            assert hero.path is not None
            assert len(hero.path) > 0
            assert hero.path[0] == dungeon.entry
            assert hero.path[-1] == dungeon.exit
    
    def test_comparison_shortest_vs_safest(self):
        """Compare shortest vs safest strategy in a scenario with traps."""
        from src.model.hero import Hero
        
        dungeon = create_dungeon_with_walls()
        
        hero_shortest = Hero(pv_total=100, strategy="shortest", coord=(0, 0))
        hero_safest = Hero(pv_total=100, strategy="safest", coord=(0, 0))
        
        hero_shortest.compute_path(dungeon, (0, 0), (4, 4))
        hero_safest.compute_path(dungeon, (0, 0), (4, 4))
        
        # Both should have valid paths
        assert len(hero_shortest.path) > 0
        assert len(hero_safest.path) > 0
        
        # Calculate damage for both paths
        shortest_damage = calculate_path_damage(dungeon, hero_shortest.path)
        safest_damage = calculate_path_damage(dungeon, hero_safest.path)
        
        # Safest should have less or equal damage
        assert safest_damage <= shortest_damage
        
        # Shortest should be shorter or equal in length
        assert len(hero_shortest.path) <= len(hero_safest.path)
