"""Configuration management for Run Watcher.

Handles persistence of watched repositories between application sessions.
"""

import json
from pathlib import Path
from typing import List


class Config:
    """Manages application configuration and persistence."""

    def __init__(self):
        """Initialize config with default paths."""
        self.config_dir = Path.home() / ".config" / "run-watcher"
        self.repos_file = self.config_dir / "repos.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_watched_repos(self) -> List[str]:
        """Load the list of watched repositories from disk.

        Returns:
            List of repository names in 'owner/repo' format.
            Returns empty list if config file doesn't exist or is invalid.
        """
        if not self.repos_file.exists():
            return []

        try:
            with open(self.repos_file, "r") as f:
                data = json.load(f)
                repos = data.get("watched_repos", [])
                # Validate that repos is a list
                if isinstance(repos, list):
                    return repos
                return []
        except (json.JSONDecodeError, IOError) as e:
            # Log error but don't crash - just return empty list
            print(f"Warning: Failed to load repos config: {e}")
            return []

    def save_watched_repos(self, repos: List[str]) -> None:
        """Save the list of watched repositories to disk.

        Args:
            repos: List of repository names in 'owner/repo' format.
        """
        try:
            data = {"watched_repos": repos}
            with open(self.repos_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            # Log error but don't crash the app
            print(f"Warning: Failed to save repos config: {e}")
