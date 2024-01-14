from enum import IntEnum, auto
import json

class ClassType(IntEnum):
    NEUTRAL: int = auto()
    MAGE: int = auto()
    HUNTER: int = auto()
    PALADIN: int = auto()
    WARRIOR: int = auto()
    DRUID: int = auto()
    ROGUE: int = auto()
    PRIEST: int = auto()
    WARLOCK: int = auto()
    SHAMAN: int = auto()
    DEMONHUNTER: int = auto()

class Rarity(IntEnum):
    NONE: int = auto()
    COMMON: int = auto()
    RARE: int = auto()
    EPIC: int = auto()
    LEGENDARY: int = auto()

class CardType(IntEnum):
    MINION: int = auto()
    SPELL: int = auto()

class CardMetadata:
    id: int
    name: str
    description: str
    manacost: int
    rarity: Rarity
    cardtype: CardType
    classtype: ClassType
    attack: int
    health: int
    tribe: str

    comment: str
    picture: bytes
    move_x: int    
    move_y: int
    zoom: int

    card_image: bytes

    def __init__(self, json_meta: dict = None) -> None:
        if not json_meta:
            return
        self.__dict__ = json_meta
        
    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)
    
    def all(self) -> dict:
        return self.__dict__

    def update(self, data: dict) -> None:
        self.__dict__.update(data)

    def pop(self, key: str) -> str:
        return self.__dict__.pop(key)

    def __getitem__(self, key: str):
        return self.__dict__.get(key)
    
    def __getattr__(self, __name: str):
        return self.__getitem__(__name)

class A:
    def __init__(self, library) -> None:
        self.library = library

class Main:
    def __init__(self) -> None:
        self.lib = {}

        self.A = A(self.lib)

        print(self.A.library)

        self.lib.clear()
        self.lib.update({"1":1})

        print(self.lib)
        print(self.A.library)