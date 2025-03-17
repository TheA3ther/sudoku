import pygame
from .state import GameState
from ui import Text, Button
from board import Grid

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.grid = Grid(9, self.game)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")  # Switch state
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.grid.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN and self.grid.selected_cell:
                self.grid.selected_cell.handle_keypress(event.key)  # Enter number

    def update(self):
        self.grid.update()

    def draw(self, screen):
        screen.fill(self.game.theme["bg"])
        self.grid.draw(screen, self.game.board_font)