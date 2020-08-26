#!/usr/bin/python3

import os
import re
import sys
import threading
import subprocess
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QDesktopServices, QFont

from GText import GTextEdit
from GSyntax import GSyntaxHighlighter
from GFile import GDocument, GTranslation, GVideo, GEGLFile
from GImage import GImageGrid, GCustomImageDialog, GCustomScreenShotDialog

from GScreenUtils import GLayeredDocumentCanvas

from time import sleep
from GServer import GServer

from GSettings import GDefaultValues, GSettingsMenu

class Main(QtWidgets.QMainWindow):
	cwd		= GDefaultValues.cwd
	home		= GDefaultValues.home
	default_pngDir  = GDefaultValues.pngDir
	default_videoId = GDefaultValues.videoId
	default_imgDir  = GDefaultValues.imgDir
	

	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.openTextFileName = ""
		self.openDocumentFileName = ""
		self.isRecording = False
		self.translationFileName = ""
		self.hasOpenTranslation = False
		self.server = GServer()
		self.server.sender.finishedRecording.connect(self.createVideo)
		self.initUI()

	#####################################
	#
	# Menubar
	#
	#####################################
	def initMenubar(self):
		menubar = self.menuBar()
		file = menubar.addMenu("Arquivos")
		avatar = menubar.addMenu("Avatar")
		traducao = menubar.addMenu("Tradução")
		imagens = menubar.addMenu("Imagens")

		fileNovo = QtWidgets.QAction("Novo", self)
		fileNovo.setShortcut("Ctrl+N")
		fileNovo.setStatusTip("Criar nova tradução")
		fileNovo.triggered.connect(self.newTextFile)

		fileAbrir = QtWidgets.QAction("Abrir documento", self)
		fileAbrir.setShortcut("Ctrl+O")
		fileAbrir.setStatusTip("Abre novo documento")
		fileAbrir.triggered.connect(self.openDocument)

		fileImportar = QtWidgets.QAction("Importar tradução", self)
		fileImportar.setShortcut("Ctrl+I")
		fileImportar.setStatusTip("Importa tradução")
		fileImportar.triggered.connect(self.importTextFile)

		fileSalvar = QtWidgets.QAction("Salvar", self)
		fileSalvar.setShortcut("Ctrl+S")
		fileSalvar.setStatusTip("Salva arquivo da tradução")
		fileSalvar.triggered.connect(self.saveTextFile)

		fileSalvarComo = QtWidgets.QAction("Salvar como...", self)
		fileSalvarComo.setShortcut("Ctrl+Shift+S")
		fileSalvarComo.setStatusTip("Salvar arquivo da tradução como...")
		fileSalvarComo.triggered.connect(self.saveTextFileAs)

		fileExportar = QtWidgets.QMenu("Exportar", self)

		self.exportarTXT = QtWidgets.QAction("TXT")
		self.exportarPDF = QtWidgets.QAction("PDF")
		self.exportarDOCX= QtWidgets.QAction("DOCX (Microsoft Word)")
		self.exportarODT = QtWidgets.QAction("ODT (Libre Office)")
		
		self.exportarTXT.triggered.connect(lambda : self.exportTextFile("txt"))
		self.exportarPDF.triggered.connect(lambda : self.exportTextFile("pdf"))
		self.exportarDOCX.triggered.connect(lambda : self.exportTextFile("docx"))
		self.exportarODT.triggered.connect(lambda : self.exportTextFile("odt"))
		
		fileExportar.setStatusTip("Exportar tradução para...")
		
		fileExportar.addAction(self.exportarTXT)
		fileExportar.addAction(self.exportarPDF)
		fileExportar.addAction(self.exportarDOCX)
		fileExportar.addAction(self.exportarODT)


		#fileExportar.triggered.connect(self.exportTextFile)	

		fileQuit = QtWidgets.QAction("Sair", self)
		fileQuit.setShortcut("Ctrl+Q")
		fileQuit.setStatusTip("Sair da aplicação")
		fileQuit.triggered.connect(self.__del__)	

		file.addAction(fileNovo)
		file.addSeparator()
		file.addAction(fileAbrir)
		file.addAction(fileImportar)
		file.addSeparator()
		file.addAction(fileSalvar)
		file.addAction(fileSalvarComo)
		file.addMenu(fileExportar)
		file.addSeparator()
		file.addAction(fileQuit)


		avatarEnviar = QtWidgets.QAction("Enviar texto", self)
		avatarEnviar.setShortcut("Ctrl+Shift+Return")
		avatarEnviar.setStatusTip("Envia o texto selecionado para o avatar sinalizar")
		avatarEnviar.triggered.connect(self.sendText)


		avatarGravar = QtWidgets.QAction("Gravar vídeo", self)
		avatarGravar.setStatusTip("Grava o vídeo para o texto selecionado")
		avatarGravar.triggered.connect(self.recordVideo)
		
		avatarMostrar = QtWidgets.QAction("Mostrar avatar", self)
		avatarMostrar.setShortcut("Ctrl+Shift+T")
		avatarMostrar.setStatusTip("Habilita/Desabilita tela do avatar")
		avatarMostrar.triggered.connect(self.toggleAvatarVisible)

		avatar.addAction(avatarEnviar)
		avatar.addAction(avatarGravar)
		avatar.addSeparator()
		avatar.addAction(avatarMostrar)

		traducaoShowAll = QtWidgets.QAction("Mostrar tudo", self)
		traducaoShowAll.setStatusTip("Exibir toda a tradução do arquivo")
		traducaoShowAll.triggered.connect(self.showAllTranslation)
		
		traducaoNext	= QtWidgets.QAction("Próxima linha", self)
		traducaoNext.setStatusTip("Próxima linha da tradução do arquivo")
		traducaoNext.triggered.connect(self.addNextTranslationParagraph)
		
		traducaoReset	= QtWidgets.QAction("Resetar tradução", self)
		traducaoReset.setStatusTip("Apaga todo o conteúdo do editor e reinicia a tradução para a primeira linha")
		traducaoReset.triggered.connect(self.resetTranslation)
		
		traducaoCreate	= QtWidgets.QAction("Gerar tradução", self)
		traducaoCreate.setStatusTip("Traduz o arquivo selecionado")
		traducaoCreate.triggered.connect(self.getTranslationFromFile)
		
		traducao.addAction(traducaoNext)
		traducao.addSeparator()
		traducao.addAction(traducaoShowAll)
		traducao.addAction(traducaoReset)
		traducao.addSeparator()
		traducao.addAction(traducaoCreate)

		imagensNewFromFile = QtWidgets.QAction("Adicionar imagem do computador", self)
		imagensNewFromFile.setStatusTip("Adiciona uma imagem do computador à lista de imagens disponíveis para o vídeo")
		imagensNewFromFile.triggered.connect(self.addImagesFromFile)

		imagensNewFromUrl = QtWidgets.QAction("Adicionar imagem da internet", self)
		imagensNewFromUrl.setStatusTip("Adiciona uma imagem da internet à lista de imagens disponíveis para o vídeo")
		imagensNewFromUrl.triggered.connect(self.addImageFromUrl)
		
		self.imagensDelete = QtWidgets.QAction("Remover imagens")
		self.imagensDelete.setStatusTip("Remover imagens da área de seleção")
		self.imagensDelete.triggered.connect(self.setRemoveImagesState)
		
		imagens.addAction(imagensNewFromFile)
		imagens.addAction(imagensNewFromUrl)
		imagens.addSeparator()
		imagens.addAction(self.imagensDelete)
		
		# Preferências
		edit = QtWidgets.QAction("Preferências", self)
		edit.setStatusTip("Opções de customização")
		edit.triggered.connect(self.openSettingsMenu)
		menubar.addAction(edit)

		bar = QtWidgets.QMenuBar(menubar)
		menubar.setCornerWidget(bar, QtCore.Qt.TopRightCorner)

		self.voltar = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowBack), "", self)
		self.voltar.setStatusTip("Voltar para a página inicial")
		self.voltar.triggered.connect(lambda: self.homePage())
		bar.addAction(self.voltar)
		self.voltar.setVisible(False)

		help = QtWidgets.QAction("Ajuda", self)
		help.setStatusTip("Manual do sistema")
		help.triggered.connect(lambda: self.openPage("textos_padrao/ajuda.html"))
		bar.addAction(help)
		
		sobre = QtWidgets.QAction("Sobre o projeto", self)
		sobre.setStatusTip("Conheça mais sobre o projeto")
		sobre.triggered.connect(lambda: self.openPage("textos_padrao/sobre"))
		bar.addAction(sobre)

		#btn_nxt.setText("Próxima linha")


	###########################################
	#
	# Componentes da UI
	#
	# Janela do servidor, editor de texto,
	# visualizador de PDF e das imagens
	#
	###########################################
	def initUI(self):
		
		# Preferências
		self.settingsMenu = GSettingsMenu()
		self.settingsMenu.newColorScheme.connect(self.onNewColorScheme)
		self.settingsMenu.newFont.connect(self.onNewFont)
	
		# Dimensões iniciais da janela
		self.screen_rect = QtWidgets.QDesktopWidget().screenGeometry()
		self.setGeometry(self.screen_rect)
		self.setWindowTitle("Inclua")
		
		# Componentes principais do editor
		self.splitter	= QtWidgets.QSplitter(self)
		self.text	= GTextEdit(self.settingsMenu.getColorScheme())
		
		self.translation = GTranslation()
		self.translation.sender.translationReady.connect(self.onTranslationReady)
		
		# Arquivo egl
		self.eglFile = GEGLFile()

		# Visualizador de pdf pode ser uma página web dentro de um webView
		self.pdf_widget = GDocument()
		self.pdf_widget.sender.formattedReady.connect(self.onPDFTextReady)
		
		self.screenshotLayer = GLayeredDocumentCanvas(self.pdf_widget)
		self.screenshotLayer.screenShot.connect(self.onScreenShot)
		#self.screenshotLayer.hide()
		
		# Widget que contém a janela do avatar e o grid com as imagens
		self.filler	= QtWidgets.QSplitter(Qt.Vertical)
		
		# Setup do widget com o display virtual
		self.server_widget = self.server.getServerWidget()
		self.server_widget.setMinimumSize(QtCore.QSize(640, 480))
		self.server_widget.setMaximumSize(QtCore.QSize(640, 480))
		
		# Widget das imagens
		self.images_widget = GImageGrid(self.default_imgDir)
		self.images_widget.onClick.connect(self.onImageClick)

		#Sobre e Ajuda
		self.view_padrao = QtWidgets.QTextEdit()
		self.view_padrao.setReadOnly(True)
		self.view_padrao.hide()

		#####################################
		#
		# Toolbar para gerenciar imagens
		#
		#####################################
		self.images_toolbar = QtWidgets.QWidget()
		self.images_toolbar.setMaximumHeight(20)
		
		self.it_layout = QtWidgets.QHBoxLayout()
		self.it_layout.setContentsMargins(5, 0, 5, 0)
		
		self.confirmar_selecao = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), "REMOVER", self)
		self.confirmar_selecao.setStatusTip("Remover as imagens selecionadas")
		self.confirmar_selecao.clicked.connect(self.removeSelected)
		
		self.confirmar_selecao.setFixedSize(QtCore.QSize(150, 20))
		self.confirmar_selecao.hide()

		self.deletar_imagens = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon), "", self)
		self.deletar_imagens.setStatusTip("Remover imagens da lista")
		self.deletar_imagens.setCheckable(True)
		self.deletar_imagens.toggled.connect(self.changeImageViewerState)

		self.printar_imagens = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView), "", self)
		self.printar_imagens.setStatusTip("Capturar parte do documento")
		self.printar_imagens.setCheckable(True)
		self.printar_imagens.toggled.connect(self.takeScreenShot)

		self.it2_layout = QtWidgets.QHBoxLayout()
		self.it2_layout.setContentsMargins(5, 0, 5, 0)
		self.it2_layout.addWidget(self.printar_imagens, alignment = Qt.AlignRight | Qt.AlignBottom)
		self.it2_layout.addWidget(self.deletar_imagens, alignment = Qt.AlignRight | Qt.AlignBottom)

		self.botoes_imagens_direita = QtWidgets.QWidget()
		self.botoes_imagens_direita.setLayout(self.it2_layout)

		self.it_layout.addWidget(self.confirmar_selecao, alignment = Qt.AlignLeft | Qt.AlignBottom)
		self.it_layout.addWidget(self.botoes_imagens_direita, alignment = Qt.AlignRight | Qt.AlignBottom)		
		
		self.images_toolbar.setLayout(self.it_layout)

		self.filler.addWidget(self.server_widget)
		self.filler.addWidget(self.images_toolbar)
		self.filler.addWidget(self.images_widget)
		
		#####################################
		#
		# Toolbar para as screenshots
		#
		#####################################
		self.screenshotsToolbar = QtWidgets.QWidget()
		self.screenshotsToolbar.setMaximumHeight(40)
		
		self.captureButton = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView), "", self)
		self.exitCaptureModeButton = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserStop), "", self)
		
		self.captureButton.clicked.connect(self.screenshotLayer.takeScreenShot)
		self.exitCaptureModeButton.clicked.connect(self.printar_imagens.toggle)
		
		self.screenshotsToolbarLayout = QtWidgets.QHBoxLayout()
		self.screenshotsToolbarLayout.addWidget(self.captureButton)
		self.screenshotsToolbarLayout.addWidget(self.exitCaptureModeButton)
		
		self.screenshotsToolbar.setLayout(self.screenshotsToolbarLayout)
		
		self.screenshotMenuWidget = QtWidgets.QWidget()
		self.screenshotMenuWidgetLayout = QtWidgets.QVBoxLayout()
		self.screenshotMenuWidgetLayout.setContentsMargins(0, 0, 0, 0)
		self.screenshotMenuWidgetLayout.addWidget(self.screenshotsToolbar)
		self.screenshotMenuWidgetLayout.addWidget(self.screenshotLayer)
		
		self.screenshotMenuWidget.setLayout(self.screenshotMenuWidgetLayout)
		
		self.screenshotsToolbar.hide()
		self.screenshotMenuWidget.hide()
		
		# Widget que aparece na janela é um splitter
		# os outros são adicionados a ele
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		self.splitter.addWidget(self.filler)
		self.splitter.addWidget(self.screenshotMenuWidget)
		self.splitter.addWidget(self.view_padrao)
		
		# Init
		self.initMenubar()

		self.statusbar = self.statusBar()
		
		# Força o widget a atualizar
		self.toggleVisible(self.server_widget)
		threading.Thread(target=self.tryCommunication).start()

	def print_cursor(self):
		cursor = self.text.textCursor()
		print("position:%2d\nachor:%5d\n" % (cursor.position(), cursor.anchor()))

	##################################
	#
	# ARQUIVOS
	#
	##################################	
	
	##################################
	#
	# Documentos
	#
	##################################
	def openDocument(self):
		filename = QtWidgets.QFileDialog().getOpenFileName(caption="Abrir documento", filter="Documentos (*.pdf *.odt *.doc *.docx *.ppt *.pptx *.rtf *.pps *.ppsx *.odp);; Todos os arquivos (*.*)")
		if filename[0] == "":
			return 1
		
		if not self.text.document().isEmpty():
			box = QtWidgets.QMessageBox()	
			box.setIcon(QtWidgets.QMessageBox.Question)
			box.setWindowTitle('Abrir documento')
			box.setText("Apagar texto do editor?")
			box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
			buttonY = box.button(QtWidgets.QMessageBox.Yes)
			buttonY.setText('Sim')
			buttonN = box.button(QtWidgets.QMessageBox.No)
			buttonN.setText('Não')
			reply = box.exec_()

