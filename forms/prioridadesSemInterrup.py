import math


'''
-Script responsável pelos cálculos do modelo com prioridade sem interrupção

-Parâmetros:
λi: taxa de chegada da classe i            L: número médio de clientes no sistema
µ: taxa de atendimento                     Lq: número médio de clientes na fila
s: número de servidores                    W: tempo médio gasto no sistema
Wq: tempo médio gasto na fila

-Fórmulas:
r = λ / µ, com λ = Σ λi
W_i = 1 / [  ( s! * (sµ - λ) / r^s * Σ_{j=0}^{s-1} r^j / j!  + sµ ) * (1 - Σ_{j=1}^{i-1} λj / (sµ)) * (1 - Σ_{j=1}^{i}   λj / (sµ)) ]
Wq_i = W_i - 1/µ
L_i  = λi * W_i
Lq_i = λi * Wq_i
'''

# Função para arredondar valores
def arredondar(valor, casas=6):
    if isinstance(valor, float):
        return round(valor, casas)
    if isinstance(valor, dict):
        return {k: arredondar(v, casas) for k, v in valor.items()}
    if isinstance(valor, list):
        return [arredondar(v, casas) for v in valor]
    return valor

# Função principal do modelo com prioridade sem interrupção
def mms_prioridade_sem_interrupcao(lambdas_, mi, servidores):
    # Validações básicas
    if mi <= 0:
        return {"Erro": "Taxa de serviço (µ) deve ser maior que zero"}
    if servidores <= 0:
        return {"Erro": "Número de servidores (s) deve ser maior que zero"}
    if any(l < 0 for l in lambdas_):
        return {"Erro": "Taxas de chegada (λi) devem ser maiores ou iguais a zero"}

    lambda_total = sum(lambdas_)
    capacidade = servidores * mi
    rho = lambda_total / capacidade

    if lambda_total >= capacidade:
        return {"Erro": "Sistema instável: soma das taxas de chegada deve ser menor que s·µ"}

    r = lambda_total / mi
    s = servidores

    soma_r = 0.0
    for j in range(s):
        soma_r += (r ** j) / math.factorial(j)

    r_pow_s = r ** s

    termo = (math.factorial(s) * (s * mi - lambda_total) / r_pow_s) * soma_r + s * mi

    resultados = {}

    for k, lambda_k in enumerate(lambdas_):
        soma_i_menos_1 = sum(lambdas_[:k])
        soma_i = soma_i_menos_1 + lambda_k

        termo2 = 1.0 - soma_i_menos_1 / capacidade
        termo3 = 1.0 - soma_i / capacidade

        if termo <= 0 or termo2 <= 0 or termo3 <= 0:
            return {"Erro": f"Divisão por zero/negativo na classe {k+1}"}

        Wq = 1.0 / (termo * termo2 * termo3) ### Da forma realizada no exercício (na explicação é invertido com W)
        W = Wq + 1.0 / mi ### Da forma realizada no exercício (na explicação é invertido com Wq)    
        L = lambda_k * W
        Lq = L - lambda_k / mi

        resultados[f"\n\n•Classe {k+1}"] = {
            "Taxa de ocupação total (ρ)": rho,
            "\n    Taxa de chegada da classe (λi)": lambda_k,
            "\n    Número médio de clientes no sistema (L)": L,
            "\n    Número médio de clientes na fila (Lq)": Lq,
            "\n    Tempo médio gasto no sistema (W)": W,
            "\n    Tempo médio gasto na fila (Wq)": Wq,
        }

    return arredondar(resultados)


class MMSPrioridadeSemInterrupcaoModelo():
    @property
    def nome(self):
        return "Prioridade sem interrupção"  # Nome do modelo

   

    # Cálculo dos resultados do modelo
    def calcular(self, **k):
        taxas_str = k["lambdas_"]
        lambdas_ = [
            float(x.strip())
            for x in taxas_str.split(",")
            if x.strip() != ""
        ]
        return mms_prioridade_sem_interrupcao(
            lambdas_,
            float(k["mi"]),
            int(k["servidores"]),
        )