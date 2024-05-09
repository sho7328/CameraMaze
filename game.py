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

class Game:
    def __init__(self, level):
        # Create the hand detector
        base_options = BaseOptions(model_asset_path='data/hand_landmarker.task')
        options = HandLandmarkerOptions(base_options=base_options, num_hands=2)
        self.detector = HandLandmarker.create_from_options(options)

        # Load video
        self.video = cv2.VideoCapture(0)
        
        # Load window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Test")

        # Load images
        self.player = pygame.image.load("player.png")
        self.player = pygame.transform.scale(self.player, (50, 50))
        self.background = pygame.image.load("wall.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.font = pygame.font.Font(None, 36)

        # Load game elements
        self.level = level
        self.maze = Maze(self.level)
        self.score = 0
        self.just_spawned = True
        self.s_cell = self.maze.return_start_cell()
        self.died = False
        self.won = False
        self.start_time = None
        self.timer_started = False
        self.elapsed_time = 0
        self.elapsed_time_when_won = None  # Updated to None

        # high score
        self.high_score = float('inf')

    def draw_landmarks_on_hand(self, image, detection_result):
        """
        Draws all the landmarks on the hand
        Args:
            image (Image): Image to draw on
            detection_result (HandLandmarkerResult): HandLandmarker detection results
        """
        # Get a list of the landmarks
        hand_landmarks_list = detection_result.hand_landmarks
        
        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # Save the landmarks into a NormalizedLandmarkList
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            # Draw the landmarks on the hand
            DrawingUtil.draw_landmarks(image,
                                       hand_landmarks_proto,
                                       solutions.hands.HAND_CONNECTIONS,
                                       solutions.drawing_styles.get_default_hand_landmarks_style(),
                                       solutions.drawing_styles.get_default_hand_connections_style())

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
            
    def is_touching_wall(self, finger_x, finger_y):
        # check if the x coordinates of the player
        for row in range(len(self.maze.maze_grid)):
            for col in range(len(self.maze.maze_grid[0])):
                if self.maze.maze_grid[row][col].is_wall:
                    if (self.maze.maze_grid[row][col].x < finger_x) and (finger_x < (self.maze.maze_grid[row][col].x + self.maze.maze_grid[row][col].width)) and (self.maze.maze_grid[row][col].y < finger_y) and (finger_y < (self.maze.maze_grid[row][col].y + self.maze.maze_grid[row][col].height)):
                        return True
        return False
    
    def is_touching_start_cell(self, finger_x, finger_y):
        if (self.s_cell.x < finger_x) and (finger_x < (self.s_cell.x + self.s_cell.width)) and ((self.s_cell.y < finger_y) and (finger_y < (self.s_cell.y + self.s_cell.height))):
            self.just_spawned = False
            return True
        return False
    
    def is_touching_end_cell(self, finger_x, finger_y):
        for row in range(len(self.maze.maze_grid)):
            for col in range(len(self.maze.maze_grid[0])):
                if self.maze.maze_grid[row][col].is_end_cell:
                    if (self.maze.maze_grid[row][col].x < finger_x) and (finger_x < (self.maze.maze_grid[row][col].x + self.maze.maze_grid[row][col].width)) and ((self.maze.maze_grid[row][col].y < finger_y) and (finger_y < (self.maze.maze_grid[row][col].y + self.maze.maze_grid[row][col].height))):
                        return True
        return False

    def run(self):
        """
        Main game loop. Runs until the 
        user presses "q".
        """    

        running = True
        # TODO: Modify loop condition  
        while self.video.isOpened() and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                    
            # Get the current frame
            frame = self.video.read()[1]

            self.screen.blit(self.background, (0,0))
            self.maze.draw()

            # Convert it to an RGB image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # the image comes mirroed-flip it
            image = cv2.flip(image, 1)

            # Convert the image to a readable format and find the hands
            to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            results = self.detector.detect(to_detect)

            # self.draw_landmarks_on_hand(image, results)
            
            # Check if player touches start cell
            if not self.timer_started and self.just_spawned == False:
                self.start_time = time.time()  # Start the timer
                self.timer_started = True

            # Update timer if started
            if self.timer_started:
                current_time = time.time()
                self.elapsed_time = int(current_time - self.start_time)
                if not self.won:
                    timer_text = self.font.render(f"Time: {self.elapsed_time} s", True, WHITE)
                else:
                    if self.elapsed_time_when_won is not None:  # Check if timer is already frozen
                        timer_text = self.font.render(f"Time: {self.elapsed_time_when_won} s", True, WHITE)  # Display stored elapsed time
                    else:
                        timer_text = self.font.render(f"Time: {self.elapsed_time} s", True, WHITE)
                self.screen.blit(timer_text, (10, 10))  # Display timer at (10, 10)

            # Draw the hand landmarks
            # self.draw_landmarks_on_hand(image, results)
            pixelCoord = self.get_finger_position(image, results)

            if pixelCoord:
                self.screen.blit(self.player, (pixelCoord[0], pixelCoord[1]))
                # pygame.draw.circle(self.background, (0, 255, 0), [pixelCoord[0], pixelCoord[1]], 5, 10)
            
                if (self.just_spawned or self.died) and not self.is_touching_start_cell(pixelCoord[0], pixelCoord[1]):
                    if self.died:
                        dead_text = self.font.render("YOU DIED", True, WHITE)
                        self.died = True
                        self.screen.blit(dead_text, (100, 100))
                    text = self.font.render("Go to", True, WHITE)
                    self.screen.blit(text, ((self.s_cell.x, self.s_cell.y - (self.s_cell.height/2))))
                    text1 = self.font.render("start cell", True, WHITE)
                    self.screen.blit(text1, ((self.s_cell.x, self.s_cell.y - (self.s_cell.height/4))))
                
                elif self.is_touching_start_cell(pixelCoord[0], pixelCoord[1]):
                    if self.died:
                        self.died = False

                elif not self.won and not self.just_spawned and self.is_touching_wall(pixelCoord[0], pixelCoord[1]):
                    text = self.font.render("YOU DIED", True, WHITE)
                    self.died = True
                    self.screen.blit(text, (100, 100))

                elif (not self.died and not self.just_spawned) and self.is_touching_end_cell(pixelCoord[0], pixelCoord[1]):
                    self.won = True
                    if self.elapsed_time_when_won is None:  # Store elapsed time if not already stored
                        self.elapsed_time_when_won = self.elapsed_time
                        if self.elapsed_time_when_won < self.high_score:
                            self.high_score = self.elapsed_time_when_won
                    text = self.font.render("YOU WIN!", True, WHITE)
                    self.screen.blit(text, (100, 100))

            # Draws the surface object to the screen.
            pygame.display.update()

            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # cv2.imshow('Hand Tracking', image)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(10) & 0xFF == ord('q'):
                print(self.score)
                break
                
        self.video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    g = Game(1)
    g.run()
