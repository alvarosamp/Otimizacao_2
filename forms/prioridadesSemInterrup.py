import math
from math import factorial

# --- FUNÇÕES AUXILIARES ---

def _calcular_lambda_i(lambda_total: float, proporcoes_str: str) -> list[float]:
    """Calcula as taxas de chegada individuais (λi) a partir da λ total e proporções."""
    proporcoes = [
        float(x.strip())
        for x in proporcoes_str.split(",")
        if x.strip()
    ]
    if not proporcoes:
        raise ValueError("Nenhuma proporção de chegada válida fornecida.")

    soma_proporcoes = sum(proporcoes)
    if soma_proporcoes <= 0:
        raise ValueError("A soma das proporções de chegada deve ser maior que zero.")
    
    # λi = (Proporção_i / ΣProporções) * λ_total
    return [(prop / soma_proporcoes) * lambda_total for prop in proporcoes]

def _calcular_wq_geral_inverso(lam_total: float, mi: float, s: int) -> float:
    """
    Calcula o inverso do tempo de espera na fila geral (1 / Wq,geral) para o modelo M/M/s.
    
    [ s! * (sµ - λ) / r^s * Σ_{j=0}^{s-1} r^j / j!  + sµ ]
    """
    r = lam_total / mi # r = λ/µ
    
    soma_erlang = sum(math.pow(r, j) / factorial(j) for j in range(s))
    
    r_pow_s = r ** s
    
    # O termo A é o fator de probabilidade de espera (Pq)
    termo_a = (factorial(s) * (s * mi - lam_total) / r_pow_s) * soma_erlang
    
    # Retorna: 1 / Wq_geral
    return termo_a + s * mi

def arredondar(valor, casas=6):
    """Função auxiliar para arredondar valores."""
    if isinstance(valor, float):
        return round(valor, casas)
    if isinstance(valor, dict):
        return {k: arredondar(v, casas) for k, v in valor.items()}
    if isinstance(valor, list):
        return [arredondar(v, casas) for v in valor]
    return valor

# ----------------------------------------------------------------------

def calcular_mms_prioridade_sem_interrupcao(lambda_total: float, mi: float, servidores: int, proporcoes_str: str) -> dict:
    """
    Função principal. Calcula as métricas do modelo M/M/s com prioridade sem interrupção.
    """
    s = servidores
    
    try:
        # 1. Pré-processamento e Validações de Entrada
        lambdas_i = _calcular_lambda_i(lambda_total, proporcoes_str)
        
        if mi <= 0 or s <= 0 or lambda_total < 0:
            raise ValueError("Taxa de serviço (µ) e servidores (s) devem ser positivos.")
        
    except ValueError as e:
        return {"Erro": f"Erro de entrada: {e}"}
    
    # 2. Validação de Estabilidade
    capacidade = s * mi
    rho = lambda_total / capacidade

    if rho >= 1.0:
        return {"Erro": f"Sistema instável. Taxa de ocupação (ρ = {rho:.4f}) deve ser menor que 1 (λ < s·µ)."}

    # 3. Cálculo do Termo Base de Espera
    try:
        wq_base_inverso = _calcular_wq_geral_inverso(lambda_total, mi, s)
    except ZeroDivisionError:
        return {"Erro": "Divisão por zero no cálculo do termo base (r^s é zero ou muito pequeno)."}
    except Exception as e:
        return {"Erro": f"Erro no cálculo do termo base: {e}"}

    # 4. Cálculo das Métricas por Classe
    
    resultados = {}
    lambda_acumulada_i_menos_1 = 0.0 # Σ λj, j=1 a i-1

    for i, lambda_i in enumerate(lambdas_i):
        classe_id = i + 1
        
        # Fatores de Prioridade
        lambda_acumulada_i = lambda_acumulada_i_menos_1 + lambda_i

        fator_prioridade_1 = 1.0 - lambda_acumulada_i_menos_1 / capacidade
        fator_prioridade_2 = 1.0 - lambda_acumulada_i / capacidade

        if fator_prioridade_1 <= 0 or fator_prioridade_2 <= 0:
             return {"Erro": f"Fator de prioridade negativo/zero na Classe {classe_id}. (sµ={capacidade:.2f})"}

        # Wq,i = Wq_geral / (Fator_1 * Fator_2)
        Wq = 1.0 / (wq_base_inverso * fator_prioridade_1 * fator_prioridade_2)
        
        # Métricas de Little
        W = Wq + 1.0 / mi 
        L = lambda_i * W
        Lq = lambda_i * Wq 
        
        lambda_acumulada_i_menos_1 = lambda_acumulada_i # Atualiza a soma para o próximo loop
        
        resultados[f"Classe {classe_id}"] = {
            "Taxa de chegada da classe (λi)": lambda_i,
            "Número médio de clientes no sistema (L)": L,
            "Número médio de clientes na fila (Lq)": Lq,
            "Tempo médio gasto no sistema (W)": W,
            "Tempo médio gasto na fila (Wq)": Wq,
            "Taxa de ocupação total (ρ)": rho,
        }

    return arredondar(resultados)