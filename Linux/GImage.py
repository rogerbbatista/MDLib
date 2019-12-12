import os
from natsort import natsorted
import re
import threading
import subprocess

from shutil import copyfile
from PyQt5 import QtWidgets, QtGui , QtCore

from GSettings import GDefaultValues

#################################
#
# Botões com imagens
#
#################################
class GImageButton(QtWidgets.QPushButton):
    onClick = QtCore.pyqtSignal(int)
    deleted = QtCore.pyqtSignal()

    default_width  = 120
    default_height = 120
    default_box_width  = 130
    default_box_height = 130
    
#    default_alignment = QtCore.Qt.AlignRight | QtCore.Qt.AlignTop
    default_alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop

    def __init__(self, img_url, index, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.image = img_url
        self.index = int(re.search(r'\d+$', os.path.splitext(self.image)[0]).group())

        self.parent = parent

        self.selected = False
        
        self.indexLabel = QtWidgets.QLabel(str(self.index))
        
        self.pixmap = QtGui.QPixmap(img_url)
        self.setIcon(QtGui.QIcon(self.pixmap))
        self.setIconSize(QtCore.QSize(self.default_width, self.default_height))
#        self.setFixedSize(self.icon().actualSize(QtCore.QSize(self.default_width, self.default_height)))
        self.setFixedSize(QtCore.QSize(self.default_box_width, self.default_box_height))
#        self.setStyleSheet("QPushButton { border-style: outset }") 
        
        self.layout = QtWidgets.QVBoxLayout()
        self.checkbox = QtWidgets.QCheckBox()
        self.layout.addWidget(self.checkbox, alignment = self.default_alignment)
        self.layout.addWidget(self.indexLabel, alignment = QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.setLayout(self.layout)
       
        self.checkbox.hide()
       	self.checkbox.toggled.connect(self.setSelected)
    
    def toggleSelectionView(self):
        self.selected = False
        self.checkbox.setChecked(False)
        if self.checkbox.isVisible():
            self.checkbox.hide()
        else:
            self.checkbox.show()

    def setSelectionView(self, visible):
        self.selected = False
        self.checkbox.setChecked(False)
        if visible:
            self.checkbox.show()
        else:
            self.checkbox.hide()
    
    def toggleSelected(self):
        self.selected = not self.selected
        self.checkbox.setChecked(self.selected)
        
    def setSelected(self, selected):
        self.selected = selected
        self.checkbox.setChecked(self.selected)

    def isSelected(self):
        return self.selected
    
    def getImagePath(self):
        return self.image
    	
    def getExtension(self):
        return os.path.splitext(self.image)[1]
    
    def getIndex(self):
        return self.index

    def remove(self):
        os.remove(self.image)

    def mousePressEvent(self, ev):
        mouseButton = ev.buttons()
        if mouseButton == QtCore.Qt.LeftButton:
            if self.checkbox.isVisible():
                self.checkbox.toggle()
            else:
                self.onClick.emit(self.index)
            	
        super().mousePressEvent(ev)

    def contextMenuEvent(self, ev):
        menu = QtWidgets.QMenu()
        delete = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserStop), "Remover", self)
        delete.setStatusTip("Remover essa imagem da lista")
        delete.triggered.connect(self.removeEmit)
	
        menu.addAction(delete)
        menu.exec(ev.globalPos())
        
    def removeEmit(self):
        self.remove()
        self.deleted.emit()
       
