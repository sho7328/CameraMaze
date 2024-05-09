# Finger tracking mechanisms sampled from Finger Tracking Gaem Lab, the rest 90% coded by me and 10% ChatGPT
import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import pygame
from maze import Maze
import time

# Library Constants
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkPoints = mp.solutions.hands.HandLandmark
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
DrawingUtil = mp.solutions.drawing_utils

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

WHITE = (255, 255, 255)
RED = (255, 0, 0)

NUM_LEVELS = 4

class Game:
    def __init__(self):
        # Create the hand detector
        base_options = BaseOptions(model_asset_path='data/hand_landmarker.task')
        options = HandLandmarkerOptions(base_options=base_options, num_hands=2)
        self.detector = HandLandmarker.create_from_options(options)

        # Load video
        self.video = cv2.VideoCapture(0)
        
        # Load window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Hopper")

        # Load game elements
        # Instruction and stats font size/style
        self.font = pygame.font.Font(None, 36)
        self.level = 0
        self.maze = Maze(self.level)
        self.just_spawned = True
        self.s_cell = None
        self.died = False
        self.won = False
        self.game_over = False

        # Timer and time variables
        self.start_time = None
        self.timer_started = False
        self.elapsed_time = 0
        self.elapsed_time_when_won = None
        self.level1_time = None
        self.level2_time = None
        self.level3_time = None
        self.level4_time = None
        self.high_score = float('inf')

        # Load images
        self.player = pygame.image.load("player.png")
        self.player = pygame.transform.scale(self.player, (50, 50))
        self.background = pygame.image.load("wall.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load button images
        self.level_up = pygame.image.load("level_up.png")
        self.level_up = pygame.transform.scale(self.level_up, (200, 200))
        self.start_button = pygame.image.load("start_button.png")
        self.start_button = pygame.transform.scale(self.start_button, (200, 200))
        self.see_stats = pygame.image.load("see_stats.png")
        self.see_stats = pygame.transform.scale(self.see_stats, (200, 200))
        self.button_x = (SCREEN_WIDTH/2) - 100
        self.button_y = SCREEN_HEIGHT / 2

    # # TAKEN FROM FINGER TRACKING GAME LAB
    # def draw_landmarks_on_hand(self, image, detection_result):
    #     """
    #     Draws all the landmarks on the hand
    #     Args:
    #         image (Image): Image to draw on
    #         detection_result (HandLandmarkerResult): HandLandmarker detection results
    #     """
    #     # Get a list of the landmarks
    #     hand_landmarks_list = detection_result.hand_landmarks
        
    #     # Loop through the detected hands to visualize.
    #     for idx in range(len(hand_landmarks_list)):
    #         hand_landmarks = hand_landmarks_list[idx]

    #         # Save the landmarks into a NormalizedLandmarkList
    #         hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    #         hand_landmarks_proto.landmark.extend([
    #         landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    #         ])

    #         # Draw the landmarks on the hand
    #         DrawingUtil.draw_landmarks(image,
    #                                    hand_landmarks_proto,
    #                                    solutions.hands.HAND_CONNECTIONS,
    #                                    solutions.drawing_styles.get_default_hand_landmarks_style(),
    #                                    solutions.drawing_styles.get_default_hand_connections_style())
    # FROM FINGER TRACKING GAME
    def get_finger_position(self, image, detection_result):
        """
        Draws a green circle on the index finger 
        and calls a method to check if we've intercepted
        with the enemy
        Args:
            image (Image): The image to draw on
            detection_result (HandLandmarkerResult): HandLandmarker detection results
        """
        # Get image details
        imageHeight, imageWidth = image.shape[:2]

        # Get a list of the landmarks
        hand_landmarks_list = detection_result.hand_landmarks
        
        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # get the coordinates of just teh index finger
            finger = hand_landmarks[HandLandmarkPoints.INDEX_FINGER_TIP.value]

            # map the coordinates back to screen dimensions
            pixelCoord = DrawingUtil._normalized_to_pixel_coordinates(finger.x, finger.y, imageWidth, imageHeight)
        
            return pixelCoord
    
    # Remaining coded mostly by me
    # Check if the player is touching a wall (compare coordinates) and return a bool.
    def is_touching_wall(self, finger_x, finger_y):
        for row in range(len(self.maze.maze_grid)):
            for col in range(len(self.maze.maze_grid[0])):
                if self.maze.maze_grid[row][col].is_wall:
                    if (self.maze.maze_grid[row][col].x < finger_x) and (finger_x < (self.maze.maze_grid[row][col].x + self.maze.maze_grid[row][col].width)) and (self.maze.maze_grid[row][col].y < finger_y) and (finger_y < (self.maze.maze_grid[row][col].y + self.maze.maze_grid[row][col].height)):
                        return True
        return False
    
    # Check if the player is at the start cell (compare coordinates) and return a bool.
    def is_touching_start_cell(self, finger_x, finger_y):
        if (self.s_cell.x < finger_x) and (finger_x < (self.s_cell.x + self.s_cell.width)) and ((self.s_cell.y < finger_y) and (finger_y < (self.s_cell.y + self.s_cell.height))):
            # Just spawned tells code to not kill player right away for not starting on the start_cell.
            # Set false because they are now touching start cell.
            self.just_spawned = False
            return True
        return False
    
    # Check if the player is at the end cell (compare coordinates) and return a bool.
    def is_touching_end_cell(self, finger_x, finger_y):
        for row in range(len(self.maze.maze_grid)):
            for col in range(len(self.maze.maze_grid[0])):
                if self.maze.maze_grid[row][col].is_end_cell:
                    if (self.maze.maze_grid[row][col].x < finger_x) and (finger_x < (self.maze.maze_grid[row][col].x + self.maze.maze_grid[row][col].width)) and ((self.maze.maze_grid[row][col].y < finger_y) and (finger_y < (self.maze.maze_grid[row][col].y + self.maze.maze_grid[row][col].height))):
                        return True
        return False
    
    # Check if the player is touching a button (start_button, see_stats, level_up) and return a bool
    def is_touching_button(self, finger_x, finger_y):
        if (self.button_x < finger_x) and (finger_x < (self.button_x + self.level_up.get_width())) and ((self.button_y < finger_y) and (finger_y < (self.button_y + self.level_up.get_height()))):
            return True
        return False
    
    # Display the title and instructions
    def display_title_instructions(self):
        text = pygame.font.Font(None, 180).render("MAZE HOPPER", True, WHITE)
        self.screen.blit(text, (30, 20))
        instructions = self.font.render("Use your pointer finger to move the frog through a maze.", True, WHITE)
        self.screen.blit(instructions, (SCREEN_WIDTH/6, 150))
        instructions1 = self.font.render("Touch the water and you die.", True, WHITE)
        self.screen.blit(instructions1, (SCREEN_WIDTH/6, 200))
        instructions2 = self.font.render("Stay on the lilypads and reach the lilyflower to win.", True, WHITE)
        self.screen.blit(instructions2, (SCREEN_WIDTH/6, 250))
        instructions3 = self.font.render("Go as fast as you can!", True, WHITE)
        self.screen.blit(instructions3, (SCREEN_WIDTH/6, 300))
        self.screen.blit(self.start_button, (self.button_x, self.button_y))
    
    # Display the ending game stats
    def show_stats(self):
        self.screen.blit(self.background, (0,0))
        text = pygame.font.Font(None, 180).render("MAZE HOPPER", True, WHITE)
        self.screen.blit(text, (30, 20))
        thanks = self.font.render("THANKS FOR PLAYING!", True, WHITE)
        self.screen.blit(thanks, (SCREEN_WIDTH/6, 150))
        t1 = self.font.render("Level 1 time: " + str(self.level1_time) + " secs", True, WHITE)
        self.screen.blit(t1, (SCREEN_WIDTH/6, 200))
        t2 = self.font.render("Level 2 time: " + str(self.level2_time) + " secs", True, WHITE)
        self.screen.blit(t2, (SCREEN_WIDTH/6, 250))
        t3 = self.font.render("Level 3 time: " + str(self.level3_time) + " secs", True, WHITE)
        self.screen.blit(t3, (SCREEN_WIDTH/6, 300))
        t4 = self.font.render("Level 4 time: " + str(self.level4_time) + " secs", True, WHITE)
        self.screen.blit(t4, (SCREEN_WIDTH/6, 350))
        hs = self.font.render("Fastest high score in all history: " + str(self.high_score) + " secs", True, WHITE)
        self.screen.blit(hs, (SCREEN_WIDTH/6, 400))

    # Main method: run the whole Game
    def run(self):
        running = True 
        while self.video.isOpened() and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                    
            # Get the current frame
            frame = self.video.read()[1]

            # Convert it to an RGB image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # The image comes mirroed-flip it
            image = cv2.flip(image, 1)

            # Convert the image to a readable format and find the hands
            to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            results = self.detector.detect(to_detect)

            # Draw background and maze
            self.screen.blit(self.background, (0,0))
            self.maze.draw()

            # If not on instruction/title screen: (which means it's an actual game level)
            if not self.level == 0:
                # Display what level it is
                level = "LEVEL " + str(self.level)
                level_text = pygame.font.Font(None, 80).render(level, True, WHITE)
                self.screen.blit(level_text, (300, 10))

                # Check whether to start the timer or not (start it when the player touches start_cell)
                if not self.timer_started and self.just_spawned == False:
                    self.start_time = time.time()  # Start the timer
                    self.timer_started = True
                # Update timer if started, and freeze the timer if the player has won that level
                if self.timer_started:
                    current_time = time.time()
                    self.elapsed_time = int(current_time - self.start_time)
                    if not self.won:
                        timer_text = pygame.font.Font(None, 60).render(f"Time: {self.elapsed_time} s", True, RED)
                    else:
                        # Check if timer is already frozen
                        if self.elapsed_time_when_won is not None:  
                            # Display stored completed time
                            timer_text = pygame.font.Font(None, 60).render(f"Time: {self.elapsed_time_when_won} s", True, RED)  
                            # For each level, save the corresponding times
                            if self.level == 1:
                                self.level1_time = self.elapsed_time_when_won
                            elif self.level == 2:
                                self.level2_time = self.elapsed_time_when_won
                            elif self.level == 3:
                                self.level3_time = self.elapsed_time_when_won
                            elif self.level == 4:
                                self.level4_time = self.elapsed_time_when_won
                        else:
                            timer_text = pygame.font.Font(None, 60).render(f"Time: {self.elapsed_time} s", True, RED)
                    self.screen.blit(timer_text, (10, 10))
            # If it's level 0/the title screen, show title and instructions
            else:
                self.display_title_instructions()

            # Get the finger position coords
            pixelCoord = self.get_finger_position(image, results)

            # If the finger is visible within the camera and there are finger coordinates
            if pixelCoord:
                # Draw the player at the finger coord
                self.screen.blit(self.player, (pixelCoord[0], pixelCoord[1]))

                # If all the levels have been beat and the player pressed the see_stats button, show the stats
                if self.game_over and self.is_touching_button(pixelCoord[0], pixelCoord[1]):
                    self.show_stats()
                # Otherwise if the game's not over yet
                else:
                    # If the level is a real game level
                    if not self.level == 0:
                        # If the player just spawned or just died and isn't touching the start cell
                        if (self.just_spawned or self.died) and not self.is_touching_start_cell(pixelCoord[0], pixelCoord[1]):
                            if self.died:
                                # If they just died, display "you died" until they touch the start cell
                                dead_text = pygame.font.Font(None, 80).render("YOU DIED", True, WHITE)
                                self.died = True
                                self.screen.blit(dead_text, (300, 500))
                            # Display "go to start cell" until they go to the start cell
                            text = self.font.render("Go to", True, WHITE)
                            self.screen.blit(text, ((self.s_cell.x, self.s_cell.y - (self.s_cell.height/2))))
                            text1 = self.font.render("start cell", True, WHITE)
                            self.screen.blit(text1, ((self.s_cell.x - 20, self.s_cell.y - (self.s_cell.height/4))))
                            # Outline the start_cell cell
                            pygame.draw.rect(self.screen, (255, 255, 255, 155), (self.s_cell.x, self.s_cell.y, self.s_cell.width, self.s_cell.height), 7)
                        
                        # If the player is touching the start cell they're not dead anymore
                        elif self.is_touching_start_cell(pixelCoord[0], pixelCoord[1]):
                            if self.died:
                                self.died = False
                        
                        # If someone didn't just spawn and they touched a wall they died
                        elif not self.just_spawned and self.is_touching_wall(pixelCoord[0], pixelCoord[1]):
                            dead_text = pygame.font.Font(None, 80).render("YOU DIED", True, WHITE)
                            self.died = True
                            self.screen.blit(dead_text, (300, 500))

                        # If the player is alive and touchign an end cell, display that they won
                        elif (not self.died and not self.just_spawned) and self.is_touching_end_cell(pixelCoord[0], pixelCoord[1]):
                            self.won = True 
                            if self.elapsed_time_when_won is None:  # Store elapsed time if not already stored
                                self.elapsed_time_when_won = self.elapsed_time
                                # Check the high score for new records
                                if self.elapsed_time_when_won < self.high_score:
                                    self.high_score = self.elapsed_time_when_won
                            text = self.font.render("YOU WIN!", True, WHITE)
                            self.screen.blit(text, (100, 100))
                        
                        # If you won adn there are more levels to go, show the next level button
                        if self.won and not self.level == NUM_LEVELS:
                            text = pygame.font.Font(None, 80).render("YOU WIN!", True, WHITE)
                            self.screen.blit(text, (350, 300))
                            self.screen.blit(self.level_up, (self.button_x, self.button_y))

                        # If you won and there are no more levels, the game is over
                        if self.won and self.level == NUM_LEVELS:
                            self.game_over = True
                        
                        # If the game is over, make the show_stats button
                        if self.game_over:
                            self.screen.blit(self.see_stats, (self.button_x, self.button_y))

                    # If there are more levels to go and the player is touching the next level button
                    if not self.level == NUM_LEVELS and (self.won and self.is_touching_button(pixelCoord[0], pixelCoord[1])) or (self.level == 0 and self.is_touching_button(pixelCoord[0], pixelCoord[1])):
                        # Increase level
                        self.level += 1
                        # New maze for that level
                        self.maze = Maze(self.level)
                        # New starting cell (it's a different maze)
                        self.s_cell = self.maze.return_start_cell()
                        # Reset other variables
                        self.just_spawned = True
                        self.died = False
                        self.won = False
                        self.start_time = None
                        self.timer_started = False
                        self.elapsed_time = 0
                        self.elapsed_time_when_won = None

            # Draws the surface object to the screen.
            pygame.display.update()

            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # cv2.imshow('Hand Tracking', image)
                
        self.video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Run the game
    g = Game()
    g.run()
