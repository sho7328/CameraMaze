import cv2
import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

class Cell:

    def __init__(self, row, col, is_wall, surface):
        
        self.row = row
        self.col = col
        self.is_wall = is_wall
        if self.is_wall:
            self.color = RED
        else:
            self.color = WHITE

        self.surface = surface

        # divided by however many cells there are
        self.width = SCREEN_WIDTH / 10
        self.height = SCREEN_HEIGHT / 8

        self.x = self.width * (self.row + 1)
        self.y = self.height * (self.height + 1)
    
    def draw(self):
        pygame.draw.rect(self.surface, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
