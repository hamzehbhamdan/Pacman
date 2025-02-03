import pytest
import pygame
from pacman import Pacman, Ghost, MAZE, COLS as MAZE_WIDTH, check_win

# Initialize pygame for tests
pygame.init()

class TestPacman:
    def setup_method(self):
        """Set up test fixtures for each test method"""
        self.pacman = Pacman()
        self.ghosts = [
            Ghost(9, 8, (255, 0, 0), "blinky"),
            Ghost(8, 8, (255, 192, 203), "pinky"),
            Ghost(10, 8, (0, 255, 255), "inky"),
            Ghost(9, 9, (255, 165, 0), "clyde")
        ]
        self.maze = [row[:] for row in MAZE]

    def test_pacman_initialization(self):
        """Test Pacman's initial state"""
        assert self.pacman.x == 9
        assert self.pacman.y == 11  # Updated to match actual initial position
        assert self.pacman.direction == (0, 0)
        assert self.pacman.next_direction == (0, 0)
        assert self.pacman.score == 0

    def test_ghost_initialization(self):
        """Test Ghost's initial state"""
        ghost = self.ghosts[0]  # Blinky
        assert ghost.x == 9
        assert ghost.y == 8
        assert ghost.direction == (0, 0)
        assert ghost.vulnerable == False
        assert ghost.eaten == False
        assert ghost.vulnerable_timer == 0
        assert ghost.respawn_timer == 0

    def test_ghost_vulnerability(self):
        """Test ghost vulnerability mechanics"""
        ghost = self.ghosts[0]
        ghost.make_vulnerable()
        assert ghost.vulnerable == True
        assert ghost.vulnerable_timer > 0
        
        # Test vulnerability timeout
        for _ in range(ghost.vulnerable_timer + 1):
            ghost.move(self.maze, self.pacman, self.ghosts)
        assert ghost.vulnerable == False

    def test_ghost_targeting(self):
        """Test different ghost targeting behaviors"""
        pacman = self.pacman
        pacman.x, pacman.y = 10, 10
        pacman.direction = (1, 0)
        
        # Test Blinky (direct chase)
        blinky = self.ghosts[0]
        blinky.x, blinky.y = 5, 5
        blinky.move(self.maze, pacman, self.ghosts)
        assert blinky.direction[0] > 0  # Should move right towards Pacman
        
        # Test Pinky (4 tiles ahead)
        pinky = self.ghosts[1]
        pinky.x, pinky.y = 5, 5
        pinky.move(self.maze, pacman, self.ghosts)
        assert pinky.direction[0] > 0  # Should move towards Pacman's future position

    def test_ghost_collision_prevention(self):
        """Test that ghosts don't overlap"""
        ghost1 = self.ghosts[0]
        ghost2 = self.ghosts[1]
        
        # Place ghosts near each other
        ghost1.x, ghost1.y = 5, 5
        ghost2.x, ghost2.y = 6, 5
        
        # Move ghosts
        ghost1.move(self.maze, self.pacman, self.ghosts)
        ghost2.move(self.maze, self.pacman, self.ghosts)
        
        # Check they maintain minimum distance
        distance = ((ghost1.x - ghost2.x) ** 2 + (ghost1.y - ghost2.y) ** 2) ** 0.5
        assert distance >= 1.0

    def test_tunnel_wrapping(self):
        """Test tunnel wrapping for Pacman and ghosts"""
        # Test Pacman wrapping
        self.pacman.x = 0
        self.pacman.y = 8  # Tunnel row
        self.pacman.direction = (-1, 0)
        self.pacman.move(self.maze, self.ghosts)
        assert self.pacman.x >= MAZE_WIDTH - 1  # Should wrap to right side
        
        # Test Ghost wrapping
        ghost = self.ghosts[0]
        ghost.x = 0
        ghost.y = 8  # Tunnel row
        ghost.direction = (-1, 0)
        ghost.move(self.maze, self.pacman, self.ghosts)
        assert ghost.x >= MAZE_WIDTH - 1  # Should wrap to right side

    def test_dot_collection(self):
        """Test dot collection and scoring"""
        # Place Pacman on a dot
        self.pacman.x = 1
        self.pacman.y = 1
        initial_score = self.pacman.score
        
        # Move Pacman to collect dot
        self.pacman.move(self.maze, self.ghosts)
        assert self.maze[1][1] == 0  # Dot should be gone
        assert self.pacman.score > initial_score

    def test_power_pellet(self):
        """Test power pellet effects"""
        # Place power pellet
        self.maze[1][1] = 3
        self.pacman.x = 1
        self.pacman.y = 1
        
        # Collect power pellet
        self.pacman.move(self.maze, self.ghosts)
        
        # Check effects
        assert self.maze[1][1] == 0  # Pellet should be gone
        for ghost in self.ghosts:
            assert ghost.vulnerable == True
            assert ghost.vulnerable_timer > 0

    def test_win_condition(self):
        """Test win condition detection"""
        # Fill maze with walls and empty spaces (no dots)
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] in [2, 3]:  # Remove dots and power pellets
                    self.maze[y][x] = 0
        
        assert check_win(self.maze) == True
        
        # Add one dot back
        self.maze[1][1] = 2
        assert check_win(self.maze) == False
