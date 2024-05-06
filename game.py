import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import pygame
from maze import Maze

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800


class Game:
    def __init__(self):
        self.level = 1
        
        self.maze = Maze(self.level)
        
    
    # def run(self):

        
