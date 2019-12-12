from PyQt5 import QtCore
from GSettings import GDefaultValues
import os

class SenderObject(QtCore.QObject):
	translationReady = QtCore.pyqtSignal(str)
	updateProgress	 = QtCore.pyqtSignal(int)

class GTranslator():

	endl = "#_#"
	
	def __init__(self):
		try:
			#self.tradutor = vlibras_translate.translation.Translation()
			self.sender = SenderObject()
			self.stopFlag = False
		except UnicodeDecodeError as ex:
			print(ex.encoding)
		
	def haltTranslation(self):
		self.stopFlag = True	
	
	def translate(self, text):

		location = "/mnt/" + GDefaultValues.cwd[0].lower() + GDefaultValues.cwd[2:]

                
		arquivoTexto = open("tempTeste.txt", "wb+")
		arquivoTexto.write(text.encode('utf-8'))
		arquivoTexto.close()

		os.system("ubuntu1804 run python3 \"" + location + "/GTranslationScript.py\" \"" + location + "\"")

		arquivoTraduzido = open("outputTranslation.txt", "rb+")
		translation = arquivoTraduzido.read()
		arquivoTraduzido.close()
		self.sender.translationReady.emit(translation.decode())
