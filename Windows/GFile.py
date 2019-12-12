import os
import sys
import unidecode
import threading
import subprocess
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.image import ImageWriter
from io import StringIO
from io import BytesIO

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QUrl

from GTranslatorInterface import GTranslator

from GSettings import GDefaultValues

############################################
# Classe para converter documentos para PDF
# extrair os textos e providenciar o widget
# que vai exibir o PDF
############################################

class documentSenderObject(QtCore.QObject):
	formattedReady  = QtCore.pyqtSignal()
	convertionReady = QtCore.pyqtSignal(str)

class GDocument(QtWebEngineWidgets.QWebEngineView):

	__pdfjs = GDefaultValues.pdfJs

	def __init__(self, parent = None):
		QtWebEngineWidgets.QWebEngineView.__init__(self, parent)
		self.name = ""
		self.file = None
		self.ready = False
		self.rawText = None
		self.formattedText = None
		self.sender = documentSenderObject()
		self.sender.formattedReady.connect(self.onFormattedReady)
		self.sender.convertionReady.connect(self.onConvertionReady)
	
	def isReady(self):
		return self.ready
	
	def isPDF(self):
		if self.file is None:
			return False
		return self.file.endswith(".pdf")

	def getBaseName(self):
		return os.path.basename(self.file)
	
	def getDirName(self):
		return os.path.dirname(self.file)
		
	def getOutputFileName(self):
		return self.getDirName() + "/" + self.getBaseName().split('.', 1)[0] + ".pdf"
	
	def convertToPDF(self, url = "file:///"):
		cmd = "ubuntu1804 -c unoconv -f pdf " + "/mnt/" + self.file[0].lower() + self.file[2:]
		resp = subprocess.call(cmd, shell=True)
		self.file = self.getOutputFileName()
		self.sender.convertionReady.emit(url)

	def load(self, f, url = "file:///"):
		self.ready = False
		self.file = f
		self.rawText = None
		self.formattedText = None
		
		if self.file is None:
			raise Exception("Nenhum arquivo especificado")

		if not self.isPDF():
			threading.Thread(target=self.convertToPDF, args=([url])).start()
		else:
			print(self.__pdfjs + "?file="+url+self.file)
			super().load(QtCore.QUrl.fromUserInput(self.__pdfjs + "?file="+url+self.file))
			threading.Thread(target=self.getFormattedText).start()
	
	def onConvertionReady(self, url = "file:///"):
		super().load(QtCore.QUrl.fromUserInput(self.__pdfjs + "?file="+url+self.file))
		threading.Thread(target=self.getFormattedText).start()
		
	def onFormattedReady(self):
		self.ready = True
		print ("REFINO!")
	
	def hasFile(self):
		return self.file is not None

	#####################################
	##
	## Códigos do arquivo newConvert.py
	##
	#####################################
	
	# Extrair o texto do PDF
	def getRawText(self):
		if self.rawText is not None:
			return self.rawText
		rsrcmgr = PDFResourceManager()
		retstr = BytesIO()
		codec = 'utf-8'
		laparams = LAParams()
		imagewriter = ImageWriter('media\\images\\') 
		device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams, imagewriter=imagewriter)

		fp = open(self.file, 'rb')
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		password = ""
		maxpages = 0
		caching = True
		pagenos=set()
		for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
			interpreter.process_page(page)
		fp.close()
		device.close()
		s = retstr.getvalue().decode("utf8", "ignore")
		retstr.close()
		self.rawText = s

	################################
	##
	## Essa função foi passada
	## para a classe GImage
	##
	################################

#		i = 0
#		for filename in os.listdir("media/images/"): 
#			dst ="IMG" + str(i) + ".JPG"
#			src ='media/images/'+ filename 
#			dst ='media/images/'+ dst 
#			os.rename(src, dst) 
#			i += 1

		return self.rawText

	# Refino
	def getFormattedText(self):
		if self.formattedText is not None:
			#self.sender.formattedReady.emit()
			return self.formattedText
			
		os.system("del /Q /F media\\images\\*")
		output = self.getRawText()
		refino = ""
		output2 = output.encode("utf-8")
		base = output2.splitlines()
		encontrou = False
		for x in base:
			if any(char != " " for char in x):
				encontrou = False
				if(x[-1] != " "):
					x = x + b" "
				refino = refino + x.decode("utf-8")
				if(refino[-2] == "." or refino[-2] == "!"):
						refino = refino + "\n"
			elif not(encontrou):
				encontrou = True
				if(refino[-3:] != "\n"):
					refino = refino + "\n"

		for count, caracter in enumerate(refino): #juntar palavras quebradas no fim de linha
			if caracter == "-" and refino[count+1] == " " and refino[count-1] != " ":
				refino = refino[:count] + refino[count+2:]

		self.formattedText = refino
		self.sender.formattedReady.emit()
		return self.formattedText

#############################################
# Classe para lidar com os arquivos de glosa
# E gerenciar o texto traduzido
#############################################

class translationSenderObject(QtCore.QObject):
	translationReady = QtCore.pyqtSignal()

