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
                    "result"
                ])
    
    def log_game_data(self, game_id, difficulty_label, completion_time, 
                     mistakes, hints_used, moves, provided_numbers,
                     n_clusters, spread_factor, result):
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
        self.max_mistakes = 8  # Increased from 3 to 8
        self.moves_made = 0
        self.hints_used = 0
        self.start_time = None
        self.hint_cell = None
        self.game_over_time = None
        self.current_game_index = 0
        self.progress_file = "sudoku_progress.txt"
        
        # 20 games with difficulty parameters
        self.baseline_games = [
            # Beginner (5 games)
            {"game_id": 1, "provided_numbers": 32, "clusters": 1, "spread": 0.9, "label": "Beginner"},
            {"game_id": 2, "provided_numbers": 32, "clusters": 1, "spread": 0.85, "label": "Beginner"},
            {"game_id": 3, "provided_numbers": 31, "clusters": 1, "spread": 0.8, "label": "Beginner"},
            {"game_id": 4, "provided_numbers": 31, "clusters": 1, "spread": 0.75, "label": "Beginner"},
            {"game_id": 5, "provided_numbers": 30, "clusters": 1, "spread": 0.7, "label": "Beginner"},
            
            # Intermediate (5 games)
            {"game_id": 6, "provided_numbers": 30, "clusters": 2, "spread": 0.8, "label": "Intermediate"},
            {"game_id": 7, "provided_numbers": 29, "clusters": 2, "spread": 0.75, "label": "Intermediate"},
            {"game_id": 8, "provided_numbers": 28, "clusters": 2, "spread": 0.7, "label": "Intermediate"},
            {"game_id": 9, "provided_numbers": 27, "clusters": 2, "spread": 0.65, "label": "Intermediate"},
            {"game_id": 10, "provided_numbers": 26, "clusters": 2, "spread": 0.6, "label": "Intermediate"},
            
            # Advanced (5 games)
            {"game_id": 11, "provided_numbers": 25, "clusters": 3, "spread": 0.7, "label": "Advanced"},
            {"game_id": 12, "provided_numbers": 24, "clusters": 3, "spread": 0.65, "label": "Advanced"},
            {"game_id": 13, "provided_numbers": 23, "clusters": 3, "spread": 0.6, "label": "Advanced"},
            {"game_id": 14, "provided_numbers": 22, "clusters": 3, "spread": 0.55, "label": "Advanced"},
            {"game_id": 15, "provided_numbers": 21, "clusters": 3, "spread": 0.5, "label": "Advanced"},
            
            # Expert (5 games)
            {"game_id": 16, "provided_numbers": 20, "clusters": 4, "spread": 0.6, "label": "Expert"},
            {"game_id": 17, "provided_numbers": 19, "clusters": 4, "spread": 0.55, "label": "Expert"},
            {"game_id": 18, "provided_numbers": 18, "clusters": 4, "spread": 0.5, "label": "Expert"},
            {"game_id": 19, "provided_numbers": 17, "clusters": 4, "spread": 0.45, "label": "Expert"},
            {"game_id": 20, "provided_numbers": 16, "clusters": 4, "spread": 0.4, "label": "Expert"}
        ]
        
        self.data_logger = DataLogger()
        self.load_progress()
        self.reset_game()
    
    def load_progress(self):
        try:
            with open(self.progress_file, 'r') as f:
                self.current_game_index = int(f.read().strip())
                # Ensure index is within bounds
                if self.current_game_index >= len(self.baseline_games):
                    self.current_game_index = 0
        except (FileNotFoundError, ValueError):
            self.current_game_index = 0

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            f.write(str(self.current_game_index))

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
    
    def remove_numbers_with_clusters(self, grid, provided_numbers, n_clusters, spread_factor):
        puzzle = [row[:] for row in grid]
        total_cells = self.grid_size * self.grid_size
        numbers_to_remove = total_cells - provided_numbers
        
        # Generate coordinates of all cells
        coords = np.array([(i, j) for i in range(9) for j in range(9)])
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(coords)
        
        # Get distances to cluster centers
        distances = kmeans.transform(coords)
        
        # Create probability distribution based on distances
        min_distances = np.min(distances, axis=1)
        probabilities = 1 / (min_distances + 1e-6)  # Avoid division by zero
        probabilities = probabilities ** (1/spread_factor)  # Adjust spread
        probabilities /= probabilities.sum()  # Normalize
        
        # Select cells to remove based on probabilities
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
        self.save_progress()
        current_game = self.baseline_games[self.current_game_index]
        provided_numbers = current_game["provided_numbers"]
        n_clusters = current_game["clusters"]
        spread = current_game["spread"]
        
        self.full_grid = self.generate_sudoku()
        self.puzzle_grid = self.remove_numbers_with_clusters(
            self.full_grid, 
            provided_numbers,
            n_clusters,
            spread
        )
        self.user_grid = [row[:] for row in self.puzzle_grid]
        self.wrong_cells = set()
        self.mistakes = 0
        self.moves_made = 0
        self.hints_used = 0
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
        self.hints_used += 1
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.user_grid[r][c] == 0]
        if empty_cells:
            self.hint_cell = random.choice(empty_cells)
            self.user_grid[self.hint_cell[0]][self.hint_cell[1]] = self.full_grid[self.hint_cell[0]][self.hint_cell[1]]
            return self.hint_cell
        return None
    
    def next_game(self):
        self.current_game_index = (self.current_game_index + 1) % len(self.baseline_games)
        self.save_progress()
        self.reset_game()
    
    def set_difficulty(self, level):
        """Set difficulty level (0-4) where 0 is easiest and 4 is hardest"""
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
            result=result
        )