@echo off
setlocal
cd /d "%~dp0.."
echo UTS CWPP - evidencia de infraestructura
echo La salida se guardara en docs\evidencias\infraestructura.txt
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { & '.\scripts\evidencia_infra.ps1' | Tee-Object -FilePath '.\docs\evidencias\infraestructura.txt' }"
set "RESULTADO=%ERRORLEVEL%"
echo.
if not "%RESULTADO%"=="0" echo Ocurrio un error. Revisa el mensaje anterior.
echo Presiona una tecla cuando termines de tomar la captura.
pause >nul
exit /b %RESULTADO%
