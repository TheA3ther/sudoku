import pygame
import time
from .state import GameState
from ui import Text, Button
from board import Grid

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.initialize_game()

    def initialize_game(self):
        self.grid = Grid(9, self.game)
        screen_width = self.game.screen.get_width()
        
        # Game info display - using current_difficulty instead of baseline_games
        self.timer_text = Text(50, 50, "Time: 0", self.game.font, self.game.theme["text"])
        self.mistakes_text = Text(50, 80, f"Mistakes: 0/{self.game.logic.max_mistakes}", 
                                self.game.font, self.game.theme["text"])
        self.game_info = Text(50, 110, f"Progress: {len(self.game.logic.learning_games)}/5", 
                            self.game.font, self.game.theme["text"])
        self.difficulty_text = Text(50, 140, f"Difficulty: {self.game.logic.current_difficulty['label']}", 
                                  self.game.font, self.game.theme["text"])
        self.note_mode_text = Text(50, 170, "Note Mode: OFF", 
                                 self.game.font, self.game.theme["text"])
        self.hint_text = Text(50, 200, f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}", 
                            self.game.font, self.game.theme["text"])
        
        # Buttons
        button_x = screen_width - 100
        button_y = 50
        button_spacing = 40
        
        self.hint_button = Button(button_x, button_y, 80, 30, 
                                self.game.theme["border"], "Hint", 
                                self.game.font, self.game.theme["text"],
                                self.provide_hint)
        button_y += button_spacing
        
        self.delete_button = Button(button_x, button_y, 80, 30,
                                  self.game.theme["border"], "Delete",
                                  self.game.font, self.game.theme["text"],
                                  self.delete_selected)
        button_y += button_spacing
        
        self.menu_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Menu",
                                self.game.font, self.game.theme["text"],
                                lambda: self.game.change_state("menu"))
        button_y += button_spacing
        
        self.next_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Next",
                                self.game.font, self.game.theme["text"],
                                self.next_game)
        button_y += button_spacing
        
        self.note_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Notes",
                                self.game.font, self.game.theme["text"],
                                self.toggle_note_mode)

    def delete_selected(self):
        if self.grid.selected_cell:
            if self.grid.selected_cell.clear_cell():
                self.update_game_info()

    def toggle_note_mode(self):
        self.grid.toggle_note_mode()
        self.note_mode_text.text = f"Note Mode: {'ON' if self.grid.note_mode else 'OFF'}"

    def provide_hint(self):
        hint_cell = self.game.logic.provide_hint()
        if hint_cell:
            row, col = hint_cell
            self.grid.cells[row][col].value = self.game.logic.user_grid[row][col]
            self.grid.cells[row][col].candidates = set()
            self.hint_text.text = f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}"

    def next_game(self):
        self.game.logic.reset_game()
        self.grid.initialize_grid()
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"
        self.hint_text.text = f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}"
        self.grid.note_mode = False

    def update_game_info(self):
        diff_info = self.game.logic.get_current_difficulty_info()
        self.game_info.text = f"Progress: {diff_info['progress']}"
        self.difficulty_text.text = f"Difficulty: {diff_info['label']}"
        self.mistakes_text.text = f"Mistakes: {self.game.logic.mistakes}/{self.game.logic.max_mistakes}"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")
                elif event.key == pygame.K_n:
                    self.toggle_note_mode()
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    if self.grid.selected_cell:
                        self.grid.selected_cell.clear_cell()
                elif self.grid.selected_cell:
                    self.grid.handle_keypress(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                button_clicked = False
                
                for button in [self.hint_button, self.delete_button, self.menu_button, 
                             self.next_button, self.note_button]:
                    if button.rect.collidepoint(mouse_pos):
                        button.on_click()
                        button_clicked = True
                        break
                
                if not button_clicked:
                    self.grid.handle_click(mouse_pos)
                
                if self.game.logic.check_completion():
                    self.handle_game_complete()

    def update(self):
        self.grid.update()
        elapsed = int(time.time() - self.game.logic.start_time)
        self.timer_text.text = f"Time: {elapsed}s"
        self.mistakes_text.text = f"Mistakes: {self.game.logic.mistakes}/{self.game.logic.max_mistakes}"
        
        if self.game.logic.mistakes >= self.game.logic.max_mistakes:
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
        self.hint_text.draw(screen)
        
        # Draw buttons
        self.hint_button.draw(screen)
        self.delete_button.draw(screen)
        self.menu_button.draw(screen)
        self.next_button.draw(screen)
        self.note_button.draw(screen)

    def handle_game_over(self):
        self.game.logic.game_over_time = time.time()
        self.game.logic.log_game_result("loss")
        self.game.logic.reset_game()
        self.game.change_state("menu")

    def handle_game_complete(self):
        self.game.logic.log_game_result("win")
        self.game.logic.next_game()
        self.grid.initialize_grid()
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"
        self.hint_text.text = f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}"
        self.grid.note_mode = False

    def on_enter(self):
        self.initialize_game()