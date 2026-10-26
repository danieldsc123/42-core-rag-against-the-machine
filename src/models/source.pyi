"""Prototipos de models.source; sem implementacao."""
from pydantic import BaseModel

class MinimalSource(BaseModel):
    """Localizacao no texto original; caminho relativo a raiz do projeto."""
    file_path: str
    first_character_index: int
    last_character_index: int
