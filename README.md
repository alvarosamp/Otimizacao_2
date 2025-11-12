# Projeto M/G/1 - Cálculos de fila (Oti2)

Este repositório contém uma implementação simples em Python do modelo M/G/1 (fila com chegadas Poisson, atendimento geral, 1 servidor). O projeto está sendo desenvolvido em grupo — este README explica o que o código faz, como usar e o que cada membro do grupo deve saber.

## Objetivo

- Implementar um modelo M/G/1 que compute as métricas clássicas de filas: ρ (taxa de utilização), L (número médio no sistema), Lq (número médio na fila), W (tempo médio no sistema) e Wq (tempo médio na fila).
- Fornecer uma versão com tratamento básico de prioridades (ex.: lista de taxas por prioridade).
- Tornar o código utilizável como biblioteca simples e também como script exemplo.

## Estrutura do repositório

- `codigo.py` — implementação principal da classe `Mg1`, exemplos de uso e um pequeno runner quando executado como script.
- `readme.md` — este arquivo explicativo.

> Observação: não há dependências externas além da biblioteca padrão do Python.

## Como executar (local)

1. Recomenda-se criar um ambiente virtual (opcional, mas recomendado):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Executar o script de exemplo:

```bash
python3 codigo.py
```

Isso executará os exemplos no final de `codigo.py`: um cenário sem prioridades e outro com prioridades (cada um chama `mg1_print()` para exibir resultados).

## Descrição técnica (classe `Mg1`)

A classe `Mg1` encapsula o modelo e suas métricas:

- Construtor: `Mg1(lam, mi, var, lam_list=None, interrupt=True)`
  - `lam` — taxa média de chegada (λ) do sistema.
  - `mi` — taxa média de atendimento (μ). Validada para != 0.
  - `var` — variância do tempo de atendimento (σ²).
  - `lam_list` — (opcional) lista de taxas de chegada por prioridade.
  - `interrupt` — bandeira para comportamento com prioridades (no código atual apenas guardada).

- Validações:
  - Se `mi == 0`, a função lança `ValueError`.
  - Calcula `rho = lam / mi` no construtor; se `rho >= 1`, lança `ValueError` porque o sistema é instável.

- Métodos principais:
  - `mg1()` — retorna `(rho, L, Lq, W, Wq)` usando as fórmulas:
    - ρ = λ / μ
    - Lq = (λ² * σ² + ρ²) / (2 * (1 - ρ))
    - L = ρ + Lq
    - Wq = Lq / λ (tratando λ == 0)
    - W = Wq + 1 / μ

  - `mg1_prioridades()` — calcula métricas por prioridade usando a mesma fórmula base para cada taxa de chegada da lista (`lam_list`) e a mesma `mi`.

  - `mg1_print()` — imprime resultados formatados (usa `try/except` em volta dos cálculos para mostrar mensagens amigáveis quando `ValueError` é lançado).



## Exemplo de uso (no código)

No final de `codigo.py` há exemplos:

```python
# Exemplo sem prioridades
modelo_simples = Mg1(lam=2, mi=5, var=0.04)
modelo_simples.mg1_print()

# Exemplo com prioridades
modelo_prioridades = Mg1(lam=3, mi=6, var=0.05, lam_list=[1,1,1])
modelo_prioridades.mg1_print()
```


