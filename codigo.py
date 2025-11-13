#Entrando com as bibliotecas
import math
from math import factorial

#Iniciando as funções
# Função M/G/1 (versão simples - conforme solicitado)
#Modelo M/G/1
class Mg1:
    """
    Modelo de Fila M/G/1 com prioridades 
    ---------------------
    Fórmulas sem prioridades:
        ρ  = λ / μ
        Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)]
        L  = ρ + Lq
        Wq = Lq / λ
        W  = Wq + (1 / μ)

    Formulas com prioridades:
        Lq_k = L_k - λ_k / μ_k
        L = λ * W
        Wq = W - 1 / μ
        W = (1 / μ) * (1 - Σ(λ_i / sμ)) + (1 / μ)
    """

    def __init__(self, lam, mi, var, lam_list = None, interrupt = True):
        """
        Inicializa o modelo com seus parâmetros básicos.
        lam = media de chegada para o sistema
        mi = media de atendimento para o sistema
        var = variância do tempo de atendimento
        lam_list = lista de taxas de chegada para prioridades (se for o modelo com prioridade)
        interrupt = True => com interrupçao, False => sem interrupção
        """
        self.lam = lam  # taxa média de chegada
        self.mi = mi    # taxa média de atendimento
        self.var = var  # variância do tempo de atendimento
        # validações básicas
        if self.mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero")

        # calcula fator de utilização global (ρ) cedo para evitar uso antes da definição
        total_rho = self.lam / self.mi
        self.rho = total_rho  # fator de utilização do sistema

        if self.rho >= 1:
            raise ValueError("O sistema está instável (ρ >= 1). Ajuste as taxas de chegada ou atendimento.")

        # lista de prioridades (opcional)
        if lam_list:  # lista de taxas de chegada para prioridades
            self.lam_list = lam_list
            self.rho_list = [l / self.mi for l in lam_list]
        else:
            self.lam_list = None
            # padrão: lista com o rho único (útil caso queira tratamento uniforme)
            self.rho_list = [self.rho]

        self.interrupt = interrupt  # indica se há interrupção entre prioridades

    def mg1(self):
        """
        Calcula as principais métricas do modelo M/G/1.
        Retorna rho, L, Lq, W, Wq.
        """
        # Probabilidade do sistema estar vazio 
        p0 = 1 - self.rho
        # Fórmula de Polzeck (var já é variância, não elevar ao quadrado)
        Lq = (math.pow(self.lam, 2) * self.var + math.pow(self.rho, 2)) / (2 * (1 - self.rho))
        # Número médio de clientes no sistema
        L = self.rho + Lq
        # Tempo médio de espera na fila
        if self.lam == 0:
            Wq = 0.0
        else:
            Wq = Lq / self.lam
        # Tempo médio no sistema (espera + atendimento)
        W = Wq + 1 / self.mi
        return self.rho, L, Lq, W, Wq

    def mg1_prioridades(self):
        """
        Calcula as métricas do modelo M/G/1 com prioridades.
        retorna listas de Lq_k, L, Wq, W por prioridade.
        """
        resultados = []
        for i,lam in enumerate(self.lam_list):
            rho = self.rho_list[i]
            # Cálculo de Lq_k comas taxas de chegada e atendimento
            Lq_k = (math.pow(lam,2) * self.var + math.pow(rho,2)) / (2 * (1 - self.rho))
            #Numero medio de clientes
            L = rho + Lq_k
            #Tempo medio na fila
            Wq = Lq_k / lam if lam != 0 else 0.0
            #Tempo medio no sistema para cada prioridade
            W = Wq + 1 / self.mi
            resultados.append((Lq_k, L, Wq, W))
        return resultados



    def mg1_print(self):
        """
        Mostra os resultados do modelo M/G/1 com frases explicativas.
        """
        if self.lam_list is None: # Sem prioridades
            try:
                rho, L, Lq, W, Wq = self.mg1()
                print(f"Modelo M/G/1:")
                print(f"Taxa de utilização (ρ): {rho:.4f}")
                print(f"Número médio de clientes na fila (Lq): {Lq:.4f}")
                print(f"Número médio de clientes no sistema (L): {L:.4f}")
                print(f"Tempo médio de espera na fila (Wq): {Wq:.4f}")
                print(f"Tempo médio no sistema (W): {W:.4f}")
            except ValueError as e:
                print(e)
        else: # Com prioridades
            try:
                resultados = self.mg1_prioridades()
                print(f"Modelo M/G/1 com Prioridades:")
                for i, (Lq_k, L, Wq, W) in enumerate(resultados):
                    print(f"\nPrioridade {i+1}:")
                    print(f"Número médio de clientes na fila (Lq_{i+1}): {Lq_k:.4f}")
                    print(f"Número médio de clientes no sistema (L_{i+1}): {L:.4f}")
                    print(f"Tempo médio de espera na fila (Wq_{i+1}): {Wq:.4f}")
                    print(f"Tempo médio no sistema (W_{i+1}): {W:.4f}")
            except ValueError as e:
                print(e)


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
    def __init__(self, lam, mi, s = None, var = None):
        """
        Inicializa o modelo com seus parâmetros básicos.
        lam = Taxa media de chegada(λ) para o sistema de filas
        mi : Taxa media de atendimento (μ)
        s : Numero de servidores (para M/M/s)
        var : Variancia do tempo de atendimento 
        """
        self.lam = lam # 
        self.mi = mi 
        self.s = s
        self.var = var

        #Calculando p 
        self.rho = lam / (mi*s if s else mi) # p para MM1 ou mms se o valor de s nao for definodo
        #Verificaçao de estabilidade do sistema
        if self.rho >= 1:
            raise ValueError("O sistema está instável (ρ >= 1). Ajuste as taxas de chegada ou atendimento.")
        
        def mm1(self):
            """
            Calcula as metricas do modelo M/M/1
            """
            #Numero medio de clientes do sistema(L)
            L = self.lam / (self.mi - self.lam)
            #Numero medio de clientes na fila
            Lq = (math.pow(self.lam, 2) / (self.mi * (self.mi - self.lam)))
            #Tempo medio no sistema(W)
            W = 1 / (self.mi - self.lam)
            #Tempo medio na fila(Wq)
            Wq = self.lam / (self.mi * (self.mi - self.lam))
            return L, Lq, W, Wq
        
        def mms(self):
            """
            Calcula as metricas do modelo M/M/s
            """
            #Calculo de P0
            P0 = sum((math.pow(self.lam / self.mi, n) / factorial(n)) for n in range(self.s))
            P0 += (math.pow(self.lam / self.mi, self.s) / (factorial(self.s) * (1 - self.rho)))
            #Probabilidade do sistema estar vazio
            P0 = 1 / P0
            #Numero medio de clientes na fila(Lq) no sistema(L) para M/M/s > 1
            L = self.lam / self.mi * (1 + (self.lam / self.mi) ** self.s / (math.factorial(self.s) * (1 - self.rho) ** 2))
            Lq = (self.lam ** 2) / (self.mi * (self.mi - self.lam))
            W = 1 / (self.mi - self.lam)
            Wq = Lq / self.lam
            return P0, L, Lq, W, Wq
        
        def resultado(self):
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
            else: #Se o numero de servidores for fornecido
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
            



#Testando os códigos
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
                     



