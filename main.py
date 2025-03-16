import pygame
from sys import exit
from states import MenuState, PlayingState

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

        # state management
        self.states = {
            "menu": MenuState(self),
            "playing": PlayingState(self)
        }
        self.current_state = self.states["menu"]

    def change_state(self, new_state):
        self.current_state = self.states[new_state]

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