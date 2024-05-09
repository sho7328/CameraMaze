# SOPHIE HO 5/8/2024
# A cell is what makes up a maze.
import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

class Cell:
    # When making the mazegrid (2D array of Cells), these parameters will eb passed through based on the .txt file
    def __init__(self, row, col, num_rows, num_cols, screen=None, is_wall=False):
        self.row = row
        self.col = col
        self.screen = screen
        self.is_wall = is_wall
        self.num_rows = num_rows
        self.num_cols = num_cols
        # These 2 will be set later, default is False
        self.is_start_cell = False
        self.is_end_cell = False

        # Calculate width and height, x and y of cell
        self.width = SCREEN_WIDTH / self.num_cols
        self.height = SCREEN_HEIGHT / self.num_rows
        self.x = self.width * (self.col)
        self.y = self.height * (self.row)

        # Images for end_cell, normal (lily pad) cell, wall_cell.
        self.end_image = pygame.image.load("end.png")
        self.end_image = pygame.transform.scale(self.end_image, (self.width, self.height))
        self.cell_image = pygame.image.load("cell.png")
        self.cell_image = pygame.transform.scale(self.cell_image, (self.width, self.height))
        self.wall_image = pygame.image.load("wall.png")
        self.wall_image = pygame.transform.scale(self.wall_image, (self.width, self.height))
    
    # Will be set in making mazegrid
    def set_wall(self, is_wall):
        self.is_wall = is_wall

    # Will be set in making mazegrid
    def set_is_start_cell(self, is_start_cell):
        self.is_start_cell = is_start_cell

    # Will be set in making mazegrid
    def set_is_end_cell(self, is_end_cell):
        self.is_end_cell = is_end_cell

    # Draw the cell's image in its designated place
    def draw(self):
        if self.is_start_cell:
            self.screen.blit(self.cell_image, (self.x, self.y))
        elif self.is_end_cell:
            self.screen.blit(self.end_image, (self.x, self.y))
        elif self.is_wall:
            self.screen.blit(self.wall_image, (self.x, self.y))
        else:
            self.screen.blit(self.cell_image, (self.x, self.y))