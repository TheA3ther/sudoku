import pygame
from states.state import GameState

class MenuState(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_state("playing")  # Switch state

    def draw(self, screen):
        screen.fill((50, 50, 50))