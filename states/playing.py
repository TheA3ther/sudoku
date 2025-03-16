import pygame
from states.state import GameState

class PlayingState(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_state("menu")  # Switch state

    def draw(self, screen):
        screen.fill((0, 128, 255))
