*This project has been created as part of the 42 curriculum by danda-si.*

# RAG against the machine

## Description

A local retrieval-augmented generation system for the supplied vLLM 0.10.1
repository. It indexes source files, retrieves exact character spans, answers
questions with Qwen/Qwen3-0.6B and evaluates retrieval with recall@k.
All six mandatory commands are implemented. Public retrieval targets have been
verified with the supplied official evaluator. Generation has been exercised
with the real Qwen model on CPU; answer quality still needs human review.

## Instructions

Requirements: Python 3.10+, uv, and enough disk/RAM for PyTorch and Qwen weights.
The lockfile installs a CPU build of PyTorch. No vLLM server or GPU is required.
The indexed vLLM repository is input data; do not install or execute it.

```sh
uv sync
make test
make lint
uv run python -m src status
```

`make install` runs `uv sync`; `make run ARGS='search "What is LoRA?" --k 5'`
executes the CLI. `make debug ARGS=status` uses pdb. `make clean` removes Python
and tooling caches without deleting data or model weights. The Makefile uses
a local uv cache; for direct commands in a restricted environment, set
`UV_CACHE_DIR=.uv-cache`.

Populate the following directories from the supplied archives:

```text
data/raw/vllm-0.10.1/                       # vllm-0.10.1.zip contents
data/datasets/AnsweredQuestions/            # datasets_public/public/ contents
data/datasets/UnansweredQuestions/
data/processed/                            # created by index
data/output/search_results/<DatasetScope>/
data/output/search_results_and_answer/<DatasetScope>/
tools/moulinette/                           # standalone evaluator binaries
```

The corpus ZIP must not introduce a duplicated `vllm-0.10.1` directory. The
public datasets contain 99 code and 100 documentation questions per scope,
with matching IDs between answered and unanswered versions. These files,
indexes, output and evaluator binaries are excluded from Git; a fresh clone
needs the archives again.

The first nonempty generation request downloads `Qwen/Qwen3-0.6B` from Hugging
Face (roughly 1.2 GB of weights). Use `HF_HOME` to choose a writable model cache;
after downloading, `HF_HUB_OFFLINE=1` enables cached-only use. CPU generation
uses four threads by default; override with `RAG_TORCH_THREADS` if needed.

## Example usage

Run from the repository root. All dataset, index, source-root and output paths
are configurable; defaults follow the required evaluation layout.

```sh
uv run python -m src index --max_chunk_size 2000
uv run python -m src search "What HTTP endpoint loads a LoRA adapter?" --k 5
uv run python -m src search_dataset \
  --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 --save_directory data/output/search_results/UnansweredQuestions
uv run python -m src evaluate \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
uv run python -m src answer "What HTTP endpoint loads a LoRA adapter?" --k 5
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory data/output/search_results_and_answer/UnansweredQuestions
```

Repeat dataset search with `dataset_code_public.json` for code. Use a separate
`--save_directory` when searching `AnsweredQuestions`, because both scopes
share filenames. `--max_new_tokens`, `--context_window_tokens`, `--model_name`
and `--device` configure generation. `index --method tfidf` selects the other
implemented lexical method; the default is BM25. Rebuild after changing
chunk size, tokenization, retrieval method or corpus contents.

The official evaluator is run separately, never imported or called by the app:

```sh
./tools/moulinette/moulinette-ubuntu evaluate_student_search_results \
  data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  data/datasets/AnsweredQuestions/dataset_docs_public.json \
  --k 10 --max_context_length 2000
```

Use the supplied Fedora binary instead if appropriate for your system.

## System architecture

```text
corpus -> ingestion -> Python/text chunking -> sparse lexical index
question -> shared tokenizer -> ranked sources -> search JSON
search JSON -> original source slices -> token-budgeted prompt -> Qwen -> answer JSON
search JSON + reference dataset -> own recall report
```

`models/` defines Pydantic contracts. `ingestion/` discovers and reads files.
`chunking/` handles source segmentation. `indexing/` builds and persists lexical
weights. `retrieval/`, `generation/` and `evaluation/` implement their services.
`storage/` owns validated file I/O. `cli/` coordinates services through Fire.
See [the architecture](docs/ARQUITETURA.md) for the detailed module map.

## Chunking strategy

Python uses AST statement and definition boundaries, attaching decorators to
functions/classes. Large blocks are inspected recursively and subdivided;
invalid syntax falls back to text segmentation. Line-based character offsets
avoid confusing AST UTF-8 byte columns with Python string positions. Imports,
constants, comments and code outside functions remain covered.

