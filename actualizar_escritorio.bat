@echo off
echo ========================================
echo  ACTUALIZANDO ACCESO DIRECTO
echo ========================================
echo.

echo Eliminando acceso directo anterior...
del "%USERPROFILE%\Desktop\TradePro.lnk" 2>nul

echo Creando nuevo acceso directo...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\TradePro.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CD%\launch_tradepro.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.Description = "TradePro - Professional Trading Platform v4.0" >> CreateShortcut.vbs
echo oLink.IconLocation = "%CD%\assets\icon.ico" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs //Nologo
del CreateShortcut.vbs

echo.
echo OK - Acceso directo actualizado en escritorio
echo.
pause
