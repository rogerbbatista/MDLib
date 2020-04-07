TITLE MDLib Windows
ECHO Habilitando a maquina virtual Linux

:: Para permitir a instalacao da WSL
PowerShell.exe -NoProfile -Command "& {Start-Process PowerShell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command ""Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux""' -Verb RunAs}"
