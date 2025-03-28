import random
import time
import csv
import os
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.csv_file = "sudoku_games.csv"
        self._initialize_csv()
        
    def _initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp", "game_id", "provided_numbers", 
                    "density", "completion_time", "result", "mistakes", "moves"
                ])
    
    def log_game_result(self, game_id, provided_numbers, density, completion_time, result, mistakes, moves):
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                game_id,
                provided_numbers,
                density,
                completion_time,
                result,
                mistakes,
                moves
            ])

class SudokuLogic:
    def __init__(self):
        self.grid_size = 9
        self.full_grid = None
        self.user_grid = None
        self.puzzle_grid = None
        self.wrong_cells = set()
        self.mistakes = 0
        self.moves_made = 0
        self.start_time = None
        self.hint_cell = None
        self.game_over_time = None
        self.current_game_index = 0
        
        self.baseline_games = [
            {"game_id": 1, "provided_numbers": 25, "density": 0.4},
            {"game_id": 2, "provided_numbers": 30, "density": 0.5},
            {"game_id": 3, "provided_numbers": 35, "density": 0.6},
            {"game_id": 4, "provided_numbers": 40, "density": 0.45},
            {"game_id": 5, "provided_numbers": 28, "density": 0.42},
            {"game_id": 6, "provided_numbers": 32, "density": 0.48},
            {"game_id": 7, "provided_numbers": 37, "density": 0.55},
            {"game_id": 8, "provided_numbers": 42, "density": 0.50},
            {"game_id": 9, "provided_numbers": 26, "density": 0.43},
            {"game_id": 10, "provided_numbers": 33, "density": 0.49},
            {"game_id": 11, "provided_numbers": 38, "density": 0.56},
            {"game_id": 12, "provided_numbers": 44, "density": 0.52},
            {"game_id": 13, "provided_numbers": 27, "density": 0.44},
            {"game_id": 14, "provided_numbers": 34, "density": 0.47},
            {"game_id": 15, "provided_numbers": 39, "density": 0.53},
            {"game_id": 16, "provided_numbers": 45, "density": 0.58},
            {"game_id": 17, "provided_numbers": 29, "density": 0.41},
            {"game_id": 18, "provided_numbers": 31, "density": 0.46},
            {"game_id": 19, "provided_numbers": 36, "density": 0.51},
            {"game_id": 20, "provided_numbers": 41, "density": 0.57},
        ]
        
        self.data_logger = DataLogger()
        self.reset_game()
    
    def is_valid_move(self, grid, row, col, num):
        for i in range(self.grid_size):
            if grid[row][i] == num or grid[i][col] == num:
                return False
        
        box_x, box_y = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if grid[box_x + i][box_y + j] == num:
                    return False
        return True
    
    def generate_sudoku(self):
        grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        def fill_grid():
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if grid[row][col] == 0:
                        numbers = list(range(1, 10))
                        random.shuffle(numbers)
                        for num in numbers:
                            if self.is_valid_move(grid, row, col, num):
                                grid[row][col] = num
                                if fill_grid():
                                    return True
                                grid[row][col] = 0
                        return False
            return True
        
        fill_grid()
        return grid
    
    def remove_numbers(self, grid, provided_numbers):
        puzzle = [row[:] for row in grid]
        total_cells = self.grid_size * self.grid_size
        numbers_to_remove = total_cells - provided_numbers

        while numbers_to_remove > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if puzzle[row][col] != 0:
                puzzle[row][col] = 0
                numbers_to_remove -= 1

        return puzzle
    
    def reset_game(self):
        current_game = self.baseline_games[self.current_game_index]
        provided_numbers = current_game["provided_numbers"]
        
        self.full_grid = self.generate_sudoku()
        self.puzzle_grid = self.remove_numbers(self.full_grid, provided_numbers)
        self.user_grid = [row[:] for row in self.puzzle_grid]
        self.wrong_cells = set()
        self.mistakes = 0
        self.moves_made = 0
        self.hint_cell = None
        self.start_time = time.time()
        self.game_over_time = None
    
    def check_move(self, row, col, num):
        is_correct = (num == self.full_grid[row][col])
        if not is_correct:
            self.mistakes += 1
            self.wrong_cells.add((row, col))
        else:
            self.wrong_cells.discard((row, col))
        return is_correct
    
    def check_completion(self):
        return self.user_grid == self.full_grid
    
    def provide_hint(self):
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.user_grid[r][c] == 0]
        if empty_cells:
            self.hint_cell = random.choice(empty_cells)
            self.user_grid[self.hint_cell[0]][self.hint_cell[1]] = self.full_grid[self.hint_cell[0]][self.hint_cell[1]]
            return self.hint_cell
        return None
    
    def next_game(self):
        self.current_game_index = (self.current_game_index + 1) % len(self.baseline_games)
        self.reset_game()
    
    def log_game_result(self, result):
        current_game = self.baseline_games[self.current_game_index]
        completion_time = int((self.game_over_time or time.time()) - self.start_time)
        
        self.data_logger.log_game_result(
            game_id=current_game["game_id"],
            provided_numbers=current_game["provided_numbers"],
            density=current_game["density"],
            completion_time=completion_time,
            result=result,
            mistakes=self.mistakes,
            moves=self.moves_made
        )