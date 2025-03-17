import pygame 
from board import Cell

class Grid:
    def __init__(self, grid_size, game):
        self.grid_size = grid_size  # 9 (for 9x9 Sudoku)
        self.game = game  # Reference to the game for theme access
        
        # Calculate cell size based on available screen space
        screen_width, screen_height = game.screen.get_size()
        grid_height = int(screen_height * 0.8)  # Use 80% of screen height
        self.cell_size = grid_height // grid_size  # Calculate cell size dynamically
        
        # Calculate center position
        self.offset_x = (screen_width - grid_size * self.cell_size) // 2
        self.offset_y = (screen_height - grid_height) // 2

        self.cells = [[Cell(r, c, self.cell_size, self.offset_x, self.offset_y, game) for c in range(grid_size)] for r in range(grid_size)]
        self.selected_cell = None  # Currently selected cell

    def draw(self, screen, font):
        theme = self.game.theme
        
        # Draw cells
        for row in self.cells:
            for cell in row:
                cell.draw(screen, font, cell == self.selected_cell)

        # Draw thick 3x3 subgrid borders
        for i in range(0, self.grid_size + 1, 3):
            thickness = 5
            pygame.draw.line(screen, theme["border"], (self.offset_x + i * self.cell_size, self.offset_y), (self.offset_x + i * self.cell_size, self.offset_y + self.grid_size * self.cell_size), thickness)
            pygame.draw.line(screen, theme["border"], (self.offset_x, self.offset_y + i * self.cell_size), (self.offset_x + self.grid_size * self.cell_size, self.offset_y + i * self.cell_size), thickness)

    def update(self):
        if self.selected_cell:
            self.selected_cell.update(True)

    def handle_click(self, mouse_pos):
        for row in self.cells:
            for cell in row:
                rect = pygame.Rect(cell.x, cell.y, cell.size, cell.size)
                if rect.collidepoint(mouse_pos):
                    self.selected_cell = cell
                    return
