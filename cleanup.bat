@echo off
echo IBM Redbooks RAG System Cleanup
echo ==============================
echo.
echo This script will remove unnecessary files and directories.
echo.

set APP_DIR=%~dp0
echo Working in: %APP_DIR%
echo.

echo Removing container-related files...
del /q "%APP_DIR%.dockerignore" 2>nul
del /q "%APP_DIR%docker-compose.yml" 2>nul
del /q "%APP_DIR%Dockerfile" 2>nul
del /q "%APP_DIR%podman-compose.yml" 2>nul
del /q "%APP_DIR%fix-podman-timestamp.bat" 2>nul
del /q "%APP_DIR%fix-podman-timestamp.sh" 2>nul
del /q "%APP_DIR%mac-fix-podman-timestamp.sh" 2>nul
del /q "%APP_DIR%macbook-docker-setup.sh" 2>nul
del /q "%APP_DIR%macbook-fix-containers.sh" 2>nul
del /q "%APP_DIR%macbook-podman-reset.sh" 2>nul
del /q "%APP_DIR%podman-setup.bat" 2>nul
del /q "%APP_DIR%podman-setup.sh" 2>nul
del /q "%APP_DIR%reset-podman-containers.ps1" 2>nul
del /q "%APP_DIR%reset-podman-containers.sh" 2>nul
del /q "%APP_DIR%cd" 2>nul

echo Removing Python cache files...
rmdir /s /q "%APP_DIR%__pycache__" 2>nul

echo.
echo Cleanup complete!
echo.
echo NOTE: If you want to remove version control files (.git, .github),
echo       please run the following command manually:
echo rmdir /s /q "%APP_DIR%.git" 2>nul
echo rmdir /s /q "%APP_DIR%.github" 2>nul
echo.
echo NOTE: If you want to remove the pdf_to_rag directory (older version),
echo       please run the following command manually:
echo rmdir /s /q "C:\Users\jamie\OneDrive\Desktop\pdf_to_rag" 2>nul
echo.

pause
