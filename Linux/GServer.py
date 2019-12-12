import socket
import threading

from os import environ
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from subprocess import Popen, PIPE, run

from GSyntax import GParser

class senderObject(QtCore.QObject):
	finishedRecording = QtCore.pyqtSignal(str)
	
class GServer():
	def __init__(self):
		self.HOST = '0.0.0.0'
		self.PORT = 5555
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverWidget = None
		self.game = None
		self.title = "GXEPHYRSV"
		self.process = QProcess()
		self.sender = senderObject()

	def kill(self):
		self.__del__()

	def __del__(self):
		print("Server dead")
		self.process.kill()

	# Inicia o display virtual Xephyr em um widget
	def getServerWidget(self):
		if self.serverWidget is not None:
			return self.serverWidget

		print("Iniciando Xephyr!")
		self.process.start("Xephyr -ac -br -resizeable -no-host-grab -reset -terminate -screen 640x480 :100 -title " + self.title)
		tries = 0
		stdout = b''
	
		# Espera inicialização do Xephyr e
		# extrai o winId da janela do display virtual
		while stdout == b'':
			sleep(1)
			if tries == 10:
				raise Exception("Servidor Xephyr não encontrado!")
			tries += 1
			p1 = Popen(["xwininfo", "-name", self.title], stdout=PIPE)
			p2 = Popen(["grep", "-o", "-E", "0x[0-9a-fA-F]+"], stdin=p1.stdout, stdout=PIPE)
			stdout = p2.communicate()[0]
		
		stdout = stdout.splitlines()[0]
		winId = int(stdout, 16)
		self.new_window = QtGui.QWindow.fromWinId(winId)
		
		print("winId = " + str(winId))
	
		# FramelessWindow permite "colar" a janela do servidor na janela do editor
		self.new_window.setFlags(Qt.FramelessWindowHint)
	
		self.game_widget = QtWidgets.QWidget.createWindowContainer(self.new_window)
	
		# O widget que recebe o vídeo deve ser algum widget que tenha
		# informações visuais, como o textEdit ou o graphicsView
		self.serverWidget = QtWidgets.QGraphicsView()
	
		# De fato "cola" a janela do servidor dentro de um widget
		self.game_box = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.serverWidget)
		self.game_box.addWidget(self.game_widget)
	
		return self.serverWidget


	# Avatar precisa de uma thread
	def startGameThread(self):
		print("Iniciando o avatar")
		run(["./unityVideo/videoCreator.x86_64", "teste_renderer", "0", "30", "32", "37", "-screen-fullscreen", "0", "-screen-quality", "Fantastic", "-force-opengl", "2>&1", "/dev/null", "&"], shell=False, env=dict(environ, DISPLAY=":100"))

	def startCommunication(self):
		if self.game is None:
			self.game = threading.Thread(target=self.startGameThread)
			self.game.start()
			sleep(2)
		try:
			print(self.game.is_alive())
			print("Connectando em %s %d" % (self.HOST, self.PORT))
			self.sock.connect((self.HOST, self.PORT))
			return 0
		except:
			print("Servidor não encontrado")
			return 1

	def send(self, text):
		text = GParser().cleanText(text)
		blocks = GParser().getCommandBlocks(text)
		try:
			i = 0
			for msg in blocks:
				if msg[0] in (' ', '\n', '\t'):
					msg = msg[1:]
				i += 1
				self.sock.send(msg.encode('utf-8'))
				self.sock.recv(2048)
		except:
			print("Não há conexação com o servidor")
	
	def sendToRecord(self, text, vName):
		threading.Thread(target=self.waitingSend, args=(text, vName)).start()
	
	def waitingSend(self, text, vName):
		text = GParser().cleanText(text)
		blocks = GParser().getCommandBlocks(text)
		try:		
			for msg in blocks:
				while msg[0] in (' ', '\n', '\t'):
					msg = msg[1:]
					
				if msg == "":
					continue
				
				msg = msg.replace('\n\r', '\n').replace(chr(0x2028), '\n').replace(chr(0x2029), '\n')
				txts = msg.split('\n')
				
				for txt in txts:
					if txt == "" or txt.isspace():
						continue

					txt = txt.encode('utf-8')
					self.sock.send(txt)
					self.sock.recv(2048)
			
			# Ao final da gravação o avatar envia mais uma mensagem
			self.sock.recv(2048)
			self.sender.finishedRecording.emit(vName)
			
		except:
			print("Não há conexação com o servidor")
