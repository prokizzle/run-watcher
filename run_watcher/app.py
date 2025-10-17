"""Main Textual application for run-watcher."""

import os
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Input
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import work
from dotenv import load_dotenv

from .github_client import GitHubClient
from .widgets import AppHeader, RepoList, RunsList, DetailView, EmptyState
from .poller import RunPoller
from .config import Config
from .commands import RunWatcherCommands


def get_github_token() -> str | None:
    """Get GitHub token from gh CLI or environment.

    Returns:
        GitHub token or None if not found
    """
    # First try gh CLI
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fall back to environment variable
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")


class SearchModal(ModalScreen):
    """Modal screen for searching and adding repositories."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Container(id="search-dialog"):
            yield Input(placeholder="Search repositories (e.g., 'org:github textual')")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        self.dismiss(event.value)

    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "escape":
            self.dismiss(None)


class RunWatcherApp(App):
    """A Textual app to monitor GitHub Actions runs."""

    CSS = """
    /* Global scrollbar styling */
    * {
        scrollbar-color: $primary 50%;
        scrollbar-color-hover: $primary 80%;
        scrollbar-color-active: $primary;
        scrollbar-background: $surface-darken-1;
        scrollbar-background-hover: $surface-darken-1;
        scrollbar-background-active: $surface-darken-1;
        scrollbar-size-vertical: 1;
    }

    *:focus {
        scrollbar-color: $primary;
    }

    Screen {
        background: $background;
    }

    /* App Header Styling */
    AppHeader {
        dock: top;
        height: auto;
        padding: 1 2;
        background: $surface;
        color: $text;
        border-bottom: solid $accent 40%;
    }

    #app-title {
        color: $text-accent;
    }

    Footer {
        dock: bottom;
        padding-left: 2;
    }

    #main-container {
        height: 1fr;
        padding: 0 1;
    }

    /* Repository List Container */
    #repo-list-container {
        width: 25%;
        height: 100%;
        background: $surface 50%;
        border: round $accent 40%;
        border-title-color: $text-accent 50%;
        border-title-align: center;
        border-subtitle-color: $text-muted;
    }

    #repo-list-container:focus-within {
        border: round $accent 100%;
        border-title-color: $text-accent;
        border-title-style: bold;
    }

    /* Runs List Container */
    #runs-list-container {
        width: 35%;
        height: 100%;
        background: $surface 25%;
        border: round $accent 40%;
        border-title-color: $text-accent 50%;
        border-title-align: center;
        border-subtitle-color: $text-muted;
        margin-left: 1;
    }

    #runs-list-container:focus-within {
        border: round $accent 100%;
        border-title-color: $text-accent;
        border-title-style: bold;
    }

    /* Detail Container */
    #detail-container {
        width: 40%;
        height: 100%;
        background: $surface 10%;
        border: round $accent 40%;
        border-title-color: $text-accent 50%;
        border-title-align: center;
        margin-left: 1;
    }

    #detail-container:focus-within {
        border: round $accent 100%;
        border-title-color: $text-accent;
        border-title-style: bold;
    }

    RepoList {
        height: 100%;
        background: transparent;
        padding: 1;
    }

    RunsList {
        height: 100%;
        background: transparent;
        padding: 1;
    }

    DetailView {
        height: 100%;
        background: transparent;
        padding: 1 2;
    }

    .empty-state {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }

    RunListItem {
        padding: 1;
        margin-bottom: 1;
        background: $panel;
        border: solid $primary 30%;
    }

    RunListItem:hover {
        background: $panel-lighten-1;
        border: solid $primary 60%;
    }

    #search-dialog {
        width: 60;
        height: 7;
        background: $panel;
        border: wide $accent;
        padding: 1;
    }

    .logs {
        background: transparent;
        color: $text;
    }

    /* Modal styling */
    ModalScreen {
        background: black 30%;
    }

    /* Command Palette Styling */
    CommandPalette {
        & > Vertical {
            width: 60%;
            max-width: 80;
            border: wide $accent;
            background: $panel;
        }

        & #--input {
            border: none;
            border-bottom: solid $accent-darken-1;
        }

        & CommandInput {
            height: auto;
            border: none;
            padding: 1 2;
            background: $panel;
        }

        & CommandList {
            border: none;
            padding: 1 0;
            background: $panel;
            max-height: 20;
        }

        & .command-palette--highlight {
            color: $text-accent;
            background: $accent-muted;
        }
    }
    """

    COMMANDS = {RunWatcherCommands}

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("slash", "search", "Search"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.github_client = None
        self.poller = None
        self.watched_repos = []
        self.current_repo = None
        self.config = Config()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield AppHeader()
        with Horizontal(id="main-container"):
            repo_container = Container(id="repo-list-container")
            repo_container.border_title = "Repositories"
            with repo_container:
                yield RepoList(id="repo-list")

            runs_container = Container(id="runs-list-container")
            runs_container.border_title = "Workflow Runs"
            with runs_container:
                yield RunsList(id="runs-list")

            detail_container = Container(id="detail-container")
            detail_container.border_title = "Details"
            with detail_container:
                yield DetailView(id="detail-view")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application on mount."""
        # Get GitHub token from gh CLI or environment
        token = get_github_token()

        if not token:
            self.exit(message="Error: GitHub token not found. Please run 'gh auth login' or create a .env file with GITHUB_TOKEN.")
            return

        try:
            self.github_client = GitHubClient(token)
            self.notify("Connected to GitHub")
        except Exception as e:
            self.exit(message=f"Error connecting to GitHub: {e}")
            return

        # Initialize poller
        self.poller = RunPoller(self.github_client, interval=30)
        self.poller.on_update(self.handle_poll_update)
        self.start_poller()

        # Load saved repositories
        self.load_saved_repositories()

        # Show initial empty states
        runs_list = self.query_one("#runs-list", RunsList)
        runs_list.mount(EmptyState("Select a repository"))

        detail_view = self.query_one("#detail-view", DetailView)
        detail_view.mount(EmptyState("Select a run"))

    def on_unmount(self) -> None:
        """Clean up when the app is unmounting."""
        if self.poller:
            self.poller.stop()

    def action_quit(self) -> None:
        """Override quit action to ensure clean shutdown."""
        if self.poller:
            self.poller.stop()
        self.exit()

    def load_saved_repositories(self) -> None:
        """Load and restore saved repositories from config."""
        saved_repos = self.config.load_watched_repos()

        if saved_repos:
            repo_list = self.query_one("#repo-list", RepoList)

            for repo_name in saved_repos:
                # Add to UI
                repo_list.add_repository(repo_name)

                # Add to poller
                if self.poller:
                    self.poller.add_repository(repo_name)

                # Fetch initial runs
                self.refresh_repo(repo_name)

            self.notify(f"Loaded {len(saved_repos)} saved repositories")

    def save_repositories(self) -> None:
        """Save current list of watched repositories to config."""
        repo_list = self.query_one("#repo-list", RepoList)
        self.config.save_watched_repos(repo_list.repos)

    def action_search(self) -> None:
        """Show the search modal."""
        def handle_search(query: str | None) -> None:
            if query:
                self.search_repositories(query)

        self.push_screen(SearchModal(), handle_search)

    @work(exclusive=True)
    async def search_repositories(self, query: str) -> None:
        """Search for repositories and add the first match."""
        if not self.github_client:
            return

        self.notify(f"Searching for: {query}")

        # Run the search in a worker
        repos = await self.run_in_executor(
            self.github_client.search_repositories, query
        )

        if repos:
            # Add the first repository
            repo_name, description = repos[0]
            repo_list = self.query_one("#repo-list", RepoList)
            repo_list.add_repository(repo_name)
            self.notify(f"Added: {repo_name}")

            # Add to poller
            if self.poller:
                self.poller.add_repository(repo_name)

            # Save updated repository list
            self.save_repositories()

            # Fetch runs for the new repo
            self.refresh_repo(repo_name)
        else:
            self.notify("No repositories found", severity="warning")

    def run_in_executor(self, func, *args):
        """Run a function in the executor."""
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, func, *args)

    @work(exclusive=True, thread=True)
    def start_poller(self) -> None:
        """Start the background poller."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.poller.start())

    def handle_poll_update(self, repo_name: str, runs) -> None:
        """Handle updates from the background poller."""
        try:
            repo_list = self.query_one("#repo-list", RepoList)
            latest_run = runs[0] if runs else None
            repo_list.update_repo_status(repo_name, latest_run)

            # Update runs list if this is the current repo
            if self.current_repo == repo_name:
                runs_list = self.query_one("#runs-list", RunsList)
                runs_list.set_runs(runs)
        except Exception as e:
            # Widgets may not be mounted yet, ignore silently
            pass

    @work(exclusive=True)
    async def refresh_repo(self, repo_name: str) -> None:
        """Refresh runs for a specific repository."""
        if not self.github_client:
            return

        runs = await self.run_in_executor(
            self.github_client.get_recent_runs, repo_name
        )

        # Update the repo list item
        repo_list = self.query_one("#repo-list", RepoList)
        latest_run = runs[0] if runs else None
        repo_list.update_repo_status(repo_name, latest_run)

        # If this is the current repo, update runs list
        if self.current_repo == repo_name:
            runs_list = self.query_one("#runs-list", RunsList)
            runs_list.set_runs(runs)

    def action_refresh(self) -> None:
        """Refresh all repositories."""
        repo_list = self.query_one("#repo-list", RepoList)
        for repo in repo_list.repos:
            self.refresh_repo(repo)
        self.notify("Refreshing all repositories...")

    def on_list_view_selected(self, event) -> None:
        """Handle list item selection (repository or run)."""
        from .widgets import RepoListItem, RunListItem

        if isinstance(event.item, RepoListItem):
            # Repository selected - show runs in middle column
            self.current_repo = event.item.repo_name
            self.refresh_repo(event.item.repo_name)

            # Clear detail view
            detail_view = self.query_one("#detail-view", DetailView)
            detail_view.remove_children()
            detail_view.mount(EmptyState("Select a run"))

        elif isinstance(event.item, RunListItem):
            # Run selected - show details in right column
            detail_view = self.query_one("#detail-view", DetailView)
            detail_view.show_run_details(event.item.run)


def main():
    """Run the application."""
    app = RunWatcherApp()
    app.run()


if __name__ == "__main__":
    main()
