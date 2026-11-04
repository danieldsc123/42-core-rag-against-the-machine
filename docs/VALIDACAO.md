# Validação do pipeline completo

Validação realizada em 04/11/2026 no ambiente local, Python 3.13.1 e CPU.
Os números abaixo são medições, não garantias para outra máquina ou dados ocultos.

## Resultado funcional

Implementados os seis comandos obrigatórios: index, search, search_dataset,
answer, answer_dataset e evaluate. Todos aceitam caminhos configuráveis.
Busca e avaliação não carregam pesos gerativos. A ferramenta oficial foi
executada externamente pelo agente, nunca chamada ou importada pelo programa.

`make test`: 102 testes passaram. `make lint`: flake8 e mypy, com todos os
argumentos obrigatórios, passaram. Os testes de geração usam um tokenizer
controlado para verificar orçamento e seleção de fontes sem acesso à rede;
a geração real foi conferida separadamente com o Qwen oficial.

Cobertura exercitada: Unicode, CRLF, offsets exatos, sintaxe inválida, títulos,
decoradores, cercas de código, tamanhos inválidos, pasta vazia, fontes fora da
raiz, symlinks, pergunta vazia, k=0, k negativo, arquivos ausentes, persistência,
checksums, falha de gravação atômica, ausência de perguntas, IDs duplicados ou
desconhecidos na avaliação e isolamento do gabarito em relação ao ranking.

## Recuperação e desempenho

Corpus fornecido: 2.874 arquivos extraídos; a política de descoberta seleciona
1.969 arquivos `.py`, `.md`, `.rst` e `.txt` (1.763 Python e 206 texto).
Nenhum arquivo selecionado foi ignorado por erro de leitura.

Configuração padrão: BM25, k1=1,2 e b=0,75, chunks de até 2.000 caracteres,
empacotamento de blocos estruturais adjacentes, 12.887 chunks no índice.

| Medida | Resultado |
| --- | --- |
| Construção e persistência | 11,23 s |
| Comando index incluindo inicialização | 11,52 s |
| Carregamento do índice persistido | 0,25 s |
| 200 consultas com índice carregado | 0,41 s |
| Comando completo para 200 consultas | 0,96 s |
| search_dataset docs incluindo inicialização e carga | 0,75 s |
| search_dataset código incluindo inicialização e carga | 0,76 s |

O teste de 200 consultas usa as 199 perguntas públicas e repete uma delas com
outro ID. Não existe um conjunto público de 200 perguntas distintas nestes ZIPs.

A moulinette Ubuntu fornecida confirmou `Student data is valid: True` nos dois
arquivos e retornou:

| Dataset | Perguntas | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
| --- | --- | --- | --- | --- | --- |
| Docs | 100 | 65,00% | 82,00% | 84,00% | 90,00% |
| Código | 99 | 58,59% | 78,79% | 84,85% | 88,89% |

Ambas as metas de Recall@5 foram atendidas nos dados públicos: docs >=80% e
código >=50%. A implementação própria reproduziu esses valores com IoU >=0,05,
caminho idêntico e média por pergunta. Isso não mede qualidade das respostas.

### Efeito do tamanho dos chunks

Experimento adicional com os mesmos arquivos, tokenização e BM25:

| Tamanho máximo | Chunks | Recall@5 docs | Recall@5 código |
| --- | --- | --- | --- |
| 2.000 | 12.887 | 84,00% | 84,85% |
| 1.000 | 24.950 | 80,00% | 82,83% |

O índice de 1.000 caracteres levou 17,30 s nesta execução (com geração em CPU
concorrente); os recalls foram calculados pela implementação própria. Mantivemos
2.000 como padrão, com melhor Recall@5 e menor índice. Nenhum gabarito foi usado
como conteúdo ou regra de ranking. O ajuste foi genérico, sem exceções por ID.

## Geração local

Modelo: Qwen/Qwen3-0.6B oficial, Transformers 4.57.6, PyTorch CPU, pensando
desativado pelo chat template e decodificação greedy. Foram exercitados `answer`
e `answer_dataset` com pesos reais em cache, além dos casos sem fontes.

Uma consulta real sobre carregamento dinâmico de LoRA retornou
`/v1/load_lora_adapter` e citou o trecho recuperado de
`data/raw/vllm-0.10.1/docs/features/lora.md`. O JSON validou com Pydantic.
O teste em lote usa uma amostra de duas perguntas públicas, não as 199.

O orçamento conta o template completo com o tokenizer real e reserva os tokens
máximos de saída. Fontes grandes que não cabem são ignoradas; as fontes incluídas
continuam em ordem de relevância. A resposta lista somente fontes efetivamente
passadas ao modelo. Sem fontes a aplicação devolve abstenção, sem baixar pesos.

CPU pode levar dezenas de segundos ou minutos por pergunta com contexto longo.
Não há meta de velocidade de geração no subject. Os testes funcionais não
certificam ausência de alucinação; a coerência e o grounding precisam ser revistos
com a régua e por leitura humana. O lote público completo não foi gerado.

## Reprodução

Na raiz do repositório, com os arquivos oficiais extraídos:

```sh
uv sync --locked
make test
make lint
uv run python -m src index --max_chunk_size 2000
uv run python -m src search_dataset \
  --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 --save_directory data/output/search_results/UnansweredQuestions
uv run python -m src evaluate \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
```

Repetir com `dataset_code_public.json`. Para a confirmação oficial, usar o comando
externo da moulinette documentado no README. Para geração, usar `answer` ou
`answer_dataset`, escolhendo `HF_HOME` se o cache padrão não for gravável.

Os artefatos locais em `data/output/evaluation/benchmark.json` e
`chunk-size-1000.json` guardam os números completos. Corpus, resultados,
experimentos e pesos não são versionados. O login `danda-si` no README foi
inferido do usuário local e deve ser confirmado antes da entrega final à 42.
