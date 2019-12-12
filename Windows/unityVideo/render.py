#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from pyvirtualdisplay import Display


# [Dependencies]
# 1. # sudo apt-get install python-pip
# 2. # sudo apt-get install xvfb linuxvnc xserver-xephyr
# 3. # pip install pyvirtualdisplay
# Execução do player ./videoCreator.x86_64 'userID' 'legenda 1(ativa) 0(desativa)' 'fps'

display = Display(visible=1, size=(640, 480))
display.start()

print("Started pyvirtualdisplay with backend '%s', screen '%s'." % (display.backend, display.screen))


try:
    subprocess.call(["./videoCreator.x86_64", str(sys.argv[1]), "1", "30", "32", "37", "-screen-fullscreen", "0", "-screen-quality", "Fantastic", "-force-opengl"], shell=False)
    print("Sucesso")
except OSError as e:
    print (e.errno)
    print (e.filename)
    print (e.strerror)

display.stop()
