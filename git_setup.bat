@echo off
echo Setting up Git repository...

:: Initialize git repository
git init

:: Add files
git add .

:: Create initial commit
git commit -m "Add containerization for IBM Redbooks RAG system"

:: Add the remote repository
git remote add origin https://github.com/jamieroszel22/docling_rag.git

echo.
echo Git repository setup complete!
echo.
echo Next steps:
echo 1. Push to GitHub:
echo    git push -u origin main
echo    (You may need to authenticate with GitHub)
echo.
echo 2. If the remote repository already has content, you might need to:
echo    git pull --rebase origin main
echo    git push -u origin main
echo.
echo 3. If you need to rename your main branch:
echo    git branch -M main
echo    git push -u origin main
echo.
