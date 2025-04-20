import random
import time
import csv
import os
from datetime import datetime
from sklearn.cluster import KMeans
import numpy as np

class DataLogger:
    def __init__(self):
        self.csv_file = "sudoku_performance.csv"
        self._initialize_csv()
        
    def _initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp", "game_id", "difficulty_label",
                    "completion_time", "mistakes", "hints_used", "moves",
                    "provided_numbers", "n_clusters", "spread_factor",
                    "max_mistakes", "result"
                ])
    
    def log_game_data(self, game_id, difficulty_label, completion_time, 
                     mistakes, hints_used, moves, provided_numbers,
                     n_clusters, spread_factor, max_mistakes, result):
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                game_id,
                difficulty_label,
                completion_time,
                mistakes,
                hints_used,
                moves,
                provided_numbers,
                n_clusters,
                spread_factor,
                max_mistakes,
                result
            ])

class SudokuLogic:
    def __init__(self):
        self.grid_size = 9
        self.full_grid = None
        self.user_grid = None
        self.puzzle_grid = None
        self.wrong_cells = set()
        self.mistakes = 0
        self.max_mistakes = 10
        self.moves_made = 0
        self.hints_used = 0
        self.max_hints = 8
        self.hints_remaining = self.max_hints
        self.start_time = None
        self.hint_cell = None
        self.game_over_time = None
        self.current_game_index = 0
        self.progress_file = "sudoku_progress.txt"
        self.cluster_centers = None
        
        self.baseline_games = [
            {"game_id": 1, "provided_numbers": 45, "clusters": 1, "spread": 0.95, "label": "Super Easy 1", "max_mistakes": 20},
            {"game_id": 2, "provided_numbers": 44, "clusters": 1, "spread": 0.94, "label": "Super Easy 2", "max_mistakes": 20},
            {"game_id": 3, "provided_numbers": 43, "clusters": 1, "spread": 0.93, "label": "Super Easy 3", "max_mistakes": 20},
            {"game_id": 4, "provided_numbers": 42, "clusters": 1, "spread": 0.92, "label": "Super Easy 4", "max_mistakes": 20},
            {"game_id": 5, "provided_numbers": 41, "clusters": 1, "spread": 0.91, "label": "Super Easy 5", "max_mistakes": 20},
            {"game_id": 6, "provided_numbers": 40, "clusters": 1, "spread": 0.9, "label": "Beginner 1", "max_mistakes": 15},
            {"game_id": 7, "provided_numbers": 39, "clusters": 1, "spread": 0.88, "label": "Beginner 2", "max_mistakes": 15},
            {"game_id": 8, "provided_numbers": 38, "clusters": 1, "spread": 0.86, "label": "Beginner 3", "max_mistakes": 15},
            {"game_id": 9, "provided_numbers": 37, "clusters": 1, "spread": 0.84, "label": "Beginner 4", "max_mistakes": 15},
            {"game_id": 10, "provided_numbers": 36, "clusters": 1, "spread": 0.82, "label": "Beginner 5", "max_mistakes": 15},
            {"game_id": 11, "provided_numbers": 35, "clusters": 1, "spread": 0.8, "label": "Intermediate 1", "max_mistakes": 10},
            {"game_id": 12, "provided_numbers": 34, "clusters": 1, "spread": 0.78, "label": "Intermediate 2", "max_mistakes": 10},
            {"game_id": 13, "provided_numbers": 32, "clusters": 2, "spread": 0.75, "label": "Intermediate 3", "max_mistakes": 10},
            {"game_id": 14, "provided_numbers": 30, "clusters": 2, "spread": 0.7, "label": "Intermediate 4", "max_mistakes": 10},
            {"game_id": 15, "provided_numbers": 28, "clusters": 2, "spread": 0.65, "label": "Intermediate 5", "max_mistakes": 10},
            {"game_id": 16, "provided_numbers": 26, "clusters": 2, "spread": 0.6, "label": "Advanced 1", "max_mistakes": 5},
            {"game_id": 17, "provided_numbers": 24, "clusters": 3, "spread": 0.55, "label": "Advanced 2", "max_mistakes": 5},
            {"game_id": 18, "provided_numbers": 22, "clusters": 3, "spread": 0.5, "label": "Advanced 3", "max_mistakes": 5},
            {"game_id": 19, "provided_numbers": 20, "clusters": 3, "spread": 0.45, "label": "Advanced 4", "max_mistakes": 5},
            {"game_id": 20, "provided_numbers": 18, "clusters": 3, "spread": 0.4, "label": "Advanced 5", "max_mistakes": 5}
        ]
        
        self.data_logger = DataLogger()
        self.load_progress()
        self.reset_game()
    
    def load_progress(self):
        try:
            with open(self.progress_file, 'r') as f:
                self.current_game_index = int(f.read().strip())
                if self.current_game_index >= len(self.baseline_games):
                    self.current_game_index = 0
        except (FileNotFoundError, ValueError):
            self.current_game_index = 0

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            f.write(str(self.current_game_index))

    def is_valid_move(self, grid, row, col, num):
        if num == 0:
            return True
            
        # Check row
        for x in range(9):
            if grid[row][x] == num and x != col:
                return False
        
        # Check column
        for x in range(9):
            if grid[x][col] == num and x != row:
                return False
        
        # Check 3x3 box
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num and (i + start_row != row or j + start_col != col):
                    return False
        return True
    
    def generate_sudoku(self):
        grid = [[0 for _ in range(9)] for _ in range(9)]
        
        def fill_diagonal():
            for box in range(0, 9, 3):
                nums = list(range(1, 10))
                random.shuffle(nums)
                for i in range(3):
                    for j in range(3):
                        grid[box + i][box + j] = nums.pop()
        
        def fill_remaining(row, col):
            if col >= 9 and row < 8:
                row += 1
                col = 0
            if row >= 9 and col >= 9:
                return True
            if row < 3:
                if col < 3:
                    col = 3
            elif row < 6:
                if col == int(row / 3) * 3:
                    col += 3
            else:
                if col == 6:
                    row += 1
                    col = 0
                    if row >= 9:
                        return True
            
            for num in range(1, 10):
                if self.is_valid_move(grid, row, col, num):
                    grid[row][col] = num
                    if fill_remaining(row, col + 1):
                        return True
                    grid[row][col] = 0
            return False
        
        fill_diagonal()
        fill_remaining(0, 3)
        return grid
    
    def remove_numbers_with_clusters(self, grid, provided_numbers, n_clusters, spread_factor):
        puzzle = [row[:] for row in grid]
        total_cells = 81
        numbers_to_remove = total_cells - provided_numbers
        
        coords = np.array([(i, j) for i in range(9) for j in range(9)])
        
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            init='k-means++',
            n_init=10
        )
        kmeans.fit(coords)
        self.cluster_centers = kmeans.cluster_centers_
        
        distances = kmeans.transform(coords)
        min_distances = np.min(distances, axis=1)
        
        probabilities = np.exp(-min_distances / (spread_factor * 2))
        probabilities /= probabilities.sum()
        
        remove_indices = np.random.choice(
            len(coords), 
            size=numbers_to_remove, 
            replace=False, 
            p=probabilities
        )
        
        for idx in remove_indices:
            row, col = coords[idx]
            puzzle[row][col] = 0
            
        return puzzle
    
    def reset_game(self):
        current_game = self.baseline_games[self.current_game_index]
        self.max_mistakes = current_game["max_mistakes"]
        
        self.full_grid = self.generate_sudoku()
        self.puzzle_grid = self.remove_numbers_with_clusters(
            self.full_grid, 
            current_game["provided_numbers"],
            current_game["clusters"],
            current_game["spread"]
        )
        self.user_grid = [row[:] for row in self.puzzle_grid]
        self.wrong_cells = set()
        self.mistakes = 0
        self.moves_made = 0
        self.hints_used = 0
        self.hints_remaining = self.max_hints
        self.hint_cell = None
        self.start_time = time.time()
        self.game_over_time = None
        self.save_progress()
    
    def check_move(self, row, col, num):
        if num == 0:
            self.user_grid[row][col] = 0
            self.wrong_cells.discard((row, col))
            self.moves_made += 1
            return True
            
        if not self.is_valid_move(self.user_grid, row, col, num):
            self.mistakes += 1
            self.wrong_cells.add((row, col))
            self.moves_made += 1
            return False
            
        is_correct = (num == self.full_grid[row][col])
        if is_correct:
            self.user_grid[row][col] = num
            self.wrong_cells.discard((row, col))
        else:
            self.mistakes += 1
            self.wrong_cells.add((row, col))
            
        self.moves_made += 1
        return is_correct
    
    def check_completion(self):
        for row in range(9):
            for col in range(9):
                if self.user_grid[row][col] != self.full_grid[row][col]:
                    return False
        return True
    
    def provide_hint(self):
        if self.hints_remaining <= 0:
            return None
            
        empty_cells = [(r, c) for r in range(9) for c in range(9) if self.user_grid[r][c] == 0]
        if empty_cells:
            self.hints_used += 1
            self.hints_remaining -= 1
            self.hint_cell = random.choice(empty_cells)
            row, col = self.hint_cell
            self.user_grid[row][col] = self.full_grid[row][col]
            return self.hint_cell
        return None
    
    def next_game(self):
        self.current_game_index = (self.current_game_index + 1) % len(self.baseline_games)
        self.reset_game()
    
    def previous_game(self):
        self.current_game_index = (self.current_game_index - 1) % len(self.baseline_games)
        self.reset_game()
    
    def set_difficulty(self, level):
        if 0 <= level < len(self.baseline_games):
            self.current_game_index = level
            self.reset_game()
    
    def log_game_result(self, result):
        current_game = self.baseline_games[self.current_game_index]
        completion_time = int((self.game_over_time or time.time()) - self.start_time)
        
        self.data_logger.log_game_data(
            game_id=current_game["game_id"],
            difficulty_label=current_game["label"],
            completion_time=completion_time,
            mistakes=self.mistakes,
            hints_used=self.hints_used,
            moves=self.moves_made,
            provided_numbers=current_game["provided_numbers"],
            n_clusters=current_game["clusters"],
            spread_factor=current_game["spread"],
            max_mistakes=current_game["max_mistakes"],
            result=result
        )
    
    def get_current_difficulty_info(self):
        current_game = self.baseline_games[self.current_game_index]
        return {
            "label": current_game["label"],
            "provided": current_game["provided_numbers"],
            "max_mistakes": current_game["max_mistakes"],
            "progress": f"{self.current_game_index + 1}/{len(self.baseline_games)}"
        }
    
    def get_game_time(self):
        return int(time.time() - self.start_time)
    
    def get_remaining_cells(self):
        return sum(1 for row in range(9) for col in range(9) if self.user_grid[row][col] == 0)