from GSyntax import GParser, GSyntaxHighlighter

from copy import deepcopy
from PyQt5 import QtGui, QtCore, QtWidgets

#######################################
#
# Completer
#
#######################################
class GCompleter(QtWidgets.QCompleter):
	insertText = QtCore.pyqtSignal(str)
	def __init__(self, alphabet, parent = None):
		QtWidgets.QCompleter.__init__(self, alphabet, parent)
		self.setCompletionMode(self.PopupCompletion)
		self.activated.connect(self.oi)
		self.highlighted.connect(self.setHighlighted)

	def oi(self):
		self.insertText.emit(self.getSelected())
		self.setCompletionMode(self.PopupCompletion)

	def setHighlighted(self, text):
	    self.lastSelected = text

	def getSelected(self):
	    return self.lastSelected

#######################################
#
# Editor de texto
#	
#######################################
class GTextEdit(QtWidgets.QTextEdit):
	def __init__(self, clScheme, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
		self.completer = GCompleter(GParser().getAlphabet())
		self.completer.setWidget(self)
		self.completer.insertText.connect(self.insertCompletion)
		self.pressed = {}
		self.onDeadKey = False
		
		self.highlighter = GSyntaxHighlighter(self)
		
		self.clScheme = clScheme
		
		self.completionEnd = " "
		
		self.setAttribute(QtCore.Qt.WA_InputMethodEnabled)
	
	def colorScheme(self):
		return self.clScheme
		
	def setColorScheme(self, colorScheme):
		self.clScheme = colorScheme
		self.highlighter.rehighlight()
		
	def getSyntaxHighlighter(self):
		return self.highlighter
	
	def isModified(self):
		return self.document().isModified()
		
	def setModified(self, m = True):
		self.document().setModified(m)
		
	#####################################
	#
	# Eventos do teclado
	#
	#####################################
	def isPressed(self, key):
		if key in self.pressed:
			return self.pressed[key]
		return False
			
	def keyReleaseEvent(self, event):
		ek = event.key()
		self.pressed[ek] = False
		
		if ek == QtCore.Qt.Key_Control:
			self.highlighter.unsetMarkedForSub()
			self.highlighter.rehighlight()
		
		QtWidgets.QTextEdit.keyReleaseEvent(self, event)
	
	####################################
	#
	# Funções auxiliares para selecionar
	# tokens com separators padrão
	#
	####################################
	
	# QChar::QParagraphSeparator 	= chr(0x2029)
	# QChar::LineSeparator 		= chr(0x2028)
	def selectToken(self, stopChars = (' ','\t', '\n', '\r', '\n\r', chr(0x2029), chr(0x2028)), leftSeparators = ('<', '['), rightSeparators = ('>', ']') ):
		cursor = self.textCursor()
		
		#cursor.select(cursor.WordUnderCursor)
		
		ini = cursor.position()
		end = cursor.position()
		
		wordLeft = False
		
		# Confere se há palavra à esquerda
		cursor.setPosition(ini, cursor.MoveAnchor)
		if cursor.movePosition(cursor.Left, cursor.KeepAnchor):
			if cursor.selectedText().startswith(stopChars):
				cursor.movePosition(cursor.Right, cursor.KeepAnchor)
		
		leftStop = stopChars + rightSeparators
		while cursor.movePosition(cursor.Left, cursor.KeepAnchor):
			if cursor.selectedText().startswith(leftSeparators):
				break
			if cursor.selectedText().startswith(leftStop):
				cursor.movePosition(cursor.Right, cursor.KeepAnchor)
				break
		
			
		ini = cursor.selectionStart()
		
		if cursor.selectedText() == "" and cursor.movePosition(cursor.Right, cursor.KeepAnchor):
			if cursor.selectedText().endswith(stopChars):
				cursor.movePosition(cursor.Left, cursor.KeepAnchor)
			
		
		rightStop = stopChars + leftSeparators			
		while cursor.movePosition(cursor.Right, cursor.KeepAnchor):
			if cursor.selectedText().endswith(rightSeparators):
				break
			if cursor.selectedText().endswith(rightStop):
				cursor.movePosition(cursor.Left, cursor.KeepAnchor)
				break
		
		end = cursor.selectionEnd()
		
		cursor.setPosition(ini, cursor.MoveAnchor)
		cursor.setPosition(end, cursor.KeepAnchor)
		
		return cursor
	
	#########################################
	#
	# Controle fino do input
	#
	# Mexer aqui para tratar teclas mortas
	# ( `, ´, ~, ^ )
	#
	#########################################
	def inputMethodEvent(self, event):
		commitString  = event.commitString()
		preeditString = event.preeditString()

		# Se for uma tecla morta que não invoca o keyPressEvent
		# cria o evento na mão já com o caractere em maiúsculo
		if commitString.upper() in GParser().getAccentedCharacters():
			newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Any, QtCore.Qt.NoModifier, commitString.upper())
			self.keyPressEvent(newEvent)
		else:
			super().inputMethodEvent(event)
	
	####################################
	#
	# keyPressEvent
	#
	####################################
	def keyPressEvent(self, event):
		ek = event.key()
		self.pressed[ek] = True

		# Provavelmente só tem o efeito desejado em sistemas
		# cujas teclas mortas não invocam esse evento
		self.onDeadKey = False
		
		if (ek == QtCore.Qt.Key_Tab or ek == QtCore.Qt.Key_Return) and self.completer.popup().isVisible():
			self.completer.insertText.emit(self.completer.getSelected())
			self.completer.setCompletionMode(self.completer.PopupCompletion)
			return
		
		moveWordFlag = False
		#srcCursor = self.textCursor()
		#srcCursor.select(srcCursor.WordUnderCursor)
		srcCursor = self.selectToken()
		if self.isPressed(QtCore.Qt.Key_Control) and ek in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right) and srcCursor.selectedText() != "" and not srcCursor.selectedText().isspace():
			moveWordFlag = True
		
			#dstCursor = self.textCursor()
			dstCursor = QtGui.QTextCursor(srcCursor)
			
			if ek == QtCore.Qt.Key_Left:
				dstCursor.setPosition(dstCursor.selectionStart(), dstCursor.MoveAnchor)
				dstCursor.movePosition(dstCursor.PreviousWord, dstCursor.MoveAnchor)
			else:
				dstCursor.setPosition(dstCursor.selectionEnd(), dstCursor.MoveAnchor)
				dstCursor.movePosition(dstCursor.NextWord, dstCursor.MoveAnchor)
			
			self.setTextCursor(dstCursor)
			#dstCursor.select(dstCursor.WordUnderCursor)
			dstCursor = self.selectToken()
			if srcCursor != dstCursor:
				w1 = srcCursor.selectedText()
				w2 = dstCursor.selectedText()
				
				self.textCursor().beginEditBlock()
				srcCursor.insertText(w2)
				dstCursor.insertText(w1)
				self.textCursor().endEditBlock()
		
		# Cópia do evento, mas com o texto em maiúsculo
		newEventText = event.text()
		if not srcCursor.selectedText().startswith(('<', '_')):
			newEventText = newEventText.upper()
		newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, event.key(), event.modifiers(), event.nativeScanCode(), event.nativeVirtualKey(), event.nativeModifiers(), newEventText, event.isAutoRepeat(), event.count())
		
		if not moveWordFlag:
			QtWidgets.QTextEdit.keyPressEvent(self, newEvent)
			
		txt = newEvent.text()
		
		# Marca a palavra debaixo do cursor se Ctrl estiver pressionado
		if self.isPressed(QtCore.Qt.Key_Control):
			newCursor = self.selectToken()
			self.highlighter.unsetMarkedForSub()
			self.highlighter.setMarkedForSub(newCursor, newCursor)
			self.highlighter.rehighlight()
		
		# Aparece o completer ao digitar uma letra, símbolo de tag ou comando, ou Ctrl+Espaço
		if txt.isalpha() or txt.isdigit() or txt == '_' or (self.isPressed(QtCore.Qt.Key_Control) and ek == QtCore.Qt.Key_Space):
			self.completerHandler()
		else:
			self.completer.popup().hide()	


	def completerHandler(self):
	#	tc = self.textCursor()
	#	tc.select(tc.WordUnderCursor)
		tc = self.selectToken()
		cr = self.cursorRect()
		
		word = tc.selectedText()
		if len(word) > 0:
			self.completer.setCompletionPrefix(word)
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0) | self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
		else:
			self.completer.popup().hide()

	###########################################
	#
	# Ações do completer
	#
	###########################################
	def insertCompletion(self, completion):
		tc = self.textCursor()
		lc = self.textCursor()
		
		
		tc.movePosition(QtGui.QTextCursor.EndOfWord, tc.MoveAnchor)
		tc.movePosition(QtGui.QTextCursor.StartOfWord, tc.KeepAnchor)
		
		lc.movePosition(QtGui.QTextCursor.StartOfWord, lc.MoveAnchor)
		lc.movePosition(QtGui.QTextCursor.Left, lc.KeepAnchor)
		lc = lc.selectedText()
		if lc == '<':
			tc.movePosition(QtGui.QTextCursor.Left, tc.KeepAnchor)
		
		if completion in GParser().keywords():
			tc.insertText(completion)
		else:
			tc.insertText(completion + self.completionEnd)
		self.setTextCursor(tc)
		self.completer.popup().hide()
	
	#########################################
	#
	# Atalho de teclado para o completer
	#
	#########################################
	def popupShowConditions(self, text, key):
		return key == QtCore.Qt.Key_Space and self.isPressed(QtCore.Qt.Key_Control)
		
	def wordSubFunction(self, target, cursor):
		cursor.insertText(target.text())
		self.setTextCursor(cursor)

	def getDisambiguationList(self, word):
		return [word, word+"YES", "NO"]
		
	##########################################
	#
	# Ações do mouse
	#
	##########################################
	def getClickedWord(self):
		#cursor = self.textCursor()
		#cursor.select(cursor.WordUnderCursor)	
		cursor = self.selectToken()
		return cursor.selectedText(), cursor
			
	def wordSwap(self, event, swapword1, swapword2):
		# Limpa o fundo da palavra 1
		self.setTextCursor(swapword1)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		# Limpa o fundo da palavra 2
		self.setTextCursor(swapword2)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		self.setTextCursor(self.cursorForPosition(event.pos()))

		if (swapword1 == swapword2):
			return

		w1 = swapword1.selectedText()
		w2 = swapword2.selectedText()
		self.textCursor().beginEditBlock()
		swapword1.insertText(w2)
		swapword2.insertText(w1)
		self.textCursor().endEditBlock()

	##########################
	#
	# Context Menu
	#
	##########################
	def contextMenuEvent(self, event):

		old_cursor = self.textCursor()

		# Pega a palavra 1
		#swapword1 = self.textCursor()
		#swapword1.select(swapword1.WordUnderCursor)
		swapword1 = self.selectToken()
		self.setTextCursor(swapword1)

		# Pega a palavra 2
		self.setTextCursor( self.cursorForPosition(event.pos()) )
		#swapword2 = self.textCursor()
		#swapword2.select(swapword1.WordUnderCursor)
		swapword2 = self.selectToken()
		
		# Remove a seleção da palavra 2
		self.setTextCursor(self.cursorForPosition(event.pos()))

		# Marca flag para o highlighter mudar a cor da fonte
		self.highlighter.setMarkedForSub(swapword1, swapword2)
		self.highlighter.rehighlight()

		menu = QtWidgets.QMenu()
		menu.addAction(QtGui.QIcon.fromTheme("view-refresh"), "Trocar Palavras", lambda:self.wordSwap(event, swapword1, swapword2))
		menu.exec(event.globalPos())
		
		# Limpa flag do highlighter
		self.highlighter.unsetMarkedForSub()
		self.highlighter.rehighlight()
		
		# Limpa o fundo da palavra 1
		self.setTextCursor(swapword1)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		# Limpa o fundo da palavra 2
		self.setTextCursor(swapword2)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		swapword1 = None
		swapword2 = None
#		self.setTextCursor(self.cursorForPosition(event.pos()))
		self.setTextCursor(old_cursor)

