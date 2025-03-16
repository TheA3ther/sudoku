import pygame
from sys import exit
from sprites import Button

# initialize pygame
pygame.init()

# initialize screen size
screen = pygame.display.set_mode((1280, 720)) 

# initialize font
font = pygame.font.Font(None, 36)

# onclick func
def on_click():
    print("Button Clicked!")

# button
button = Button(200, 150, 200, 50, (0, 0, 0), "Click Me", font, (0, 0, 0), on_click)

running = True

# game loop
while running:
    screen.fill("White")

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        button.handle_event(event)
            
    # update frame
    button.draw(screen)
    pygame.display.update()