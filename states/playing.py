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
        self.note_mode_text = Text(50, 170, "Note Mode: OFF", self.game.font, self.game.theme["text"])
        
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
        self.note_button = Button(screen_width - 100, 170, 80, 30,
                                self.game.theme["border"], "Notes",
                                self.game.font, self.game.theme["text"],
                                self.toggle_note_mode)

    def toggle_note_mode(self):
        self.grid.note_mode = not self.grid.note_mode
        # Update all cells to show/hide candidates
        for row in self.grid.cells:
            for cell in row:
                cell.show_candidates = self.grid.note_mode
        self.note_mode_text.text = f"Note Mode: {'ON' if self.grid.note_mode else 'OFF'}"

    def provide_hint(self):
        hint_cell = self.game.logic.provide_hint()
        if hint_cell:
            row, col = hint_cell
            self.grid.cells[row][col].value = self.game.logic.user_grid[row][col]
            self.grid.cells[row][col].candidates = set()  # Clear candidates when hint is used

    def next_game(self):
        self.game.logic.next_game()
        self.grid.initialize_grid()
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"  # Reset note mode display
        self.grid.note_mode = False  # Reset note mode

    def update_game_info(self):
        self.game_info.text = f"Puzzle: {self.game.logic.current_game_index + 1}/{len(self.game.logic.baseline_games)}"
        self.difficulty_text.text = f"Difficulty: {self.game.logic.baseline_games[self.game.logic.current_game_index]['label']}"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")
                elif event.key == pygame.K_n:  # Toggle note mode with N key
                    self.toggle_note_mode()
                elif self.grid.selected_cell:
                    self.grid.handle_keypress(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.grid.handle_click(event.pos)
                for button in [self.hint_button, self.menu_button, self.next_button, self.note_button]:
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
        self.note_mode_text.draw(screen)
        
        # Draw buttons
        self.hint_button.draw(screen)
        self.menu_button.draw(screen)
        self.next_button.draw(screen)
        self.note_button.draw(screen)

    def handle_game_over(self):
        self.game.logic.log_game_result("loss")
        self.game.change_state("menu")

    def handle_game_complete(self):
        self.game.logic.log_game_result("win")
        self.game.logic.next_game()
        self.grid.initialize_grid()
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"
        self.grid.note_mode = False