# GitHub Integration Guide

This guide explains how to work with this repository on GitHub.

## Initial Setup

If you've just cloned this repository:

1. Ensure you have Git installed on your system
2. Run the setup script to initialize the environment:
   ```bash
   # On Windows
   setup.bat
   
   # On Linux/Mac
   chmod +x setup.sh && ./setup.sh
   ```

## Contributing to This Repository

### Creating a Fork

1. Navigate to [https://github.com/jamieroszel22/docling_rag](https://github.com/jamieroszel22/docling_rag)
2. Click the "Fork" button in the top-right corner
3. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/docling_rag.git
   cd docling_rag
   ```
4. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/jamieroszel22/docling_rag.git
   ```

### Making Changes

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Create a Pull Request from your fork to the main repository

### Keeping Your Fork Updated

Periodically update your fork with changes from the main repository:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## GitHub Actions

This repository uses GitHub Actions for continuous integration. The workflow in `.github/workflows/docker-build.yml` automatically tests Docker builds on every push to the main branch.

You can view the workflow results in the "Actions" tab of the repository.

## Repository Structure

- `.github/workflows/` - Contains GitHub Actions workflow definitions
- `data/` - Directory structure for storing PDFs and processed files (ignored by Git)
- `scripts/` - Helper scripts for the containerized application
- Docker configuration files - Dockerfile, docker-compose.yml, etc.

## Adding Large Files

If you need to add large files to the repository (e.g., example PDFs), consider using Git LFS (Large File Storage). This repository is not currently configured for Git LFS, but it can be added if needed.

## Release Process

To create a new release:

1. Update version numbers in relevant files
2. Create a new tag:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```
3. Go to the "Releases" section on GitHub
4. Click "Draft a new release"
5. Select your tag and add release notes
6. Publish the release
