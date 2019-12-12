import os
import configparser

from PyQt5 import QtCore, QtGui, QtWidgets

class GDefaultValues():
	cwd		= os.getcwd()
	home		= os.path.expanduser("~")
	pngDir		= home + "/.config/unity3d/LAViD/VLibrasVideoMaker"
	pngDirSuffix	= "/.config/unity3d/LAViD/VLibrasVideoMaker"
	videoId 	= "teste_renderer"
	imgDir		= cwd + "\\media\\images"
	
	imgPrefix	= "IMG"
	cwd = cwd.replace("\\", "/")
	pdfJs		= 'file:///' + cwd + '/pdfjs/web/viewer.html'
	
	ini_filename	= "inclua.ini"
	#######################
	#
	# Colors
	#
	#######################
	
	# tokens
	cl_known	= QtGui.QColor(0x000000)
	cl_unknown	= QtGui.QColor(0xFF0000)
	cl_tag		= QtGui.QColor(0x000088)
	cl_cmd	  	= QtGui.QColor(0x2200FF)

	# markers
	cl_textEditBackground = None
	cl_subWordFont = None
	cl_subWordBackground = None
	
	utilizarCorInversa = True
	
	#######################
	#
	# Fonts
	#
	#######################
	font = None
	
	def __init__(self):
		self.txtEditor = QtWidgets.QTextEdit()
		self.__class__.cl_textEditBackground = self.txtEditor.palette().color(QtGui.QPalette.Window)
		self.__class__.cl_subWordFont = self.cl_textEditBackground
		rgba = [abs(x - y) for x in (255, 255, 255, 0) for y in self.cl_subWordFont.getRgb()]
		self.__class__.cl_subWordBackground = QtGui.QColor(rgba[0], rgba[1], rgba[2], 255)
		
		self.__class__.font = self.txtEditor.font()
		self.__class__.font.setStyleName("Regular")
		
		if not os.path.exists(self.ini_filename):
			with open(self.ini_filename, "w") as f:
				f.write("[CORES]\n")
				f.write("palavras_conhecidas=" + str(self.cl_known.getRgb()) + '\n')
				f.write("palavras_desconhecidas=" + str(self.cl_unknown.getRgb()) + '\n')
				f.write("tags=" + str(self.cl_tag.getRgb()) + '\n')
				f.write("comandos=" + str(self.cl_cmd.getRgb()) + '\n')
				f.write("fonte_texto_marcado=" + str(self.cl_subWordFont.getRgb()) + '\n')
				f.write("fundo_texto_marcado=" + str(self.cl_subWordBackground.getRgb()) + '\n')
				f.write("utilizar_cor_inversa=" + str(self.utilizarCorInversa) + '\n')
				f.write('\n[FONTES]\n')
				f.write("fonte=" + str(self.font.key()) + '\n')
	
class GColorScheme():
	Known			= 0
	Unknown			= 1
	Tags			= 2
	Commands 		= 3
	SubWordBackground	= 4
	SubWordFont		= 5
	
	def __init__(self, known = GDefaultValues.cl_known, unknown = GDefaultValues.cl_unknown, tags = GDefaultValues.cl_tag, commands = GDefaultValues.cl_cmd, subWordBackground = GDefaultValues.cl_subWordBackground, subWordFont = GDefaultValues.cl_subWordFont):
		self.cl_known 	= known
		self.cl_unknown = unknown
		self.cl_tag	= tags
		self.cl_cmd	= commands
		
		self.cl_subWordBackground = subWordBackground
		self.cl_subWordFont = subWordFont
		
	def knownColor(self):
		return self.cl_known
		
	def unknownColor(self):
		return self.cl_unknown
		
	def tagsColor(self):
		return self.cl_tag
		
	def commandsColor(self):
		return self.cl_cmd

	def subWordBackgroundColor(self):
		return self.cl_subWordBackground
		
	def subWordFontColor(self):
		return self.cl_subWordFont
		
	def getInverseColor(self, color):
		rgba = [abs(x - y) for x in (255, 255, 255, 0) for y in color.getRgb()]
		return QtGui.QColor(rgba[0], rgba[1], rgba[2], 255)
		
