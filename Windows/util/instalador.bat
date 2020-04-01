TITLE MDLib Windows
ECHO Habilitando a máquina virtual Linux

:: Para permitir a instalação da WSL
PowerShell.exe -NoProfile -Command "& {Start-Process PowerShell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command ""Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux""' -Verb RunAs}"

ECHO Instalando as dependências do sistema...

:: Para executar o instalador de dependências automaticamente
python3 %~dp0pip_install_win.py
