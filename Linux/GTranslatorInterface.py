import vlibras_translate
from PyQt5 import QtCore

class SenderObject(QtCore.QObject):
	translationReady = QtCore.pyqtSignal(str)
	updateProgress	 = QtCore.pyqtSignal(int)

class GTranslator():

	endl = "#_#"
	
	def __init__(self):
		try:
			self.tradutor = vlibras_translate.translation.Translation()
			self.sender = SenderObject()
			self.stopFlag = False
		except UnicodeDecodeError as ex:
			print(ex.encoding)
		
	def haltTranslation(self):
		self.stopFlag = True	
	
	def translate(self, text):
		translation = ""
		i = 0
		lines = text.splitlines()
		l = len(lines)
		for line in lines:
			translation += self.tradutor.rule_translation(line)
			translation += GTranslator.endl
			i += 1
			self.sender.updateProgress.emit(int(100*i / l))
			if self.stopFlag:
				self.stopFlag = False
				return
				
		self.sender.translationReady.emit(translation)
