import pygame
import random
from typing import List, Tuple
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 40
COLS = 19
ROWS = 19
WINDOW_WIDTH = CELL_SIZE * COLS
WINDOW_HEIGHT = CELL_SIZE * ROWS + 60
FPS = 45
PACMAN_SPEED = 0.2
GHOST_SPEED = 0.18
POWER_PELLET_DURATION = 10 * FPS
GHOST_POINTS = 200

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 192, 203)
RED = (255, 0, 0)
VULNERABLE_GHOST_COLOR = (0, 0, 255)
BLINKING_GHOST_COLOR = (255, 255, 255)

# Game States
MENU = 0
SINGLE_PLAYER = 1
MULTI_PLAYER = 2
GAME_OVER = 3

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Pacman')
clock = pygame.time.Clock()

# Game maze (0: empty path, 1: wall, 2: dot, 3: power pellet, 4: tunnel)
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [4,0,0,0,2,0,0,1,1,0,1,1,0,0,2,0,0,0,4],
    [1,1,1,1,2,1,0,1,0,0,0,1,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,2,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Convert the text pattern to a maze
def create_bonus_maze_from_pattern():
    pattern = [
        "XXX_XXX__X_XXX_XXX_XXX",
        "X___X____X_X_X_X___X_X",
        "X___XXX__X_X_X_XXX_X_X",
        "X_____X__X_X_X_X_X_X_X",
        "XXX_XXX__X_XXX_XXX_XXX"
    ]
    
    # Create base maze with borders
    maze = []
    maze.append([1] * 19)  # Top border
    
    # Add dots row
    dots_row = [1] + [2] * 17 + [1]
    maze.append(dots_row[:])
    
    # Convert pattern to maze walls
    for row in pattern:
        maze_row = [1]  # Left border
        for char in row:
            if char == 'X':
                maze_row.append(1)  # Wall
            else:  # '_'
                maze_row.append(0)  # Empty space
        maze_row.append(1)  # Right border
        maze.append(maze_row)
    
    # Add dots row after pattern
    maze.append(dots_row[:])
    
    # Add tunnel row
    tunnel_row = [1] * 7 + [4] * 5 + [1] * 7
    maze.append(tunnel_row)
    
    # Add remaining rows with dots
    for _ in range(9):
        maze.append(dots_row[:])
    
    # Add bottom border
    maze.append([1] * 19)
    
    return maze

BONUS_MAZE = create_bonus_maze_from_pattern()

def find_path(maze: List[List[int]], start: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Find path using BFS algorithm."""
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == target:
            return path
            
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            
            # Handle tunnel wrapping
            if y == 8 and maze[y][x] == 4:  
                if next_x < 0:
                    next_x = COLS - 1
                elif next_x >= COLS:
                    next_x = 0
            
            if (0 <= next_x < COLS and 0 <= next_y < ROWS and 
                maze[next_y][next_x] != 1 and 
                (next_x, next_y) not in visited):
                queue.append(((next_x, next_y), path + [(next_x, next_y)]))
                visited.add((next_x, next_y))
    
    return []  

def check_win(maze: List[List[int]]) -> bool:
    """Check if all dots and power pellets have been eaten."""
    for row in maze:
        for cell in row:
            if cell in [2, 3]:  
                return False
    return True

class Pacman:
    def __init__(self, x=9, y=11, color=YELLOW, is_ms_pacman=False):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.score = 0
        self.power_pellet_timer = 0
        self.mouth_open = True
        self.animation_count = 0
        self.color = color
        self.is_ms_pacman = is_ms_pacman
        self.alive = True

    def can_move_in_direction(self, maze, x, y, direction, radius=0.35):
        # Check if Pacman can move in a given direction from a position
        test_x = x + direction[0] * PACMAN_SPEED
        test_y = y + direction[1] * PACMAN_SPEED
        
        test_points = [
            (test_x, test_y),  # Center
            (test_x - radius, test_y),  # Left
            (test_x + radius, test_y),  # Right
            (test_x, test_y - radius),  # Top
            (test_x, test_y + radius)   # Bottom
        ]
        
        for px, py in test_points:
            cell_x = int(round(px))
            cell_y = int(round(py))
            if 0 <= cell_x < COLS and 0 <= cell_y < ROWS:
                if maze[cell_y][cell_x] == 1:  # Wall
                    return False
        return True

    def move(self, maze: List[List[int]], ghosts: List['Ghost']):
        # Update power pellet timer
        if self.power_pellet_timer > 0:
            self.power_pellet_timer -= 1

        # First try to apply queued direction change
        if self.next_direction != (0, 0):
            # Check if we're close to a grid center (within 0.1 units)
            grid_aligned = (abs(self.x - round(self.x)) < 0.1 and 
                          abs(self.y - round(self.y)) < 0.1)
            
            if grid_aligned and self.can_move_in_direction(maze, round(self.x), round(self.y), self.next_direction):
                self.x = round(self.x)  # Snap to grid
                self.y = round(self.y)
                self.direction = self.next_direction
        
        # Move in current direction
        new_x = self.x + self.direction[0] * PACMAN_SPEED
        new_y = self.y + self.direction[1] * PACMAN_SPEED
        
        # Handle tunnel wrapping
        if self.direction[0] != 0 and int(self.y) == 8 and maze[8][int(self.x)] == 4:
            new_x = (new_x + COLS) % COLS
            self.x = new_x
            self.y = new_y
        else:
            # Check if we can move in current direction
            if self.can_move_in_direction(maze, self.x, self.y, self.direction):
                if 0 <= new_x < COLS and 0 <= new_y < ROWS:
                    self.x = new_x
                    self.y = new_y

        # Collect dots and power pellets
        cell_x, cell_y = int(round(self.x)), int(round(self.y))
        if 0 <= cell_x < COLS and 0 <= cell_y < ROWS:
            if maze[cell_y][cell_x] == 2:  # Regular dot
                maze[cell_y][cell_x] = 0
                self.score += 10
            elif maze[cell_y][cell_x] == 3:  # Power pellet
                maze[cell_y][cell_x] = 0
                self.score += 50
                self.power_pellet_timer = POWER_PELLET_DURATION
                # Make all ghosts vulnerable
                for ghost in ghosts:
                    ghost.make_vulnerable()

    def draw(self, screen):
        # Update mouth animation
        self.animation_count = (self.animation_count + 1) % 10
        self.mouth_open = self.animation_count < 5

        # Calculate position
        center = (int(self.x * CELL_SIZE + CELL_SIZE // 2), 
                 int(self.y * CELL_SIZE + CELL_SIZE // 2))
        
        if self.mouth_open:
            # Calculate start and end angles based on direction
            if self.direction == (1, 0):  # Right
                start_angle = 20
                end_angle = 340
            elif self.direction == (-1, 0):  # Left
                start_angle = 200
                end_angle = 160
            elif self.direction == (0, -1):  # Up
                start_angle = 110
                end_angle = 70
            elif self.direction == (0, 1):  # Down
                start_angle = 290
                end_angle = 250
            else:  # Default (facing right)
                start_angle = 20
                end_angle = 340

            # Draw pacman with mouth
            pygame.draw.arc(screen, self.color, 
                          (center[0] - CELL_SIZE//2, center[1] - CELL_SIZE//2,
                           CELL_SIZE, CELL_SIZE),
                          start_angle * (3.14/180), end_angle * (3.14/180),
                          CELL_SIZE//2)
        else:
            # Draw full circle when mouth is closed
            pygame.draw.circle(screen, self.color, center, CELL_SIZE//2 - 2)

        # Add bow for Ms. Pacman
        if self.is_ms_pacman:
            bow_color = RED
            bow_x = center[0]
            bow_y = center[1] - CELL_SIZE//2 + 2
            pygame.draw.circle(screen, bow_color, (bow_x, bow_y), 4)
            pygame.draw.circle(screen, bow_color, (bow_x - 4, bow_y - 2), 4)
            pygame.draw.circle(screen, bow_color, (bow_x + 4, bow_y - 2), 4)

class Ghost:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.direction = (0, 0)
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.eaten = False
        self.respawn_timer = 0

    def make_vulnerable(self):
        if not self.eaten:
            self.vulnerable = True
            self.vulnerable_timer = 7 * FPS  # 7 seconds of vulnerability

    def reset_vulnerability(self):
        self.vulnerable = False

    def get_valid_moves(self, maze, current_pos):
        x, y = current_pos
        valid_moves = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = x + dx
            new_y = y + dy
            
            # Handle tunnel wrapping
            if int(y) == 8:  # Tunnel row
                if new_x < 0:
                    new_x = COLS - 1
                elif new_x >= COLS:
                    new_x = 0
            
            # Check if move is valid
            if (0 <= new_x < COLS or int(y) == 8) and 0 <= new_y < ROWS:
                if maze[new_y][int(new_x % COLS)] != 1:  # Use modulo for x position
                    valid_moves.append((dx, dy))
        return valid_moves

    def move(self, maze: List[List[int]], pacman: 'Pacman', ghosts: List['Ghost']):
        if self.eaten:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.eaten = False
                self.vulnerable = False
                self.x = 9  # Reset position
                self.y = 8
            return

        if self.vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False

        current_cell = (int(round(self.x)), int(round(self.y)))
        
        # Only change direction when centered on a cell
        if abs(self.x - round(self.x)) < 0.1 and abs(self.y - round(self.y)) < 0.1:
            self.x = round(self.x)  # Snap to grid
            self.y = round(self.y)
            
            valid_moves = self.get_valid_moves(maze, current_cell)
            if not valid_moves:
                return

            # Remove opposite direction unless it's the only option
            if len(valid_moves) > 1 and (-self.direction[0], -self.direction[1]) in valid_moves:
                valid_moves.remove((-self.direction[0], -self.direction[1]))

            if self.vulnerable:
                # Move randomly when vulnerable
                self.direction = random.choice(valid_moves)
            else:
                # Normal targeting behavior
                target = self.get_target(pacman, ghosts)
                
                # Choose the direction that gets closest to the target
                best_move = None
                min_distance = float('inf')
                for dx, dy in valid_moves:
                    new_x = current_cell[0] + dx
                    new_y = current_cell[1] + dy
                    
                    # Handle wrapping for distance calculation
                    if int(current_cell[1]) == 8:
                        # Consider both direct and wrapped distances
                        direct_dist = ((new_x - target[0]) ** 2 + (new_y - target[1]) ** 2) ** 0.5
                        wrap_left = ((new_x + COLS - target[0]) ** 2 + (new_y - target[1]) ** 2) ** 0.5
                        wrap_right = ((new_x - COLS - target[0]) ** 2 + (new_y - target[1]) ** 2) ** 0.5
                        distance = min(direct_dist, wrap_left, wrap_right)
                    else:
                        distance = ((new_x - target[0]) ** 2 + (new_y - target[1]) ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_move = (dx, dy)
                
                self.direction = best_move

        # Move in current direction
        new_x = self.x + self.direction[0] * GHOST_SPEED
        new_y = self.y + self.direction[1] * GHOST_SPEED

        # Handle tunnel wrapping
        if int(self.y) == 8:  # In tunnel row
            if new_x < 0:
                new_x = COLS - 1
            elif new_x >= COLS:
                new_x = 0
            
            # Always allow horizontal movement in tunnel
            if self.direction[0] != 0:  # Moving horizontally
                self.x = new_x
                self.y = new_y
            elif 0 <= new_y < ROWS and maze[int(round(new_y))][int(round(new_x % COLS))] != 1:
                # Allow vertical movement if not into a wall
                self.x = new_x
                self.y = new_y
        else:
            # Normal movement
            if (0 <= new_x < COLS and 0 <= new_y < ROWS and 
                maze[int(round(new_y))][int(round(new_x))] != 1):
                self.x = new_x
                self.y = new_y

    def get_target(self, pacman: 'Pacman', ghosts: List['Ghost']) -> Tuple[int, int]:
        if self.name == "blinky":
            # Directly target Pacman
            return (int(round(pacman.x)), int(round(pacman.y)))
        elif self.name == "pinky":
            # Target 4 tiles ahead of Pacman
            target_x = int(round(pacman.x + 4 * pacman.direction[0]))
            target_y = int(round(pacman.y + 4 * pacman.direction[1]))
            return (target_x, target_y)
        elif self.name == "inky":
            # Complex targeting using Blinky's position
            blinky = next(g for g in ghosts if g.name == "blinky")
            # Get point 2 tiles ahead of Pacman
            ahead_x = int(round(pacman.x + 2 * pacman.direction[0]))
            ahead_y = int(round(pacman.y + 2 * pacman.direction[1]))
            # Double the vector from Blinky to this point
            target_x = ahead_x + (ahead_x - int(round(blinky.x)))
            target_y = ahead_y + (ahead_y - int(round(blinky.y)))
            return (target_x, target_y)
        else:  # clyde
            # If far from Pacman, target directly, if close, go to corner
            dist = ((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2) ** 0.5
            if dist > 8:
                return (int(round(pacman.x)), int(round(pacman.y)))
            else:
                return (0, ROWS-1)  # Bottom-left corner

    def draw(self, screen):
        if self.eaten:
            return  # Don't draw if eaten
            
        x = int(self.x * CELL_SIZE)
        y = int(self.y * CELL_SIZE)
        
        # Determine ghost color
        if self.vulnerable:
            if self.vulnerable_timer < 2 * FPS:  # Flash when about to end
                color = (0, 0, 255) if (self.vulnerable_timer // 15) % 2 == 0 else WHITE
            else:
                color = (0, 0, 255)
        else:
            color = self.color
            
        # Draw ghost body (semi-circle for head)
        pygame.draw.circle(screen, color, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//2)
        
        # Draw ghost skirt (wavy bottom)
        skirt_points = [
            (x, y + CELL_SIZE//2),  # Left edge
            (x + CELL_SIZE//4, y + CELL_SIZE//2 + 3),  # First wave down
            (x + CELL_SIZE//2, y + CELL_SIZE//2),  # Middle wave up
            (x + 3*CELL_SIZE//4, y + CELL_SIZE//2 + 3),  # Second wave down
            (x + CELL_SIZE, y + CELL_SIZE//2),  # Right edge
            (x + CELL_SIZE, y + CELL_SIZE),  # Bottom right
            (x, y + CELL_SIZE),  # Bottom left
        ]
        pygame.draw.polygon(screen, color, skirt_points)

def draw_maze(screen, maze):
    for y in range(ROWS):
        for x in range(COLS):
            cell = maze[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            if cell == 1:  
                pygame.draw.rect(screen, BLUE, rect)
            elif cell == 2:  
                pygame.draw.circle(screen, WHITE, 
                                 (x * CELL_SIZE + CELL_SIZE // 2, 
                                  y * CELL_SIZE + CELL_SIZE // 2), 
                                 CELL_SIZE // 8)
            elif cell == 3:  
                pygame.draw.circle(screen, WHITE, 
                                 (x * CELL_SIZE + CELL_SIZE // 2, 
                                  y * CELL_SIZE + CELL_SIZE // 2), 
                                 CELL_SIZE // 4)
            # Don't draw anything for tunnel (4) - keep it black

def draw_menu(screen):
    """Draw the main menu screen."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    title = font.render('PACMAN', True, YELLOW)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//4))
    
    font = pygame.font.Font(None, 36)
    single = font.render('Press 1 for Single Player', True, WHITE)
    multi = font.render('Press 2 for Two Players', True, WHITE)
    screen.blit(single, (WINDOW_WIDTH//2 - single.get_width()//2, WINDOW_HEIGHT//2))
    screen.blit(multi, (WINDOW_WIDTH//2 - multi.get_width()//2, WINDOW_HEIGHT//2 + 50))

def draw_game_over(screen, won, score, mode):
    """Draw the game over screen."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    if won:
        title = font.render('YOU WIN!', True, YELLOW)
    else:
        title = font.render('GAME OVER', True, RED)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//4))
    
    font = pygame.font.Font(None, 36)
    if mode == MULTI_PLAYER:
        score_text = font.render(f'Total Score: {score}', True, WHITE)
    else:
        score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
    
    restart = font.render('Press R to Restart', True, WHITE)
    menu = font.render('Press M for Menu', True, WHITE)
    screen.blit(restart, (WINDOW_WIDTH//2 - restart.get_width()//2, WINDOW_HEIGHT//2 + 50))
    screen.blit(menu, (WINDOW_WIDTH//2 - menu.get_width()//2, WINDOW_HEIGHT//2 + 100))

def reset_game(pacman, ms_pacman, ghosts, maze):
    """Reset the game state."""
    # Reset Pacman
    pacman.x = 9
    pacman.y = 11
    pacman.direction = (0, 0)
    pacman.next_direction = (0, 0)
    pacman.score = 0
    pacman.power_pellet_timer = 0
    pacman.alive = True

    # Reset Ms. Pacman if in multiplayer mode
    if ms_pacman:
        ms_pacman.x = 9
        ms_pacman.y = 11
        ms_pacman.direction = (0, 0)
        ms_pacman.next_direction = (0, 0)
        ms_pacman.score = 0
        ms_pacman.power_pellet_timer = 0
        ms_pacman.alive = True

    # Reset ghosts
    ghost_positions = [(9, 8), (8, 8), (10, 8), (9, 9)]
    ghost_colors = [(255, 0, 0), (255, 192, 203), (0, 255, 255), (255, 165, 0)]
    ghost_names = ["blinky", "pinky", "inky", "clyde"]
    
    for ghost, (x, y), color, name in zip(ghosts, ghost_positions, ghost_colors, ghost_names):
        ghost.x = x
        ghost.y = y
        ghost.color = color
        ghost.name = name
        ghost.direction = (0, 0)
        ghost.vulnerable = False
        ghost.vulnerable_timer = 0
        ghost.eaten = False
        ghost.respawn_timer = 0

    # Reset maze
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            maze[y][x] = MAZE[y][x]

def main():
    """Main game loop."""
    # Initialize game objects
    pacman = Pacman()
    ms_pacman = None
    ghosts = [
        Ghost(9, 8, (255, 0, 0), "blinky"),
        Ghost(8, 8, (255, 192, 203), "pinky"),
        Ghost(10, 8, (0, 255, 255), "inky"),
        Ghost(9, 9, (255, 165, 0), "clyde")
    ]
    
    # Create maze copy
    maze = [row[:] for row in MAZE]
    
    # Game state
    game_state = MENU
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key == pygame.K_1:
                        game_state = SINGLE_PLAYER
                        reset_game(pacman, None, ghosts, maze)
                    elif event.key == pygame.K_2:
                        game_state = MULTI_PLAYER
                        ms_pacman = Pacman(9, 11, PINK, True)
                        reset_game(pacman, ms_pacman, ghosts, maze)
                
                elif game_state == GAME_OVER:
                    if event.key == pygame.K_r:
                        if ms_pacman:
                            game_state = MULTI_PLAYER
                        else:
                            game_state = SINGLE_PLAYER
                        reset_game(pacman, ms_pacman, ghosts, maze)
                    elif event.key == pygame.K_m:
                        game_state = MENU
                        ms_pacman = None
        
        if game_state == MENU:
            draw_menu(screen)
        
        elif game_state in [SINGLE_PLAYER, MULTI_PLAYER]:
            # Handle Pacman input
            keys = pygame.key.get_pressed()
            
            # Mr. Pacman controls (arrow keys)
            if keys[pygame.K_LEFT]:
                pacman.next_direction = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                pacman.next_direction = (1, 0)
            elif keys[pygame.K_UP]:
                pacman.next_direction = (0, -1)
            elif keys[pygame.K_DOWN]:
                pacman.next_direction = (0, 1)
            
            # Ms. Pacman controls (WASD)
            if game_state == MULTI_PLAYER and ms_pacman:
                if keys[pygame.K_a]:
                    ms_pacman.next_direction = (-1, 0)
                elif keys[pygame.K_d]:
                    ms_pacman.next_direction = (1, 0)
                elif keys[pygame.K_w]:
                    ms_pacman.next_direction = (0, -1)
                elif keys[pygame.K_s]:
                    ms_pacman.next_direction = (0, 1)
            
            # Update game objects
            if pacman.alive:
                pacman.move(maze, ghosts)
            if game_state == MULTI_PLAYER and ms_pacman and ms_pacman.alive:
                ms_pacman.move(maze, ghosts)
            
            for ghost in ghosts:
                ghost.move(maze, pacman, ghosts)
                
                # Check collisions with Mr. Pacman
                if pacman.alive and abs(ghost.x - pacman.x) < 0.5 and abs(ghost.y - pacman.y) < 0.5:
                    if ghost.vulnerable:
                        ghost.eaten = True
                        pacman.score += GHOST_POINTS
                    else:
                        pacman.alive = False
                
                # Check collisions with Ms. Pacman
                if game_state == MULTI_PLAYER and ms_pacman and ms_pacman.alive:
                    if abs(ghost.x - ms_pacman.x) < 0.5 and abs(ghost.y - ms_pacman.y) < 0.5:
                        if ghost.vulnerable:
                            ghost.eaten = True
                            ms_pacman.score += GHOST_POINTS
                        else:
                            ms_pacman.alive = False
            
            # Draw everything
            screen.fill(BLACK)
            draw_maze(screen, maze)
            if pacman.alive:
                pacman.draw(screen)
            if game_state == MULTI_PLAYER and ms_pacman and ms_pacman.alive:
                ms_pacman.draw(screen)
            for ghost in ghosts:
                ghost.draw(screen)
            
            # Draw scores
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'P1: {pacman.score}', True, YELLOW)
            screen.blit(score_text, (10, WINDOW_HEIGHT - 40))
            if game_state == MULTI_PLAYER and ms_pacman:
                ms_score_text = font.render(f'P2: {ms_pacman.score}', True, PINK)
                screen.blit(ms_score_text, (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 40))
            
            # Check win/lose conditions
            if game_state == SINGLE_PLAYER:
                if not pacman.alive:
                    game_state = GAME_OVER
                elif check_win(maze):
                    game_state = GAME_OVER
            else:  # Multi-player
                if not pacman.alive and not ms_pacman.alive:
                    game_state = GAME_OVER
                elif check_win(maze):
                    game_state = GAME_OVER
        
        elif game_state == GAME_OVER:
            total_score = pacman.score
            if ms_pacman:
                total_score += ms_pacman.score
            won = check_win(maze)
            draw_game_over(screen, won, total_score, game_state)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == '__main__':
    main()
