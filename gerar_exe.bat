@echo off
REM Precisa ter o Python instalado. Gera dist\limpar_banco.exe
pip install pyinstaller
pyinstaller --onefile --console --name limpar_banco limpar_banco.py
echo.
echo Pronto! O executavel esta em: dist\limpar_banco.exe
echo Copie ele pra mesma pasta do controle_instrumentos.db
pause
