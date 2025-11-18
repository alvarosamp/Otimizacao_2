from math import factorial


'''
-Script responsável pelos cálculos do modelo com prioridade e interrupção

-Parâmetros:
λi: taxa de chegada da classe i            L: número médio de clientes no sistema
µ: taxa de atendimento                     Lq: número médio de clientes na fila
s: número de servidores                    W: tempo médio gasto no sistema
Wq: tempo médio gasto na fila

-Fórmulas:
• Para s = 1:
    W_i = (1/µ) / [(1 - Σ_{j=1}^{i-1} λ_j / µ) * (1 - Σ_{j=1}^{i} λ_j / µ)]
    Wq_i = W_i - 1/µ
    L_i  = (Σ_{j=1}^{i} λ_j) * W_i
    Lq_i = L_i - (Σ_{j=1}^{i} λ_j)/µ

• Para s > 1:
    Usa-se Erlang C com λ̄_i = Σ_{j=1}^{i} λ_j:
    Pw(λ̄_i) = ErlangC(λ̄_i, µ, s)
    Wq_i = Pw(λ̄_i) / (sµ - λ̄_i)
    W_i  = Wq_i + 1/µ
    L_i  = λ_i * W_i
    Lq_i = λ_i * Wq_i
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

# Função principal do modelo com prioridade e interrupção
def mms_prioridade_com_interrupcao(lambdas_, mi, servidores):
    # Validação básica
    if mi <= 0:
        return {"Erro": "Taxa de serviço deve ser maior que zero"}
    if servidores <= 0:
        return {"Erro": "Número de servidores deve ser maior que zero"}
    if any(l < 0 for l in lambdas_):
        return {"Erro": "Taxas de chegada devem ser maiores ou iguais a zero"}

    lambdas_total = sum(lambdas_)
    capacidade = mi * servidores
    rho = lambdas_total / capacidade

    if rho >= 1:
        return {"Erro": "Soma das taxas deve ser menor que a capacidade do servidor"}

    resultados = {}

    # Para o caso s = 1
    if servidores == 1:
        for i, lam_i in enumerate(lambdas_):
            soma_lambdas = sum(lambdas_[j] for j in range(i + 1))
            soma_lambdas_i_menos_1 = sum(lambdas_[j] for j in range(i)) if i > 0 else 0.0

            denom = (1.0 - (soma_lambdas_i_menos_1 / mi)) * (1.0 - (soma_lambdas / mi))

            if denom <= 0:
                return {"Erro": f"Denominador inválido na classe {i+1}. Verifique os dados de λ e µ."}

            W = (1.0 / mi) / denom
            Wq = W - (1.0 / mi)

            L = soma_lambdas * W
            Lq = L - (soma_lambdas / mi)

            resultados[f"\n\n•Classe {i+1}"] = {
                "Taxa de ocupação total (ρ)": rho,
                "\n    Taxa de chegada da classe (λi)": lam_i,
                "\n    Número médio de clientes no sistema (L)": L,
                "\n    Número médio de clientes na fila (Lq)": Lq,
                "\n    Tempo médio gasto no sistema (W)": W,
                "\n    Tempo médio gasto na fila (Wq)": Wq,
            }

    # Para o caso s > 1
    else:
        def Pw(lambd, mi, s):
            a = lambd / mi
            sum_terms = sum((a ** k) / factorial(k) for k in range(s))
            last_term = (a ** s / factorial(s)) * (s * mi) / (s * mi - lambd)
            if s * mi - lambd <= 0:
                return {"Erro": "Denominador inválido no cálculo de Pw. Verifique os dados de λ e µ."}
            return last_term / (sum_terms + last_term)

        Ws = []

        for i, lam_i in enumerate(lambdas_):
            soma_lambdas = sum(lambdas_[j] for j in range(i + 1))

            Pw_bar = Pw(soma_lambdas, mi, servidores)
            Wq_bar = Pw_bar / (servidores * mi - soma_lambdas)
            W_bar = Wq_bar + 1.0 / mi

            if i == 0:
                W = W_bar
            else:
                soma_previas = sum(lambdas_[j] * Ws[j] for j in range(i))
                W = (soma_lambdas * W_bar - soma_previas) / lam_i

            Ws.append(W)

            Wq = W - 1.0 / mi

            L = soma_lambdas * W
            Lq = L - soma_lambdas / mi

            resultados[f"\n\n•Classe {i+1}"] = {
                "Taxa de ocupação total (ρ)": rho,
                "\n    Taxa de chegada da classe (λi)": lam_i,
                "\n    Tempo médio ponderado (W̄)": W_bar,
                "\n    Número médio de clientes no sistema (L)": L,
                "\n    Número médio de clientes na fila (Lq)": Lq,
                "\n    Tempo médio gasto no sistema (W)": W,
                "\n    Tempo médio gasto na fila (Wq)": Wq,
            }

    return arredondar(resultados)


class MMSPrioridadeComInterrupcaoModelo():
    @property
    def nome(self):
        return "Prioridade com interrupção"  # Nome do modelo


    # Cálculo dos resultados do modelo
    def calcular(self, **k):
        taxas_str = k["lambdas_"]
        taxas = [
            float(x.strip())
            for x in taxas_str.split(",")
            if x.strip() != ""
        ]
        return mms_prioridade_com_interrupcao(
            taxas,
            float(k.get("mi")),
            int(k["servidores"]),
        )