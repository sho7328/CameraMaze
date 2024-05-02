import cv2
import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

class Cell:

    def __init__(self, row, col, num_rows, num_cols, screen=None, is_wall=False):
        self.row = row
        self.col = col
        self.screen = screen
        self.color = WHITE
        self.is_wall = is_wall
        self.num_rows = num_rows
        self.num_cols = num_cols

        # divided by however many cells there are
        self.width = SCREEN_WIDTH / self.num_cols
        self.height = SCREEN_HEIGHT / self.num_rows

        self.x = self.width * (self.row + 1)
        # fix the Y
        self.y = self.height * (self.col + 1)
    
    def set_wall(self, is_wall):
        self.is_wall = is_wall
        if self.is_wall:
            self.color = RED

    def draw(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height), 3)
