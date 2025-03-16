# IBM Redbooks RAG System

[![Docker Build Test](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml/badge.svg)](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml)

A containerized Retrieval-Augmented Generation (RAG) system for IBM Redbooks technical documentation that leverages Docling for PDF processing and understanding.

## Prerequisites

- Podman and Podman Compose (recommended for IBM environments)
- Docker and Docker Compose (alternative option)
- NVIDIA GPU with drivers installed (for optimal performance on Windows)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/jamieroszel22/docling_rag.git
   cd docling_rag
   ```

2. Place your IBM Redbooks PDFs in the `data/pdfs` directory (will be created automatically)

3. Run the appropriate setup script for your environment:
   ```bash
   # For Windows with Podman
   podman-setup.bat
   
   # For Windows with Docker
   setup.bat
   
   # For Mac/Linux with Podman (recommended)
   chmod +x podman-setup.sh && ./podman-setup.sh
   
   # For Mac/Linux with Docker
   chmod +x setup.sh && ./setup.sh
   ```

4. Process your Redbooks:
   ```bash
   # With Podman
   podman exec redbooks-rag sh /app/scripts/process_redbooks.sh
   
   # With Docker
   docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
   ```

5. Run the interactive RAG system:
   ```bash
   # With Podman
   podman exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
   
   # With Docker
   docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
   ```

6. Prepare data for Open WebUI (optional):
   ```bash
   # With Podman
   podman exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
   
   # With Docker
   docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
   ```

## Platform-Specific Setup

### Windows with NVIDIA GPU

Windows with an NVIDIA GPU provides the best performance for this system.

#### Using Podman (Recommended)

1. Install [Podman Desktop](https://podman-desktop.io/downloads)
   - During installation, choose to install Podman Machine for Windows

2. For GPU support:
   - Ensure your NVIDIA drivers are up to date
   - Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

3. Run the Windows Podman setup script:
   ```
   podman-setup.bat
   ```

4. Windows path considerations:
   - The `.env` file uses Windows-style paths (e.g., `C:/Users/your-username/Documents/...`)
   - Podman internally converts these to Linux-style paths

#### Using Docker (Alternative)

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

2. For GPU support:
   - Install [NVIDIA Container Toolkit for Windows](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
   - Ensure your NVIDIA drivers are up to date

3. Run the Windows Docker setup script:
   ```
   setup.bat
   ```

### macOS Setup

#### Using Podman (Recommended)

1. Install Podman via Homebrew:
   ```bash
   brew install podman
   ```

2. Initialize the Podman machine:
   ```bash
   podman machine init
   podman machine start
   ```

3. Install Podman Compose:
   ```bash
   pip install podman-compose
   ```

4. Run the Podman setup script:
   ```bash
   chmod +x podman-setup.sh
   ./podman-setup.sh
   ```

5. Update the `.env` file with macOS-style paths:
   ```
   PDF_PATH=/Users/your-username/Documents/Redbooks/pdfs
   PROCESSED_PATH=/Users/your-username/Documents/Redbooks/processed_redbooks
   OPENWEBUI_PATH=/Users/your-username/Documents/Redbooks/openwebui
   ```

6. Note for Apple Silicon (M1/M2) Macs:
   - The containers will run in emulation mode
   - Performance may be slower than on x86_64 hardware

#### Using Docker (Alternative)

1. Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

2. Run the Docker setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Linux Setup

#### Using Podman (Recommended for RHEL/Fedora/CentOS)

1. Install Podman and Podman Compose:
   ```bash
   # For RHEL/Fedora/CentOS
   sudo yum install podman podman-compose
   
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install podman
   pip install podman-compose
   ```

2. For GPU support:
   ```bash
   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/libnvidia-container/stable/$distribution/libnvidia-container.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
   sudo yum install -y nvidia-container-toolkit
   ```

3. Run the Podman setup script:
   ```bash
   chmod +x podman-setup.sh
   ./podman-setup.sh
   ```

4. Update the `.env` file with Linux-style paths:
   ```
   PDF_PATH=/home/your-username/Documents/Redbooks/pdfs
   PROCESSED_PATH=/home/your-username/Documents/Redbooks/processed_redbooks
   OPENWEBUI_PATH=/home/your-username/Documents/Redbooks/openwebui
   ```

#### Using Docker (Alternative)

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

3. Run the Docker setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## Important Podman Considerations

Podman, developed by Red Hat, offers several advantages over Docker especially in IBM environments:

- **Enhanced Security**: Runs in rootless mode by default
- **Daemonless Architecture**: No background daemon required
- **OCI-Compliant**: Follows Open Container Initiative standards
- **Drop-in Replacement**: Compatible with Docker CLI commands
- **IBM Corporate Compliance**: Approved for use on IBM corporate laptops

### Podman Command Reference

Docker commands can be easily converted to Podman:

```bash
# Docker command
docker run -it --name test nginx

# Equivalent Podman command
podman run -it --name test nginx
```

For this project, simply replace `docker` with `podman` in any command.

### Podman-specific considerations:

- **Rootless Mode**: Enhances security but may cause permission issues with certain volume mounts
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

After running the prepare_for_openwebui.sh script, the files in the `data/openwebui` directory can be uploaded to your Open WebUI instance as a collection named "IBM Z Knowledge Base".

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

This project uses GitHub Actions for continuous integration. Each push to the main branch will trigger a build test to ensure the container builds successfully.

## Troubleshooting

### Common Platform-Specific Issues

#### Windows
- **Path Issues**: Ensure paths in `.env` use forward slashes (`/`) or escaped backslashes (`\\`)
- **Permission Errors**: Run as Administrator if you encounter permission issues
- **WSL Issues**: If using WSL 2 backend, ensure it's properly configured with enough memory

#### macOS
- **Resource Limits**: Increase memory/CPU allocation in container settings
- **M1/M2 Chips**: Be aware that containers will run in emulation mode which may impact performance
- **Filesystem Performance**: For better performance, store data in locations not synced with iCloud

#### Linux
- **Permission Issues**: If using Podman in rootless mode and encountering permission errors:
  ```bash
  podman unshare chown -R 1000:1000 /path/to/data
  ```
- **GPU Access**: Verify GPU is accessible within container:
  ```bash
  # For Podman
  podman run --rm --hooks-dir=/usr/share/containers/oci/hooks.d nvidia/cuda:11.0-base nvidia-smi
  
  # For Docker
  docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
  ```

#### Podman
- **Connection Errors**: If you see "connection refused" errors, check if your Podman machine is running:
  ```bash
  podman machine list
  podman machine start
  ```
- **Compatibility Issues**: If a container doesn't work with Podman, try running with:
  ```bash
  podman run --security-opt label=disable ...
  ```
- **Debugging**: Inspect logs from your containers with:
  ```bash
  podman logs redbooks-rag
  podman logs redbooks-ollama
  ```

## About

This project uses [Docling](https://github.com/DS4SD/docling) for advanced PDF understanding and document processing.