class GSettingsMenu(QtWidgets.QWidget):
	# Signals
	newColorScheme = QtCore.pyqtSignal(GColorScheme)
	currentColorSchemeChanged = QtCore.pyqtSignal(GColorScheme)
	newFont	= QtCore.pyqtSignal(QtGui.QFont)
	currentFontChanged = QtCore.pyqtSignal(QtGui.QFont)

	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.setWindowTitle("Preferências")
		self.tabsMenu = QtWidgets.QTabWidget()
		
		self.currentColorSchemeChanged.connect(self.onCurrentColorSchemeChanged)
		self.currentFontChanged.connect(self.onCurrentFontChanged)
		
		##########################
		#
		# CORES
		#
		##########################
		self.retrieveSettings()
		self.colorsTab = QtWidgets.QWidget()
		
		## TOKENS
		self.changeKnownColor		= QtWidgets.QPushButton("Palavras conhecidas")
		self.changeUnknownColor		= QtWidgets.QPushButton("Palavras desconhecidas")
		self.changeTagsColor		= QtWidgets.QPushButton("Tags/Marcações")
		self.changeCommandsColor	= QtWidgets.QPushButton("Comandos")

		self.changeKnownColor.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.changeUnknownColor.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.changeTagsColor.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.changeCommandsColor.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

		self.changeKnownColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Known))
		self.changeUnknownColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Unknown))
		self.changeTagsColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Tags))
		self.changeCommandsColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Commands))

		self.changeKnownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeUnknownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeTagsColor.setStyleSheet("text-align:left; padding:3px")
		self.changeCommandsColor.setStyleSheet("text-align:left; padding:3px")

		colorsTokensLayout = QtWidgets.QVBoxLayout()
		colorsTokensLayout.addWidget(self.changeKnownColor)
		colorsTokensLayout.addWidget(self.changeUnknownColor)
		colorsTokensLayout.addWidget(self.changeTagsColor)
		colorsTokensLayout.addWidget(self.changeCommandsColor)

		colorsTokensGroup = QtWidgets.QGroupBox("Tokens")
		colorsTokensGroup.setLayout(colorsTokensLayout)
		
		## MARCADORES
		
		self.utilizarCorInversaCheck = QtWidgets.QCheckBox("Utilizar fonte na cor inversa do fundo")
		self.utilizarCorInversaCheck.setChecked(self.utilizarCorInversa)
		self.utilizarCorInversaCheck.stateChanged.connect(self.colorMarkerCheckBoxChanged)
		
		self.changeSubWordFontColor = QtWidgets.QPushButton("Fonte das palavras para trocar")
		self.changeSubWordBackgroundColor = QtWidgets.QPushButton("Fundo  das palavras para trocar")
		
		self.changeSubWordFontColor.setEnabled(not self.utilizarCorInversa)
		
		self.changeSubWordFontColor.setStyleSheet("text-align:left; padding:3px")
		self.changeSubWordBackgroundColor.setStyleSheet("text-align:left; padding:3px")
		
		self.changeSubWordFontColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.SubWordFont))
		self.changeSubWordBackgroundColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.SubWordBackground))
		
		colorsMarkersLayout = QtWidgets.QVBoxLayout()
		colorsMarkersLowerLayout = QtWidgets.QVBoxLayout()
		colorsMarkersLowerLayout.setContentsMargins(0, 0, 0, 0)
		colorsMarkersLowerLayout.addWidget(self.utilizarCorInversaCheck)
		colorsMarkersLowerLayout.addWidget(self.changeSubWordFontColor)
		
		colorsMarkersLayout.addWidget(self.changeSubWordBackgroundColor)
		colorsMarkersLayout.addLayout(colorsMarkersLowerLayout)
		
		colorsMarkersGroup = QtWidgets.QGroupBox("Marcadores")
		colorsMarkersGroup.setLayout(colorsMarkersLayout)

		## LAYOUT PRINCIPAL MENU DE CORES
		colorsMainLayout = QtWidgets.QVBoxLayout()
		colorsUpperLayout = QtWidgets.QHBoxLayout()
		
		colorsUpperLayout.addWidget(colorsTokensGroup)
		colorsUpperLayout.addWidget(colorsMarkersGroup)
		
		colorsMainLayout.addLayout(colorsUpperLayout)

		self.updateButtons()
		
		self.colorsTab.setLayout(colorsMainLayout)


		###############################
		#
		# FONTES
		#
		###############################
		
		self.fontsTab = QtWidgets.QWidget()
		
		self.fontDialog = QtWidgets.QFontDialog()
		self.fontDialog.setModal(False)
		self.fontDialog.setOption(self.fontDialog.DontUseNativeDialog)
		self.fontDialog.setOption(self.fontDialog.NoButtons)
		
		self.fontDialog.setCurrentFont(self.currentFont)
		self.fontDialog.currentFontChanged.connect(lambda font : self.currentFontChanged.emit(font))
		
		fontsTabLayout = QtWidgets.QVBoxLayout()
		fontsTabLayout.addWidget(self.fontDialog)
		
		self.fontsTab.setLayout(fontsTabLayout)

		###############################
		#
		# FINALIZAR
		#
		###############################
		self.aplicar	= QtWidgets.QPushButton("Aplicar")
		self.salvar	= QtWidgets.QPushButton("Ok")
		self.cancelar	= QtWidgets.QPushButton("Fechar")
		self.resetar	= QtWidgets.QPushButton("Valores padrão")

		self.aplicar.setEnabled(False)

		self.aplicar.clicked.connect(self.onApplyButtonPressed)
		self.salvar.clicked.connect(self.onSaveButtonPressed)
		self.cancelar.clicked.connect(self.onCancelButtonPressed)
		self.resetar.clicked.connect(self.resetDefaultValues)

		exitLayout = QtWidgets.QHBoxLayout()
		exitLayout.addWidget(self.aplicar)
