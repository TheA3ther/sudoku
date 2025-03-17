import pygame
from sys import exit
from states import MenuState, PlayingState


LIGHT_MODE = {"bg": (255, 255, 255), "border": (0, 0, 0), "text": (0, 0, 0)}
DARK_MODE = {"bg": (0, 0, 0), "border": (255, 255, 255), "text": (255, 255, 255)}

class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()

        # initialize screen size
        self.screen = pygame.display.set_mode((1280, 720)) 

        # initialize clock
        self.clock = pygame.time.Clock()

        # initialize font
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 144)

        # initialize theme
        self.theme = LIGHT_MODE

        # state management
        self.states = {
            "menu": MenuState(self),
            "playing": PlayingState(self)
        }
        self.current_state = self.states["menu"]

    def change_state(self, new_state):
        self.current_state = self.states[new_state]

    def toggle_theme(self):
        """Toggles theme globally for all states."""
        self.theme = DARK_MODE if self.theme == LIGHT_MODE else LIGHT_MODE

    def quit(*args):
        pygame.quit()
        exit()

    def run(self):
        running = True

        while running:
            # get event list
            events = pygame.event.get()

            # general event handler
            for event in events:
                # quit game
                if event.type == pygame.QUIT:
                    print("bye")
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    self.toggle_theme()


            # run current_state funcs
            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.draw(self.screen)
                        
            # update frame
            pygame.display.update()
            self.clock.tick(30)

if __name__ == "__main__":
    game = Game()
    game.run()