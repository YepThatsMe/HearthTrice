from typing import List
from PyQt5.QtCore import QObject
import io
import json
import hashlib

from Widgets.Communication import Communication
from Widgets.components.BytesEncoder import BytesEncoder, base64_to_bytes, hash_library
from Widgets.components.DataTypes import CardMetadata, Deck, DeckCard, Response


class DataPresenter(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.login = ""
        self.password = ""
        self.comm = Communication()

    # def set_connection(self, server: str, login: str, password: str):
    #     self.comm.set_connection(server, login, password)

    def get_library(self) -> List[CardMetadata]:
        if not self.comm.is_connected:
            print("Connection is not established")
            return 
        card_raw_data = self.comm.fetch_all_cards()
        if not card_raw_data:
            print("Fetch error: empty list")
            return
        library = []
        for params_list in card_raw_data:
            meta = CardMetadata()
            meta.id = params_list[0]
            meta.name = params_list[1]
            meta.description = params_list[2]
            meta.manacost = params_list[3]
            meta.rarity = params_list[4]
            meta.cardtype = params_list[5]
            meta.classtype = params_list[6]
            meta.attack = params_list[7]
            meta.health = params_list[8]
            meta.tribe = params_list[9]
            meta.comment = params_list[10]
            meta.picture = params_list[11]
            meta.move_x = params_list[12]
            meta.move_y = params_list[13]
            meta.zoom = params_list[14]
            meta.card_image = params_list[15]
            library.append(meta)
        return library
    
    def get_decks(self) -> List[Deck]:
        if not self.comm.is_connected:
            print("Connection is not established")
            return
        deck_raw_data = self.comm.fetch_all_decks()
        if not deck_raw_data:
            print("Fetch error: empty list")
            return
        decks = []
        for row in deck_raw_data:
            deck = Deck()
            deck.id = row[0]
            deck.name = row[1]

            cards = self.str_to_cards(row[2])
            if not cards:
                print("Error parsing card data")
                return
            
            deck.cards = cards
            deck.owner = row[3]
            decks.append(deck)
        return decks
    
    def str_to_cards(self, cards_data: str) -> List[DeckCard]:
        # format: "4,1,0;25,1,0;14,1,0;15,1,0;"
        try:
            if cards_data[-1] == ';':
                cards_data = cards_data[:-1]

            card_data = cards_data.split(';')
            cards = []
            for i in card_data:
                card = DeckCard()
                card_meta = i.split(',')            
                card.id = int(card_meta[0])
                card.count = int(card_meta[1])
                card.side = int(card_meta[2])
                cards.append(card)
            return cards
        except Exception as e:
            print(e)
            return None

    def upload_card(self, metadata: CardMetadata) -> Response:
        return self.comm.upload_card(metadata)

    def upload_edit_card(self, metadata: CardMetadata) -> Response:
        return self.comm.upload_edit_card(metadata)
        

    def delete_card(self, metadata: CardMetadata) -> Response:
        return self.comm.delete_card(metadata)








    # def post_library(self, library: dict, backup=True):

    #     library_json = json.dumps(library, indent=2, cls=BytesEncoder)
    #     lib_hash = hash_library(library_json)

    #     buffer = io.BytesIO()
    #     buffer.write(library_json.encode('utf-8'))

    #     if backup:
    #         self.comm.back_up_file(self.LIBRARY_FILE_ID)

    #     new_name = "library-" + lib_hash + "-.json"
    #     self.comm.update_file(self.LIBRARY_FILE_ID, buffer, new_name=new_name)

    #     buffer.close()


    # def get_library(self) -> dict:
    #     """
    #     Returns a library with images in base64.
    #     """
    #     file = self.comm.download_file(self.LIBRARY_FILE_ID).decode('utf-8')
    #     return json.loads(file)
    
    # def get_library_decoded(self) -> dict:
    #     """
    #     Returns a library with images in binary.
    #     """
    #     library = self.get_library()
    #     for k, v in library.items():
    #         if "picture" in v:
    #             v["picture"] = base64_to_bytes(v["picture"])
    #         if "card_image" in v:
    #             v["card_image"] = base64_to_bytes(v["card_image"])

    #     return library

    # def find_library_id(self) -> dict:
    #     files = self.comm.list_files()
    #     for k, v in files.items():
    #         if 'library' in v['name']:
    #             return k
