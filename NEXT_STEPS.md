# Next Steps for Homebrew Tap

## Quick Start

Here's what you need to do to make Run Watcher installable via Homebrew:

### 1. Create a GitHub Repository for the Tap

```bash
# On GitHub, create a new repository called: homebrew-run-watcher
# (The name MUST start with "homebrew-")
```

### 2. Set Up the Tap Repository

```bash
# Clone your new tap repository
git clone https://github.com/YOUR_USERNAME/homebrew-run-watcher.git
cd homebrew-run-watcher

# Create the Formula directory
mkdir -p Formula

# Copy the formula from run-watcher
cp /path/to/run-watcher/Formula/run-watcher.rb Formula/

# Commit and push
git add Formula/run-watcher.rb
git commit -m "Add run-watcher formula"
git push origin main
```

### 3. Create a Release of Run Watcher

```bash
# In your run-watcher repository
cd /path/to/run-watcher

# Tag and push the release
git tag v0.1.0
git push origin v0.1.0
```

Then go to GitHub and create a release for `v0.1.0`.

### 4. Update the Formula with SHA256

```bash
# Get the SHA256 of the release tarball
curl -sL https://github.com/YOUR_USERNAME/run-watcher/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256

# Update Formula/run-watcher.rb in your tap repository:
# - Replace YOUR_USERNAME with your actual GitHub username
# - Replace YOUR_SHA256_HERE with the SHA256 you just calculated
# - Make sure the version matches (v0.1.0)
```

### 5. Test the Installation

```bash
# Add your tap
brew tap YOUR_USERNAME/run-watcher

# Install run-watcher
brew install run-watcher

# Test it works
run-watcher --help
```

### 6. Update README

Edit `README.md` in both repositories:
- Replace `YOUR_USERNAME` with your actual GitHub username

### 7. Share with Users

Users can now install with:
```bash
brew tap YOUR_USERNAME/run-watcher
brew install run-watcher
```

Or in one line:
```bash
brew install YOUR_USERNAME/run-watcher/run-watcher
```

## Future Updates

When you release a new version:

1. Tag the new version in run-watcher repo
2. Get the new SHA256
3. Update `Formula/run-watcher.rb` in the tap repo with:
   - New version number
   - New URL
   - New SHA256
4. Commit and push the tap repo

Users update with:
```bash
brew update
brew upgrade run-watcher
```

## Troubleshooting

If the formula doesn't work:

```bash
# Test the formula
brew audit --strict run-watcher

# Check for style issues
brew style run-watcher

# Install from source to see errors
brew install --build-from-source run-watcher
```

## Resources

See `HOMEBREW_TAP.md` for detailed documentation.
