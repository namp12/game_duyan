import json
import os

SCORE_FILE = "highscores.json"

def load_high_scores():
    """
    Load high scores for all levels from JSON file
    Returns: dict with level as key, high_score (ms) as value
    Example: {1: 45000, 2: 60000, 3: 80000}
    """
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert string keys back to integers
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Error loading high scores: {e}")
            return {}
    return {}

def save_high_scores(high_scores):
    """
    Save high scores dictionary to JSON file
    high_scores: dict with level as key, high_score (ms) as value
    """
    try:
        # Convert int keys to strings for JSON
        data = {str(k): v for k, v in high_scores.items()}
        with open(SCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving high scores: {e}")

def get_high_score_for_level(level):
    """
    Get high score for a specific level
    Returns: high score in ms, or 0 if no record
    """
    high_scores = load_high_scores()
    return high_scores.get(level, 0)

def update_high_score(level, new_time):
    """
    Update high score for a level if new time is better (higher)
    Returns: (is_new_record: bool, high_score: int)
    """
    high_scores = load_high_scores()
    current_high = high_scores.get(level, 0)
    
    is_new_record = new_time > current_high
    
    if is_new_record:
        high_scores[level] = new_time
        save_high_scores(high_scores)
        return True, new_time
    
    return False, current_high

def format_time(ms):
    """Format milliseconds to MM:SS"""
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

# ==================== LEVEL PROGRESS PERSISTENCE ====================
PROGRESS_FILE = "level_progress.txt"

def save_level_progress(max_level):
    """
    Save max level reached to file
    
    Args:
        max_level: Highest level unlocked (1-9)
    """
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            f.write(str(max_level))
        print(f"✓ Saved progress: Level {max_level} unlocked")
    except Exception as e:
        print(f"✗ Error saving progress: {e}")

def load_level_progress():
    """
    Load max level reached from file
    
    Returns:
        int: Highest level unlocked (default: 1)
    """
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                max_level = int(f.read().strip())
                print(f"✓ Loaded progress: Level {max_level} unlocked")
                return max_level
        except Exception as e:
            print(f"✗ Error loading progress: {e}")
            return 1
    return 1  # Default: only level 1 unlocked