class GTranslation():
	def __init__(self, text = None, raw = True, paragraphs = [], parseIndex = 0):
		self.text = text
		self.parseIndex = parseIndex
		self.paragraphs = paragraphs
		self.raw = raw
		
		self.sender = translationSenderObject()
		
		self.translator = GTranslator()
		self.translator.sender.translationReady.connect(self.updateStatus)
		self.translator.sender.updateProgress.connect(self.updateProgress)
		
		if self.text is not None and raw:
			self.translate()
		
	def __getitem__(self, key):
		return self.paragraphs[key]
	
	def __len__(self):
		return len(self.paragraphs)
	
	def isReady(self):
		return self.text is None or self.raw
	
	def index(self):
		return self.parseIndex

	def translate(self):
		self.progress = QtWidgets.QProgressDialog("Traduzindo...", "Cancelar!", 0, 100)
		self.progress.setWindowTitle("Tradutor")
		self.progress.canceled.connect(self.haltTranslation)
		self.progress.setValue(0)
		threading.Thread(target=self.translator.translate, args=([self.text])).start()
		
		
	def update(self, text):
		self.progress = QtWidgets.QProgressDialog("Traduzindo...", "Cancelar!", 0, 100)
		self.progress.setWindowTitle("Tradutor")
		self.progress.canceled.connect(self.haltTranslation)
		self.progress.setValue(0)
		threading.Thread(target=self.translator.translate, args=([text])).start()
		
	def haltTranslation(self):
		self.translator.haltTranslation()
		self.progress.hide()
	
	def updateStatus(self, text):
		self.text = text
		self.paragraphs = [line if line else '\n' for line in self.text.split(GTranslator.endl)]
		self.parseIndex = 0
		self.raw  = False
		self.progress.hide()
		self.sender.translationReady.emit()
		
	def updateProgress(self, progress):
		if not self.progress.wasCanceled():
			self.progress.setValue(progress)

	def getRawText(self):
		return self.text
	
	def next(self):
		if self.parseIndex is None or self.parseIndex >= len(self.paragraphs):
			return ""
		self.parseIndex += 1
		return self.paragraphs[self.parseIndex-1]
		
	def prev(self):
		if self.parseIndex is None or self.parseIndex <= 0:
			return ""
		self.parseIndex -= 1
		return self.paragraphs[self.parseIndex]
	
	def paragraphsToDisplay(self):
		return self.paragraphs[0:self.parseIndex]
	
	def getParagraphs(self):
		return self.paragraphs
		
	def getParagraphsTillEnd(self):
		oldIndex = self.parseIndex
		self.parseIndex = len(self.paragraphs)
		return self.paragraphs[oldIndex:]
	
	def resetIndex(self):
		self.parseIndex = 0
	
	def setIndex(self, index):
		self.parseIndex = index
		
	def clear(self):
		self.text = None
		self.raw = True
		self.paragraphs = []
		self.parseIndex = 0

###############################################
#
# Classe para ler e escrever arquivos .egl
#
###############################################
class GEGLFile():
	def __init__(self):
		self.text = ""
		self.translationText = ""
		self.translationParagraphs = []
		self.parseIndex = 0
		
	def load(self, document):
		with open(document, "r") as doc:
			self.blockLen = int(doc.readline())
			self.text = ""
			for _ in range(self.blockLen):
				self.text += doc.readline()
			
			self.parseIndex = int(doc.readline())
			self.translationText = doc.read()
			self.translationParagraphs = [line if line else '\n' for line in self.translationText.split(GTranslator.endl)]
		self.raw = False
		
	def save(self, document):
		with open(document, "w") as doc:
			# QChar::QParagraphSeparator 	= chr(0x2029)
			# QChar::LineSeparator 		= chr(0x2028)
			self.text = self.text.replace(chr(0x2028), '\n')
			self.text = self.text.replace(chr(0x2029), '\n')
			doc.write(str(self.text.count("\n")+1))
			doc.write("\n")
			doc.write(self.text)
			doc.write("\n")
			doc.write(str(self.parseIndex) + "\n")
			for line in self.translationParagraphs:
				doc.write(line)
				doc.write(GTranslator.endl)
				
	def translation(self):
		return GTranslation(self.translationText, False, self.translationParagraphs, self.parseIndex)

	def plainText(self):
		return self.text

	def setPlainText(self, text):
		self.text = text

	def setTranslation(self, translation):
		self.translationText = translation.getRawText()
		self.translationParagraphs = translation.getParagraphs()
		self.parseIndex = translation.index()

###############################################
#
# Cria os arquivos de vídeo
#
###############################################
class videoSenderObject(QtCore.QObject):
	videoReady = QtCore.pyqtSignal(str)
	
class GVideo():
	def __init__(self):
		self.sender = videoSenderObject()
		
	def createVideo(self, vId, vFname, pngDir):
		if not vFname.endswith(".mp4"):
			vFname += ".mp4"
		threading.Thread(target=self.videoCreatorThread, args=(vId, vFname, pngDir)).start()
		
	def videoCreatorThread(self, vId, vFname, pngDir):
		png = pngDir + "/" + vId + "/frame_%d.png"
		vFname = "/mnt/" + vFname[0].lower() + vFname[2:]		
		cmd = "ubuntu1804 -c ffmpeg -y -v quiet -framerate 30 -i %s -pix_fmt yuv420p %s" % (png, vFname)
		subprocess.run(cmd, shell=True)

		self.sender.videoReady.emit(os.path.basename(vFname))
		
