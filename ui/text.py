import pygame

class Text:
    def __init__(self, x, y, text, font, text_color):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        surface.blit(text_surface, text_rect)
