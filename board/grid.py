import pygame
from .cell import Cell

class Grid:
    def __init__(self, grid_size, game):
        self.grid_size = grid_size
        self.game = game
        
        screen_width, screen_height = game.screen.get_size()
        grid_height = int(screen_height * 0.8)
        self.cell_size = grid_height // grid_size
        self.offset_x = (screen_width - grid_size * self.cell_size) // 2
        self.offset_y = (screen_height - grid_height) // 2

        self.cells = [[Cell(r, c, self.cell_size, self.offset_x, self.offset_y, game) 
                      for c in range(grid_size)] for r in range(grid_size)]
        self.selected_cell = None
        self.note_mode = False
        self.initialize_grid()

    def initialize_grid(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.cells[r][c].value = self.game.logic.puzzle_grid[r][c] if self.game.logic.puzzle_grid[r][c] != 0 else None
                self.cells[r][c].candidates = set()
                self.cells[r][c].temp_wrong = False
                self.cells[r][c].show_candidates = self.note_mode

    def draw(self, screen, font):
        theme = self.game.theme
        
        # Draw cells
        for row in self.cells:
            for cell in row:
                cell.draw(screen, font, cell == self.selected_cell)

        # Draw thick borders for 3x3 boxes
        for i in range(0, self.grid_size + 1, 3):
            thickness = 3
            pygame.draw.line(screen, theme["border"], 
                           (self.offset_x + i * self.cell_size, self.offset_y),
                           (self.offset_x + i * self.cell_size, self.offset_y + self.grid_size * self.cell_size),
                           thickness)
            pygame.draw.line(screen, theme["border"],
                           (self.offset_x, self.offset_y + i * self.cell_size),
                           (self.offset_x + self.grid_size * self.cell_size, self.offset_y + i * self.cell_size),
                           thickness)

    def update(self):
        for row in self.cells:
            for cell in row:
                cell.update()

    def handle_click(self, mouse_pos):
        grid_rect = pygame.Rect(self.offset_x, self.offset_y, 
                               self.grid_size * self.cell_size, 
                               self.grid_size * self.cell_size)

        if grid_rect.collidepoint(mouse_pos):
            for row in self.cells:
                for cell in row:
                    if pygame.Rect(cell.x, cell.y, cell.size, cell.size).collidepoint(mouse_pos):
                        self.selected_cell = cell
                        self.highlight_cells()
                        return
        self.selected_cell = None
        self.clear_highlights()

    def handle_keypress(self, key):
        if self.selected_cell:
            if key == pygame.K_n:  # Toggle note mode
                self.toggle_note_mode()
            else:
                self.selected_cell.handle_keypress(key, self.note_mode)

    def toggle_note_mode(self):
        self.note_mode = not self.note_mode
        for row in self.cells:
            for cell in row:
                cell.show_candidates = self.note_mode

    def highlight_cells(self):
        self.clear_highlights()
        if not self.selected_cell or self.selected_cell.value is None:
            return
            
        selected_value = self.selected_cell.value
        for row in self.cells:
            for cell in row:
                # Highlight row, column and box
                if (cell.row == self.selected_cell.row or 
                    cell.col == self.selected_cell.col or
                    (cell.row // 3 == self.selected_cell.row // 3 and 
                     cell.col // 3 == self.selected_cell.col // 3)):
                    cell.highlighted = True
                
                # Highlight same numbers
                if cell.value == selected_value:
                    cell.same_number = True

    def clear_highlights(self):
        """Clear all cell highlighting"""
        for row in self.cells:
            for cell in row:
                cell.highlighted = False
                cell.same_number = False
                cell.temp_wrong = False