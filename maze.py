# SOPHIE HO 5/8/2024
# The maze class makes the 2D array mazgrid which is translated from different txt files that I made.
# Repurposed code from CS2's MazeSolver (create_maze)
# Was also used as a proof for creating a maze from cells (that is why is can run on its own)
import pygame
from cell import Cell

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

class Maze:
    # Need to know the level since each level has a different maze .txt file/design
    def __init__(self, level, screen=None):
        # Set filename
        self.filename = "maze" + str(level) + ".txt"
        # These will be set in create_maze
        self.num_rows = None
        self.num_cols = None
        self.maze_grid = None
        self.start_cell = None
        self.end_cell = None

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Hopper")

        # Load background image
        self.background = pygame.image.load("background_image.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Create the maze
        self.create_maze(self.filename)


    def create_maze(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

                # The row and col are specified in the first line of the file
                self.num_rows, self.num_cols = map(int, lines[0].split())

                self.maze_grid = [[None] * self.num_cols for _ in range(self.num_rows)]

                for row in range(self.num_rows):
                    line = lines[row + 1].strip()
                    for col in range(self.num_cols):
                        # Create a new MazeCell for each location
                        self.maze_grid[row][col] = Cell(row, col, self.num_rows, self.num_cols, screen=self.screen)

                        # Set if it is a wall or the start or end cell
                        # Hashtag measn it's a wall
                        if line[col] == '#':
                            self.maze_grid[row][col].set_wall(True)
                        # A is start cell
                        elif line[col] == 'A':
                            self.start_cell = self.maze_grid[row][col]
                            self.maze_grid[row][col].set_is_start_cell(True)
                            # B is end cell
                        elif line[col] == 'B':
                            self.end_cell = self.maze_grid[row][col]
                            self.maze_grid[row][col].set_is_end_cell(True)

        except FileNotFoundError as e:
            print(f"Missing {filename}")
            print(e)

    # Return the start_cell (needed for game)
    def return_start_cell(self):
        return self.start_cell
    
    # Draws entire maze
    def draw(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.maze_grid[row][col].draw()