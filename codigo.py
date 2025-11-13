import math
from math import factorial

# Classe M/G/1
class Mg1:
    """
    Modelo de Fila M/G/1 com Prioridades 
    ---------------------
    Fórmulas sem prioridades:
        ρ  = λ / μ
        Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)]
        L  = ρ + Lq
        Wq = Lq / λ
        W  = Wq + (1 / μ)

    Fórmulas com prioridades:
        Lq_k = L_k - λ_k / μ_k
        L = λ * W
        Wq = W - 1 / μ
        W = (1 / μ) * (1 - Σ(λ_i / sμ)) + (1 / μ)
    """

    def __init__(self, lam, mi, var, lam_list=None, interrupt=True):
        """
        Inicializa o modelo com seus parâmetros básicos.
        lam = taxa média de chegada para o sistema
        mi = taxa média de atendimento para o sistema
        var = variância do tempo de atendimento
        lam_list = lista de taxas de chegada para prioridades (se for o modelo com prioridade)
        interrupt = True => com interrupção, False => sem interrupção
        """
        self.lam = lam  # taxa média de chegada
        self.mi = mi    # taxa média de atendimento
        self.var = var  # variância do tempo de atendimento
        
        # Validações básicas
        if self.mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero")

        # Calcula fator de utilização global (ρ) cedo para evitar uso antes da definição
        self.rho = self.lam / self.mi  # fator de utilização do sistema

        # Verifica se o sistema está instável (ρ >= 1)
        if self.rho >= 1:
            raise ValueError("O sistema está instável (ρ >= 1). Ajuste as taxas de chegada ou atendimento.")

        # Lista de prioridades (opcional)
        if lam_list:  # Se lam_list for fornecido, é um modelo com prioridades
            self.lam_list = lam_list
            self.rho_list = [l / self.mi for l in lam_list]  # Calcula ρ para cada prioridade
        else:
            self.lam_list = None  # Se não houver lista de prioridades, utiliza um único valor de ρ
            self.rho_list = [self.rho]  # Apenas um ρ, igual ao cálculo original

        # A variável "interrupt" indica se as prioridades podem interromper o atendimento
        self.interrupt = interrupt

    def mg1(self):
        """
        Calcula as principais métricas do modelo M/G/1.
        Retorna rho, L, Lq, W, Wq.
        """
        # Probabilidade do sistema estar vazio 
        p0 = 1 - self.rho
        # Fórmula de Pollaczek (variância já é variância, não elevar ao quadrado)
        Lq = (math.pow(self.lam, 2) * self.var + math.pow(self.rho, 2)) / (2 * (1 - self.rho))
        # Número médio de clientes no sistema
        L = self.rho + Lq
        # Tempo médio de espera na fila
        Wq = Lq / self.lam if self.lam != 0 else 0.0
        # Tempo médio no sistema (espera + atendimento)
        W = Wq + (1 / self.mi)
        return self.rho, L, Lq, W, Wq

    def mg1_prioridades(self):
        """
        Calcula as métricas do modelo M/G/1 com prioridades.
        Retorna uma lista de métricas (Lq_k, L, Wq, W) para cada prioridade.
        """
        resultados = []
        for i, lam in enumerate(self.lam_list):
            rho = self.rho_list[i]  # Calcula ρ para cada classe de prioridade
            # Cálculo de Lq_k para cada prioridade, com a fórmula adaptada
            Lq_k = (math.pow(lam, 2) * self.var + math.pow(rho, 2)) / (2 * (1 - self.rho))
            # Número médio de clientes no sistema para a prioridade
            L = rho + Lq_k
            # Tempo médio na fila para a prioridade
            Wq = Lq_k / lam if lam != 0 else 0.0
            # Tempo médio no sistema para a prioridade
            W = Wq + 1 / self.mi
            resultados.append((Lq_k, L, Wq, W))  # Armazena os resultados para cada prioridade
        return resultados

    def mg1_print(self):
        """
        Exibe os resultados do modelo M/G/1 com explicações detalhadas.
        Dependendo de ser com ou sem prioridades, ele faz os cálculos e exibe os resultados.
        """
        if self.lam_list is None:  # Se não for modelo com prioridades
            try:
                rho, L, Lq, W, Wq = self.mg1()  # Calcula as métricas para o modelo M/G/1
                print(f"Modelo M/G/1:")
                print(f"Taxa de utilização (ρ): {rho:.4f}")
                print(f"Número médio de clientes na fila (Lq): {Lq:.4f}")
                print(f"Número médio de clientes no sistema (L): {L:.4f}")
                print(f"Tempo médio de espera na fila (Wq): {Wq:.4f}")
                print(f"Tempo médio no sistema (W): {W:.4f}")
            except ValueError as e:
                print(e)
        else:  # Se for modelo com prioridades
            try:
                resultados = self.mg1_prioridades()  # Calcula as métricas com prioridades
                print(f"Modelo M/G/1 com Prioridades:")
                # Exibe os resultados para cada prioridade
                for i, (Lq_k, L, Wq, W) in enumerate(resultados):
                    print(f"\nPrioridade {i+1}:")
                    print(f"Número médio de clientes na fila (Lq_{i+1}): {Lq_k:.4f}")
                    print(f"Número médio de clientes no sistema (L_{i+1}): {L:.4f}")
                    print(f"Tempo médio de espera na fila (Wq_{i+1}): {Wq:.4f}")
                    print(f"Tempo médio no sistema (W_{i+1}): {W:.4f}")
            except ValueError as e:
                print(e)


