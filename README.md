# Linux Process Dashboard

Dashboard de monitoramento em tempo real para Linux, desenvolvido com Python, Dash e Plotly. A aplicação lê diretamente dados do pseudo-sistema de arquivos `/proc` para exibir processos ativos, uso de CPU e consumo de memória.

## Principais recursos

- Listagem de processos ativos
- Exibição de PID, nome do processo, uso de CPU e memória
- Indicadores de CPU e memória em tempo real
- Ordenação por PID, CPU ou memória
- Coleta de dados em threads de background
- Atualização automática da interface a cada 5 segundos
- Separação inspirada em MVC entre model, controller e view

## Como funciona

O dashboard coleta informações diretamente do Linux:

- `/proc/<pid>/stat` para dados dos processos
- `/proc/stat` para estatísticas de CPU
- `/proc/meminfo` para informações de memória

A coleta acontece em threads de background, enquanto callbacks do Dash atualizam a interface periodicamente.

## Arquitetura

```text
Linux /proc
    |
    v
SystemModel
    |
    v
SystemController
  (threads)
    |
    v
SystemView
(Dash + Plotly)
    |
    v
Navegador
```

## Tech Stack

- Python
- Dash
- Plotly
- Linux `/proc`
- Multithreading

## Execução local

O projeto foi desenvolvido para Linux, pois depende diretamente de `/proc`.

Instale as dependências:

```bash
pip install dash plotly
```

Execute:

```bash
python dashboard.py
```

Depois acesse o endereço local exibido pelo Dash, normalmente:

```text
http://127.0.0.1:8050
```

## Estrutura

```text
Dashboard-SO/
├── dashboard.py
├── dash2.py
├── dashboard.ipynb
└── README.md
```

## Contexto acadêmico

Projeto desenvolvido na área de Sistemas Operacionais com foco em monitoramento de processos e visualização de recursos do sistema.

**Equipe:** Antonio Galvão Martins Neto e Laís Lisboa.
