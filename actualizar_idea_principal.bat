@echo off
chcp 65001 > nul
echo ========================================================
echo  Sincronizando Repositorio: Idea-Principal (Modo Lectura)
echo ========================================================
cd /d "%~dp0Idea-Principal"
git pull origin main
echo ========================================================
echo  Idea-Principal actualizado correctamente.
echo ========================================================
pause
