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
        
        # Value
        if self.value is not None:
            text_color = (255, 0, 0) if self.temp_wrong else theme["text"]
            text_surface = font.render(str(self.value), True, text_color)
            text_rect = text_surface.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
            screen.blit(text_surface, text_rect)
        
        # Selection highlight
        if selected:
            pygame.draw.rect(screen, (100, 149, 237), rect, 3)

    def update(self):
        if self.temp_wrong:
            self.wrong_timer += 1
            if self.wrong_timer > 30:  # Show wrong move for 30 frames
                self.temp_wrong = False
                self.wrong_timer = 0

    def handle_keypress(self, key):
        if pygame.K_1 <= key <= pygame.K_9 or pygame.K_KP1 <= key <= pygame.K_KP9:
            num = int(pygame.key.name(key))
            if self.game.logic.check_move(self.row, self.col, num):
                self.value = num
                self.game.logic.user_grid[self.row][self.col] = num
                self.game.logic.moves_made += 1
            else:
                self.value = num
                self.temp_wrong = True
                self.game.logic.user_grid[self.row][self.col] = num
                self.game.logic.moves_made += 1
        elif key == pygame.K_BACKSPACE:
            self.value = None
            self.game.logic.user_grid[self.row][self.col] = 0