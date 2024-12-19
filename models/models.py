from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import uuid

@dataclass
class User:
    """Base user class - referenced by most other models"""
    id: str = str(uuid.uuid4())
    name: str = ""
    email: str = ""
    created_at: datetime = datetime.now()
    # Referenced by:
    # - Deck.created_by
    # - Game.hive_host_id
    # - Entry.user_id
    # - SoloPostcard.user_id

@dataclass
class Deck:
    """Deck of cards - owned by a user, contains many cards through DeckCard"""
    id: str = str(uuid.uuid4())
    name: str = ""
    desc: str = ""
    created_at: datetime = datetime.now()
    created_by: str = ""  # Foreign key -> User.id
    # Referenced by:
    # - Game.deck_id
    # - DeckCard.deck_id

@dataclass
class Card:
    """Individual card - can belong to multiple decks through DeckCard"""
    id: str = str(uuid.uuid4())
    image_path: str = ""
    # Referenced by:
    # - Entry.card_id
    # - DeckCard.card_id

@dataclass
class Game:
    """Game session - has one host, one deck, many entries and postcards"""
    id: str = str(uuid.uuid4())
    hive_name: str = ""
    hive_invitation_msg: str = ""
    hive_host_id: str = ""      # Foreign key -> User.id
    collective_postcard: Optional[str] = None  # URL
    deck_id: str = ""           # Foreign key -> Deck.id
    prompt: str = ""
    created_at: datetime = datetime.now()
    # Referenced by:
    # - Entry.game_id
    # - SoloPostcard.game_id

@dataclass
class Entry:
    """Player entry in a game - connects user, game, and chosen card"""
    user_id: str               # Foreign key -> User.id
    game_id: str               # Foreign key -> Game.id
    card_id: str               # Foreign key -> Card.id
    entry_text: str = ""
    created_at: datetime = datetime.now()
    id: str = str(uuid.uuid4())

@dataclass
class DeckCard:
    """Junction table between Deck and Card (many-to-many)"""
    deck_id: str               # Foreign key -> Deck.id
    card_id: str               # Foreign key -> Card.id

@dataclass
class SoloPostcard:
    """Individual player's postcard in a game"""
    user_id: str               # Foreign key -> User.id
    game_id: str               # Foreign key -> Game.id
    id: str = str(uuid.uuid4())
    individual_postcard: Optional[str] = None  # URL