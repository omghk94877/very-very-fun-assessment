"""
name :
date : 2026 january 15
description : Manages the game state including saving and loading progress.
"""

from make_save import SaveSystem

class GameState:
    """Tracks the current game state for saving."""
    
    def __init__(self, player_name="Player"):
        self.player_name = player_name
        self.progress = 0  # level progress
        self.death_count = 0
        self.level = 1  # current level
        self.story_state = None  # current story state
        self.story_index = 0  # current index in the story
        self.level1_completed = False
        self.obsidian_unlocked = False
        self.hard_mode = False
        self.save_system = SaveSystem()
    
    def increment_progress(self, amount):
        """Increase progress (e.g., when moving through the world)."""
        self.progress += amount
    
    def increment_death_count(self):
        """Increment death count when player dies."""
        self.death_count += 1
    
    def save(self):
        """Save the current game state."""
        return self.save_system.save_game(
            self.player_name,
            self.progress,
            self.death_count,
            self.level,
            self.story_state,
            self.story_index,
            self.level1_completed,
            self.obsidian_unlocked,
            self.hard_mode
        )
    
    def load(self, player_name):
        """Load a game state for a player."""
        data = self.save_system.load_game(player_name)
        if data:
            self.player_name = data["player_name"]
            self.progress = data["progress"]
            self.death_count = data["death_count"]
            self.level = data.get("level", 1)
            self.story_state = data.get("story_state", None)
            self.story_index = data.get("story_index", 0)
            self.level1_completed = data.get("level1_completed", False)
            self.obsidian_unlocked = data.get("obsidian_unlocked", False)
            self.hard_mode = data.get("hard_mode", False)
            return True
        return False
    
    def new_game(self, player_name):
        """Start a new game with a player name."""
        self.player_name = player_name
        self.progress = 0
        self.death_count = 0
        self.level = 1
        self.story_state = "intro"
        self.story_index = 0
        self.level1_completed = False
        self.obsidian_unlocked = False

