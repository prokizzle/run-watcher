"""Custom widgets for the run watcher TUI."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, ListItem, ListView, Label
from textual.reactive import reactive
from rich.text import Text
from typing import List, Optional
from .github_client import RunInfo


class AppHeader(Horizontal):
    """The header of the app showing title and version."""

    def compose(self) -> ComposeResult:
        """Create header widgets."""
        yield Label("[b]Run Watcher[/] [dim]v0.1.0[/]", id="app-title")


class RepoListItem(ListItem):
    """A list item representing a repository."""

    def __init__(self, repo_name: str, latest_run: Optional[RunInfo] = None):
        super().__init__()
        self.repo_name = repo_name
        self.latest_run = latest_run

    def render(self) -> Text:
        """Render the repository list item."""
        text = Text()

        # Status indicator
        if self.latest_run:
            if self.latest_run.is_running:
                text.append("⟳ ", style="yellow")
            elif self.latest_run.is_success:
                text.append("✓ ", style="green")
            elif self.latest_run.is_failure:
                text.append("✗ ", style="red")
            else:
                text.append("○ ", style="dim")
        else:
            text.append("○ ", style="dim")

        # Repository name
        text.append(self.repo_name, style="bold")

        # Run number if available
        if self.latest_run:
            text.append(f" #{self.latest_run.run_number}", style="dim")

        return text


class RepoList(ListView):
    """Widget displaying the list of watched repositories."""

    def __init__(self, repos: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.repos = repos or []

    def add_repository(self, repo_name: str) -> None:
        """Add a repository to the watch list."""
        if repo_name not in self.repos:
            self.repos.append(repo_name)
            self.append(RepoListItem(repo_name))

    def update_repo_status(self, repo_name: str, latest_run: Optional[RunInfo]) -> None:
        """Update the status of a repository."""
        for child in self.children:
            if isinstance(child, RepoListItem) and child.repo_name == repo_name:
                # Update the item's data and trigger a refresh
                child.latest_run = latest_run
                child.refresh()
                break


class RunListItem(ListItem):
    """A single workflow run item for the runs list."""

    def __init__(self, run: RunInfo):
        super().__init__()
        self.run = run

    def render(self) -> Text:
        """Render the run item."""
        text = Text()

        # Status icon
        if self.run.is_running:
            text.append("⟳ ", style="yellow")
        elif self.run.is_success:
            text.append("✓ ", style="green")
        elif self.run.is_failure:
            text.append("✗ ", style="red")
        else:
            text.append("○ ", style="dim")

        # Run information
        text.append(f"#{self.run.run_number} ", style="bold cyan")
        text.append(f"{self.run.name}\n", style="bold")
        text.append(f"  {self.run.head_branch[:30]}  ", style="dim")
        text.append(f"{self.run.head_sha}", style="dim")

        return text


class RunsList(ListView):
    """Widget displaying the list of runs for a repository."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runs: List[RunInfo] = []

    def set_runs(self, runs: List[RunInfo]) -> None:
        """Set the list of runs to display."""
        self.runs = runs
        # Remove all children including empty states
        self.remove_children()

        if runs:
            # Add run items
            for run in runs:
                self.append(RunListItem(run))
        else:
            # Show empty state if no runs
            self.mount(EmptyState("No runs found"))


class DetailView(VerticalScroll):
    """Widget displaying details of the selected run."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_run: Optional[RunInfo] = None

    def show_run_details(self, run: RunInfo) -> None:
        """Display details for a specific run."""
        self.current_run = run
        self.remove_children()

        # Run header
        header = Text()
        header.append(f"{run.name}\n", style="bold cyan")
        header.append(f"Run #{run.run_number}\n\n", style="bold")

        # Status
        if run.is_running:
            header.append("Status: ", style="bold")
            header.append("Running ⟳\n", style="yellow")
        elif run.is_success:
            header.append("Status: ", style="bold")
            header.append("Success ✓\n", style="green")
        elif run.is_failure:
            header.append("Status: ", style="bold")
            header.append("Failed ✗\n", style="red")
        else:
            header.append(f"Status: {run.display_status}\n", style="bold")

        # Details
        header.append(f"\nBranch: {run.head_branch}\n", style="dim")
        header.append(f"SHA: {run.head_sha}\n", style="dim")
        header.append(f"Created: {run.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n", style="dim")
        header.append(f"Updated: {run.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n", style="dim")
        header.append(f"\nURL: {run.html_url}\n", style="blue underline")

        self.mount(Static(header))

    def show_logs(self, logs: str) -> None:
        """Display logs for a specific run."""
        self.remove_children()
        self.mount(Static(logs, classes="logs"))


class EmptyState(Static):
    """Widget showing empty state messages."""

    def __init__(self, message: str):
        super().__init__(message, classes="empty-state")
