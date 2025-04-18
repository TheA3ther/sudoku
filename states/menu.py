import pygame
from .state import GameState
from ui import Text, Button

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.initialize_ui()

    def initialize_ui(self):
        font = self.game.font
        title_font = self.game.title_font
        self.border_color = self.game.theme["border"]
        self.text_color = self.game.theme["text"]

        # Getting screen dimensions
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()

        # Title
        self.title = Text(screen_width/2, 200, "Sudoku", title_font, self.text_color)

        # Buttons
        self.play_button = Button(screen_width/2, 450, 200, 50, self.border_color, 
                                "Play", font, self.text_color, 
                                lambda: self.game.change_state("playing"))
        self.quit_button = Button(screen_width/2, 525, 200, 50, self.border_color, 
                                "Quit", font, self.text_color, self.game.quit)

        self.elements = [self.title, self.play_button, self.quit_button]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_state("playing")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle buttons first
                for element in self.elements:
                    if isinstance(element, Button):
                        if element.handle_event(event):
                            return  # Stop processing if button was clicked

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.game.theme["bg"])
        for element in self.elements:
            element.text_color = self.game.theme["text"]  # Update text color
            if isinstance(element, Button):
                element.color = self.game.theme["border"]  # Update button border
            element.draw(screen)

    def on_enter(self):
        self.initialize_ui()