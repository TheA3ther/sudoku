import pygame

class Text:
    def __init__(self, x, y, text, font, text_color):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.text_color = text_color
        self.image = self.font.render(self.text, True, self.text_color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