#			reply = QtWidgets.QMessageBox.question(self, "Abrir documento", "Apagar texto do editor?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if reply == QtWidgets.QMessageBox.Yes:
				if not self.closeTextFile():
					return

		self.pdf_widget.load(filename[0])
		self.text.setModified(False)
		
		# Força o widget a atualizar
#		self.screenshotLayer.setGeometry(0, 0, self.screen_rect.width() / 10, self.screen_rect.height())

		
#		self.screenshotMenuWidget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, self.screenshotMenuWidget.sizePolicy().verticalPolicy())
#		self.screenshotMenuWidget.setGeometry(0, 0, self.geometry().width() // 10000, self.geometry().height())
		
		self.screenshotMenuWidget.setFixedWidth(self.geometry().width() // 3)
		
		self.screenshotMenuWidget.hide()
		self.screenshotMenuWidget.show()

		self.screenshotMenuWidget.setMinimumWidth(0)
		self.screenshotMenuWidget.setMaximumWidth(5000)

		self.hasOpenDocument = True
		
		return 0

	
	def onPDFTextReady(self, txt):
		self.images_widget.scanForImages(GDefaultValues.imgDir)
		self.images_widget.loadImages()
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Question)
		box.setWindowTitle('Abrir documento')
		box.setText("Traduzir documento?")
		box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		buttonY = box.button(QtWidgets.QMessageBox.Yes)
		buttonY.setText('Sim')
		buttonN = box.button(QtWidgets.QMessageBox.No)
		buttonN.setText('Não')
		reply = box.exec_()
