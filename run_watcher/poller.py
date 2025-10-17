"""Background polling service for GitHub Actions runs."""

import asyncio
from typing import Callable, Set
from .github_client import GitHubClient


class RunPoller:
    """Background poller for monitoring GitHub Actions runs."""

    def __init__(self, github_client: GitHubClient, interval: int = 30):
        """Initialize the poller.

        Args:
            github_client: GitHub API client
            interval: Polling interval in seconds (default: 30)
        """
        self.github_client = github_client
        self.interval = interval
        self.watched_repos: Set[str] = set()
        self.callbacks: list[Callable] = []
        self.running = False
        self._task = None

    def add_repository(self, repo_name: str) -> None:
        """Add a repository to watch.

        Args:
            repo_name: Full repository name (owner/repo)
        """
        self.watched_repos.add(repo_name)

    def remove_repository(self, repo_name: str) -> None:
        """Remove a repository from watch list.

        Args:
            repo_name: Full repository name (owner/repo)
        """
        self.watched_repos.discard(repo_name)

    def on_update(self, callback: Callable) -> None:
        """Register a callback for run updates.

        Args:
            callback: Function to call with (repo_name, runs) when updates occur
        """
        self.callbacks.append(callback)

    async def poll_once(self) -> None:
        """Poll all watched repositories once."""
        for repo_name in self.watched_repos:
            try:
                runs = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.github_client.get_recent_runs,
                    repo_name,
                    10
                )

                # Notify all callbacks
                for callback in self.callbacks:
                    callback(repo_name, runs)

            except Exception as e:
                # Log error but continue polling other repos
                print(f"Error polling {repo_name}: {e}")

    async def start(self) -> None:
        """Start the background polling loop."""
        self.running = True

        while self.running:
            await self.poll_once()

            # Sleep in smaller chunks to be more responsive to stop signals
            for _ in range(self.interval):
                if not self.running:
                    break
                await asyncio.sleep(1)

    def stop(self) -> None:
        """Stop the background polling loop."""
        self.running = False
