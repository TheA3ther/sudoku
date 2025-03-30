import pygame
import time
from .state import GameState
from ui import Text, Button
from board import Grid

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.grid = Grid(9, self.game)
        
        # Game info display
        self.timer_text = Text(50, 50, "Time: 0", self.game.font, self.game.theme["text"])
        self.mistakes_text = Text(50, 80, "Mistakes: 0/3", self.game.font, self.game.theme["text"])
        self.game_info = Text(50, 110, f"Puzzle: {self.game.logic.current_game_index + 1}/{len(self.game.logic.baseline_games)}", 
                            self.game.font, self.game.theme["text"])
        self.difficulty_text = Text(50, 140, f"Difficulty: {self.game.logic.baseline_games[self.game.logic.current_game_index]['label']}", 
                                  self.game.font, self.game.theme["text"])
        
        # Buttons
        screen_width = self.game.screen.get_width()
        self.hint_button = Button(screen_width - 100, 50, 80, 30, 
                                self.game.theme["border"], "Hint", 
                                self.game.font, self.game.theme["text"],
                                self.provide_hint)
        self.menu_button = Button(screen_width - 100, 90, 80, 30,
                                self.game.theme["border"], "Menu",
                                self.game.font, self.game.theme["text"],
                                lambda: self.game.change_state("menu"))
        self.next_button = Button(screen_width - 100, 130, 80, 30,
                                self.game.theme["border"], "Next",
                                self.game.font, self.game.theme["text"],
                                self.next_game)

    def provide_hint(self):
        hint_cell = self.game.logic.provide_hint()
        if hint_cell:
            row, col = hint_cell
            self.grid.cells[row][col].value = self.game.logic.user_grid[row][col]

    def next_game(self):
        self.game.logic.next_game()
        self.grid.initialize_grid()
        self.update_game_info()

    def update_game_info(self):
        self.game_info.text = f"Puzzle: {self.game.logic.current_game_index + 1}/{len(self.game.logic.baseline_games)}"
        self.difficulty_text.text = f"Difficulty: {self.game.logic.baseline_games[self.game.logic.current_game_index]['label']}"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")
                elif self.grid.selected_cell:
                    self.grid.selected_cell.handle_keypress(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.grid.handle_click(event.pos)
                for button in [self.hint_button, self.menu_button, self.next_button]:
                    button.handle_event(event)
                
                if self.game.logic.check_completion():
                    self.handle_game_complete()

    def update(self):
        self.grid.update()
        elapsed = int(time.time() - self.game.logic.start_time)
        self.timer_text.text = f"Time: {elapsed}s"
        self.mistakes_text.text = f"Mistakes: {self.game.logic.mistakes}/3"
        
        if self.game.logic.mistakes >= 3:
            self.handle_game_over()

    def draw(self, screen):
        screen.fill(self.game.theme["bg"])
        self.grid.draw(screen, self.game.board_font)
        
        # Draw game info
        self.timer_text.draw(screen)
        self.mistakes_text.draw(screen)
        self.game_info.draw(screen)
        self.difficulty_text.draw(screen)
        
        # Draw buttons
        self.hint_button.draw(screen)
        self.menu_button.draw(screen)
        self.next_button.draw(screen)

    def handle_game_over(self):
        self.game.logic.log_game_result("loss")
        self.game.change_state("menu")

    def handle_game_complete(self):
        self.game.logic.log_game_result("win")
        self.game.logic.next_game()
        self.grid.initialize_grid()
        self.update_game_info()