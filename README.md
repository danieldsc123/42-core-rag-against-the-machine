*This project has been created as part of the 42 curriculum by <login1>.*

# RAG against the machine

## Description

A planned local retrieval-augmented generation system for the supplied vLLM
0.10.1 corpus. It will index source files, retrieve relevant character spans,
and generate grounded answers with Qwen/Qwen3-0.6B.

**Current status: architecture and interface prototypes only.** There is no
working pipeline, CLI, dependency setup, or measured retrieval score yet.
Replace the login placeholder before submission.

## Instructions

Start with [the architecture and implementation roadmap](docs/ARQUITETURA.md)
(in Portuguese). The files under `src/` are `.pyi` interface declarations, not
implementations. Write the corresponding `.py` modules as you learn each stage.

Dependency installation through `uv sync` and commands through
`uv run python -m src <command>` will become available after project setup and
implementation. The required configuration, lockfile and Makefile remain to be
created. The supplied ZIP archives have not been extracted.

## System architecture

Corpus reading -> Python/text chunking -> lexical index -> top-k retrieval ->
context preparation -> local answer generation. Evaluation is a separate consumer
of search results and reference answers. Each functionality has its own folder under `src/`: `models`, `ingestion`,
`chunking`, `indexing`, `retrieval`, `generation`, `storage`, `evaluation` and
`cli`. See the roadmap for the complete folder tree and file contracts.

## Chunking strategy

Planned: use Python syntax boundaries for code and headings/paragraphs for text,
with subdivision of oversized spans. Preserve original character offsets and
limit every returned source to at most 2000 characters.

## Retrieval method

Proposed baseline: TF-IDF with a sparse representation, shared tokenization for
queries and documents, and deterministic ranking. This is not implemented yet.

## Performance analysis

No measurements yet. Required targets: indexing within 5 minutes, retrieval of
200 questions within 90 seconds, Recall@5 >= 80% for docs and >= 50% for code.

## Design decisions

Separate public Pydantic schemas, file I/O, lexical retrieval, generation and CLI.
Keep model loading out of search-only commands. Reference answers are reserved
for evaluation and must not be used as retrieval content.

## Challenges faced

Implementation has not started. Anticipated challenges include exact corpus paths,
Unicode character offsets, distinct chunking strategies and model token budgets.
Record actual difficulties and solutions during development.

## Example usage

Planned commands include `index`, `search`, `search_dataset`, `answer`,
`answer_dataset` and `evaluate`. They are not executable yet; see the roadmap for
arguments and expected outputs.

## Resources

- Supplied RAG subject, version 2.0: requirements and evaluation contracts.
- Supplied evaluator README: external evaluation formats and usage.
- Supplied public question datasets and vLLM 0.10.1 corpus archive.
- Add the documentation and articles actually used during implementation here.

AI assistance was used to inspect the supplied requirements, propose the module
architecture, write this planning documentation and declare interface prototypes.
No algorithm implementations were generated in this scaffolding step.