# Classe M/M/1 e M/M/s
class Mm1:
    """
    Modelo de Fila M/M/1 e M/M/s
    ---------------------
    Fórmulas principais para M/M/1:
        ρ = λ / μ
        L = λ / (μ - λ)
        Lq = (λ²) / (μ(μ - λ))
        W = 1 / (μ - λ)
        Wq = λ / (μ(μ - λ))

    Fórmulas para M/M/s > 1:
        P0 = [Σ_{n=0}^{s-1} (λ/μ)^n / n!] + (λ/μ)^s / s! * (1 - ρ)^2
        Pn = (λ/μ)^n / n! * P0, for n <= s
        Pn = (λ/μ)^n / s^n * P0, for n > s
        L = λ / μ * (1 + (λ/μ)^s / s! * (1 - ρ)^2)
        Lq = λ² / (μ(μ - λ))
        W = 1 / (μ - λ)
        Wq = Lq / λ
    """
    def __init__(self, lam, mi, s=None, var=None):
        """
        Inicializa o modelo com seus parâmetros básicos.
        lam = Taxa média de chegada(λ) para o sistema de filas
        mi : Taxa média de atendimento (μ)
        s : Número de servidores (para M/M/s)
        var : Variância do tempo de atendimento 
        """
        self.lam = lam  # Taxa de chegada (λ)
        self.mi = mi    # Taxa de atendimento (μ)
        self.s = s      # Número de servidores (para M/M/s)
        self.var = var  # Variância (σ²)

        # Calculando o fator de utilização (ρ)
        self.rho = lam / (mi * s if s else mi)

        # Verificação de estabilidade do sistema
        if self.rho >= 1:
            raise ValueError("O sistema está instável (ρ >= 1). Ajuste as taxas de chegada ou atendimento.")

    def mm1(self):
        """
        Calcula as métricas do modelo M/M/1.
        """
        L = self.lam / (self.mi - self.lam)
        Lq = (math.pow(self.lam, 2) / (self.mi * (self.mi - self.lam)))
        W = 1 / (self.mi - self.lam)
        Wq = self.lam / (self.mi * (self.mi - self.lam))
        return L, Lq, W, Wq

    def mms(self):
        """
        Calcula as métricas do modelo M/M/s.
        """
        P0 = sum((math.pow(self.lam / self.mi, n) / factorial(n)) for n in range(self.s))
        P0 += (math.pow(self.lam / self.mi, self.s) / (factorial(self.s) * (1 - self.rho)))
        P0 = 1 / P0
        L = self.lam / self.mi * (1 + (self.lam / self.mi) ** self.s / (math.factorial(self.s) * (1 - self.rho) ** 2))
        Lq = (self.lam ** 2) / (self.mi * (self.mi - self.lam))
        W = 1 / (self.mi - self.lam)
        Wq = Lq / self.lam
        return P0, L, Lq, W, Wq

    def resultado(self):
        """
        Exibe os resultados de acordo com o modelo M/M/1 ou M/M/s.
        """
        if self.s is None:
            try:
                L, Lq, W, Wq = self.mm1()
                print(f"Modelo M/M/1:")
                print(f"Número médio de clientes no sistema (L): {L:.4f}")
                print(f"Número médio de clientes na fila (Lq): {Lq:.4f}")
                print(f"Tempo médio no sistema (W): {W:.4f}")
                print(f"Tempo médio na fila (Wq): {Wq:.4f}")
            except ValueError as e:
                print(e)
        else:  # Se o número de servidores for fornecido
            try:
                P0, L, Lq, W, Wq = self.mms()
                print(f"Modelo M/M/{self.s}:")
                print(f"Probabilidade do sistema estar vazio (P0): {P0:.4f}")
                print(f"Número médio de clientes no sistema (L): {L:.4f}")
                print(f"Número médio de clientes na fila (Lq): {Lq:.4f}")
                print(f"Tempo médio no sistema (W): {W:.4f}")
                print(f"Tempo médio na fila (Wq): {Wq:.4f}")
            except ValueError as e:
                print(e)


# Testando os códigos
if __name__ == "__main__":
    # Exemplo sem prioridades
    modelo_simples = Mg1(lam=2, mi=5, var=0.04)
    modelo_simples.mg1_print()

    print("\n" + "="*50 + "\n")

    # Exemplo com prioridades
    modelo_prioridades = Mg1(lam=3, mi=6, var=0.05, lam_list=[1, 1, 1], interrupt=True)
    modelo_prioridades.mg1_print()

    print("\n" + "="*50 + "\n")

    # Exemplo M/M/1
    modelo_mm1 = Mm1(lam=2, mi=5)
    modelo_mm1.resultado()
    print("\n" + "="*50 + "\n")
    # Exemplo M/M/s
    modelo_mms = Mm1(lam=4, mi=3, s=2)
    modelo_mms.resultado()
