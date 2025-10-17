# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Run Watcher is a Python-based Textual TUI application for monitoring GitHub Actions runs across multiple repositories within an organization.

### Core Functionality
- Monitor active and recent GitHub Actions runs for selected repositories
- Display run status, logs, and test/build failures
- Two-pane interface:
  - Left pane: List of watched repositories with compact status indicators for recent/active runs
  - Right pane: Detailed view showing run status, failures, or full logs
- Search functionality to add repositories to the watch list
- Scope monitoring to specific GitHub organizations

## Technology Stack

- **UI Framework**: [Textual](https://textual.textualize.io/) - Python TUI framework
- **GitHub Integration**: GitHub API (via PyGithub)
- **Language**: Python 3.13
- **Build System**: Hatchling

## Development Setup

This project uses [mise](https://mise.jdx.dev/) for Python version management.

1. Install mise (if not already installed):
```bash
curl https://mise.run | sh
```

2. Install Python and activate the environment:
```bash
mise install
# The .venv will be automatically created and activated by mise
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Set up GitHub authentication (choose one):

**Option A: Using GitHub CLI (recommended)**
```bash
gh auth login
```

**Option B: Using a personal access token**
```bash
cp .env.example .env
# Edit .env and add your GitHub personal access token
```

Create a token at https://github.com/settings/tokens with `repo` and `workflow` scopes.

**Note**: The `.mise.toml` file configures Python 3.13 and automatic venv creation. The app will automatically use `gh auth token` if available, otherwise it will look for `GITHUB_TOKEN` in the environment.

## Running the Application

```bash
run-watcher
```

Or directly:
```bash
python -m run_watcher.app
```

## Architecture

### Key Components

1. **github_client.py**: GitHub API client using PyGithub
   - `GitHubClient`: Handles all GitHub API interactions
   - `RunInfo`: Data class representing a workflow run
   - Methods for searching repos, fetching runs, and retrieving logs

2. **widgets.py**: Custom Textual widgets
   - `RepoListItem`: Individual repository list item with status indicator
   - `RepoList`: ListView for watched repositories
   - `RunListItem`: Display widget for a single workflow run
   - `DetailView`: Right pane showing run details
   - `EmptyState`: Placeholder for empty views

3. **poller.py**: Background polling service
   - `RunPoller`: Polls GitHub API every 30 seconds for run updates
   - Manages watched repositories and notifies callbacks of changes
   - Runs in a separate thread to avoid blocking the UI

4. **app.py**: Main Textual application
   - `SearchModal`: Modal dialog for searching and adding repositories
   - `RunWatcherApp`: Main application with two-pane layout
   - Handles user interactions and coordinates between components

### Data Flow

1. User searches for repositories via `/` key
2. Repository is added to watch list and poller
3. Poller fetches latest runs every 30 seconds
4. UI updates automatically via callbacks
5. User can select a repository to view detailed run information

### Keyboard Shortcuts

- `q` - Quit application
- `/` - Search/add repository
- `r` - Refresh all repositories
- `↑/↓` - Navigate repository list
- `Enter` - View repository details
