import pygame
import time
import numpy as np
from .state import GameState
from ui import Text, Button
from board import Grid

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.grid = Grid(9, self.game)
        self.adaptive_notice_text = ""
        self.adaptive_notice_time = 0
        self.show_adaptive_notice = False
        self._init_ui()

    def _init_ui(self):
        """Initialize UI elements"""
        screen_width = self.game.screen.get_width()
        
        # Game info texts
        self.timer_text = Text(50, 50, "Time: 0", self.game.font, self.game.theme["text"])
        self.mistakes_text = Text(50, 80, f"Mistakes: 0/{self.game.logic.max_mistakes}", 
                                self.game.font, self.game.theme["text"])
        
        diff_info = self.game.logic.get_current_difficulty_info()
        self.game_info = Text(50, 110, f"Puzzle: {diff_info['progress']}", 
                            self.game.font, self.game.theme["text"])
        self.difficulty_text = Text(50, 140, f"Difficulty: {diff_info['label']}", 
                                  self.game.font, self.game.theme["text"])
        
        self.mode_text = Text(50, 170, f"Mode: {'ADAPTIVE' if self.game.logic.adaptive_mode else 'LEARNING'}", 
                             self.game.font, (0, 150, 0) if self.game.logic.adaptive_mode else (200, 150, 0))
        
        self.note_mode_text = Text(50, 200, "Note Mode: OFF", 
                                 self.game.font, self.game.theme["text"])
        self.hint_text = Text(50, 230, f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}", 
                             self.game.font, self.game.theme["text"])
        
        # Buttons initialization
        button_x = screen_width - 100
        button_y = 50
        button_spacing = 40
        
        self.hint_button = Button(button_x, button_y, 80, 30, 
                                self.game.theme["border"], "Hint", 
                                self.game.font, self.game.theme["text"],
                                action=self.provide_hint)
        button_y += button_spacing
        
        self.delete_button = Button(button_x, button_y, 80, 30,
                                  self.game.theme["border"], "Delete",
                                  self.game.font, self.game.theme["text"],
                                  action=self.delete_selected)
        button_y += button_spacing
        
        self.menu_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Menu",
                                self.game.font, self.game.theme["text"],
                                action=lambda: self.game.change_state("menu"))
        button_y += button_spacing
        
        self.next_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Next",
                                self.game.font, self.game.theme["text"],
                                action=self.next_game)
        button_y += button_spacing
        
        self.note_button = Button(button_x, button_y, 80, 30,
                                self.game.theme["border"], "Notes",
                                self.game.font, self.game.theme["text"],
                                action=self.toggle_note_mode)

        self.buttons = [self.hint_button, self.delete_button, 
                       self.menu_button, self.next_button, 
                       self.note_button]

    def delete_selected(self):
        if self.grid.selected_cell:
            self.grid.selected_cell.clear_cell()

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
        self.game.logic.save_progress()
        self.game.logic.reset_game()
        self.grid.initialize_grid()
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"
        self.hint_text.text = f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}"
        self.grid.note_mode = False

    def update_game_info(self):
        diff_info = self.game.logic.get_current_difficulty_info()
        self.game_info.text = f"Puzzle: {diff_info['progress']}"
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
                pos = pygame.mouse.get_pos()
                self.grid.handle_click(pos)
                
                for button in self.buttons:
                    button.handle_event(event)
                
                if self.game.logic.check_completion():
                    self._handle_game_completion()

    def update(self):
        self.grid.update()
        elapsed = int(time.time() - self.game.logic.start_time)
        self.timer_text.text = f"Time: {elapsed}s"
        self.mistakes_text.text = f"Mistakes: {self.game.logic.mistakes}/{self.game.logic.max_mistakes}"
        
        if self.game.logic.mistakes >= self.game.logic.max_mistakes:
            self._handle_game_over()

    def draw(self, screen):
        screen.fill(self.game.theme["bg"])
        self.grid.draw(screen, self.game.board_font)
        
        # Draw game info
        self.timer_text.draw(screen)
        self.mistakes_text.draw(screen)
        self.game_info.draw(screen)
        self.difficulty_text.draw(screen)
        self.mode_text.draw(screen)
        self.note_mode_text.draw(screen)
        self.hint_text.draw(screen)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
        # Draw adaptive notice
        if self.show_adaptive_notice and time.time() - self.adaptive_notice_time < 5:
            notice = Text(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() - 50,
                self.adaptive_notice_text,
                self.game.font,
                (0, 200, 0)
            )
            notice.rect.centerx = self.game.screen.get_width() // 2
            notice.draw(screen)

    def _handle_game_over(self):
        self.game.logic.game_over_time = time.time()
        self.game.logic.log_game_result("loss")
        self.game.logic.reset_game()
        self.game.change_state("menu")

    def _handle_game_completion(self):
        """Handle puzzle completion and transition to next game"""
        if self.game.logic.check_completion():
            # Show completion message
            self._show_completion_message()
            
            # Check if we just switched to adaptive mode
            if len(self.game.logic.learning_games) == 5 and not self.game.logic.adaptive_mode:
                self.adaptive_notice_text = "ADAPTIVE MODE ACTIVATED!"
                self.adaptive_notice_time = time.time()
                self.show_adaptive_notice = True
            
            # Log result and get next puzzle
            self.game.logic.log_game_result("win")
            self._prepare_next_game()

    def _show_completion_message(self):
        """Display puzzle completion message"""
        screen = self.game.screen
        font = pygame.font.Font(None, 48)
        text = font.render("Puzzle Completed! Loading next...", True, (0, 255, 0))
        text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        
        # Draw on transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(1500)  # Show for 1.5 seconds

    def _prepare_next_game(self):
        """Reset game state for next puzzle"""
        # Reset logic
        self.game.logic.reset_game()
        
        # Reset grid display
        self.grid.initialize_grid()
        self.grid.selected_cell = None
        self.grid.clear_highlights()
        
        # Reset UI elements
        self.update_game_info()
        self.note_mode_text.text = "Note Mode: OFF"
        self.hint_text.text = f"Hints: {self.game.logic.hints_remaining}/{self.game.logic.max_hints}"
        self.grid.note_mode = False
        
        # Redraw everything
        self.draw(self.game.screen)

    def on_enter(self):
        self._init_ui()
        self.grid.initialize_grid()
        self.update_game_info()