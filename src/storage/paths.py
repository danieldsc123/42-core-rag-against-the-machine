"""Definir nomes de saída em diretórios configuráveis por escopo."""
from pathlib import Path


def dataset_output_path(input_path: Path, save_directory: Path) -> Path:
    """Manter o nome do JSON de entrada no diretório de saída escolhido."""
    if input_path.suffix.lower() != '.json':
        raise ValueError('dataset input must have a .json extension')
    return save_directory / input_path.name
