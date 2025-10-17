"""Command palette provider for Run Watcher."""

from textual.command import Provider, Hit, Hits


class RunWatcherCommands(Provider):
    """Command provider for Run Watcher application."""

    @property
    def commands(self):
        """Get list of available commands.

        Returns:
            List of tuples (name, callable, help_text) for each command.
        """
        app = self.app

        commands_list = []

        # Search/Add Repository
        if hasattr(app, 'action_search'):
            commands_list.append((
                "Search/Add Repository",
                self.action_search,
                "Search for and add a repository to watch"
            ))

        # Refresh commands
        if hasattr(app, 'action_refresh'):
            commands_list.append((
                "Refresh All Repositories",
                self.action_refresh,
                "Refresh workflow runs for all watched repositories"
            ))

        commands_list.append((
            "Refresh Current Repository",
            self.refresh_current_repo,
            "Refresh workflow runs for the currently selected repository"
        ))

        # Focus navigation commands
        commands_list.append((
            "Focus Repository List",
            self.focus_repo_list,
            "Move focus to the repository list"
        ))

        commands_list.append((
            "Focus Workflow Runs",
            self.focus_runs_list,
            "Move focus to the workflow runs list"
        ))

        commands_list.append((
            "Focus Details",
            self.focus_details,
            "Move focus to the details view"
        ))

        return commands_list

    async def search(self, query: str) -> Hits:
        """Search for commands matching the query.

        Args:
            query: The user's search query.

        Yields:
            Hit objects for commands matching the query.
        """
        matcher = self.matcher(query)

        for name, runnable, help_text in self.commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text
                )

    async def action_search(self) -> None:
        """Trigger the search action."""
        self.app.action_search()

    async def action_refresh(self) -> None:
        """Trigger the refresh action."""
        self.app.action_refresh()

    async def refresh_current_repo(self) -> None:
        """Refresh the currently selected repository."""
        if hasattr(self.app, 'current_repo') and self.app.current_repo:
            self.app.refresh_repo(self.app.current_repo)
            self.app.notify(f"Refreshing {self.app.current_repo}...")
        else:
            self.app.notify("No repository selected", severity="warning")

    async def focus_repo_list(self) -> None:
        """Focus the repository list."""
        try:
            from .widgets import RepoList
            repo_list = self.app.query_one(RepoList)
            self.app.set_focus(repo_list)
        except Exception as e:
            self.app.notify(f"Error focusing repository list: {e}", severity="error")

    async def focus_runs_list(self) -> None:
        """Focus the workflow runs list."""
        try:
            from .widgets import RunsList
            runs_list = self.app.query_one(RunsList)
            self.app.set_focus(runs_list)
        except Exception as e:
            self.app.notify(f"Error focusing runs list: {e}", severity="error")

    async def focus_details(self) -> None:
        """Focus the details view."""
        try:
            from .widgets import DetailView
            detail_view = self.app.query_one(DetailView)
            self.app.set_focus(detail_view)
        except Exception as e:
            self.app.notify(f"Error focusing details: {e}", severity="error")
