from json_loader import load_json, dump_json
import os


class SaveSystem:
    """
    Handles saving and loading game data for players.
    Saves: name, progress (distance/level), death_count
    """
    
    def __init__(self, save_dir="saves"):
        """Initialize the save system with a directory for save files."""
        self.save_dir = save_dir
        # Create saves directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_save_path(self, player_name):
        """Get the file path for a specific player's save file."""
        # Sanitize player name for use in filename
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in player_name)
        return os.path.join(self.save_dir, f"{safe_name}_save.json")
    
    def save_game(self, player_name, progress, death_count, level1_completed=False, obsidian_unlocked=False):
        """
        Save the game state to a JSON file.
        
        Args:
            player_name (str): The name of the player
            progress (int/float): Current progress (distance, level, etc.)
            death_count (int): Number of deaths
            level1_completed (bool): Whether level 1 is completed
            obsidian_unlocked (bool): Whether obsidian sword is unlocked
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            save_data = {
                "player_name": player_name,
                "progress": progress,
                "death_count": death_count,
                "level1_completed": level1_completed,
                "obsidian_unlocked": obsidian_unlocked
            }
            
            save_path = self.get_save_path(player_name)
            dump_json(save_data, save_path)
            
            print(f"Game saved successfully for {player_name}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, player_name):
        """
        Load the game state from a JSON file.
        
        Args:
            player_name (str): The name of the player to load
            
        Returns:
            dict: Dictionary containing player_name, progress, death_count, and last_saved
            or None if the save file doesn't exist or an error occurs
        """
        try:
            save_path = self.get_save_path(player_name)
            
            if not os.path.exists(save_path):
                print(f"No save file found for {player_name}")
                return None
            
            save_data = load_json(save_path)
            
            print(f"Game loaded successfully for {player_name}")
            return save_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saves(self):
        """
        Get a list of all available save files.
        
        Returns:
            list: List of dictionaries containing save file information
        """
        saves = []
        try:
            if os.path.exists(self.save_dir):
                for filename in os.listdir(self.save_dir):
                    if filename.endswith("_save.json"):
                        filepath = os.path.join(self.save_dir, filename)
                        try:
                            data = load_json(filepath)
                            saves.append(data)
                        except Exception as e:
                            print(f"Error reading {filename}: {e}")
        except Exception as e:
            print(f"Error listing saves: {e}")
        
        return saves
    
    def delete_save(self, player_name):
        """
        Delete a save file for a player.
        
        Args:
            player_name (str): The name of the player to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            save_path = self.get_save_path(player_name)
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Save file deleted for {player_name}")
                return True
            else:
                print(f"No save file found for {player_name}")
                return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def save_exists(self, player_name):
        """
        Check if a save file exists for a player.
        
        Args:
            player_name (str): The name of the player
            
        Returns:
            bool: True if save exists, False otherwise
        """
        save_path = self.get_save_path(player_name)
        return os.path.exists(save_path)


