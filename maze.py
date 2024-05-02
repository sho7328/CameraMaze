import pygame
from cell import Cell

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# get maze to show up on the screen first then worry ab combining it

class Maze:
    def __init__(self, level, screen=None):
        self.filename = "maze" + str(level) + ".txt"
        self.num_rows = None
        self.num_cols = None
        self.maze_grid = None
        self.start_cell = None
        self.end_cell = None

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Test")

        # Load background image
        self.background = pygame.image.load("background_image.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

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
                        if line[col] == '#':
                            self.maze_grid[row][col].set_wall(True)
                        elif line[col] == 'A':
                            # self.maze_grid[row][col].set_explored(True)
                            self.start_cell = self.maze_grid[row][col]
                        elif line[col] == 'B':
                            self.end_cell = self.maze_grid[row][col]

        except FileNotFoundError as e:
            print("An error occurred.")
            print(e)

    def draw(self):
        # pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(50, 50, 50, 50))
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.maze_grid[row][col].draw()

if __name__ == "__main__":
    maze = Maze(2)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        maze.draw()

        # pygame.draw.circle(background, (0, 255, 0), [SCREEN_WIDTH/2, SCREEN_HEIGHT/2], 15, 3)
        
        # Draws the surface object to the screen.
        pygame.display.update()