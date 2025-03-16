# IBM Redbooks RAG System

[![Docker Build Test](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml/badge.svg)](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml)

A containerized Retrieval-Augmented Generation (RAG) system for IBM Redbooks technical documentation that leverages Docling for PDF processing and understanding.

## Prerequisites

- Docker and Docker Compose (or Podman and Podman Compose for IBM laptops)
- NVIDIA GPU with drivers installed (for optimal performance)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/jamieroszel22/docling_rag.git
   cd docling_rag
   ```

2. Place your IBM Redbooks PDFs in the `data/pdfs` directory (will be created automatically)

3. Run the setup script to initialize the environment:
   ```bash
   # On Windows
   setup.bat
   
   # On Linux/Mac
   chmod +x setup.sh && ./setup.sh
   ```

4. Process your Redbooks:
   ```bash
   docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
   ```

5. Run the interactive RAG system:
   ```bash
   docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
   ```

6. Prepare data for Open WebUI (optional):
   ```bash
   docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
   ```

## Platform-Specific Setup

### Windows Setup

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. For GPU support:
   - Install [NVIDIA Container Toolkit for Windows](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
   - Ensure your NVIDIA drivers are up to date
3. Run the Windows-specific setup script:
   ```
   setup.bat
   ```
4. Windows path considerations:
   - The `.env` file uses Windows-style paths (e.g., `C:/Users/your-username/Documents/...`)
   - Docker internally converts these to Linux-style paths

### macOS Setup

1. Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Update the `.env` file with macOS-style paths:
   ```
   PDF_PATH=/Users/your-username/Documents/Redbooks/pdfs
   PROCESSED_PATH=/Users/your-username/Documents/Redbooks/processed_redbooks
   OPENWEBUI_PATH=/Users/your-username/Documents/Redbooks/openwebui
   ```

### Linux Setup

1. Install Docker and Docker Compose:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   
   # For CentOS/RHEL/Fedora
   sudo yum install docker docker-compose
   ```
2. For GPU support:
   ```bash
   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```
3. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
4. Update the `.env` file with Linux-style paths:
   ```
   PDF_PATH=/home/your-username/Documents/Redbooks/pdfs
   PROCESSED_PATH=/home/your-username/Documents/Redbooks/processed_redbooks
   OPENWEBUI_PATH=/home/your-username/Documents/Redbooks/openwebui
   ```

### Podman Setup (for IBM Laptops)

IBM corporate laptops often don't allow Docker due to security policies, but Podman provides a compatible alternative that works similarly.

#### Installing Podman

