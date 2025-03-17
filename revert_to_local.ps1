# PowerShell script to revert to a local non-containerized setup
Write-Host "Reverting to local non-containerized version..." -ForegroundColor Cyan

# List of container-related files to remove
$filesToRemove = @(
    ".dockerignore",
    "docker-compose.yml",
    "Dockerfile",
    "Dockerfile.fix",
    "fix-podman-timestamp.bat",
    "fix-podman-timestamp.sh",
    "mac-fix-podman-timestamp.sh",
    "macbook-docker-setup.sh",
    "macbook-fix-containers.sh",
    "macbook-podman-reset.sh",
    "podman-compose.yml",
    "podman-setup.bat",
    "podman-setup.sh",
    "reset-podman-containers.ps1",
    "reset-podman-containers.sh",
    "setup.bat",
    "setup.sh",
    "GITHUB_GUIDE.md",
    "NEXT_STEPS.md"
)

# Remove each file
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "Removing $file..." -ForegroundColor Yellow
        Remove-Item -Path $file -Force
    }
}

# Remove scripts directory
if (Test-Path "scripts") {
    Write-Host "Removing scripts directory..." -ForegroundColor Yellow
    Remove-Item -Path "scripts" -Recurse -Force
}

Write-Host "Done removing container files." -ForegroundColor Green
Write-Host ""
Write-Host "Your IBM Redbooks RAG system is now back to local non-containerized mode." -ForegroundColor Green
Write-Host ""
Write-Host "To use the system:" -ForegroundColor White
Write-Host "1. Place IBM Redbook PDFs in the pdfs directory" -ForegroundColor White
Write-Host "2. Run process_redbooks.bat to process them" -ForegroundColor White
Write-Host "3. Run run_rag_interactive.bat to query them" -ForegroundColor White
