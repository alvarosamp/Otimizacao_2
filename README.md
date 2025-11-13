Projeto de Filas em Python (M/G/1 e outros modelos)

Este repositório contém implementações em Python de vários modelos de filas clássicos (M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N). O código foi escrito para ser simples, didático e reutilizável tanto como biblioteca quanto como script de exemplos.

## Objetivo

- Implementar fórmulas clássicas de teoria de filas para calcular métricas como ρ (taxa de utilização), L (número médio no sistema), Lq (número médio na fila), W (tempo médio no sistema) e Wq (tempo médio na fila).
- Incluir suporte a um tratamento básico de prioridades no caso M/G/1 (não preemptivo).
- Manter o projeto leve, sem dependências externas além da biblioteca padrão do Python.

## Estrutura do repositório

- `formulas.py` — implementação principal com as classes e métodos para os modelos M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N. O arquivo contém exemplos no bloco `if __name__ == "__main__"`.
- `interface.py` — interface CLI simples para executar e testar modelos interativamente.
- `README.md` — este arquivo explicativo.
- `requirements.txt` — mantido para sinalizar dependências (atualmente apenas stdlib).

> Observação: não há dependências externas além da biblioteca padrão do Python.

## Como executar (local)

1. (Opcional, recomendado) Crie um ambiente virtual.

