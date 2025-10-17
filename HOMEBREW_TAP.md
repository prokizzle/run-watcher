# Homebrew Tap Setup Guide

This guide will help you set up Run Watcher as a Homebrew tap so users can install it with `brew install`.

## Option 1: Create a Separate Tap Repository (Recommended)

### Step 1: Create a new GitHub repository

Create a new repository called `homebrew-run-watcher` (or `homebrew-tap` if you want to host multiple formulas).

**Important:** The repository MUST be named `homebrew-*` for Homebrew to recognize it as a tap.

### Step 2: Add the formula

1. Clone your new tap repository:
```bash
git clone https://github.com/YOUR_USERNAME/homebrew-run-watcher.git
cd homebrew-run-watcher
```

2. Copy the formula file:
```bash
cp /path/to/run-watcher/Formula/run-watcher.rb ./Formula/run-watcher.rb
```

3. Edit the formula to update placeholders:
   - Replace `YOUR_USERNAME` with your GitHub username
   - Replace `YOUR_SHA256_HERE` with the actual SHA256 (see below)

### Step 3: Create a release of run-watcher

1. Tag a release in your run-watcher repository:
```bash
cd /path/to/run-watcher
git tag v0.1.0
git push origin v0.1.0
```

2. Create a GitHub release for v0.1.0

3. Get the SHA256 of the release tarball:
```bash
curl -sL https://github.com/YOUR_USERNAME/run-watcher/archive/refs/tags/v0.1.0.tar.gz | sha256sum
```

4. Update the SHA256 in the formula file

### Step 4: Push the tap

```bash
cd homebrew-run-watcher
git add Formula/run-watcher.rb
git commit -m "Add run-watcher formula"
git push origin main
```

### Step 5: Test installation

Users can now install with:
```bash
brew tap YOUR_USERNAME/run-watcher
brew install run-watcher
```

Or in one command:
```bash
brew install YOUR_USERNAME/run-watcher/run-watcher
```

## Option 2: Include in Main Repository

You can keep the Formula directory in this repository, but users will need to:

```bash
brew tap YOUR_USERNAME/run-watcher https://github.com/YOUR_USERNAME/run-watcher
brew install run-watcher
```

## Updating the Formula

When you release a new version:

1. Create a new git tag and GitHub release
2. Update the `url` and `sha256` in the formula
3. Update the `version` in the formula
4. Commit and push the updated formula

## Testing the Formula Locally

Before publishing, test the formula:

```bash
# Install from the formula file directly
brew install --build-from-source Formula/run-watcher.rb

# Or test with brew create
brew create https://github.com/YOUR_USERNAME/run-watcher/archive/refs/tags/v0.1.0.tar.gz
```

## Formula Audit

Ensure your formula follows Homebrew guidelines:

```bash
brew audit --strict run-watcher
brew style run-watcher
```

## Common Issues

### Missing Dependencies

If Python dependencies are missing, you may need to add more `resource` blocks. Use:

```bash
brew update-python-resources run-watcher
```

### Version Conflicts

Make sure the version in `pyproject.toml` matches the git tag and formula version.

## Resources

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Python for Formula Authors](https://docs.brew.sh/Python-for-Formula-Authors)
- [How to Create Homebrew Taps](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
