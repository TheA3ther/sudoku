import pygame
from random import randint

class Cell:
    def __init__(self, row, col, size, offset_x, offset_y, game):
        self.row = row
        self.col = col
        self.size = size  # Width/height of the cell
        self.value = None  # The number inside the cell (None if empty)
        self.game = game  # Reference to the game for theme access
        self.blink_timer = 0  # Timer for blinking effect
        self.show_border = True  # Toggle for blinking effect

        # Calculate position on screen with offset
        self.x = offset_x + col * size
        self.y = offset_y + row * size

    def draw(self, screen, font, selected):
        theme = self.game.theme
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        # Draw cell background
        pygame.draw.rect(screen, theme["bg"], rect)
        
        # Draw thin border
        pygame.draw.rect(screen, theme["border"], rect, 1)
        
        # Draw the value if it's not empty
        if self.value is not None:
            text_surface = font.render(str(self.value), True, theme["text"])
            text_rect = text_surface.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
            screen.blit(text_surface, text_rect)
        
        # Highlight if selected (blinking effect)
        if selected and self.show_border:
            highlight_color = (100, 149, 237)  # Cornflower Blue
            pygame.draw.rect(screen, highlight_color, rect, 7)  # Highlight over everything

    def update(self, selected):
        if selected:
            self.blink_timer += 1
            if self.blink_timer % 30 == 0:  # Toggle every 30 frames
                self.show_border = not self.show_border

    def handle_keypress(self, key):
        if pygame.K_1 <= key <= pygame.K_9 or pygame.K_KP1 <= key <= pygame.K_KP9:
            self.value = int(pygame.key.name(key))
            print(f"Number {self.value} entered, check if it's correct!")
