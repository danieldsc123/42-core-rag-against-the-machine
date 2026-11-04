"""Modelo de localização das fontes no texto original."""
from pathlib import PurePosixPath
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator


class MinimalSource(BaseModel):
    """Localização no texto original; caminho relativo à raiz do projeto."""
    file_path: str
    first_character_index: int = Field(ge=0, strict=True)
    last_character_index: int = Field(gt=0, strict=True)

    @model_validator(mode="after")
    def validate_location(self) -> Self:
        """Exigir caminho POSIX relativo e intervalo semiaberto não vazio."""
        path = PurePosixPath(self.file_path)
        if (not self.file_path or path.is_absolute()
                or ".." in path.parts or "\\" in self.file_path
                or ":" in self.file_path or str(path) == "."):
            raise ValueError("file_path must be a relative POSIX file path")
        if self.last_character_index <= self.first_character_index:
            raise ValueError(
                "last_character_index must exceed first_character_index"
            )
        return self