#		exitLayout.addWidget(self.salvar)
		exitLayout.addWidget(self.cancelar)
		exitLayout.addWidget(self.resetar)

		exitGroup = QtWidgets.QGroupBox()
		exitGroup.setLayout(exitLayout)

		###############################
		#
		# LAYOUT DAS TABS
		#
		###############################
		self.tabsMenu.addTab(self.colorsTab, "Cores")
		self.tabsMenu.addTab(self.fontsTab, "Fontes")

		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.tabsMenu)
		layout.addWidget(exitGroup)
		self.setLayout(layout)

	def retrieveColorScheme(self):
		if os.path.exists(GDefaultValues.ini_filename):
			self.config = configparser.ConfigParser()
			self.config.sections()
			self.config.read(GDefaultValues.ini_filename)
			
			tmp = eval(self.config['CORES']['palavras_conhecidas'])
			self.cl_known			= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])
			
			tmp = eval(self.config['CORES']['palavras_desconhecidas'])
			self.cl_unknown			= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])
			
			tmp = eval(self.config['CORES']['tags'])
			self.cl_tag			= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])

			tmp = eval(self.config['CORES']['comandos'])
			self.cl_cmd			= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])
			
			tmp = eval(self.config['CORES']['fonte_texto_marcado'])
			self.cl_subWordFont		= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])
			
			tmp = eval(self.config['CORES']['fundo_texto_marcado'])
			self.cl_subWordBackground	= QtGui.QColor(tmp[0], tmp[1], tmp[2], tmp[3])
			
			self.utilizarCorInversa	= eval(self.config['CORES']['utilizar_cor_inversa'])
		else:
			self.cl_known		= GDefaultValues.cl_known
			self.cl_unknown		= GDefaultValues.cl_unknown
			self.cl_tag		= GDefaultValues.cl_tag
			self.cl_cmd	  	= GDefaultValues.cl_cmd
			self.cl_subWordFont	= GDefaultValues.cl_subWordFont
			self.cl_subWordBackground = GDefaultValues.cl_subWordBackground

			self.utilizarCorInversa = GDefaultValues.utilizarCorInversa
		
		self.colorScheme = GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont))
		
	def retrieveFont(self):
		if os.path.exists(GDefaultValues.ini_filename):
			self.config = configparser.ConfigParser()
			self.config.sections()
			self.config.read(GDefaultValues.ini_filename)
			
			self.currentFont = QtGui.QFont(self.config['FONTES']['fonte'])
			self.currentFont.setPointSize(int(self.config['FONTES']['fonte'].split(',')[1]))
			self.currentFont.setStyleName(self.config['FONTES']['fonte'].split(',')[10])
			
		else:
			self.currentFont = GDefaultValues.font
			
	def retrieveSettings(self):
		self.retrieveColorScheme()
		self.retrieveFont()

	def getColorScheme(self):
		return self.colorScheme
		
	def colorMarkerCheckBoxChanged(self, state):
		self.changeSubWordFontColor.setEnabled(not state)
		self.aplicar.setEnabled(True)

	def updateButtons(self):
		# Bordas
		painter = QtGui.QPainter()
	
		color_w = 150
		color_h = 140
		
		border1_w = 10
		border1_h = 10
		
		border2_w = 14
		border2_h = 14
		
		border3_w = 10
		border3_h = 10
		
		icon_w = 100
		icon_h = 100
		
		border1 = QtGui.QPixmap(color_w + border1_w, color_h + border1_h)
		border2 = QtGui.QPixmap(color_w + border1_w + border2_w, color_h + border1_h + border2_h)
		
		borderPixmapTemplate = QtGui.QPixmap(color_w + border1_w + border2_w + border3_w, color_h + border1_h + border2_h + border3_h)
	
		border1.fill(QtCore.Qt.black)
		border2.fill(QtCore.Qt.white)
		borderPixmapTemplate.fill(QtCore.Qt.black)
		
		painter.begin(borderPixmapTemplate)
		painter.drawPixmap(border3_w/2, border3_h/2, border2)
		painter.drawPixmap((border2_w + border3_w)/2, (border2_h + border3_h)/2, border1)
		painter.end()
		
		# Ícones
		border_w = border1_w + border2_w + border3_w
		border_h = border1_h + border2_h + border3_h
		iconPixmap = QtGui.QPixmap(borderPixmapTemplate)
		
		# Palavras conhecidas
		knownPixmap = QtGui.QPixmap(color_w, color_h)
		knownPixmap.fill(self.cl_known)
		
		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, knownPixmap)
		painter.end()
		
		self.changeKnownColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeKnownColor.setIconSize(QtCore.QSize(100, 100))

		# Palavras desconhecidas
		unknownPixmap = QtGui.QPixmap(color_w, color_h)
		unknownPixmap.fill(self.cl_unknown)
		
		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, unknownPixmap)
		painter.end()
		
		self.changeUnknownColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeUnknownColor.setIconSize(QtCore.QSize(icon_w, icon_h))

		# Tags
		tagsPixmap = QtGui.QPixmap(color_w, color_h)
		tagsPixmap.fill(self.cl_tag)

		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, tagsPixmap)
		painter.end()
		
		self.changeTagsColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeTagsColor.setIconSize(QtCore.QSize(icon_w, icon_h))

		# Comandos
		commandsPixmap = QtGui.QPixmap(color_w, color_h)
		commandsPixmap.fill(self.cl_cmd)
		
		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, commandsPixmap)
		painter.end()
		
		self.changeCommandsColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeCommandsColor.setIconSize(QtCore.QSize(icon_w, icon_h))
		
		# Background das palavras a substituir
		subWordBackgroundPixmap = QtGui.QPixmap(color_w, color_h)
		subWordBackgroundPixmap.fill(self.cl_subWordBackground)
		
		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, subWordBackgroundPixmap)
		painter.end()
		
		self.changeSubWordBackgroundColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeSubWordBackgroundColor.setIconSize(QtCore.QSize(icon_w, icon_h))
		
		# Fonte das palavras a substituir
		subWordFontPixmap = QtGui.QPixmap(color_w, color_h)
		subWordFontPixmap.fill(self.cl_subWordFont)
		
		painter.begin(iconPixmap)
		painter.drawPixmap(border_w / 2, border_h / 2, subWordFontPixmap)
		painter.end()
		
		self.changeSubWordFontColor.setIcon(QtGui.QIcon(iconPixmap))
		self.changeSubWordFontColor.setIconSize(QtCore.QSize(icon_w, icon_h))
	
	def newColorSelectionMenu(self, target):
		self.dialog = QtWidgets.QColorDialog()
		
		self.dialog.setOption(self.dialog.DontUseNativeDialog)
		self.dialog.colorSelected.connect(lambda color: self.onColorSelected(target, color))
		if target == GColorScheme.Known:
			self.dialog.setCurrentColor(self.cl_known)
		elif target == GColorScheme.Unknown:
			self.dialog.setCurrentColor(self.cl_unknown)
		elif target == GColorScheme.Tags:
			self.dialog.setCurrentColor(self.cl_tag)
		elif target == GColorScheme.Commands:
			self.dialog.setCurrentColor(self.cl_cmd)
		elif target == GColorScheme.SubWordBackground:
			self.dialog.setCurrentColor(self.cl_subWordBackground)
		elif target == GColorScheme.SubWordFont:
			self.dialog.setCurrentColor(self.cl_subWordFont)

		self.dialog.open()

	def onColorSelected(self, target, color):
		if target == GColorScheme.Known:
			self.cl_known = color
		elif target == GColorScheme.Unknown:
			self.cl_unknown = color
		elif target == GColorScheme.Tags:
			self.cl_tag = color
		elif target == GColorScheme.Commands:
			self.cl_cmd = color
		elif target == GColorScheme.SubWordBackground:
			self.cl_subWordBackground = color
		elif target == GColorScheme.SubWordFont:
			self.cl_subWordFont = color
		
		self.currentColorSchemeChanged.emit(GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont)))
		
		self.updateButtons()

	def commitColorChanges(self):
		self.colorScheme = GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont))
		
		self.utilizarCorInversa = self.utilizarCorInversaCheck.isChecked()
		
		self.config['CORES']["palavras_conhecidas"]	= str(self.cl_known.getRgb())
		self.config['CORES']["palavras_desconhecidas"]	= str(self.cl_unknown.getRgb())
		self.config['CORES']["tags"]			= str(self.cl_tag.getRgb())
		self.config['CORES']["comandos"]		= str(self.cl_cmd.getRgb())
		self.config['CORES']["fonte_texto_marcado"]	= str(self.cl_subWordFont.getRgb())
		self.config['CORES']["fundo_texto_marcado"]	= str(self.cl_subWordBackground.getRgb())
		self.config['CORES']["utilizar_cor_inversa"]	= str(self.utilizarCorInversa)
		
		
		with open(GDefaultValues.ini_filename, "w") as configfile:
			self.config.write(configfile)
		
		self.newColorScheme.emit(self.colorScheme)

	def cancelColorChanges(self):
		self.cl_known	= self.colorScheme.knownColor()
		self.cl_unknown	= self.colorScheme.unknownColor()
		self.cl_tag	= self.colorScheme.tagsColor()
		self.cl_cmd	= self.colorScheme.commandsColor()
		self.cl_subWordBackground = self.colorScheme.subWordBackgroundColor()
		self.cl_subWordFont	  = self.colorScheme.subWordFontColor()
		
		self.utilizarCorInversaCheck.setChecked(self.utilizarCorInversa)
		
		self.currentColorSchemeChanged.emit(GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont)))
		
		self.updateButtons()

	def resetDefaultColorScheme(self):
		self.cl_known	= GDefaultValues.cl_known
		self.cl_unknown	= GDefaultValues.cl_unknown
		self.cl_tag	= GDefaultValues.cl_tag
		self.cl_cmd	= GDefaultValues.cl_cmd
		self.cl_subWordBackground = GDefaultValues.cl_subWordBackground
		self.cl_subWordFont	  = GDefaultValues.cl_subWordFont
		
		self.utilizarCorInversaCheck.setChecked(GDefaultValues.utilizarCorInversa)
		
		self.currentColorSchemeChanged.emit(GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont)))
		
		self.updateButtons()
		
	def resetDefaultFont(self): 
		self.currentFont = GDefaultValues.font
		self.fontDialog.setCurrentFont(self.currentFont)
		self.currentFontChanged.emit(self.currentFont)
		
	def resetDefaultValues(self):
		if self.tabsMenu.currentIndex() == self.tabsMenu.indexOf(self.colorsTab):
			self.resetDefaultColorScheme()
		if self.tabsMenu.currentIndex() == self.tabsMenu.indexOf(self.fontsTab):
			self.resetDefaultFont()
		
	def commitFontChanges(self):
		self.currentFont = self.fontDialog.currentFont()
		self.config['FONTES']['fonte'] = self.currentFont.key()
		#print(self.currentFont.key())
		with open(GDefaultValues.ini_filename, "w") as configfile:
			self.config.write(configfile)
		self.newFont.emit(self.currentFont)
		
	def cancelFontChanges(self):
		self.fontDialog.setCurrentFont(self.currentFont)
		self.currentFontChanged.emit(self.currentFont)
		
	def onApplyButtonPressed(self):
		self.commitColorChanges()
		self.commitFontChanges()
		self.aplicar.setEnabled(False)

	def onSaveButtonPressed(self):
		self.commitColorChanges()
		self.commitFontChanges()
		self.hide()
		self.aplicar.setEnabled(False)

	def onCancelButtonPressed(self):
		self.cancelColorChanges()
		self.cancelFontChanges()
		self.hide()
		self.aplicar.setEnabled(False)
		
	def onCurrentColorSchemeChanged(self, colorScheme):
		self.aplicar.setEnabled(True)
	
	def onCurrentFontChanged(self, font):
		self.aplicar.setEnabled(True)
