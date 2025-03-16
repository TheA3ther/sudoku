import pygame
from sys import exit
from sprites import Button

# initialize pygame
pygame.init()

# initialize screen size
screen = pygame.display.set_mode((1280, 720)) 

# game loop
while True:
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
    # update frame
    pygame.display.update()