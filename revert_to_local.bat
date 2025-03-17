@echo off
echo Reverting to local non-containerized version...

:: Remove container-related files
echo Removing container-related files...
del /f /q .dockerignore 2>nul
del /f /q docker-compose.yml 2>nul
del /f /q Dockerfile 2>nul
del /f /q Dockerfile.fix 2>nul
del /f /q fix-podman-timestamp.bat 2>nul
del /f /q fix-podman-timestamp.sh 2>nul
del /f /q mac-fix-podman-timestamp.sh 2>nul
del /f /q macbook-docker-setup.sh 2>nul
del /f /q macbook-fix-containers.sh 2>nul
del /f /q macbook-podman-reset.sh 2>nul
del /f /q podman-compose.yml 2>nul
del /f /q podman-setup.bat 2>nul
del /f /q podman-setup.sh 2>nul
del /f /q reset-podman-containers.ps1 2>nul
del /f /q reset-podman-containers.sh 2>nul
del /f /q setup.bat 2>nul
del /f /q setup.sh 2>nul
rmdir /s /q scripts 2>nul

echo Done removing container files.
echo.
echo Your IBM Redbooks RAG system is now back to local non-containerized mode.
echo.
echo To use the system:
echo 1. Place IBM Redbook PDFs in the pdfs directory
echo 2. Run process_redbooks.bat to process them
echo 3. Run run_rag_interactive.bat to query them
echo.
pause
