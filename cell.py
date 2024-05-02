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
        self.is_start_cell = False
        self.is_end_cell = False

        # divided by however many cells there are
        self.width = SCREEN_WIDTH / self.num_cols
        self.height = SCREEN_HEIGHT / self.num_rows

        self.x = self.width * (self.col)
        # fix the Y
        self.y = self.height * (self.row)
    
    def set_wall(self, is_wall):
        self.is_wall = is_wall
        if self.is_wall:
            self.color = RED

    def set_is_start_cell(self, is_start_cell):
        self.is_start_cell = is_start_cell

    def set_is_end_cell(self, is_end_cell):
        self.is_end_cell = is_end_cell

    def draw(self):
        if self.is_start_cell:
            # start cell image
        
        elif self.is_end_cell:
            # end cell image
        else:
            pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
