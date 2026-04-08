@echo off
setlocal

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set dt=%%I
set logfile=logs\sync_%dt:~0,8%_%dt:~8,6%.log

cd /d "C:\Users\Ygor\Desktop\Projetos\Estrutura de Degustações"
if not exist logs mkdir logs

C:\Python314\python.exe sincronizar_portal.py >> %logfile% 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Sincronização falhou em %date% %time% >> logs\sync_erros.log
)

endlocal
