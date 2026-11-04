"""Dataset output naming within configurable scope directories."""
from pathlib import Path


def dataset_output_path(input_path: Path, save_directory: Path) -> Path:
    """Keep the input JSON filename inside the chosen output directory."""
    if input_path.suffix.lower() != '.json':
        raise ValueError('dataset input must have a .json extension')
    return save_directory / input_path.name
