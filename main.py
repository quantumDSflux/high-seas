import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Shooting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)  # Color for obstacles

# Fonts
font = pygame.font.Font(None, 36)

# Game settings
laser_pos = (0, 0)  # Starting position of the laser shooter
laser_direction = (1, 0)  # Initial direction (moving right)

# Levels (including mirrors as part of each level)
levels = [
    {"target": (9, 9), "mirrors": {}, "obstacles": set()},
    {"target": (8, 2), "mirrors": {}, "obstacles": set()},
    {"target": (2, 7), "mirrors": {}, "obstacles": set()},
    {"target": (5, 5), "mirrors": {}, "obstacles": set()},
    {"target": (3, 8), "mirrors": {}, "obstacles": set()}
]

max_levels = len(levels)

# Function to generate obstacles for each level
def generate_obstacles(level):
    num_obstacles = level * 5  # Increase obstacles per level (5 obstacles per level)
    num_obstacles = min(num_obstacles, 26)  # Limit to a maximum of 26 obstacles
    obstacles = set()

    # Ensure obstacles don't overlap with target position
    target_pos = levels[level-1]["target"]
    
    while len(obstacles) < num_obstacles:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) != target_pos and (x, y) not in obstacles:
            obstacles.add((x, y))
    
    return obstacles

# Reset level state
def reset_level():
    global laser_pos, laser_direction, target_pos, click_counts, obstacles
    laser_pos = (0, 0)
    laser_direction = (1, 0)
    target_pos = levels[current_level]["target"]
    obstacles = generate_obstacles(current_level + 1)  # Add more obstacles as the level increases
    click_counts = {}  # Clear mirrors for the new level

# Initialize first level
current_level = 0
reset_level()

# Create a dictionary to track click counts for each cell
click_counts = {}

# Main game loop
running = True
while running:
    screen.fill(WHITE)

    # Draw level number at the top of the screen
    level_text = font.render(f"Level {current_level + 1}/{max_levels}", True, BLACK)
    screen.blit(level_text, (10, 10))

    # Draw grid
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

    # Draw laser shooter as a red circle
    shooter_rect_center = (
        laser_pos[0] * CELL_SIZE + CELL_SIZE // 2,
        laser_pos[1] * CELL_SIZE + CELL_SIZE // 2
    )
    pygame.draw.circle(screen, RED, shooter_rect_center, CELL_SIZE // 4)

    # Draw target as a blue circle
    target_rect_center = (
        target_pos[0] * CELL_SIZE + CELL_SIZE // 2,
        target_pos[1] * CELL_SIZE + CELL_SIZE // 2
    )
    pygame.draw.circle(screen, BLUE, target_rect_center, CELL_SIZE // 4)

    # Draw obstacles as green rectangles
    for obstacle in obstacles:
        pygame.draw.rect(screen, BLACK, (obstacle[0] * CELL_SIZE, obstacle[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw mirrors from the click_counts dictionary
    for pos, mirror_state in click_counts.items():
        if mirror_state == 1:  # First click, place '/'
            pygame.draw.line(screen, RED, 
                             (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE), 
                             ((pos[0] + 1) * CELL_SIZE, (pos[1] + 1) * CELL_SIZE), 3)
        elif mirror_state == 2:  # Second click, place '//'
            pygame.draw.line(screen, RED, 
                             (pos[0] * CELL_SIZE, (pos[1] + 1) * CELL_SIZE), 
                             ((pos[0] + 1) * CELL_SIZE, pos[1] * CELL_SIZE), 3)

    # Laser mechanics
    current_pos = list(laser_pos)
    direction = laser_direction
    laser_path = []

    while True:
        # Move laser position
        current_pos[0] += direction[0]
        current_pos[1] += direction[1]
        laser_path.append(tuple(current_pos))

        # Check boundaries
        if not (0 <= current_pos[0] < GRID_SIZE and 0 <= current_pos[1] < GRID_SIZE):
            break

        # Check target hit
        if tuple(current_pos) == target_pos:
            print("Target Hit! Moving to next level...")
            current_level += 1
            if current_level < max_levels:
                reset_level()
            else:
                print("Congratulations! You completed all levels!")
                running = False
            break

        # Check for obstacles (laser stops here)
        if tuple(current_pos) in obstacles:
            break

        # Check for mirrors and reflect
        if tuple(current_pos) in click_counts:
            mirror_state = click_counts[tuple(current_pos)]
            if mirror_state == 1:  # '/' mirror
                if direction == (1, 0):    # Right
                    direction = (0, 1)    # Down
                elif direction == (-1, 0): # Left
                    direction = (0, -1)   # Up
                elif direction == (0, 1):  # Down
                    direction = (1, 0)    # Right
                elif direction == (0, -1): # Up
                    direction = (-1, 0)   # Left
            elif mirror_state == 2:  # '//' mirror
                if direction == (1, 0):    # Right
                    direction = (0, -1)   # Up
                elif direction == (-1, 0): # Left
                    direction = (0, 1)    # Down
                elif direction == (0, 1):  # Down
                    direction = (-1, 0)   # Left
                elif direction == (0, -1): # Up
                    direction = (1, 0)    # Right

    # Draw the laser path as a thin red line (laser beam)
    for i in range(len(laser_path) - 1):
        start_pos = (laser_path[i][0] * CELL_SIZE + CELL_SIZE // 2, laser_path[i][1] * CELL_SIZE + CELL_SIZE // 2)
        end_pos = (laser_path[i + 1][0] * CELL_SIZE + CELL_SIZE // 2, laser_path[i + 1][1] * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.line(screen, RED, start_pos, end_pos, 2)  # Thin red line for laser beam

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the position of the mouse click
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            cell = (grid_x, grid_y)
            
            # Cycle through the mirror states (1: '/', 2: '//', 0: no mirror)
            if cell in click_counts:
                click_counts[cell] += 1
                if click_counts[cell] > 2:
                    del click_counts[cell]  # Remove the mirror after the third click
            else:
                click_counts[cell] = 1  # First click, place '/'

    pygame.display.flip()
