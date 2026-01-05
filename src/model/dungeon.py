from __future__ import annotations

from .cell import Cell

class Dungeon:
    """
    Représente un donjon.
    
    Attributes:
        dimension : tuple(int, int): Dimensions du donjon (lignes, colonnes)
        grid : list[list[Cell]]: Grille 2D de cellules du donjon
        entry : tuple(int, int): Coordonnées de l'entrée du donjon
        exit : tuple(int, int): Coordonnées de la sortie du donjon
    """
    

    
    def __init__(self, dimension: tuple[int,int], grid: list[list[Cell]], entry: tuple[int,int], exit: tuple[int,int]):   
        """
        Initialise un donjon avec des dimensions, une grille de cellules, une entrée et une sortie.
        """    
        self.dimension = dimension
        self.grid = grid
        self.entry = entry
        self.exit = exit
    
    def get_cell(self, coord: tuple[int,int]) -> Cell:
        """Retourne la cellule aux coordonnées spécifiées."""
        row, col = coord
        return self.grid[row][col]
    
    def is_within_bounds(self, coord: tuple[int,int]) -> bool:
        """Vérifie si les coordonnées sont dans les limites du donjon."""
        row, col = coord
        return 0 <= row < self.dimension[0] and 0 <= col < self.dimension[1]
    
    def __repr__(self) -> str:
        return f"Dungeon(dimension={self.dimension}, entry={self.entry}, exit={self.exit})"
    
