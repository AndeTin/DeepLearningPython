import random
import os
import sys
import tty
import termios
from collections import deque

def getch():
    """Reads a single character from standard input without requiring Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class MazeGame:
    def __init__(self, size):
        self.size = size
        self.maze = [[1 for _ in range(size)] for _ in range(size)]
        self.player_position = (0, 0)
        self.exit_position = (size - 1, size - 1)
        self.recorded_path = []
        self.show_auto_path = False
        self.generate_maze()
        self.solve_maze()

    def generate_maze(self):
        # Recursive Backtracking (DFS) to generate a real maze
        stack = [(0, 0)]
        self.maze[0][0] = 0
        
        while stack:
            x, y = stack[-1]
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            
            carved = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check bounds and if it's a wall
                if 0 <= nx < self.size and 0 <= ny < self.size and self.maze[nx][ny] == 1:
                    # Check how many '0' (path) neighbors the target cell has.
                    # If more than 1, carving it would create a loop/cycle.
                    path_neighbors = 0
                    for ddx, ddy in directions:
                        nnx, nny = nx + ddx, ny + ddy
                        if 0 <= nnx < self.size and 0 <= nny < self.size and self.maze[nnx][nny] == 0:
                            path_neighbors += 1
                    
                    if path_neighbors == 1:
                        self.maze[nx][ny] = 0
                        stack.append((nx, ny))
                        carved = True
                        break
                        
            if not carved:
                stack.pop()
                
        # Ensure the exit position is accessible (it might occasionally get walled off)
        self.maze[self.exit_position[0]][self.exit_position[1]] = 0
        exit_x, exit_y = self.exit_position
        if all(self.maze[exit_x+dx][exit_y+dy] == 1 for dx, dy in [(-1, 0), (0, -1)] if 0 <= exit_x+dx < self.size and 0 <= exit_y+dy < self.size):
            self.maze[exit_x-1][exit_y] = 0 # Force a connection to the exit

    def solve_maze(self):
        # BFS to find the shortest path from start to exit
        queue = deque([[(0, 0)]])
        visited = set([(0, 0)])
        
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            
            if (x, y) == self.exit_position:
                self.recorded_path = path
                return
                
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.maze[nx][ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(path + [(nx, ny)])

    def move_player(self, direction):
        if direction == 'g':
            self.show_auto_path = True
            return
            
        x, y = self.player_position
        # Check boundaries and ensure the destination is not a wall (1)
        if direction == 'w' and x > 0 and self.maze[x - 1][y] == 0:
            self.player_position = (x - 1, y)
        elif direction == 's' and x < self.size - 1 and self.maze[x + 1][y] == 0:
            self.player_position = (x + 1, y)
        elif direction == 'a' and y > 0 and self.maze[x][y - 1] == 0:
            self.player_position = (x, y - 1)
        elif direction == 'd' and y < self.size - 1 and self.maze[x][y + 1] == 0:
            self.player_position = (x, y + 1)

    def check_game_status(self):
        if self.player_position == self.exit_position:
            return 'Win'
        return 'Continue'

    def display_game(self):
        # Clear the terminal for a cleaner UX
        os.system('cls' if os.name == 'nt' else 'clear')
        
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) == self.player_position:
                    print('P', end=' ')
                elif (i, j) == self.exit_position:
                    print('E', end=' ')
                elif self.show_auto_path and (i, j) in self.recorded_path:
                    print('*', end=' ')
                elif self.maze[i][j] == 1:
                    print('#', end=' ')
                else:
                    print(' ', end=' ') # Changed empty space to ' ' instead of '.' for cleaner look
            print()
        print("\nControls:")
        print("  W/A/S/D : Move")
        print("  G       : Show Solution")
        print("  Q       : Quit")

if __name__ == "__main__":
    maze_game = MazeGame(10)

    while True:
        maze_game.display_game()
        
        move = getch().lower()
        
        # Handle quit or Ctrl+C (\x03)
        if move == 'q' or move == '\x03':
            print("\nExiting the game. Goodbye!")
            break
            
        maze_game.move_player(move)
            
        status = maze_game.check_game_status()
        if status == 'Win':
            maze_game.display_game()
            print("\nCongratulations! You win!")
            break
