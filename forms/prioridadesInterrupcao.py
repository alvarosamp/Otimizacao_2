import math
from math import factorial

# --- FUNÇÕES AUXILIARES ---

def arredondar(valor, casas=6):
    """Função auxiliar para arredondar valores."""
    if isinstance(valor, float):
        return round(valor, casas)
    if isinstance(valor, dict):
        return {k: arredondar(v, casas) for k, v in valor.items()}
    if isinstance(valor, list):
        return [arredondar(v, casas) for v in valor]
    return valor

def _erlang_c(lam: float, mi: float, s: int) -> float:
    """Calcula a Probabilidade de Espera (Pw) usando a fórmula de Erlang C."""
    a = lam / mi # r = λ/µ
    
    # 1. Numerador: (a^s / s!) * (sµ / (sµ - λ))
    try:
        if s * mi - lam <= 0:
            raise ValueError("Instabilidade local no Erlang C.")
            
        prob_espera_num = (math.pow(a, s) / factorial(s)) * (s * mi / (s * mi - lam))
        
    except ValueError as e:
        raise ValueError(f"Instabilidade local no cálculo de Erlang C: {e}")
    except ZeroDivisionError:
        return 0.0

    # 2. Denominador: Σ_{k=0}^{s-1} (a^k / k!) + Numerador
    sum_terms = sum(math.pow(a, k) / factorial(k) for k in range(s))
    
    prob_espera_denom = sum_terms + prob_espera_num
    
    # Pw = Numerador / Denominador
    return prob_espera_num / prob_espera_denom

# ----------------------------------------------------------------------

def calcular_mms_prioridade_com_interrupcao(lambda_total: float, mi: float, servidores: int, proporcoes_str: str) -> dict:
    """
    Calcula as métricas do modelo M/M/s com prioridade e interrupção (Preemptive Priority),
    aplicando as fórmulas L = λ̄_i * W e Lq = L - λ_i / μ.
    """
    s = servidores
    
    # 1. Pré-processamento: Calcular λi a partir de λ_total e proporções
    try:
        proporcoes = [
            float(x.strip())
            for x in proporcoes_str.split(",")
            if x.strip() != ""
        ]
        if not proporcoes:
            return {"Erro": "Nenhuma proporção de chegada válida fornecida."}

        soma_proporcoes = sum(proporcoes)
        if soma_proporcoes <= 0:
            return {"Erro": "A soma das proporções de chegada deve ser maior que zero."}
        
        lambdas_ = [(prop / soma_proporcoes) * lambda_total for prop in proporcoes]
        
    except ValueError:
        return {"Erro": "As proporções de chegada devem ser números válidos separados por vírgula."}

    # 2. Validações e Estabilidade Global
    capacidade = mi * s
    rho = lambda_total / capacidade

    if mi <= 0 or s <= 0 or rho >= 1:
        return {"Erro": "Parâmetros inválidos (µ, s) ou sistema instável (λ > s·µ)."}

    resultados = {}
    Ws_acumulado = [] # Armazena W_i para o cálculo subsequente (s > 1)

    # 3. Iteração sobre as classes (i=0, 1, 2, ...)
    for i, lam_i in enumerate(lambdas_):
        classe_id = i + 1
        
        # λ̄_i: Taxa de chegada acumulada (λ1 + ... + λi)
        lambda_acumulada_i = sum(lambdas_[j] for j in range(i + 1))
        lambda_acumulada_i_menos_1 = sum(lambdas_[j] for j in range(i)) if i > 0 else 0.0

        # Inicializa variáveis
        W_bar = None 
        W = 0.0
        Wq = 0.0
        L = 0.0
        Lq = 0.0
        
        # Se λi = 0, L, Lq, W, Wq são 0. O código continua para o armazenamento.
        if lam_i == 0.0:
            pass 

        # --- CASO S = 1 (M/M/1 com Prioridade) ---
        elif s == 1:
            denom = (1.0 - (lambda_acumulada_i_menos_1 / mi)) * (1.0 - (lambda_acumulada_i / mi))

            if denom <= 0:
                return {"Erro": f"Denominador inválido na classe {classe_id}. (Instabilidade local: λ̄_i >= µ)"}

            W = (1.0 / mi) / denom
            Wq = W - (1.0 / mi)
            
            # CORREÇÃO 1: L agora usa a taxa acumulada (λ̄_i)
            L = lambda_acumulada_i * W

            # CORREÇÃO 2: Lq usa a fórmula de diferença Lq = L - λ_i / μ
            Lq = L - (lam_i / mi) 

        # --- CASO S > 1 (M/M/s com Prioridade) ---
        else:
            try:
                Pw_bar = _erlang_c(lambda_acumulada_i, mi, s)
                Wq_bar = Pw_bar / (capacidade - lambda_acumulada_i)
                W_bar = Wq_bar + 1.0 / mi
                
            except ValueError as e:
                 return {"Erro": f"Instabilidade local na Classe {classe_id}: {e}"}

            # W_i: Tempo médio no sistema para a classe i
            if i == 0:
                W = W_bar
            else:
                soma_previas = sum(lambdas_[j] * Ws_acumulado[j] for j in range(i))
                
                if lam_i == 0:
                    W = 0.0
                else:
                    W = (lambda_acumulada_i * W_bar - soma_previas) / lam_i

            Ws_acumulado.append(W) 

            Wq = W - 1.0 / mi
            
            # CORREÇÃO 1: L agora usa a taxa acumulada (λ̄_i)
            L = lambda_acumulada_i * W
            
            # CORREÇÃO 2: Lq usa a fórmula de diferença Lq = L - λ_i / μ
            Lq = L - (lam_i / mi)

            # Inicializa resultados para evitar KeyError
            if f"Classe {classe_id}" not in resultados:
                resultados[f"Classe {classe_id}"] = {}

            resultados[f"Classe {classe_id}"]["Tempo médio ponderado (W̄)"] = W_bar

        # 4. Armazenamento dos Resultados
        # Sobrescreve/Cria o dicionário final com as métricas
        resultados[f"Classe {classe_id}"] = {
            "Taxa de chegada da classe (λi)": lam_i,
            "Número médio de clientes no sistema (L)": L,
            "Número médio de clientes na fila (Lq)": Lq,
            "Tempo médio gasto no sistema (W)": W,
            "Tempo médio gasto na fila (Wq)": Wq,
            "Taxa de ocupação total (ρ)": rho,
        }
        
        # Adiciona W_bar apenas se s > 1
        if s > 1 and W_bar is not None:
            resultados[f"Classe {classe_id}"]["Tempo médio ponderado (W̄)"] = W_bar 

    return arredondar(resultados)