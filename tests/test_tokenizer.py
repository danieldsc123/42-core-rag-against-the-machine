"""Check shared retrieval tokenization without changing source text."""
from src.indexing.tokenizer import tokenize


def test_identifiers() -> None:
    """Support exact names, snake case, acronyms and camel case."""
    assert tokenize('max_model_len EngineConfig HTTPServer') == [
        'max_model_len', 'max', 'model', 'len',
        'engineconfig', 'engine', 'config', 'httpserver', 'http', 'server',
    ]
    assert tokenize('the AND ???') == []
    assert tokenize('Olá café 42') == ['olá', 'café', '42']