#		reply = QtWidgets.QMessageBox.question(self, "Abrir documento", "Traduzir documento?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		if reply == QtWidgets.QMessageBox.Yes:
			self.translation.update(txt)

	#################################
	#
	# Arquivos de traduçao
	#
	#################################
	def newTextFile(self):
		
		if not self.closeTextFile():
			return
		
		self.translationFileName = ""
		self.hasOpenTranslationFile = False
		self.text.setModified(False)	
	
	def closeTextFile(self):
		if self.text.isModified():
			box = QtWidgets.QMessageBox()
			box.setIcon(QtWidgets.QMessageBox.Question)
			box.setWindowTitle('Salvar documento')
			
			if self.translationFileName != "":
				box.setText("Salvar mudanças no arquivo %s?" % (self.translationFileName))
			else:
				box.setText("Salvar mudanças no novo arquivo?")
			box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
			buttonY = box.button(QtWidgets.QMessageBox.Yes)
			buttonY.setText('Sim')
			buttonN = box.button(QtWidgets.QMessageBox.No)
			buttonN.setText('Não')
			buttonC = box.button(QtWidgets.QMessageBox.Cancel)
			buttonC.setText('Cancelar')
			reply = box.exec_()


			if reply == QtWidgets.QMessageBox.Cancel:
				return False
				
			if reply == QtWidgets.QMessageBox.Yes:
				if not self.saveTextFile():
					return False
		
		self.text.clear()
		self.text.setModified(False)	
		return True
	
	def getTranslationFromFile(self):
		if not self.pdf_widget.hasFile():
			self.openDocument()
			return
			
		if self.hasOpenTranslation:
			box = QtWidgets.QMessageBox()
			box.setIcon(QtWidgets.QMessageBox.Question)
			box.setWindowTitle('Gerar tradução')
			box.setText("Já existe uma tradução aberta. Substituir?")
			box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
			buttonY = box.button(QtWidgets.QMessageBox.Yes)
			buttonY.setText('Sim')
			buttonN = box.button(QtWidgets.QMessageBox.No)
			buttonN.setText('Não')
			reply = box.exec_()
			if reply == QtWidgets.QMessageBox.No:
				return 

		self.pdf_widget.getFormattedText()
	def importTextFile(self):
		filename = QtWidgets.QFileDialog().getOpenFileName(caption="Abrir arquivo de tradução", filter="EGL (*.egl)")
		if filename[0] == "":
			return
			
		if not self.closeTextFile():
			return
			
		#self.translation.load(filename[0])
		self.eglFile.load(filename[0])
		self.text.setText(self.eglFile.plainText())
		self.translation = self.eglFile.translation()
		self.translationFileName = filename[0]

	def saveTextFile(self):
		if self.translationFileName == "":
			return self.saveTextFileAs()
		else:
			#self.translation.save(self.translationFileName)
			self.eglFile.setPlainText(self.text.toPlainText())
			self.eglFile.setTranslation(self.translation)
			self.eglFile.save(self.translationFileName)
			self.text.setModified(False)
			return True
		
	def saveTextFileAs(self):
		filename = QtWidgets.QFileDialog().getSaveFileName(caption="Salvar arquivo de tradução")
		
		fname = filename[0]
		if fname == "":
			return False
			
		if not fname.endswith(".egl"):
			fname += ".egl"
			
		self.translationFileName = fname
		#self.translation.save(self.translationFileName)
		self.eglFile.setPlainText(self.text.toPlainText())
		self.eglFile.setTranslation(self.translation)
		self.eglFile.save(self.translationFileName)
		self.text.setModified(False)
		return True
		
	def exportTextFile(self, fmt):
		filename = QtWidgets.QFileDialog().getSaveFileName(caption="Exportar arquivo de tradução")
		fname = filename[0]
		if fname == "":
			return False
			
		tmpFileName = ".tmpFileName"
		
		with open(tmpFileName, "w") as doc:
			doc.write(self.text.toPlainText())

		os.system("unoconv -f %s \"%s\"" % (fmt, tmpFileName))

		os.system("mv \"%s.%s\" \"%s.%s\"" %  (tmpFileName, fmt, fname, fmt))

		return True

	def addNextTranslationParagraph(self):
		cursor = self.text.textCursor()
		cursor.movePosition(cursor.End, cursor.MoveAnchor)
		
		spaces = ""
		text = self.translation.next()
		
		while text.isspace():
			spaces += text
			text = self.translation.next()
		
		end = "\n"
		if text == "":
			end = ""
		text = spaces + text + end
		cursor.insertText(text)

	def showAllTranslation(self):
		cursor = self.text.textCursor()
		for line in self.translation.getParagraphsTillEnd():
			self.text.textCursor().insertText(line + "\n")	

	def clearTranslation(self):
		#self.text.clear()
		self.translation = GTranslation()
		self.hasOpenTranslation = False
		self.text.setModified(True)
		
	def resetTranslation(self):
		#self.text.clear()
		self.translation.resetIndex()
		self.text.setModified(True)
		
	def onTranslationReady(self):
		self.hasOpenTranslation = True


	##################################
	#
	# IMAGENS
	#
	##################################

	def addImagesFromFile(self):
		filename = QtWidgets.QFileDialog().getOpenFileNames(caption="Adicionar imagem do computador", filter="Imagens (*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG);; JPG (*.jpg *.JPG *.jpeg *JPEG);; PNG (*.png *.PNG);; Todos os arquivos (*.*)")
		print(filename[0])
		if len(filename[0]) == 0:
			return
		self.images_widget.addImagesFromFile(filename[0])
	
	def addImageFromUrl(self):
		dlg = QtWidgets.QInputDialog(self)
		dlg.setOkButtonText("Enviar")
		dlg.setCancelButtonText("Cancelar")
		dlg.setInputMode(QtWidgets.QInputDialog.TextInput) 
		dlg.setWindowTitle("Adicionar imagem por url")
		dlg.setLabelText("Url da imagem:")
		dlg.resize(500,100)                             
		ok = dlg.exec_()                                
		lineEdit = dlg.textValue()
		print ("LINEEDIT " + lineEdit)
		if lineEdit == '':
			return
		self.images_widget.addImageFromUrl(lineEdit)

	def setRemoveImagesState(self):
		self.confirmar_selecao.show()
		self.deletar_imagens.setChecked(True)
		self.images_widget.setMode(GImageGrid.selectable)

	def setClickableImagesState(self):
		self.confirmar_selecao.hide()
		self.deletar_imagens.setChecked(False)
		self.images_widget.setMode(GImageGrid.clickable)
		
	def changeImageViewerState(self, checked):
		if checked:
			self.setRemoveImagesState()
		else:
			self.setClickableImagesState()
	
	def removeSelected(self):
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Question)
		box.setWindowTitle('Remover imagens')
		box.setText("Remover todas as imagens selecionadas?")
		box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		buttonY = box.button(QtWidgets.QMessageBox.Yes)
		buttonY.setText('Confirmar')
		buttonN = box.button(QtWidgets.QMessageBox.No)
		buttonN.setText('Cancelar')
		reply = box.exec_()
