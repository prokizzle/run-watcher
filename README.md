# Run Watcher

A Textual TUI application for monitoring GitHub Actions runs across multiple repositories.

## Installation

### Via Homebrew (Recommended)

```bash
brew tap YOUR_USERNAME/run-watcher
brew install run-watcher
```

### From Source

1. Install [mise](https://mise.jdx.dev/) if you haven't already:
```bash
curl https://mise.run | sh
```

2. Install Python and activate the environment:
```bash
mise install
# The venv will be automatically created and activated when you cd into the directory
```

3. Install dependencies:
```bash
pip install -e .
```

## Setup

Set up GitHub authentication (choose one):

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

## Usage

```bash
run-watcher
```

## Keyboard Shortcuts

- `q` - Quit
- `/` - Search/add repository
- `Ctrl+P` - Open command palette
- `↑/↓` - Navigate lists
- `Enter` - Select item
- `r` - Refresh all repositories

## Features

- 🎨 **Beautiful TUI** - Inspired by [Posting](https://github.com/darrenburns/posting) with rounded borders and focus states
- 📊 **Real-time Monitoring** - Watch workflow runs update every 30 seconds
- 🔍 **Command Palette** - Quick access to all features with fuzzy search (Ctrl+P)
- ❌ **Test Failure Display** - Click failed steps to see detailed logs
- 💾 **Persistent Repositories** - Your watched repos are saved between sessions
- ⌨️ **Keyboard-Centric** - Navigate everything without touching the mouse
