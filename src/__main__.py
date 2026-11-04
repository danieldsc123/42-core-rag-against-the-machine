"""Expose the local RAG CLI with concise, nonzero-exit error reporting."""
import sys

import fire

from src.cli.commands import RagCLI


def status() -> str:
    """Report which project components are currently implemented."""
    return (
        "Ready: index, search, search_dataset, answer, answer_dataset, "
        "evaluate. Generation uses local Qwen/Qwen3-0.6B; "
        "first use downloads model weights."
    )


def main() -> None:
    """Run available commands; pipeline commands are not implemented yet."""
    fire.Fire({"status": status})


if __name__ == "__main__":
    main()
