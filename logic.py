import random
import time
import csv
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.csv_file = "sudoku_performance.csv"
        self._initialize_csv()
        
    def _initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp", "mode", "difficulty_label",
                    "completion_time", "mistakes", "hints_used", "moves",
                    "provided_numbers", "n_clusters", "spread_factor",
                    "max_mistakes", "result"
                ])
    
    def log_game_data(self, game_data):
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                game_data['timestamp'],
                game_data['mode'],
                game_data['difficulty_label'],
                game_data['completion_time'],
                game_data['mistakes'],
                game_data['hints_used'],
                game_data['moves'],
                game_data['provided_numbers'],
                game_data['n_clusters'],
                game_data['spread_factor'],
                game_data['max_mistakes'],
                game_data['result']
            ])

class SudokuLogic:
    def __init__(self):
        # Game state variables
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
        self.cluster_centers = None
        
        # Adaptive difficulty system
        self.model_path = Path(__file__).parent / "models" / "sudoku_model_new.pkl"
        os.makedirs(self.model_path.parent, exist_ok=True)
        self.model_loaded = False
        self.learning_games = []
        self.adaptive_mode = False
        self.current_difficulty = {
            'label': 'Medium',
            'provided_numbers': 30,
            'spread': 0.7,
            'clusters': 2,
            'max_mistakes': 10
        }
        
        # Initialize systems
        self._load_or_create_model()
        self.data_logger = DataLogger()
        self.reset_game()

    def _load_or_create_model(self):
        """Initialize or load the model with better error handling"""
        try:
            if self.model_path.exists():
                model_data = joblib.load(self.model_path)
                if not all(key in model_data for key in ['clues_model', 'spread_model', 'scaler', 'features']):
                    raise ValueError("Invalid model structure")
                
                self.clues_model = model_data['clues_model']
                self.spread_model = model_data['spread_model']
                self.scaler = model_data['scaler']
                self.feature_columns = model_data['features']
                self.feature_imputer = SimpleImputer(strategy='median')
                self.model_loaded = True
                print("✅ Model loaded successfully")
            else:
                print("⚠️ No model found, creating new one...")
                self._create_new_model()
        except Exception as e:
            print(f"❌ Model initialization failed: {e}")
            self.model_loaded = False
            self._create_new_model()

    def _create_new_model(self):
        """Create a new model with default structure"""
        try:
            # Initialize with small dummy data
            dummy_X = np.array([[1, 0, 0, 5, 0.2, 0.01, 0.01]])
            dummy_y_clues = np.array([30])
            dummy_y_spread = np.array([0.7])
            
            self.clues_model = LinearRegression()
            self.spread_model = LinearRegression()
            self.clues_model.fit(dummy_X, dummy_y_clues)
            self.spread_model.fit(dummy_X, dummy_y_spread)
            
            self.scaler = StandardScaler()
            self.scaler.fit(dummy_X)
            
            self.feature_columns = [
                'completion_time', 'mistakes', 'hints_used', 'moves',
                'time_per_move', 'mistake_rate', 'hint_rate'
            ]
            self.feature_imputer = SimpleImputer(strategy='median')
            
            joblib.dump({
                'clues_model': self.clues_model,
                'spread_model': self.spread_model,
                'scaler': self.scaler,
                'features': self.feature_columns
            }, self.model_path)
            
            self.model_loaded = True
            print("✅ Created new model structure")
        except Exception as e:
            print(f"❌ Failed to create new model: {e}")
            self.model_loaded = False

    def is_model_available(self):
        """Check if model is ready for predictions"""
        return self.model_loaded and len(self.learning_games) >= 5

    def generate_sudoku(self):
        """Generate a completed Sudoku grid using a more traditional approach"""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal boxes first (they are independent)
        self._fill_diagonal_boxes(grid)
        
        # Fill remaining cells
        self._fill_remaining(grid, 0, 3)
        
        return grid

    def _fill_diagonal_boxes(self, grid):
        """Fill the three diagonal 3x3 boxes"""
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    grid[box + i][box + j] = nums.pop()

    def _fill_remaining(self, grid, row, col):
        """Recursively fill the remaining cells"""
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
        
        for num in self._shuffled_numbers():
            if self.is_valid_move(grid, row, col, num):
                grid[row][col] = num
                if self._fill_remaining(grid, row, col + 1):
                    return True
                grid[row][col] = 0
        return False

    def _shuffled_numbers(self):
        """Return numbers 1-9 in random order"""
        nums = list(range(1, 10))
        random.shuffle(nums)
        return nums

    def remove_numbers(self, grid, provided_numbers):
        """Remove numbers to create a puzzle with better distribution"""
        puzzle = [row[:] for row in grid]
        cells_to_remove = 81 - provided_numbers
        
        # Create list of all cell coordinates
        all_cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(all_cells)
        
        removed = 0
        for row, col in all_cells:
            # Don't remove if it would make the puzzle unsolvable
            if puzzle[row][col] == 0:
                continue
                
            # Store the value in case we need to put it back
            backup = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if the puzzle still has a unique solution
            if not self._has_unique_solution(puzzle):
                puzzle[row][col] = backup
            else:
                removed += 1
                if removed >= cells_to_remove:
                    break
                    
        return puzzle

    def _has_unique_solution(self, puzzle):
        """Check if the puzzle has exactly one solution"""
        # Make a copy to work with
        temp_grid = [row[:] for row in puzzle]
        
        # Count solutions (we stop after finding 2)
        count = [0]
        self._count_solutions(temp_grid, count)
        return count[0] == 1

    def _count_solutions(self, grid, count):
        """Recursively count solutions (stop at 2)"""
        if count[0] > 1:
            return
            
        empty = self._find_empty_cell(grid)
        if not empty:
            count[0] += 1
            return
            
        row, col = empty
        for num in range(1, 10):
            if self.is_valid_move(grid, row, col, num):
                grid[row][col] = num
                self._count_solutions(grid, count)
                grid[row][col] = 0
                
                if count[0] > 1:
                    return

    def _find_empty_cell(self, grid):
        """Find the next empty cell (returns None if no empty cells)"""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    return (row, col)
        return None

    def is_valid_move(self, grid, row, col, num):
        """Check if a number can be placed in a cell"""
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

    def predict_difficulty(self):
        """Predict optimal difficulty based on player performance"""
        if not self.is_model_available() or len(self.learning_games) < 5:
            return None
            
        try:
            recent_games = self.learning_games[-5:]
            
            # Prepare features
            features = pd.DataFrame([{
                'completion_time': np.mean([g['completion_time'] for g in recent_games]),
                'mistakes': np.mean([g['mistakes'] for g in recent_games]),
                'hints_used': np.mean([g['hints_used'] for g in recent_games]),
                'moves': np.mean([g['moves'] for g in recent_games]),
                'time_per_move': np.mean([g['completion_time']/(g['moves']+1e-6) for g in recent_games]),
                'mistake_rate': np.mean([g['mistakes']/(g['completion_time']+1e-6) for g in recent_games]),
                'hint_rate': np.mean([g['hints_used']/(g['completion_time']+1e-6) for g in recent_games])
            }], columns=self.feature_columns)
            
            # Preprocess and predict
            features = self.feature_imputer.transform(features)
            features_scaled = self.scaler.transform(features)
            
            provided = np.clip(self.clues_model.predict(features_scaled)[0], 25, 45)
            spread = np.clip(self.spread_model.predict(features_scaled)[0], 0.65, 0.95)
            clusters = 1 if provided >= 35 else (2 if provided >= 25 else 3)
            
            return {
                'provided_numbers': int(provided),
                'spread': float(spread),
                'clusters': clusters,
                'max_mistakes': max(5, 20 - int(provided)//3),
                'label': self._get_difficulty_label(provided)
            }
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return None

    def _get_difficulty_label(self, clues):
        """Convert clue count to difficulty label"""
        if clues >= 35: return 'Beginner'
        elif clues >= 30: return 'Easy'
        elif clues >= 25: return 'Medium'
        elif clues >= 20: return 'Hard'
        return 'Expert'

    def reset_game(self):
        """Start a new game based on current mode"""
        if not self.model_loaded:
            self._setup_fallback_game()
        elif len(self.learning_games) < 5:
            self._setup_learning_game()
        else:
            self._setup_adaptive_game()
        self._reset_tracking()

    def _setup_fallback_game(self):
        """Default game when model isn't available"""
        self.current_difficulty = {
            'label': 'Medium',
            'provided_numbers': 30,
            'spread': 0.7,
            'clusters': 2,
            'max_mistakes': 10
        }
        self._generate_puzzle()

    def _setup_learning_game(self):
        """Medium difficulty games for initial learning phase"""
        self.current_difficulty = {
            'label': f'Learning {len(self.learning_games)+1}/5',
            'provided_numbers': 30,
            'spread': 0.7,
            'clusters': 2,
            'max_mistakes': 10
        }
        self._generate_puzzle()

    def _setup_adaptive_game(self):
        """Games with predicted difficulty after learning phase"""
        params = self.predict_difficulty()
        if params:
            self.current_difficulty = {
                'label': f'Adaptive: {params["label"]}',
                'provided_numbers': params['provided_numbers'],
                'spread': params['spread'],
                'clusters': params['clusters'],
                'max_mistakes': params['max_mistakes']
            }
        else:
            self._setup_fallback_game()
        self._generate_puzzle()

    def _generate_puzzle(self):
        """Generate the actual puzzle based on current difficulty"""
        self.full_grid = self.generate_sudoku()
        self.puzzle_grid = self.remove_numbers(
            self.full_grid,
            self.current_difficulty['provided_numbers']
        )
        self.user_grid = [row[:] for row in self.puzzle_grid]

    def _reset_tracking(self):
        """Reset game tracking variables"""
        self.wrong_cells = set()
        self.mistakes = 0
        self.moves_made = 0
        self.hints_used = 0
        self.hints_remaining = self.max_hints
        self.hint_cell = None
        self.start_time = time.time()
        self.game_over_time = None

    def check_move(self, row, col, num):
        """Validate a player's move"""
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
        """Check if puzzle is complete"""
        for row in range(9):
            for col in range(9):
                if self.user_grid[row][col] != self.full_grid[row][col]:
                    return False
        return True

    def provide_hint(self):
        """Provide a hint to the player"""
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

    def log_game_result(self, result):
        """Record game results and switch to adaptive after 5 games"""
        game_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'mode': 'adaptive' if self.adaptive_mode else 'learning',
            'difficulty_label': self.current_difficulty['label'],
            'completion_time': int((self.game_over_time or time.time()) - self.start_time),
            'mistakes': self.mistakes,
            'hints_used': self.hints_used,
            'moves': self.moves_made,
            'provided_numbers': self.current_difficulty['provided_numbers'],
            'n_clusters': self.current_difficulty['clusters'],
            'spread_factor': self.current_difficulty['spread'],
            'max_mistakes': self.current_difficulty['max_mistakes'],
            'result': result
        }
        
        # Store for adaptive difficulty
        self.learning_games.append(game_data)
        
        # Keep only last 5 games for predictions
        if len(self.learning_games) > 5:
            self.learning_games.pop(0)
        
        # Switch to adaptive mode after 5 learning games
        if len(self.learning_games) == 5 and not self.adaptive_mode:
            print("🎯 Switching to adaptive difficulty mode")
            self.adaptive_mode = True
        
        # Log to CSV
        self.data_logger.log_game_data(game_data)

    def get_current_difficulty_info(self):
        """Get current difficulty settings for UI"""
        return {
            'label': self.current_difficulty['label'],
            'provided': self.current_difficulty['provided_numbers'],
            'max_mistakes': self.current_difficulty['max_mistakes'],
            'progress': f"{len(self.learning_games)}/5" if not self.adaptive_mode else "Adaptive"
        }

    def get_game_time(self):
        """Get elapsed game time in seconds"""
        return int(time.time() - self.start_time)

    def get_remaining_cells(self):
        """Count remaining empty cells"""
        return sum(1 for row in range(9) for col in range(9) if self.user_grid[row][col] == 0)