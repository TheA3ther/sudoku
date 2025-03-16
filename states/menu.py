import pygame
from .state import GameState
from ui import Text, Button

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        font = game.font
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)

        # Title
        self.title = Text(150, 50, "Sudoku", font, self.text_color)

        # Buttons
        self.play_button = Button(200, 150, 200, 50, self.border_color, "Play", font, self.text_color, lambda: game.change_state("playing"))
        self.quit_button = Button(200, 220, 200, 50, self.border_color, "Quit", font, self.text_color, game.quit)

        self.elements = [self.title, self.play_button, self.quit_button]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_state("playing")  # Switch state
            if event.type == pygame.MOUSEBUTTONDOWN:
                for element in self.elements:
                    if isinstance(element, Button):
                        element.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.bg_color)
        for element in self.elements:
            element.draw(screen)
