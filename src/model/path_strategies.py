from abc import ABC, abstractmethod
from typing import List, Tuple
import heapq


class PathStrategy(ABC):
    """Abstract base class for pathfinding strategies."""
    
    @abstractmethod
    def find_path(
        self,
        dungeon,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Find a path from start to goal.
        
        Args:
            dungeon: Dungeon instance containing the grid
            start: Starting coordinates (row, col)
            goal: Goal coordinates (row, col)
        
        Returns:
            List of coordinates from start to goal (inclusive)
        """
        pass


class ShortestPathStrategy(PathStrategy):
    """A* pathfinding that ignores traps (shortest path)."""
    
    def find_path(
        self,
        dungeon,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Find shortest path using A* algorithm, ignoring trap damage."""
        if start == goal:
            return [start]
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                return self._reconstruct_path(came_from, current)
            
            for neighbor in self._get_neighbors(dungeon, current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _get_neighbors(
        self,
        dungeon,
        coord: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Get walkable neighbors (including traps)."""
        row, col = coord
        neighbors = []
        
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_coord = (row + d_row, col + d_col)
            if dungeon.validMove(new_coord):
                neighbors.append(new_coord)
        
        return neighbors
    
    def _reconstruct_path(
        self,
        came_from: dict,
        current: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]


class SafestPathStrategy(PathStrategy):
    """Pathfinding that minimizes damage from traps."""
    
    def find_path(
        self,
        dungeon,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Find path minimizing total trap damage using Dijkstra's algorithm."""
        if start == goal:
            return [start]
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        damage_score = {start: 0}
        
        while open_set:
            current_damage, current = heapq.heappop(open_set)
            
            if current == goal:
                return self._reconstruct_path(came_from, current)
            
            if current_damage > damage_score[current]:
                continue
            
            for neighbor in self._get_neighbors(dungeon, current):
                cell = dungeon.get_cell(neighbor)
                cell_damage = cell.entity.damage if cell.entity else 0
                new_damage = damage_score[current] + cell_damage
                
                if neighbor not in damage_score or new_damage < damage_score[neighbor]:
                    came_from[neighbor] = current
                    damage_score[neighbor] = new_damage
                    heapq.heappush(open_set, (new_damage, neighbor))
        
        return []
    
    def _get_neighbors(
        self,
        dungeon,
        coord: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Get walkable neighbors (including traps)."""
        row, col = coord
        neighbors = []
        
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_coord = (row + d_row, col + d_col)
            if dungeon.validMove(new_coord):
                neighbors.append(new_coord)
        
        return neighbors
    
    def _reconstruct_path(
        self,
        came_from: dict,
        current: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]


class PathStrategyFactory:
    """Factory for creating path strategies."""
    
    _strategies = {
        "shortest": ShortestPathStrategy,
        "safest": SafestPathStrategy,
    }
    
    @classmethod
    def create(cls, strategy_name: str) -> PathStrategy:
        """Create a path strategy by name.
        
        Args:
            strategy_name: Name of the strategy ("shortest" or "safest")
        
        Returns:
            PathStrategy instance
        
        Raises:
            ValueError: If strategy name is unknown
        """
        strategy_class = cls._strategies.get(strategy_name.lower())
        if strategy_class is None:
            raise ValueError(f"Unknown strategy: {strategy_name}. "
                           f"Available strategies: {list(cls._strategies.keys())}")
        return strategy_class()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type) -> None:
        """Register a new strategy.
        
        Args:
            name: Strategy name
            strategy_class: Strategy class (must inherit from PathStrategy)
        """
        if not issubclass(strategy_class, PathStrategy):
            raise TypeError(f"{strategy_class} must inherit from PathStrategy")
        cls._strategies[name.lower()] = strategy_class
