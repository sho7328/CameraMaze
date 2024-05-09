# NOT USED FOR THE GAME.
# FIRST STEP OF MY PROVING PROCESS:
# Get a white screen to show up using pygame
# Draw a green circle

import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test")

# Load background image
background = pygame.image.load("background_image.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw background
    screen.blit(background, (0, 0))

    pygame.draw.circle(background, (0, 255, 0), [SCREEN_WIDTH/2, SCREEN_HEIGHT/2], 15, 3)
    
    # Draws the surface object to the screen.
    pygame.display.update()