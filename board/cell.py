import pygame

class Cell:
    def __init__(self, row, col, size, offset_x, offset_y, game):
        self.row = row
        self.col = col
        self.size = size
        self.value = None
        self.game = game
        self.temp_wrong = False
        self.wrong_timer = 0
        self.highlighted = False
        self.same_number = False
        self.x = offset_x + col * size
        self.y = offset_y + row * size
        self.candidates = set()  # Track possible numbers
        self.show_candidates = False  # Whether to display candidates

    def draw(self, screen, font, selected):
        theme = self.game.theme
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        # Background
        if self.temp_wrong:
            pygame.draw.rect(screen, (255, 200, 200), rect)  # Light red for wrong moves
        elif self.same_number or selected:
            pygame.draw.rect(screen, (90, 90, 90), rect)
        elif self.highlighted:
            pygame.draw.rect(screen, (180, 180, 180), rect)
        else:
            pygame.draw.rect(screen, theme["bg"], rect)
        
        # Border
        border_color = (255, 0, 0) if self.temp_wrong else theme["border"]
        pygame.draw.rect(screen, border_color, rect, 1)
        
        # Value or Candidates
        if self.value is not None:
            text_color = (255, 0, 0) if self.temp_wrong else theme["text"]
            text_surface = font.render(str(self.value), True, text_color)
            text_rect = text_surface.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
            screen.blit(text_surface, text_rect)
        elif self.show_candidates and self.candidates:
            self.draw_candidates(screen, font)
        
        # Selection highlight
        if selected:
            pygame.draw.rect(screen, (100, 149, 237), rect, 3)

    def draw_candidates(self, screen, font):
        """Draw small candidate numbers in the cell"""
        candidate_font = pygame.font.Font(None, self.size//3)  # Smaller font for candidates
        cell_width = self.size // 3
        cell_height = self.size // 3
        
        for num in sorted(self.candidates):
            # Calculate position for each candidate (1-9 in 3x3 grid)
            pos_x = (num - 1) % 3
            pos_y = (num - 1) // 3
            
            x = self.x + pos_x * cell_width + cell_width//2
            y = self.y + pos_y * cell_height + cell_height//2
            
            text_surface = candidate_font.render(str(num), True, self.game.theme["text"])
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)

    def update(self):
        if self.temp_wrong:
            self.wrong_timer += 1
            if self.wrong_timer > 30:  # Show wrong move for 30 frames
                self.temp_wrong = False
                self.wrong_timer = 0

    def handle_keypress(self, key, note_mode=False):
        if pygame.K_1 <= key <= pygame.K_9 or pygame.K_KP1 <= key <= pygame.K_KP9:
            num = int(pygame.key.name(key))
            
            if note_mode:
                # Toggle candidate number
                if num in self.candidates:
                    self.candidates.remove(num)
                else:
                    self.candidates.add(num)
            else:
                # Regular number input
                if self.game.logic.check_move(self.row, self.col, num):
                    self.value = num
                    self.game.logic.user_grid[self.row][self.col] = num
                    self.game.logic.moves_made += 1
                    self.candidates = set()  # Clear candidates when placing a number
                else:
                    self.value = num
                    self.temp_wrong = True
                    self.game.logic.user_grid[self.row][self.col] = num
                    self.game.logic.moves_made += 1
        elif key == pygame.K_BACKSPACE:
            if note_mode and self.candidates:
                self.candidates = set()  # Clear all candidates in note mode
            elif not note_mode:
                self.value = None
                self.game.logic.user_grid[self.row][self.col] = 0