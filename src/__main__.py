"""Expose the implemented project status through Python Fire."""
import fire


def status() -> str:
    """Report which project components are currently implemented."""
    return (
        "Implemented: validated data models, document reader and setup. "
        "Pending: file discovery, chunking, index, retrieval, generation "
        "and evaluation."
    )


def main() -> None:
    """Run available commands; pipeline commands are not implemented yet."""
    fire.Fire({"status": status})


if __name__ == "__main__":
    main()