Text uses paragraph boundaries, ATX/Setext Markdown headings and fenced code
blocks. Headings and empty lines inside fences do not create semantic cuts;
oversized fences still need subdivision. The indexing pipeline packs adjacent
structural chunks up to the configured size to avoid isolated one-line results.
Every returned span is nonempty and at most 2000 characters. Offsets use Python
half-open slices `[start, end)`; UTF-8 and original CRLF are preserved.

## Retrieval method

BM25 is the default, with k1=1.2 and b=0.75. The alternative TF-IDF uses
logarithmic term frequencies, smoothed IDF and cosine normalization. Both use
SciPy sparse matrices and shared Unicode tokenization. Full identifiers are
retained alongside snake_case/camelCase parts; common question stopwords are
removed. Corpus-relative paths are included as searchable metadata.

Scores are sorted descending with stable index-order ties; zero-score results
are omitted. Unknown terms return no sources. No reference answers, source
labels from datasets or question-specific rules are used in indexing/ranking.
Snapshots contain JSON, JSONL, NumPy and sparse NPZ files rather than pickle.
An atomic CURRENT pointer selects a complete snapshot; checksums and version,
vocabulary and matrix-shape checks detect damaged or incompatible indexes.

## Performance analysis

Measured on the local CPU environment with the supplied public corpus and BM25,
2000-character limit, 12,887 packed chunks and no skipped input files:

| Measure | Result | Required |
| --- | --- | --- |
| Indexing 1,969 selected source files | 11.23 s (11.52 s including CLI startup) | <= 300 s |
| Loading saved index | 0.25 s | — |
| Searching 200 questions, loaded index | 0.41 s | <= 90 s |
| Full CLI search of 200 questions | 0.96 s | <= 90 s |
| Docs Recall@5, 100 questions | 84.00% | >= 80% |
| Code Recall@5, 99 questions | 84.85% | >= 50% |

The 200-query throughput run uses the 199 public questions plus one repeated
query with a distinct ID. Individual full CLI search runs, including index
loading, took about 0.75 s for each public dataset. The official evaluator
accepted both output files and confirmed the recalls below:

| Dataset | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
| --- | --- | --- | --- | --- |
| Docs | 65.00% | 82.00% | 84.00% | 90.00% |
| Code | 58.59% | 78.79% | 84.85% | 88.89% |

These are public-set measurements on one machine, not guarantees for hidden
questions or other hardware. Generation has no throughput claim. Detailed
validation and chunk-size comparison are in [VALIDACAO.md](docs/VALIDACAO.md).

## Design decisions

- Search, indexing and evaluation never load Qwen or download model weights.
- Reference answers are consumed only by evaluation; matching uses question IDs.
- `answer_dataset` consumes existing searches, reusing one generator per batch.
- Context selection counts the actual chat template and reserves output tokens.
  Whole source chunks are included in rank order when they fit; answer JSON lists
  only sources actually supplied to the model, while `k` stays as requested.
- Qwen thinking is disabled; deterministic greedy decoding returns only new
  tokens. The prompt treats retrieved text as untrusted evidence and asks for
  citations and abstention when evidence is insufficient.
- Source reads reject path escapes (including symlinks) and invalid offsets.
  Outputs are written through temporary files and atomic replacement.
- CLI failures produce readable messages and nonzero exit codes. Empty or
  whitespace queries are rejected; k=0 and empty datasets produce valid empty
  retrieval output. Missing evidence produces an explicit abstention.

## Challenges faced

Exact paths and character offsets are essential because evaluation compares
source locations. We preserved CRLF and Unicode and tested complete source
reconstruction. Very small structural Python chunks created fragmented evidence;
packing adjacent chunks reduced the default index to 12,887 chunks. Pydantic
union fallback could discard malformed reference answers; explicit validation
prevents that. The type checker is configured to exclude the third-party corpus.
Token budgets include chat-template overhead, rather than estimating tokens
from character counts.

## Resources

- Supplied project subject, version 2.0; public datasets, vLLM 0.10.1 archive and
  standalone evaluator from the project page.
- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B): local loading,
  chat-template and thinking-mode instructions.
- [Qwen Transformers guide](https://qwen.readthedocs.io/en/stable/inference/transformers.html).
- [Python ast documentation](https://docs.python.org/3/library/ast.html).
- [SciPy sparse matrices](https://docs.scipy.org/doc/scipy/reference/sparse.html).
- [Pydantic validation](https://docs.pydantic.dev/latest/concepts/validators/).

AI assistance was used for subject analysis, architecture, dependency setup,
Pydantic schemas, guided ingestion/chunking development, implementation of the
lexical index, retrieval, local generation, evaluation and CLI, tests and
review documentation. The student must understand and be able to explain or
modify every component during defense. The 42 login in the first line currently
uses the local account name `danda-si`; confirm it matches the intra login.
