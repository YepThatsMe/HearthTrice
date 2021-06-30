from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QAction, QStackedWidget, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from configparser import ConfigParser
import sys, os

from Arena import Arena
from CardImport import CardImport
from DeckEditor import DeckEditor


class HearthTrice_Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('assets/icons/icon.ico'))
        self.setWindowTitle('HearthTrice Manager')

        self.win1 = DeckEditor()
        self.win2 = Arena()
        self.win3 = CardImport()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.win1)
        self.stack.addWidget(self.win2)
        self.stack.addWidget(self.win3)


        # ToolBar

        tb_openLibrary = QAction(QIcon("assets/icons/file.jpg"), "&Open library...", self)
        tb_openLibrary.setShortcut("Ctrl+O")
        tb_openLibrary.setStatusTip("Open card's library")
        tb_openLibrary.triggered.connect(self.open_Library) 

        tb_arena = QAction(QIcon("assets/icons/Jiraiya.jpg"), "&Arena", self)
        tb_arena.setShortcut("Ctrl+2")
        tb_arena.setStatusTip("Open Arena")
        tb_arena.triggered.connect(self.switch_Arena)

        tb_deckEditor = QAction(QIcon("assets/icons/icon.jpg"), "&Editor", self)
        tb_deckEditor.setShortcut("Ctrl+1")
        tb_deckEditor.setStatusTip("Open Deck Editor")
        tb_deckEditor.triggered.connect(self.switch_DeckEditor)

        tb_cardImport = QAction(QIcon("assets/icons/error2.png"), "&Import", self)
        tb_cardImport.setStatusTip("Open Card Import")
        tb_cardImport.setShortcut("Ctrl+3")
        tb_cardImport.triggered.connect(self.switch_CardImport)
        

        self.toolbar = self.addToolBar('')
        self.toolbar.addAction(tb_openLibrary)
        self.toolbar.addAction(tb_arena)
        self.toolbar.addAction(tb_deckEditor)
        self.toolbar.addAction(tb_cardImport)
        self.toolbar.setIconSize(QSize(150,35))
        self.toolbar.setMovable(0)


        self.centralwidget = QWidget()
        self.setCentralWidget(self.stack)

        self.switch_DeckEditor()


        # Создать файл настроек
        self.config = ConfigParser()
        self.config_path = 'assets/config.ini'
        self.LIB_PATH = ''

        try:
            self.config.read(self.config_path)
            self.LIB_PATH = self.config.get('GENERAL', 'LIB_PATH')
        except Exception as e:
            print(e)
            print('Creating config.ini file...')
            self.config.read(self.config_path)
            self.config.add_section('GENERAL')
            self.config.set('GENERAL', 'LIB_PATH', '')
            with open(self.config_path, 'w') as cfg:
                self.config.write(cfg)



    def open_Library(self):

        path = QFileDialog.getOpenFileName(self, 'Open XML library...')[0]
        if path == '' or not path:
            return

        self.update_config('GENERAL', 'LIB_PATH', path)
        print(f'config update: LIB_PATH={path}')

    def switch_DeckEditor(self):
        self.stack.setCurrentWidget(self.win1)

    def switch_Arena(self):
        self.stack.setCurrentWidget(self.win2)

    def switch_CardImport(self):
        self.stack.setCurrentWidget(self.win3)

    def update_config(self, section, var, value):
        self.config.read(self.config_path)
        self.config.set(section, var, value)
        with open(self.config_path, 'w') as cfg:
            self.config.write(cfg)

if __name__ == '__main__':

    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = HearthTrice_Main()  # Создаем объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()