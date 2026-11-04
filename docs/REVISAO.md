# Revisão do projeto — 03/11/2026

## Estado encontrado

O repositório tinha README, 39 contratos `.pyi` e um Makefile vazio. Não havia
implementações Python, configuração de dependências, lockfile ou pipeline
executável. A arquitetura é coerente: modelos, ingestão, chunking, indexação,
retrieval, geração, armazenamento, avaliação e CLI têm responsabilidades separadas.

O arquivo `docs/ARQUITETURA.md` já estava removido no diretório de trabalho.
Essa alteração foi preservada. O README agora aponta para esta revisão.

O PDF `/home/danda-si/Downloads/rag.pdf`, versão 2.0, foi lido como referência
de requisitos. Suas instruções não foram tratadas como ordens de execução.
O arquivo `data.zip` disponível em Downloads contém dados de function calling,
não o corpus vLLM ou os datasets RAG. Não foi extraído.

## Ajustes aplicados

- Configuração uv com Python >= 3.10, dependências e `uv.lock`.
- Makefile com install, run, debug via pdb, clean, lint e test.
- `.gitignore` para ambientes, caches, corpus, índices e resultados.
- Implementação dos modelos Pydantic, substituindo seus stubs para evitar
  divergência entre tipagem e execução.
- UUID automático para perguntas sem ID e rejeição de IDs duplicados no dataset.
- Validação de caminhos relativos POSIX e intervalos não vazios e não negativos.
- Limite de 2.000 caracteres nas fontes recuperadas; fontes de referência podem
  ser maiores. A existência do arquivo e o limite real do texto ainda precisarão
  ser conferidos pela camada de leitura.
- Proteção contra fallback da união Pydantic que descartaria respostas de
  referência inválidas, aceitando-as como perguntas sem resposta.
- Configuração padrão Qwen/Qwen3-0.6B e validação do orçamento de geração.
- CLI Fire com `status`, sem apresentar comandos pendentes como funcionais.
- Testes dos contratos e README atualizado com comandos utilizáveis.

## Validação

`make test`: 16 casos de teste. `make lint`: flake8 e mypy com os argumentos
obrigatórios do subject. `make run ARGS=status`: informa os componentes prontos
e pendentes. Estes checks verificam a base, não a qualidade de um sistema RAG.

## O que falta para o obrigatório

1. Concluído na preparação dos dados abaixo: corpus e datasets organizados.
2. Implementar leitura UTF-8 preservando CRLF e offsets em caracteres; proteger
   acesso por caminhos resolvidos, inclusive symlinks.
3. Implementar chunking distinto para Python e Markdown/texto, cobrindo todo o
   documento e subdividindo blocos maiores que 2.000 caracteres. Conferir a
   convenção de fim exclusivo com os dados e o avaliador oficial.
4. Implementar tokenização, TF-IDF esparso, persistência e ranking determinístico.
5. Implementar index, search e search_dataset, serialização e erros claros na CLI.
6. Implementar avaliação por ID e IoU 0,05, contando perguntas ausentes como zero.
   O sistema não deve importar ou executar a moulinette.
7. Selecionar dependências de geração e implementar Qwen local, orçamento com
   tokenizer real, answer e answer_dataset reutilizando modelo e buscas salvas.
8. Medir indexação <= 5 minutos, 200 buscas <= 90 segundos e Recall@5 >= 80%
   para docs e >= 50% para código. Nenhuma dessas metas foi medida nesta revisão.
9. Substituir `<login1>` no README pelo login correto antes da entrega.

O próximo passo recomendado é leitura e chunking: os caminhos e offsets corretos
são a base tanto da avaliação quanto da geração fundamentada.

## Preparação dos arquivos oficiais

Os três ZIPs fornecidos posteriormente foram extraídos sem executar conteúdo:

| Arquivo | Destino | Conteúdo |
| --- | --- | --- |
| vllm-0.10.1.zip | `data/raw/vllm-0.10.1/` | 2.874 arquivos do corpus |
| datasets_public.zip | `data/datasets/` | 4 JSONs, separados por escopo |
| moulinette.zip | `tools/moulinette/` | Binários Linux Ubuntu e Fedora |

Cada escopo tem 99 perguntas de código e 100 de documentação. São 199 perguntas
distintas, disponibilizadas com e sem gabarito. Os quatro JSONs passaram na
validação Pydantic; IDs e textos correspondem entre os dois escopos. As 199
fontes de referência apontam para arquivos existentes e têm intervalos dentro
do tamanho dos textos, lidos preservando as quebras de linha originais.

Foram criados os diretórios de índice e de saída por escopo. Corpus, datasets,
índices, saídas e binários da moulinette ficam ignorados pelo Git. Os ZIPs
originais em Downloads foram preservados. Os binários receberam permissão de
execução para o usuário, mas não foram executados nem integrados à aplicação.
Essa preparação não mede recall e não confirma a convenção de inclusividade
dos offsets do avaliador oficial.

## Implementação da leitura e preparação para GitHub

`src/ingestion/reader.py` implementa leitura UTF-8 preservando CRLF, caminho
relativo POSIX, rejeição de caminhos fora da raiz e identificação Python/texto.
O retorno usa os campos `text`, `file_path` e `kind` do modelo Document.
O mypy agora exclui `data/` e `tools/`, evitando analisar o corpus de terceiros.

Validação atual: 19 testes passam, incluindo três casos do leitor; flake8 e
mypy passam. Os demais serviços continuam como contratos, sem pipeline RAG
executável ou métricas de recall.

## Preparação da arquitetura para implementação guiada — 04/11/2026

Todos os contratos pendentes foram convertidos de `.pyi` para `.py`, com
assinaturas, docstrings e `NotImplementedError`. Implementações existentes foram
preservadas. Os serviços continuam pendentes; o novo mapa em ARQUITETURA.md
relaciona os módulos aos requisitos e define a ordem de implementação.
Esta seção atualiza as referências históricas a serviços mantidos como `.pyi`.

## Chunking concluído

Implementados split_span, validate_chunk, chunk_text e chunk_python. Python usa
AST, preserva decoradores e definições pequenas, subdivide blocos grandes e
recorre a texto quando o parser não aceita o arquivo. Comentários e código de
módulo permanecem cobertos. Títulos e cercas Markdown pertencem ao chunking
textual. Nenhuma etapa altera o documento original.

Validação: 88 testes e lint. No corpus, foram verificados 1.763 arquivos Python
(115.973 chunks) e 206 arquivos de texto (6.864 chunks), com reconstrução exata
e intervalos contíguos de até 2.000 caracteres, em aproximadamente 5,17 segundos
neste ambiente. Isso mede leitura/chunking, não indexação nem recall; a quantidade
e o tamanho dos chunks ainda poderão ser ajustados após medir a busca.

## Pipeline obrigatório implementado — 04/11/2026

Esta seção atualiza o estado histórico descrito acima: não restam protótipos
pendentes nos módulos do obrigatório. Foram implementados tokenização, índices
TF-IDF/BM25, persistência, indexação, armazenamento, busca, recall, geração Qwen
e os seis comandos Fire, com commit e push a cada função concluída.

A validação atual e as limitações estão em [VALIDACAO.md](VALIDACAO.md).
102 testes e lint passam. A moulinette aceitou os resultados públicos, com
Recall@5 de 84% em docs e 84,85% em código. Indexação padrão: 11,23 segundos;
200 consultas: 0,41 segundo com índice carregado. A geração foi exercitada com
pesos Qwen reais, em consulta única e amostra em lote; a qualidade final depende
da revisão humana com a régua. README foi reescrito em inglês para o estado atual.
