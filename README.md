# Run Watcher

A Textual TUI application for monitoring GitHub Actions runs across multiple repositories.

## Setup

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

## Usage

```bash
run-watcher
```

## Keyboard Shortcuts

- `q` - Quit
- `/` - Search/add repository
- `↑/↓` - Navigate repository list
- `Enter` - View repository details
- `r` - Refresh runs
