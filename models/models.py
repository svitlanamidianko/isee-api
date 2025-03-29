from dataclasses import dataclass
import uuid


@dataclass
class Media:
    id: str = str(uuid.uuid4())
    media_name: str = ""
    media_path: str = ""
    text: str = ""
    linkie: str = ""
    order: int = 0  # Position in the sequence, default to 0


@dataclass
class Entry:
    media_id: str               
    entry_text: str = ""
    id: str = str(uuid.uuid4())
