"""Verificar a tokenização compartilhada sem alterar o texto da fonte."""
from src.indexing.tokenizer import tokenize


def test_identifiers() -> None:
    """Reconhecer nomes exatos, snake_case, siglas e camelCase."""
    assert tokenize('max_model_len EngineConfig HTTPServer') == [
        'max_model_len', 'max', 'model', 'len',
        'engineconfig', 'engine', 'config', 'httpserver', 'http', 'server',
    ]
    assert tokenize('the AND ???') == []
    assert tokenize('Olá café 42') == ['olá', 'café', '42']
