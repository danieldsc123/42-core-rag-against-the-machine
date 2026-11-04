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
    """Dispatch commands and report failures without unhandled tracebacks."""
    cli = RagCLI()
    commands = {
        'index': cli.index, 'search': cli.search,
        'search_dataset': cli.search_dataset, 'answer': cli.answer,
        'answer_dataset': cli.answer_dataset, 'evaluate': cli.evaluate,
        'status': status,
    }
    try:
        fire.Fire(commands)
    except KeyboardInterrupt:
        print('Interrupted.', file=sys.stderr)
        raise SystemExit(130) from None
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
