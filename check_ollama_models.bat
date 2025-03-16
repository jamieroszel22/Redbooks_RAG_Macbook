@echo off
echo Checking Ollama Models...
echo =======================
echo.

echo Available models in Ollama:
ollama list

echo.
echo If you need to pull a model, use:
echo ollama pull modelname 
echo.
echo Examples:
echo ollama pull llama3
echo ollama pull mistral
echo ollama pull gemma:7b
echo.
