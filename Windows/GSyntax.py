import re
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

from GSettings import GDefaultValues

class GParser():
	instance = None

	class __parser():
		def __init__(self):
			
			self.known_words = None
			
			self.retrieveKnownWords()
			self.retrieveAliases()

			self.tags = ["<", ">", "[", "]"]
			self.keywords = ["__img0_", "__img1_", "__img2_", "__img3_", "_img0__", "_img1__", "_img2__", "_img3__"]
			self.commands = ["__save", "__stop", "__rec", "__last"]
			self.accentedCharacters = ['Á', 'À', 'Â', 'Ã',\
						   'É', 'È', 'Ê', 'Ẽ',\
						   'Í', 'Ì', 'Î', 'Ĩ',\
						   'Ó', 'Ò', 'Ô', 'Õ',\
						   'Ú', 'Ù', 'Û', 'Ũ',\
						   'Ń', 'Ǹ', 'Ñ', 'Ṕ']
						   
		def retrieveKnownWords(self):
			self.known_words = ahocorasick.Automaton()
			f = open("palavras")
			for w in f.read().splitlines():
				self.known_words.add_word(w, len(w))
			f.close()
			self.known_words.make_automaton()
			
		def retrieveAliases(self):
			return

	def __init__(self):
		if GParser.instance is None:
			GParser.instance = GParser.__parser()
	
	def known_words(self):
		return GParser.instance.known_words

	def tags(self):
		return GParser.instance.tags

	def known_words(self):
		return GParser.instance.known_words

	def keywords(self):
		return GParser.instance.keywords

	def commands(self):
		return GParser.instance.commands

	def getAccentedCharacters(self):
		return GParser.instance.accentedCharacters
	
	def getAlphabet(self):
		f = open("palavras")
		l = []
		for w in f:
			l.append(w[0:-1])
	
		for w in GParser.instance.keywords:
			l.append(w)
		
		for w in GParser.instance.commands:
			l.append(w)
		
		return l

	def cleanText(self, text):
		text = re.sub(r'[,\'; ]+', ' ', text)
		return text
	
	def getCommandBlocks(self, text):
		patterns = "("
		i = 0
		for cmd in GParser.instance.commands:
			if i == 0:
				patterns += cmd
				i = 1
			else:
				patterns += "|" + cmd
	
		patterns += ")"
		blocks = re.split(patterns, text)
		return list(filter(lambda a: a != "" and a != " ", blocks))

class GSyntaxHighlighter(QtGui.QSyntaxHighlighter):
	def __init__(self, txtEdit):
		self.txtEdit = txtEdit
		self.parent = self.txtEdit.document()
		self.markedForSub = False
		self.cursor1 = None
		self.cursor2 = None
		QtGui.QSyntaxHighlighter.__init__(self, self.parent)

	def highlightBlock(self, text):
		cl_known	= self.txtEdit.colorScheme().knownColor()
		cl_unknown	= self.txtEdit.colorScheme().unknownColor()
		cl_tag		= self.txtEdit.colorScheme().tagsColor()
		cl_cmd	  	= self.txtEdit.colorScheme().commandsColor()

		known		= QtGui.QTextCharFormat()
		unknown	 	= QtGui.QTextCharFormat()
		tag		= QtGui.QTextCharFormat()
		cmd		= QtGui.QTextCharFormat()

		known.setForeground(cl_known)
		unknown.setForeground(cl_unknown)
		tag.setForeground(cl_tag)
		cmd.setForeground(cl_cmd)
		
		cmd.setFontWeight(QtGui.QFont.Bold)

		word  = QtCore.QRegularExpression(r"[^<>\[\]=\(\).,;\s\n]+")
		tags  = QtCore.QRegularExpression(r"[<>\[\]]")
		links = QtCore.QRegularExpression(r"=.+?>")
		keywords = QtCore.QRegularExpression(r"(__[a-z0-9]+_[0-9]+)|(_[a-z0-9]+)__")

		i = word.globalMatch(text)
		while i.hasNext():
			match = i.next()
			end = match.capturedStart() + match.capturedLength()
			w = text[match.capturedStart():end]
			if w.isnumeric():
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in GParser().known_words():
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in GParser().commands():
				self.setFormat(match.capturedStart(), match.capturedLength(), cmd)
			elif w in GParser().keywords():
				self.setFormat(match.capturedStart(), match.capturedLength(), tag)
			else:
				self.setFormat(match.capturedStart(), match.capturedLength(), unknown)
		
		i = tags.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart(), match.capturedLength(), tag)
		
		
		i = keywords.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart(), match.capturedLength(), tag)
		
		i = links.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart()+1, match.capturedLength()-2, cmd)
			
		if self.markedForSub:
			self.subWordFont = self.txtEdit.colorScheme().subWordFontColor()
			self.subWordBackground = self.txtEdit.colorScheme().subWordBackgroundColor()
			self.subFormat = QtGui.QTextCharFormat()
			self.subFormat.setForeground(self.subWordFont)
			self.subFormat.setBackground(self.subWordBackground)
			
			if self.currentBlock().blockNumber() == self.block1:
				self.arg = len(self.cursor1.selectedText())
				self.cursor1.setPosition(self.cursor1.selectionStart(), self.cursor1.KeepAnchor)
				self.setFormat(self.cursor1.positionInBlock(), self.arg, self.subFormat)

			if self.currentBlock().blockNumber() == self.block2:
				self.arg = len(self.cursor2.selectedText())
				self.cursor2.setPosition(self.cursor2.selectionStart(), self.cursor2.KeepAnchor)
				self.setFormat(self.cursor2.positionInBlock(), self.arg, self.subFormat)
		
	def setMarkedForSub(self, c1, c2):
		self.cursor1 = QtGui.QTextCursor(c1)
		self.cursor2 = QtGui.QTextCursor(c2)
		
		self.block1 = self.cursor1.blockNumber()
		self.block2 = self.cursor2.blockNumber()
		self.markedForSub = True
	
	def unsetMarkedForSub(self):
		self.markedForSub = False
		self.cursor1 = None
		self.cursor2 = None
		