#		reply = QtWidgets.QMessageBox.question(self, "Remover imagens", "Remover todas as imagens selecionadas?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		if reply == QtWidgets.QMessageBox.Yes:
			self.images_widget.removeSelected()
			self.setClickableImagesState()
	
	def onImageClick(self, index):
		lc = self.text.textCursor()
		range_content = lc.selectedText()
		pos = GCustomImageDialog().question()
		if pos == GCustomImageDialog.NoImage:
			return 
		img = self.images_widget.getImageButtonFromIndex(index)
		lc.insertText("__img%d_%d %s _img%d__" % (pos, index, range_content, pos))
	
	##################################
	#
	# SCREENSHOTS
	#
	##################################
	def setScreenCaptureState(self, state):
		print("YE")
		print(state)
		
		if self.screenshotMenuWidget.isVisible():
			self.screenshotLayer.setCaptureMode(state)
			self.screenshotsToolbar.setVisible(state)
					
	
	def takeScreenShot(self):
		self.setScreenCaptureState(not self.screenshotLayer.getCaptureMode())
	
	def onScreenShot(self, pixmap):
		self.targetPixmap = pixmap
		reply = GCustomScreenShotDialog(self.targetPixmap).question()
		if reply == GCustomScreenShotDialog.No:
			return
		self.images_widget.addImageFromPixmap(self.targetPixmap)
	
	##################################
	#
	# AVATAR
	#
	##################################
	
	def linkImages(self, text):
		matches = re.findall(r"(__img)([0-9])_([0-9]+)", text)			
		mentions = {"__img0_" : [], "__img1_" : [], "__img2_" : [], "__img3_" : []}
		for match in matches:
			mentions[match[0]+match[1] + "_"].append(match[2])
		
		for key in mentions:
			i = int(re.search(r'\d+', key).group())
			for index in mentions[key]:
				text = text.replace(key + index, ("<img%d=" % i) + "file://" + self.images_widget.getImageButtonFromIndex(int(index)).getImagePath())
			i += 1
				
		for i in range(0, 4):
			text = text.replace("_img%d__" % i, "<\\img%d>" % i)
		
		return text
	
	def sendText(self):
		cursor = self.text.textCursor()
		if cursor.hasSelection():
			text = self.linkImages(cursor.selection().toPlainText())
			self.server.send(text)
		else:
			text = self.text.toPlainText()
			QtWidgets.QMessageBox.information(self, "Gerar vídeo", "Para gerar o vídeo, selecione o texto desejado", (QtWidgets.QMessageBox.Ok))

		print(text)
		
	def toggleAvatarVisible(self):
		self.toggleVisible(self.server_widget)
		self.toggleVisible(self.filler)
	
	def toggleVisible(self, widget):
		if widget.isVisible():
			widget.hide()
		else:
			widget.show()

	def createVideo(self, vName, vId = default_videoId, pngDir = default_pngDir):
		vid = GVideo()
		vid.sender.videoReady.connect(self.onVideoReady)
		vid.createVideo(vId, vName, pngDir)
		
	def recordVideo(self):
		fName = QtWidgets.QFileDialog().getSaveFileName(caption="Gerar vídeo", filter="MP4 (*.mp4)")
		vName = fName[0]
		if vName == "":
			return
		cmd = "rm %s/%s/*" % (self.default_pngDir, self.default_videoId)
		subprocess.run(cmd, shell=True)
		cursor = self.text.textCursor()
		if cursor.hasSelection():
			txt = self.linkImages(cursor.selection().toPlainText())
			if not txt.isspace():
				txt = "__rec " + txt + " __stop"
				self.server.sendToRecord(txt, vName)

	def tryCommunication(self, n = 10):
		tries = 0
		while self.server.startCommunication() != 0 and tries < n:	
			print("Tentativa %d" % (tries))
			tries += 1
			sleep(3)
	
	def onVideoReady(self, title):
		QtWidgets.QMessageBox.question(self, "Gerar vídeo", "Vídeo %s criado com sucesso!" % title, (QtWidgets.QMessageBox.Ok))

	####################################
	#
	# PREFERÊNCIAS
	#
	####################################
	def openSettingsMenu(self):
		self.settingsMenu.show()

	def onNewColorScheme(self, colorScheme):
		self.text.setColorScheme(colorScheme)
		
	def onNewFont(self, font):
		self.text.setFont(font)
		
	####################################
	#
	# TELAS ESTÁTICAS
	#
	###################################

	def showOne(self, widget):
		for i in range(self.splitter.count()):
			self.splitter.widget(i).hide()
		widget.show()

	def openPage(self, page):
		self.showOne(self.view_padrao)
		self.initPage(page)
		self.voltar.setVisible(True)

	def initPage(self, page):
		self.textGrid = QtWidgets.QGridLayout()
		self.view_padrao.clear()

		cursor = self.view_padrao.textCursor()

		fs = cursor.charFormat()
		prop_id = 0x100000 + 1
		fs.setProperty(prop_id, 100)
		fs.setFont(QFont("arial", 12, weight=QtGui.QFont.Bold ))

		with open(page,'r',encoding = 'utf-8') as f:
			for line in f:
				cursor.insertHtml(line + "\n")
		
	
	def homePage(self):
		for i in range(self.splitter.count()):
			self.splitter.widget(i).show()
		self.view_padrao.hide()
		self.voltar.setVisible(False)


	##################################
	#
	# DESTRUTOR
	#
	##################################
	def __del__(self):
		print("Destrutor")
		self.server.kill()
		self.images_widget.clearImages()
#		exit()
	
	def closeEvent(self, event):
		if not self.closeTextFile():
			event.ignore()
			return

		super().closeEvent(event)				
#		self.__del__()

		
########################################################

def main():
	global app
	app = QtWidgets.QApplication(sys.argv)
	
	GDefaultValues()
	
	main = Main()
	main.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