#################################
#
# Container em grid das imagens
#
################################# 
class GImageGrid(QtWidgets.QScrollArea):
	onClick = QtCore.pyqtSignal(int)
	onDownloadFinished = QtCore.pyqtSignal()
	imagesDeleted = QtCore.pyqtSignal(list)
	
	clickable  = 0
	selectable = 1
	
	def __init__(self, imagesDir, mode = clickable, parent = None):
		QtWidgets.QScrollArea.__init__(self, parent)
		self.imgGrid = QtWidgets.QGridLayout()
		self.next_id = 0
		self.raise_id = 1
		self.n_images = 0
		self.dl_index = 0
		self.mode = mode
		self.imagesPerRow = 5

		self.imagesDir = imagesDir
		
		self.onDownloadFinished.connect(self.onImageDownloaded)

		self.ensureImagesDir()
		self.clearImages()
	
	def __del__(self):
		self.clearImages()
	
	def ensureImagesDir(self):
		subprocess.run("mkdir -p %s" % (self.imagesDir), shell=True)
	
	def clearImages(self):
		subprocess.run("rm %s/*" % (self.imagesDir), shell=True)

		
	def loadImages(self):
		names = []
		for filename in os.listdir(self.imagesDir):
			names.append(filename)
		names = natsorted(names)
		
		self.n_images = 0
		self.imgGrid = QtWidgets.QGridLayout()
		for filename in names:
			label = GImageButton("%s/%s" % (self.imagesDir, filename), self.n_images, self)
			label.onClick.connect(self.imageClicked)
			label.deleted.connect(lambda : self.loadImages())
			self.imgGrid.addWidget(label, self.n_images // self.imagesPerRow, self.n_images % self.imagesPerRow)
			#self.next_id  += self.raise_id
			self.n_images += 1
		
		self.raise_id = 0
		#view = QtWidgets.QGroupBox()
		view = QtWidgets.QWidget()
		view.setLayout(self.imgGrid)
		self.setWidget(view)

	def scanForImages(self, path = GDefaultValues.imgDir):
		path += "/"
		for filename in os.listdir(path): 
			dst = GDefaultValues.imgPrefix + str(self.next_id) + ".JPG"
			src = path + filename 
			dst = path + dst 
			os.rename(src, dst) 
			self.next_id += 1

	def imageClicked(self, index):
		self.onClick.emit(index)
		
	def addImagesFromFile(self, files):
		for src in files:
			filename, file_extension = os.path.splitext(src)
			filename = "%s/%s%d%s" % (self.imagesDir, GDefaultValues.imgPrefix, self.next_id, file_extension.upper())
			copyfile(src, filename)
			self.next_id += 1
		
		self.loadImages()
		
	def addImageFromUrl(self, src):
		self.next_id += 1
		threading.Thread(target=self.handle_web_image, args=([src])).start()
	
	def addImageFromPixmap(self, px, file_extension = "JPG"):
		filename = "%s/%s%d.%s" % (self.imagesDir, GDefaultValues.imgPrefix, self.next_id, file_extension.upper())
		if px.save(filename):
			self.next_id += 1
			self.loadImages()
	
	def onImageDownloaded(self):
		self.loadImages()
		self.dl_index += 1
		self.next_id += 1
	
	def handle_web_image(self, src):
		filename, file_extension = os.path.splitext(src)
		cmd = "wget -O %s/%s%d%s %s" % (self.imagesDir, GDefaultValues.imgPrefix, self.next_id, file_extension, src)
		subprocess.run(cmd, shell=True)
		self.onDownloadFinished.emit()
	
	def mode(self):
		return self.mode
	
	def setMode(self, mode):
		self.mode = mode
		visible = self.mode == self.selectable
		for img in self.findChildren(GImageButton):
			img.setSelectionView(visible)
	
	def selectAll(self):
		for img in self.findChildren(GImageButton):
			img.setSelection(True)
			
	def getImageButtonFromIndex(self, index):
		# Se for o index no grid utiliziar:
		# return self.imgGrid.itemAtPosition(index // self.imagesPerRow, index % self.imagesPerRow).widget()
	
		# Se o índice for o nome da imagem:
		for img in self.findChildren(GImageButton):
			if img.getIndex() == index:
				return img
		
		return None
		
	def getSelected(self):
		l = []
		for img in self.findChildren(GImageButton):
			if img.isSelected():
				l.append(img.index)
	
	def onDeleteImage(self, img):
		img.remove()
		self.loadImages()
		
	def removeSelected(self):
		for img in self.findChildren(GImageButton):
			if img.isSelected():
				img.remove()
		self.loadImages()
	
	def clear(self):
		self.next_id  = 0
		self.n_images = 0
		self.raise_id = 1

class GCustomImageDialog(QtWidgets.QDialog):

	NoImage = 5

	def __init__(self, parent = None):
		QtWidgets.QDialog.__init__(self, parent)
		
		self.hide()
		self.setWindowTitle("Posição da imagem")
		self.layout = QtWidgets.QGridLayout()
		self.b0 = QtWidgets.QPushButton("Topo esquerdo")
		self.b1 = QtWidgets.QPushButton("Topo direito")
		self.b2 = QtWidgets.QPushButton("Base esquerda")
		self.b3 = QtWidgets.QPushButton("Base direita")
		
		self.layout.addWidget(self.b0, 0, 0)
		self.layout.addWidget(self.b1, 0, 1)
		self.layout.addWidget(self.b2, 1, 0)
		self.layout.addWidget(self.b3, 1, 1)
		
		self.b0.clicked.connect(lambda : self.done(0))
		self.b1.clicked.connect(lambda : self.done(1))
		self.b2.clicked.connect(lambda : self.done(2))
		self.b3.clicked.connect(lambda : self.done(3))
				
		self.setLayout(self.layout)
	
	def question(self):
		return self.exec()
		
	def reject(self):
		self.done(self.NoImage)
		
class GCustomScreenShotDialog(QtWidgets.QDialog):
	Yes = 1
	No  = 0 
	def __init__(self, pixmap, parent = None):
		QtWidgets.QDialog.__init__(self, parent)
		
		self.hide()
		
		self.setWindowTitle("Imagem capturada")
		
		self.b0 = QtWidgets.QPushButton("Cancelar", self)
		self.b1 = QtWidgets.QPushButton("Salvar", self)
		
		self.b0.clicked.connect(lambda : self.done(self.No))
		self.b1.clicked.connect(lambda : self.done(self.Yes))
		
		self.screenshotLabel = QtWidgets.QLabel(self)
		self.screenshotLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding);
		self.screenshotLabel.setAlignment(QtCore.Qt.AlignCenter);

		self.screenshotLabel.setPixmap(pixmap)
	
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.screenshotLabel)
		
		self.buttonsLayout = QtWidgets.QHBoxLayout()
		self.buttonsLayout.addWidget(self.b0)
		self.buttonsLayout.addWidget(self.b1)
		
		self.layout.addLayout(self.buttonsLayout)
		
		self.setLayout(self.layout)
	
	def question(self):
		return self.exec()
