import json
import os
import sys
import threading
import time
import zipfile

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from Zipper import Ui_MainWindow


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(690, 420)
        self.setWindowTitle("Z-Zipper")
        self.setWindowIcon(QtGui.QIcon('zip-icon.ico'))
        self.show()
        self.ui.button_zip.pressed.connect(self.pick_file)
        self.ui.button_output.pressed.connect(self.pick_folder)
        self.ui.button_archive.pressed.connect(self.zip_thread)
        self.names = self.ui.edit_filename.setText("MyZip")
        self.levels = ['Store', 'Fastest', 'Fast', 'Normal', 'Normal++', 'Medium', 'Maximum', 'Ultra',
                       'Ultra++']  # Set ComboBox values for zip compression levels
        self.ui.comp_levelbox.addItems(self.levels)
        self.methods = ['No Compression', 'Zip Deflated - (Normal)', 'Zip BZIP2 - (Medium)',
                        'Zip LZMA - (Ultra)']  # Set ComboBox values for zip compression methods
        self.ui.comp_methodbox.addItems(self.methods)
        self.ui.comp_methodbox.activated.connect(self.NoComp)
        self.ui.comp_levelbox.setHidden(True)  # Hide compression Levels
        self.ui.label_5.setHidden(True)
        self.ui.progbrar.setHidden(True)
        self.isLoading = False
        with open('config.json') as file:  # Retrive Last used paths
            config = json.load(file)
            print(config)
            self.lastsourcepath = config["LastSourcePath"]
            self.lastoutputpath = config["LastOutputPath"]
            if self.lastsourcepath != "":
                self.ui.edit_zip.setText(self.lastsourcepath)
            if self.lastoutputpath != "":
                self.ui.edit_output.setText(self.lastoutputpath)

    def NoComp(self):  # No Compression Selection
        if self.ui.comp_methodbox.currentText() == 'No Compression':
            self.ui.comp_levelbox.setHidden(True)
            self.ui.label_5.setHidden(True)
        else:
            self.ui.comp_levelbox.setHidden(False)
            self.ui.label_5.setHidden(False)

    def pick_file(self):  # Pick Source Folder
        self.filename = QFileDialog.getExistingDirectory(self, "Select Directory", self.ui.edit_zip.text())
        if self.filename == "":
            pass
        else:
            self.ui.edit_zip.setText(self.filename)
            self.ZipName0 = self.filename.rsplit("/")
            self.ZipName = self.ZipName0[len(self.ZipName0) - 1]
            self.names = self.ui.edit_filename.setText(self.ZipName)

    def pick_folder(self):  # Pick Destination Folder
        self.folname = QFileDialog.getExistingDirectory(self, "Select Directory", self.ui.edit_output.text())
        if self.folname == "":
            pass
        else:
            self.ui.edit_output.setText(self.folname)

    def zip_thread(self):  # Start Archive Thread
        za = threading.Thread(target=self.zip_archive)
        za.start()

    def zip_archive(self):
        self.ui.progbrar.setHidden(False)
        self.isLoading = True  # Progress bar loading True
        threading.Thread(target=self.addProg).start()  # Start Progressbar
        self.ZipName = self.ui.edit_filename.text()  # Get Zip file Name
        self.archivePath = self.ui.edit_output.text() + "/" + self.ZipName + ".zip"  # Create New Zip file path
        with zipfile.ZipFile(self.archivePath, 'w', compression=self.getCompMethod(), compresslevel=self.getComLevel(),
                             allowZip64=True) as zips:  # set up zipfile <get compresion method and level>
            self.sourcePath = self.ui.edit_zip.text()
            self.archiveFiles = os.listdir(self.sourcePath)  # create list of files in source path
            for names in self.archiveFiles:  # enumerate through all files and add to archive
                if os.path.isdir(self.sourcePath + "/" + names):  # if contains directory make list of files inside
                    self.subfolderItems = os.listdir(self.sourcePath + "/" + names)
                    for eachitems in self.subfolderItems:  # enumerate through all files in subfolder and add to archive
                        if os.path.isdir(
                                self.sourcePath + "/" + names + "/" + eachitems):  # if subfolder contains folders get list of files
                            for sndeachitem in self.filenamesList:
                                zips.write(
                                    self.sourcePath + "/" + names + "/" + eachitems + "/" + sndeachitem)  # enumerate through all files in subfolders folder and add to archive
                        else:  # add the files if not folder
                            zips.write(self.sourcePath + "/" + names + "/" + eachitems)
                else:
                    zips.write(self.sourcePath + "/" + names)  # add the files if not folder
        self.isLoading = False
        self.ui.progbrar.setValue(100)
        time.sleep(0.2)
        self.ui.progbrar.setHidden(True)
        self.TempPathData1 = {"LastSourcePath": self.filename,  # Save LastSourcePath
                              "LastOutputPath": self.folname}  # Save LastOutPath
        with open('config.json', 'w', encoding='utf-8') as files:
            json.dump(self.TempPathData1, files, ensure_ascii=False)

    def checkfolder(self, path):  # check if Folder & Send list of files
        if os.path.isdir(path):
            self.pathStuff = os.listdir(path)
            return self.pathStuff

    def getComLevel(self):
        self.currText = self.ui.comp_levelbox.currentText()
        if self.currText == "Store":
            return 1
        elif self.currText == "Fastest":
            return 2
        elif self.currText == "Fast":
            return 3
        elif self.currText == "Normal":
            return 4
        elif self.currText == "Normal++":
            return 5
        elif self.currText == "Medium":
            return 6
        elif self.currText == "Maximum":
            return 7
        elif self.currText == "Ultra":
            return 8
        elif self.currText == "Ultra++":
            return 9

    def getCompMethod(self):
        self.currTextM = self.ui.comp_methodbox.currentText()
        if self.currTextM == 'No Compression':
            return zipfile.ZIP_STORED
        elif self.currTextM == 'Zip Deflated - (Normal)':
            return zipfile.ZIP_DEFLATED
        elif self.currTextM == 'Zip BZIP2 - (Medium)':
            return zipfile.ZIP_BZIP2
        elif self.currTextM == 'Zip LZMA - (Ultra)':
            return zipfile.ZIP_LZMA

    def addProg(self):
        self.pValue = self.ui.progbrar.value()
        self.stV = 0
        while self.stV <= 100:
            if self.isLoading == False:
                break
            self.ui.progbrar.setValue(self.stV)
            self.stV = self.stV + 1
            time.sleep(0.4)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
