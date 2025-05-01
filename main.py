import pygame
from sys import exit
from states import MenuState, PlayingState
from logic import SudokuLogic

# Enhanced theme system with all required keys
LIGHT_MODE = {
    "bg": (255, 255, 255),        # White background
    "border": (0, 0, 0),          # Black borders
    "text": (0, 0, 0),            # Black text
    "button_bg": (200, 200, 200), # Light gray buttons
    "button_text": (0, 0, 0),     # Black button text
    "button_hover": (170, 170, 170), # Button hover state
    "button_press": (140, 140, 140)  # Button pressed state
}

DARK_MODE = {
    "bg": (0, 0, 0),              # Black background
    "border": (255, 255, 255),    # White borders
    "text": (255, 255, 255),      # White text
    "button_bg": (50, 50, 50),    # Dark gray buttons
    "button_text": (255, 255, 255), # White button text
    "button_hover": (80, 80, 80),   # Button hover state
    "button_press": (110, 110, 110)  # Button pressed state
}

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Sudoku")

        # Initialize screen
        self.screen = pygame.display.set_mode((1280, 720))
        
        # Initialize clock
        self.clock = pygame.time.Clock()

        # Initialize fonts
        self.font = pygame.font.Font(None, 36)
        self.board_font = pygame.font.Font(None, 56)
        self.title_font = pygame.font.Font(None, 144)

        # Initialize theme
        self.theme = LIGHT_MODE

        # Initialize game logic
        self.logic = SudokuLogic()

        # State management
        self.states = {
            "menu": MenuState(self),
            "playing": PlayingState(self)
        }
        self.current_state = self.states["menu"]

    def change_state(self, new_state):
        self.current_state = self.states[new_state]
        self.current_state.on_enter()

    def toggle_theme(self):
        self.theme = DARK_MODE if self.theme == LIGHT_MODE else LIGHT_MODE
        # Force redraw of all UI elements
        if hasattr(self.current_state, 'on_enter'):
            self.current_state.on_enter()

    def quit(self):
        self.logic.save_progress()
        pygame.quit()
        exit()

    def run(self):
        while True:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    self.toggle_theme()

            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(30)

if __name__ == "__main__":
    game = Game()
    game.run()