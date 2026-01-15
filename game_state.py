"""
Example integration of the SaveSystem with the main game.
Shows how to track and save player progress, deaths, and name.
"""

from make_save import SaveSystem

class GameState:
    """Tracks the current game state for saving."""
    
    def __init__(self, player_name="Player"):
        self.player_name = player_name
        self.progress = 0  # level progress
        self.death_count = 0
        self.level1_completed = False
        self.obsidian_unlocked = False
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
            self.level1_completed,
            self.obsidian_unlocked
        )
    
    def load(self, player_name):
        """Load a game state for a player."""
        data = self.save_system.load_game(player_name)
        if data:
            self.player_name = data["player_name"]
            self.progress = data["progress"]
            self.death_count = data["death_count"]
            self.level1_completed = data.get("level1_completed", False)
            self.obsidian_unlocked = data.get("obsidian_unlocked", False)
            return True
        return False
    
    def new_game(self, player_name):
        """Start a new game with a player name."""
        self.player_name = player_name
        self.progress = 0
        self.death_count = 0
        self.level1_completed = False
        self.obsidian_unlocked = False

