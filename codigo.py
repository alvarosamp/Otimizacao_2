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


#Testando os códigos
if __name__ == "__main__":
    # Exemplo sem prioridades
    modelo_simples = Mg1(lam=2, mi=5, var=0.04)
    modelo_simples.mg1_print()

    print("\n" + "="*50 + "\n")

    # Exemplo com prioridades
    modelo_prioridades = Mg1(lam=3, mi=6, var=0.05, lam_list=[1, 1, 1], interrupt=True)
    modelo_prioridades.mg1_print()



