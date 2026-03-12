import torch
import random

class MazeGame:
    def __init__(self, size):
        self.size = size
        self.maze = torch.zeros(size, size)
        self.player_position = (0, 0)
        self.exit_position = (size - 1, size - 1)
        self.generate_maze()
    
    def generate_maze(self):
        for i in range(self.size):
            for j in range(self.size):
                # 生成隨機迷宮，0 表示通道，1 表示障礙物
                self.maze[i, j] = random.choice([0, 1])

        # 確保起點和終點是通道
        self.maze[0, 0] = 0
        self.maze[self.size - 1, self.size - 1] = 0

    def move_player(self, direction):
        x, y = self.player_position
        if direction == 'up' and x > 0 and self.maze[x - 1, y] == 0:
            self.player_position = (x - 1, y)
        elif direction == 'down' and x < self.size - 1 and self.maze[x + 1, y] == 0:
            self.player_position = (x + 1, y)
        elif direction == 'left' and y > 0 and self.maze[x, y - 1] == 0:
            self.player_position = (x, y - 1)
        elif direction == 'right' and y < self.size - 1 and self.maze[x, y + 1] == 0:
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
                else:
                    print('.', end=' ')
            print()

# 
maze_game = MazeGame(5)

# 
while True:
    maze_game.display_game()
    print("Enter your move (up, down, left, right):")
    move = input().strip().lower()
    maze_game.move_player(move)
    status = maze_game.check_game_status()
    if status == 'Win':
        print("Congratulations! You win!")
        break
    elif status == 'Hit obstacle':
        print("Oops! You hit an obstacle. Game over!")
        break
    else:
        print("Continue exploring...")
