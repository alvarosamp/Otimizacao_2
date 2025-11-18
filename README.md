# Projeto de Filas em Python (M/G/1 e outros modelos)

Este repositório contém implementações em Python de vários modelos de filas clássicos (M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N). O código foi escrito para ser simples, didático e reutilizável tanto como biblioteca quanto como script de exemplos.

## Objetivo

- Implementar fórmulas clássicas de teoria de filas para calcular métricas como ρ (taxa de utilização), L (número médio no sistema), Lq (número médio na fila), W (tempo médio no sistema) e Wq (tempo médio na fila).
- Incluir suporte a prioridades no caso M/G/1 (não preemptivo) e M/M/1 (preemptivo).
- Resolver exercícios propostos em sala de aula sobre teoria de filas.
- Manter o projeto leve, sem dependências externas além da biblioteca padrão do Python.

## Estrutura do repositório

- `formulas.py` — implementação principal com as classes e métodos para os modelos M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N, M/M/s/N e M/M/1 com prioridades preemptivas.
- `interface.py` — interface CLI simples para executar e testar modelos interativamente (detecta automaticamente o repositório).
- `ListaExercicios.py` — script que executa os exercícios propostos em sala de aula, validando as implementações contra os casos de teste fornecidos.
- `README.md` — este arquivo explicativo.
- `requirements.txt` — mantido para sinalizar dependências (atualmente apenas stdlib).

> **Observação:** não há dependências externas além da biblioteca padrão do Python.

## Como executar (local)

1. **(Opcional, recomendado)** Crie um ambiente virtual:

**Unix / macOS (bash/zsh):**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell (v5+):**
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. **Execute os scripts:**

```powershell
# Para rodar os exemplos embutidos em formulas.py
python formulas.py

# Para interface interativa (permite testar modelos com parâmetros personalizados)
python interface.py

# Para executar os exercícios propostos em sala de aula
python ListaExercicios.py

# Para abrir a interface gráfica (Tkinter)
python app.py
```

## Interface gráfica (Tkinter)

A aplicação gráfica em `app.py` fornece abas para calcular rapidamente as métricas:

- M/M/1 e M/M/s (capacidade infinita)
- M/G/1 simples e com prioridades não preemptivas; e M/M/1 com prioridades preemptivas
- Filas com capacidade finita: M/M/1/K e M/M/s/K
- População finita: M/M/1/N e M/M/s/N
- Aba “Resolver Lista Exercícios” que roda `ListaExercicios.py` e mostra os resultados

Como executar:

```powershell
python app.py
```

Se aparecer erro de import, garanta que `formulas.py` e `ListaExercicios.py` estão na mesma pasta do `app.py`.
O Tkinter já vem com o Python padrão para Windows/macOS; se estiver usando uma distribuição mínima, instale o suporte ao Tk.

## Requisitos

- Python 3.8 ou superior
- Sem dependências externas (usa apenas a biblioteca padrão)

## Visão geral (principais classes em `formulas.py`)

- **`Mg1(lam, mi, var, lam_list=None, interrupt=False)`**
  - Modelo M/G/1 (Poisson arrivals, general service time, 1 server).
  - Parâmetros: `lam` (λ total), `mi` (μ), `var` (variância do tempo de serviço), `lam_list` (taxas por prioridade, opcional).
  - Métodos: `mg1()`, `mg1_prioridades_nao_preemptivo()`, `mg1_print()`.

- **`Mm(lam, mi, s=1)`**
  - Modelo M/M/1 (s=1) e M/M/s (s>1).
  - Métodos: `mm1()`, `mms()`, `resultado()`.

- **`Mm1k(lam, mi, k)`** — M/M/1/K (capacidade finita K).
- **`Mmsk(lam, mi, s, k)`** — M/M/s/K (s servidores, capacidade K).
- **`Mm1n(lam_por_cliente, mi, n_pop)`** — M/M/1/N (população finita N).
- **`Mmsn(lam_por_cliente, mi, s, n_pop)`** — M/M/s/N (s servidores, população N).
- **`Mm1PrioridadePreemptiva(lam_list, mi)`** — M/M/1 com prioridades preemptivas (COM interrupção).

Cada classe contém validações básicas (por exemplo, `mi != 0`) e tratamento de casos especiais (por exemplo, ρ = 1 quando necessário).

## Exercícios de sala de aula

O arquivo `ListaExercicios.py` contém implementações dos exercícios propostos durante as aulas, organizados por tipo de modelo:

- **Lista M/M/1 e M/M/s** — exercícios 5, 7, 15
- **Lista M/G/1 e Prioridades** — exercícios 1, 6a, 6b, 6c
- **Lista M/M/1/K e M/M/s/K** — exercícios 1, 4, 5
- **Lista M/M/1/N e M/M/s/N** — exercícios 3, 4d, 6

Para executar todos os testes:
 
```powershell
python ListaExercicios.py
```

## Exemplos de uso rápido

**M/G/1 sem prioridades:**
 
```python
from formulas import Mg1
modelo = Mg1(lam=2, mi=5, var=0.04)
modelo.mg1_print()
```

**M/G/1 com prioridades (não preemptivo):**
 
```python
modelo = Mg1(lam=3, mi=6, var=0.05, lam_list=[1,1,1], interrupt=False)
modelo.mg1_print()
```

**M/M/1 com prioridades (preemptivo):**
 
```python
from formulas import Mm1PrioridadePreemptiva
modelo = Mm1PrioridadePreemptiva(lam_list=[2, 4, 2], mi=10)
modelo.resultado()
```

## Como contribuir / observações

- O código é intencionalmente simples e didático.
- Se quiser adicionar novos modelos ou melhorias, crie uma branch e envie um Pull Request.
- Antes de abrir uma PR, garanta que o código segue a mesma formatação e que os exemplos continuam funcionando.

## Licença

Consulte o arquivo `LICENSE` neste repositório.

## Contato

Se houver dúvidas sobre o conteúdo ou problemas reproduzindo os exemplos, abra uma issue descrevendo o ambiente (OS, versão do Python) e o erro observado.


