from typing import List, Tuple
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QLineEdit, QLabel, QDialog, QHBoxLayout, QVBoxLayout, QWidget, QApplication, QAction, QStackedWidget, QTabWidget, QSizePolicy, QTabBar
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import QSize

import resources
import resources_std
from Widgets.Arena import Arena
from Widgets.LibraryView import LibraryView
from utils.Thread import Thread, send_to_thread
from DataPresenter import DataPresenter
from Widgets.CardBuilderView import CardBuilderView

from DataTypes import CardMetadata, Deck, Response
from Widgets.components.ConnectionSettings import ConnectionSettingsDialog

class MainMediator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':icons/icon.ico'))
        self.setWindowTitle('HearthTrice Manager')

        self.data_presenter = DataPresenter()

        self.bool = True
        
        self.set_up_ui()
        self.set_up_connections()

    def set_up_connections(self):
        self.card_builder_view.upload_requested.connect(self.upload_card)
            #lambda n: send_to_thread(self, self.upload_card, args=(n,), kwargs=()))
        self.card_builder_view.upload_edit_requested.connect(self.upload_edit_card)

        self.library_view.create_new_deck_requested.connect(
            lambda name: send_to_thread(self, self.data_presenter.create_new_deck, self.on_deck_created, args=(name,)))
        self.library_view.update_deck_requested.connect(
            lambda deckdata: send_to_thread(self, self.data_presenter.update_deck, self.on_deck_updated, args=(deckdata[0],deckdata[1],)))
        self.library_view.get_decks_requsted.connect(
            lambda: send_to_thread(self, self.data_presenter.get_decks, self.update_decks))
        self.library_view.update_library_requested.connect(
            lambda: send_to_thread(self, self.data_presenter.get_library, self.update_library))
        self.library_view.edit_card_requested.connect(self.on_edit_card_requested)
        self.library_view.delete_card_requested.connect(self.on_delete_card_requested)

        self.connection_settings.settings_button.button.clicked.connect(self.on_settings_clicked)
        self.connection_settings.connection_response_received.connect(self.library_view.update)

    def set_up_ui(self):
        self.connection_settings = ConnectionSettingsDialog(self.data_presenter, self)

        self.card_builder_view = CardBuilderView(self)
        self.library_view = LibraryView(self)
        self.arena_view = Arena()

        self.central_widget = QWidget(self)
        self.gen_layout = QVBoxLayout()
        self.layout_inlay1 = QHBoxLayout()
        self.connection_settings.settings_button.setParent(self)


        self.tab_bar = QTabBar(self)
        self.stacked_widget = QStackedWidget(self)
        self.tab_bar.currentChanged.connect(self.stacked_widget.setCurrentIndex)
        
        self.tab_bar.addTab("Редактор карт")
        self.stacked_widget.addWidget(self.card_builder_view)
        self.tab_bar.addTab("Библиотека")
        self.stacked_widget.addWidget(self.library_view)
        self.tab_bar.addTab("Арена")
        self.stacked_widget.addWidget(self.arena_view)

        self.stacked_widget.setCurrentIndex(0)        

        self.layout_inlay1.addWidget(self.tab_bar)
        self.layout_inlay1.addWidget(self.connection_settings.settings_button)
        self.gen_layout.addLayout(self.layout_inlay1)
        self.gen_layout.addWidget(self.stacked_widget)

        self.central_widget.setLayout(self.gen_layout)
        self.setCentralWidget(self.central_widget)

    def on_deck_created(self, new_deck_data: tuple):
        if not new_deck_data:
            return
        self.library_view.deck_view.on_new_deck_data_received(new_deck_data)

    def on_deck_updated(self, response: Response):
        if response.ok:
            QMessageBox.information(None, "Сохранено", "Колода успешно обновлена.")
        else:
            QMessageBox.warning(None, "Ошибка", "Не удалось обновить колоду: " + response.msg)


    def on_settings_clicked(self):
        self.connection_settings.show()

    def update_decks(self, decks: List[Deck]):
        if not decks:
            return
        self.library_view.set_updated_decks(decks)

    def update_library(self, cards: List[CardMetadata]):
        if not cards:
            return
        self.library_view.set_updated_library(cards)

    def upload_card(self, metadata: CardMetadata):
        response = self.data_presenter.upload_card(metadata)
        if response.ok:
            self.library_view.update()
            QMessageBox.information(None, "Информация", "Карта загружена в библиотеку.")
        else:
            QMessageBox.warning(None, "Предупреждение", response.msg)


    def upload_edit_card(self, metadata: CardMetadata):
        response = self.data_presenter.upload_edit_card(metadata)
        if response.ok:
            self.library_view.update()
            QMessageBox.information(None, "Информация", "Карта изменена.")
        else:
            QMessageBox.warning(None, "Предупреждение", response.msg)

    def on_edit_card_requested(self, metadata: CardMetadata):
        self.card_builder_view.on_edit_card_requested(metadata)
        self.stacked_widget.setCurrentIndex(0)
        self.tab_bar.setCurrentIndex(0)

    def on_delete_card_requested(self, metadata: CardMetadata):
        response = self.data_presenter.delete_card(metadata)
        if response.ok:
            self.library_view.update()
            QMessageBox.information(None, "Информация", "Карта удалена.")
        else:
            QMessageBox.warning(None, "Предупреждение", response.msg)

    # def f(self, c=None, d='r'):
    #     print(c,d)
    #     return requests.get('http://example.com').text

    # def handle_reply2(self, data):
    #     print(data)

    def resizeEvent(self, a0) -> None:
        tab_width = str( (self.width() / self.tab_bar.count()) - 45)
        self.tab_bar.setStyleSheet("QTabBar::tab {min-width: " + tab_width + "px; min-height: 50px; font-family: Arial; font-weight: bold; font-size: 16pt}")
        if self.width() > 1500 and self.bool:
            self.bool = False
            
            #self.send_to_thread(self.data_presenter.get_library_decoded, self.update_library)

        return super().resizeEvent(a0)