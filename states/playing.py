import pygame
from .state import GameState
from ui import Text, Button

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.elements = []
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")  # Switch state

    def draw(self, screen):
        screen.fill(self.game.theme["bg"])
        for element in self.elements:
            element.text_color = self.game.theme["text"]  # Update text color
            if isinstance(element, Button):
                element.color = self.game.theme["border"]  # Update button border
            element.draw(screen)