1. **Windows**:
   - Install [Podman Desktop](https://podman-desktop.io/downloads)
   - During installation, choose to install Podman Machine for Windows

2. **macOS**:
   - Install Podman via Homebrew:
     ```bash
     brew install podman
     ```
   - Initialize Podman machine:
     ```bash
     podman machine init
     podman machine start
     ```

3. **Linux** (RHEL/Fedora/CentOS):
   ```bash
   sudo yum install podman podman-compose
   ```

#### Setting Up Podman Compose

1. Install Podman Compose:
   ```bash
   pip install podman-compose
   ```

#### Using with this Project

1. Create a podman-compatible compose file:
   ```bash
   # Copy the existing compose file
   cp docker-compose.yml podman-compose.yml
   ```

2. Create a podman setup script (podman-setup.sh):
   ```bash
   #!/bin/bash
   
   # Create necessary directories
   mkdir -p data/pdfs
   mkdir -p data/processed_redbooks/docs
   mkdir -p data/processed_redbooks/chunks
   mkdir -p data/processed_redbooks/ollama
   mkdir -p data/openwebui
   
   # Build and start containers with Podman
   podman-compose -f podman-compose.yml up -d --build
   ```

3. Run the containers:
   ```bash
   chmod +x podman-setup.sh
   ./podman-setup.sh
   ```

4. For Windows users, create a batch file (podman-setup.bat):
   ```
   @echo off
   mkdir data\pdfs 2>nul
   mkdir data\processed_redbooks\docs 2>nul
   mkdir data\processed_redbooks\chunks 2>nul
   mkdir data\processed_redbooks\ollama 2>nul
   mkdir data\openwebui 2>nul
   
   podman-compose -f podman-compose.yml up -d --build
   ```

5. Convert Docker commands to Podman:
   ```bash
   # Instead of:
   docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
   
   # Use:
   podman exec redbooks-rag sh /app/scripts/process_redbooks.sh
   ```

#### Podman-specific considerations:

- **Rootless Mode**: Podman runs in rootless mode by default (unlike Docker), which enhances security but may cause permission issues
- **GPU Support**: Use the `--hooks-dir=/usr/share/containers/oci/hooks.d` flag when running with NVIDIA GPU support
- **Volume Mounts**: When specifying volume paths in podman-compose.yml, use absolute paths for better compatibility
- **SELinux**: If running on RHEL/Fedora with SELinux enabled, use the `:z` suffix for volume mounts

## Configuration

Edit the `.env` file to configure:
- Custom paths for your data
- Ollama model to use

## Project Structure

```
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── podman-compose.yml    # Podman-compatible compose file
├── requirements.txt      # Python dependencies
├── scripts/              # Helper scripts
│   ├── process_redbooks.sh
│   ├── run_rag_interactive.sh
│   └── prepare_for_openwebui.sh
├── data/                 # Data directory (created on first run)
│   ├── pdfs/             # Place your Redbook PDFs here
│   ├── processed_redbooks/
│   │   ├── docs/         # Processed documents
│   │   ├── chunks/       # Text chunks for retrieval
│   │   └── ollama/       # JSONL files for Ollama
│   └── openwebui/        # Files for Open WebUI integration
```

## Open WebUI Integration

After running the `prepare_for_openwebui.sh` script, the files in the `data/openwebui` directory can be uploaded to your Open WebUI instance as a collection named "IBM Z Knowledge Base".

1. Access your Open WebUI instance
2. Create a new collection
3. Upload the JSON files from the `data/openwebui` directory
4. Enable RAG when chatting with the model

## LLM Support

This container comes with Ollama, which can run various models. The default configuration uses:
- granite3.2:8b-instruct-fp16

To use a different model, edit the `.env` file and change the `OLLAMA_MODEL` variable.

## Development

To contribute to this project:

1. Fork the repository on GitHub
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a new Pull Request

## CI/CD

This project uses GitHub Actions for continuous integration. Each push to the main branch will trigger a Docker build test to ensure the container builds successfully.

## Troubleshooting

- If you encounter GPU-related issues, check that the NVIDIA Container Toolkit is properly installed.
- For memory issues, you may need to adjust the model size in the `.env` file.
- Check container logs with: `docker logs redbooks-rag` or `docker logs redbooks-ollama`

### Common Platform-Specific Issues

#### Windows
- **Path Issues**: Ensure paths in `.env` use forward slashes (`/`) or escaped backslashes (`\\`)
- **Permission Errors**: Run Docker Desktop as Administrator if you encounter permission issues
- **WSL Issues**: If using WSL 2 backend, ensure it's properly configured with enough memory

#### macOS
- **Resource Limits**: Increase memory/CPU allocation in Docker Desktop settings
- **M1/M2 Chips**: Use ARM64-compatible Docker images when available
- **Filesystem Performance**: For better performance, store data in locations not synced with iCloud

#### Linux
- **Docker Group**: Add your user to the docker group to run Docker without sudo:
  ```bash
  sudo usermod -aG docker $USER
  ```
  (logout and login required after this change)
- **GPU Access**: Verify GPU is accessible within container:
  ```bash
  docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
  ```

#### Podman
- **Connection Errors**: If you see "connection refused" errors, check if your Podman machine is running:
  ```bash
  podman machine list
  podman machine start
  ```
- **Permission Issues**: If experiencing permission issues with volume mounts, try:
  ```bash
  podman unshare chown -R 1000:1000 /path/to/data
  ```
- **Compatibility Issues**: If a container doesn't work with Podman, try running with:
  ```bash
  podman run --security-opt label=disable ...
  ```

## About

This project uses [Docling](https://github.com/DS4SD/docling) for advanced PDF understanding and document processing.
