import torch
import random
import numpy as np

class MazeGame:
    def __init__(self, size):
        self.size = size
        self.maze = torch.zeros(size, size)
        self.player_position = (0, 0)
        self.exit_position = (size - 1, size - 1)
        self.generate_maze()

    def generate_maze(self):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        stack = [(0, 0)]
        self.maze[0, 0] = 2
        self.recorded_path = []

        while stack:
            current = stack[-1]
            if current == self.exit_position:
                # The stack now contains the clean path from start to exit
                self.recorded_path = list(stack)
                break

            next_steps = []
            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.maze[nx, ny] == 0:
                    next_steps.append((nx, ny))

            if next_steps:
                # Prioritize steps that move closer to the exit (Manhattan distance)
                # This prevents the path from wandering aimlessly and "taking too much space"
                next_steps.sort(key=lambda p: abs(p[0] - self.exit_position[0]) + abs(p[1] - self.exit_position[1]))
                
                # 80% chance to take the most direct step, 20% for random exploration
                if random.random() < 0.8:
                    choice = next_steps[0]
                else:
                    choice = random.choice(next_steps)

                self.maze[choice[0], choice[1]] = 2
                stack.append(choice)
            else:
                stack.pop()

        # Fill unvisited areas with more walls to make it look like a real maze
        for i in range(self.size):
            for j in range(self.size):
                if self.maze[i, j] == 0:
                    self.maze[i, j] = np.random.choice([0, 1], p=[0.6, 0.4])

        self.maze[self.maze == 2] = 0

    def move_player(self, direction):
        if direction == 'auto':
            for rx, ry in self.recorded_path:
                # Mark the path with '*' (represented by 3 in the grid)
                if (rx, ry) != self.player_position and (rx, ry) != self.exit_position:
                    self.maze[rx, ry] = 3
            self.player_position = self.exit_position
            self.display_game()
            return
            
        x, y = self.player_position
        if direction in ['up', 'w', '\x1b[A'] and x > 0 and self.maze[x - 1, y] == 0:
            self.player_position = (x - 1, y)
        elif direction in ['down', 's', '\x1b[B'] and x < self.size - 1 and self.maze[x + 1, y] == 0:
            self.player_position = (x + 1, y)
        elif direction in ['left', 'a', '\x1b[D'] and y > 0 and self.maze[x, y - 1] == 0:
            self.player_position = (x, y - 1)
        elif direction in ['right', 'd', '\x1b[C'] and y < self.size - 1 and self.maze[x, y + 1] == 0:
            self.player_position = (x, y + 1)

    def check_game_status(self):
        if self.player_position == self.exit_position:
            return 'Win'
        elif self.maze[self.player_position[0], self.player_position[1]] == 1:
            return 'Hit obstacle'
        else:
            return 'Continue'

    def display_game(self):
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) == self.player_position:
                    print('P', end=' ')
                elif (i, j) == self.exit_position:
                    print('E', end=' ')
                elif self.maze[i, j] == 1:
                    print('#', end=' ')
                elif self.maze[i, j] == 3:
                    print('*', end=' ')
                else:
                    print('.', end=' ')
            print()

maze_game = MazeGame(10)

while True:
    maze_game.display_game()
    print("Enter your move (up, down, left, right):")
    try:
        move = input().strip().lower()
        maze_game.move_player(move)
    except EOFError:
        print("\nExiting the game. Goodbye!")
        break
    status = maze_game.check_game_status()
    if status == 'Win':
        print("Congratulations! You win!")
        break
    elif status == 'Hit obstacle':
        print("Oops! You hit an obstacle. Game over!")
        break
    else:
        print("Continue exploring...")