- Unix / macOS (bash/zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

- Windows PowerShell (v5+):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. Execute o script de exemplo / interface:

```powershell
python formulas.py
# ou para a interface interativa
python interface.py
```

Isso executará os exemplos no final de `formulas.py` (cobertura de M/G/1, M/M/1, M/M/s, etc.) ou iniciará a `interface.py` para testes interativos.

## Visão geral (principais classes em `formulas.py`)

- `Mg1(lam, mi, var, lam_list=None, interrupt=False)`
  - Modelo M/G/1 (Poisson arrivals, general service time, 1 server).
  - Parâmetros: `lam` (λ total de chegada), `mi` (μ, taxa de atendimento), `var` (variância do tempo de serviço), `lam_list` (lista de λ por prioridade, opcional), `interrupt` (flag para comportamento preemptivo — atualmente não implementado para preempção).
  - Métodos: `mg1()` (retorna rho, L, Lq, W, Wq), `mg1_prioridades()` (calcula métricas por prioridade — não preemptivo), `mg1_print()` (imprime resultados legíveis).

- `Mm(lam, mi, s=1)`
  - Modelo M/M/1 (s=1) e M/M/s (s>1). Fornece métodos `mm1()` e `mms()` e `resultado()` para impressão.

- `Mm1k(lam, mi, k)` — M/M/1/K (capacidade finita K).
- `Mmsk(lam, mi, s, k)` — M/M/s/K (s servidores, capacidade K).
- `Mm1n(lam_por_cliente, mi, n_pop)` — M/M/1/N (população finita N).
- `Mmsn(lam_por_cliente, mi, s, n_pop)` — M/M/s/N (s servidores, população N).

Cada classe contém validações básicas (por exemplo, `mi != 0`) e tratamento de casos especiais (por exemplo, ρ = 1 quando necessário).

## Exemplos (resumido)

- M/G/1 sem prioridades (no final de `formulas.py`):

```python
modelo_simples = Mg1(lam=2, mi=5, var=0.04)
modelo_simples.mg1_print()
```

- M/G/1 com prioridades (lista de chegadas por prioridade):

```python
modelo_prioridades = Mg1(lam=3, mi=6, var=0.05, lam_list=[1,1,1], interrupt=False)
modelo_prioridades.mg1_print()
```

Há exemplos adicionais cobrindo M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N no final de `formulas.py`.

## Como contribuir / observações

- O código é intencionalmente simples e didático. Se quiser adicionar preempção para prioridades no M/G/1 ou testes automatizados, crie uma branch e envie um Pull Request.
- Antes de abrir uma PR, garanta que o código segue a mesma formatação e que exemplos no `if __name__ == "__main__"` continuam funcionando.

## Licença

Consulte o arquivo `LICENSE` neste repositório.

## Contato

Se houver dúvidas sobre o conteúdo ou problemas reproduzindo os exemplos, abra uma issue descrevendo o ambiente (OS, versão do Python) e o erro observado.
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
# Projeto de Filas em Python (M/G/1 e outros modelos)

Este repositório contém implementações em Python de vários modelos de filas clássicos (M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N). O código foi escrito para ser simples, didático e reutilizável tanto como biblioteca quanto como script de exemplos.

## Objetivo

- Implementar fórmulas clássicas de teoria de filas para calcular métricas como ρ (taxa de utilização), L (número médio no sistema), Lq (número médio na fila), W (tempo médio no sistema) e Wq (tempo médio na fila).
- Incluir suporte a um tratamento básico de prioridades no caso M/G/1 (não preemptivo).
- Manter o projeto leve, sem dependências externas além da biblioteca padrão do Python.

## Estrutura do repositório

- `formulas.py` — implementação principal com as classes e métodos para os modelos M/G/1, M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N. O arquivo contém exemplos no bloco `if __name__ == "__main__"`.
- `README.md` — este arquivo explicativo.
- `requirements.txt` — mantido para sinalizar dependências (atualmente apenas stdlib).

> Observação: não há dependências externas além da biblioteca padrão do Python.

## Como executar (local)

1. (Opcional, recomendado) Crie um ambiente virtual.

- Unix / macOS (bash/zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

- Windows PowerShell (v5+):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

1. Execute o script de exemplo:

```powershell
python formulas.py
```

Isso executará os exemplos no final de `formulas.py`: um cenário M/G/1 sem prioridades e outro com prioridades, além de exemplos para M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N.

## Visão geral (principais classes em `formulas.py`)

- `Mg1(lam, mi, var, lam_list=None, interrupt=False)`
  - Modelo M/G/1 (Poisson arrivals, general service time, 1 server).
  - Parâmetros: `lam` (λ total de chegada), `mi` (μ, taxa de atendimento), `var` (variância do tempo de serviço), `lam_list` (lista de λ por prioridade, opcional), `interrupt` (flag para comportamento preemptivo — atualmente não implementado para preempção).
  - Métodos: `mg1()` (retorna rho, L, Lq, W, Wq), `mg1_prioridades()` (calcula métricas por prioridade — não preemptivo), `mg1_print()` (imprime resultados legíveis).

- `Mm(lam, mi, s=1)`
  - Modelo M/M/1 (s=1) e M/M/s (s>1). Fornece métodos `mm1()` e `mms()` e `resultado()` para impressão.

- `Mm1k(lam, mi, k)` — M/M/1/K (capacidade finita K).
- `Mmsk(lam, mi, s, k)` — M/M/s/K (s servidores, capacidade K).
- `Mm1n(lam_por_cliente, mi, n_pop)` — M/M/1/N (população finita N).
- `Mmsn(lam_por_cliente, mi, s, n_pop)` — M/M/s/N (s servidores, população N).

Cada classe contém validações básicas (por exemplo, `mi != 0`) e tratamento de casos especiais (por exemplo, ρ = 1 quando necessário).

## Exemplos (resumido)

- M/G/1 sem prioridades (no final de `formulas.py`):

```python
modelo_simples = Mg1(lam=2, mi=5, var=0.04)
modelo_simples.mg1_print()
```

- M/G/1 com prioridades (lista de chegadas por prioridade):

```python
modelo_prioridades = Mg1(lam=3, mi=6, var=0.05, lam_list=[1,1,1], interrupt=False)
modelo_prioridades.mg1_print()
```

Há exemplos adicionais cobrindo M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N e M/M/s/N no final de `formulas.py`.

## Como contribuir / observações

- O código é intencionalmente simples e didático. Se quiser adicionar preempção para prioridades no M/G/1 ou testes automatizados, crie uma branch e envie um Pull Request.
- Antes de abrir uma PR, garanta que o código segue a mesma formatação e que exemplos no `if __name__ == "__main__"` continuam funcionando.

## Licença

Consulte o arquivo `LICENSE` neste repositório.

## Contato

Se houver dúvidas sobre o conteúdo ou problemas reproduzindo os exemplos, abra uma issue descrevendo o ambiente (OS, versão do Python) e o erro observado.


