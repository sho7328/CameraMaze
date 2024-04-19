import cv2

class Cell:

    def __init__(self, row, col, is_wall):
        

        self.row = row
        self.col = col
        self.is_wall = True

        self.width = 5
        self.height = 5

        self.x = self.width * (self.row + 1)
        self.y = self.height * (self.height + 1)
    
    def draw(self):


