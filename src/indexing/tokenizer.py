"""Shared identifier-aware lexical tokenization for queries and documents."""
import re

TOKENIZER_VERSION = 'identifier-v1'
STOP_WORDS = frozenset('''a an and are as at be been being by can could did do
 does for from had has have how i if in into is it its may of on or our should
 that the their them there these they this those to use used using was were
 what when where which who why will with would you your'''.split())


def tokenize(text: str) -> list[str]:
    """Keep full identifiers and their snake/camel components, in order."""
    tokens: list[str] = []
    for word in re.findall(r'\w+', text, flags=re.UNICODE):
        full = word.casefold()
        if full not in STOP_WORDS and full.strip('_'):
            tokens.append(full)
        separated = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', word)
        separated = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', separated)
        parts = re.findall(r'[^\W_]+', separated, flags=re.UNICODE)
        for part in parts:
            lowered = part.casefold()
            if lowered != full and lowered not in STOP_WORDS:
                tokens.append(lowered)
    return tokens
