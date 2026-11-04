*This project has been created as part of the 42 curriculum by <login1>.*

# RAG against the machine

## Description

A planned local retrieval-augmented generation system for the supplied vLLM
0.10.1 corpus. It will index source files, retrieve relevant character spans,
and generate grounded answers with Qwen/Qwen3-0.6B.

**Current status: development setup, validated data models and document reader implemented.**
The RAG pipeline remains an interface prototype; retrieval and generation do not
run yet, and no retrieval score has been measured.
Replace the login placeholder before submission.

## Instructions

Read [the project review and next steps](docs/REVISAO.md) (in Portuguese).
All planned modules are now `.py` files. Models and the document reader are
implemented; pending services contain typed prototypes that raise
`NotImplementedError`. See [the architecture and implementation order](docs/ARQUITETURA.md).
`src/ingestion/reader.py` reads UTF-8 without changing line endings, validates
that paths are within the project root and identifies Python/text documents.

Install Python 3.10+ and uv, then run:

```sh
make install
make run ARGS=status
make test
make lint
```

`uv sync` installs the locked dependencies directly. `make debug ARGS=status`
starts the available CLI in pdb. `make clean` removes Python and tooling caches.
On restricted filesystems, use `UV_CACHE_DIR=.uv-cache uv sync`.
The CLI currently exposes only `status`; pipeline commands are pending.
The supplied vLLM corpus is extracted to `data/raw/vllm-0.10.1/` and the
public datasets to `data/datasets/{AnsweredQuestions,UnansweredQuestions}/`.
They contain 99 code and 100 documentation questions per scope. Local data is
excluded from Git; a fresh clone must be populated from the supplied archives.
The two standalone official evaluator binaries are in `tools/moulinette/`,
also excluded from Git. They are separate from the application and have not
been executed. See [the review](docs/REVISAO.md) for validation details.
Model runtime dependencies will be selected when generation is implemented.

## System architecture

Corpus reading -> Python/text chunking -> lexical index -> top-k retrieval ->
context preparation -> local answer generation. Evaluation is a separate consumer
of search results and reference answers. Each functionality has its own folder under `src/`: `models`, `ingestion`,
`chunking`, `indexing`, `retrieval`, `generation`, `storage`, `evaluation` and
`cli`. See the roadmap for the complete folder tree and file contracts.

## Chunking strategy

Implemented for text: paragraph boundaries, ATX/Setext Markdown headings and
fenced code blocks, with subdivision of oversized spans. Original character
offsets are preserved and chunks are limited to at most 2000 characters.
Python syntax chunking remains pending.

## Retrieval method

Proposed baseline: TF-IDF with a sparse representation, shared tokenization for
queries and documents, and deterministic ranking. This is not implemented yet.

## Performance analysis

Model validation tests pass; full-corpus performance is not measured. Required targets: indexing within 5 minutes, retrieval of
200 questions within 90 seconds, Recall@5 >= 80% for docs and >= 50% for code.

## Design decisions

Separate public Pydantic schemas, file I/O, lexical retrieval, generation and CLI.
Keep model loading out of search-only commands. Reference answers are reserved
for evaluation and must not be used as retrieval content.

## Challenges faced

Initial validation addressed malformed reference answers being discarded by union
fallback, duplicate question IDs, invalid spans, and generation token budgets.
Remaining challenges include exact corpus paths,
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
The continuation added dependency setup, validated Pydantic models, a status CLI,
and validation tests with AI assistance. The document reader was implemented
through guided development and reviewed with AI assistance. Retrieval and generation algorithms have
not been implemented.
