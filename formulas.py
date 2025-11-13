import math
from math import factorial

# Classe M/G/1
class Mg1:
    """
    Modelo de Fila M/G/1 com e sem Prioridades 
    ---------------------
    Fórmulas sem prioridades (Pollaczek-Khintchine):
    (Ref: PDF ...Modelo MG1... p. 5)
        ρ  = λ / μ
        Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)]
        L  = ρ + Lq
        Wq = Lq / λ
        W  = Wq + (1 / μ)

    Fórmulas com prioridades (não preemptivo, M/G/1):
    (Ref: PDF ...Modelo MG1... p. 19, Ex. 2)
        A = Σ [λ_i * (V(S_i) + E(S_i)²)]
        Wq_k = A / [2 * (1 - R_{k-1}) * (1 - R_k)]
        onde R_k = Σ_{i=1}^{k} ρ_i
    """

    def __init__(self, lam, mi, var, lam_list=None, interrupt=False):
        """
        Inicializa o modelo com seus parâmetros básicos.
        
        Parâmetros:
        lam (float): Taxa média de chegada total (λ). *Ignorado se lam_list for fornecido.*
        mi (float): Taxa média de atendimento (μ).
        var (float): Variância do tempo de atendimento (σ²).
        lam_list (list, opcional): Lista de taxas de chegada (λ_i) por classe de prioridade.
        interrupt (bool, opcional): Define se o modelo de prioridades é preemptivo (com interrupção).
        """
        self.mi = mi      # taxa média de atendimento (μ)
        self.var = var    # variância do tempo de atendimento (σ²)
        
        # Validações básicas
        if self.mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero")

        # Configuração das taxas de chegada e utilização
        if lam_list:  # Modelo com prioridades
            self.lam_list = lam_list
            self.lam = sum(lam_list)  # λ total é a soma das taxas de prioridade
            self.rho_list = [l / self.mi for l in lam_list]  # ρ para cada prioridade
        else: # Modelo sem prioridades
            self.lam_list = None
            self.lam = lam  # usa o λ total fornecido
            self.rho_list = None

        # Fator de utilização global (ρ)
        self.rho = self.lam / self.mi

        # Verificação de estabilidade (não se aplica a modelos finitos K ou N)
        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas de chegada ou atendimento.")

        self.interrupt = interrupt

    def mg1(self):
        """
        Calcula as métricas do modelo M/G/1 (sem prioridades).
        Fórmulas de Pollaczek-Khintchine (Ref: PDF ...Modelo MG1... p. 5)
        
        Retorna:
        tuple: (rho, L, Lq, W, Wq)
        """
        # Probabilidade do sistema estar vazio 
        p0 = 1 - self.rho
        
        # Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)]
        lq = (math.pow(self.lam, 2) * self.var + math.pow(self.rho, 2)) / (2 * (1 - self.rho))
        
        # L = ρ + Lq
        l = self.rho + lq
        
        # Wq = Lq / λ
        wq = lq / self.lam if self.lam != 0 else 0.0
        
        # W = Wq + (1 / μ)
        w = wq + (1 / self.mi)
        
        return self.rho, l, lq, w, wq

    def mg1_prioridades(self):
        """
        Calcula as métricas do modelo M/G/1 com prioridades.
        Implementa o modelo NÃO PREEMPTIVO (sem interrupção).
        (Ref: PDF ...Modelo MG1... p. 19, Ex. 2)
        
        Assume que E(S) = 1/μ e Var(S) = self.var são os mesmos para todas as classes.
        
        Retorna:
        list: Lista de tuplas [(Lq_k, L_k, Wq_k, W_k), ...] para cada prioridade.
        """
        if self.interrupt:
            # As fórmulas para M/G/1 com interrupção (preemptivo) não estão
            # claramente definidas nos PDFs fornecidos. As p.10-13 são para M/M/s.
            print("AVISO: O cálculo para M/G/1 com prioridades PREEMPTIVAS (com interrupção) não está implementado.")
            return None

        # --- M/G/1 Prioridades NÃO PREEMPTIVO ---
        resultados = []
        
        # E(S²) = V(S) + E(S)²
        # Assumindo E(S) = 1/μ e V(S) = self.var para todas as classes
        e_s2 = self.var + math.pow(1 / self.mi, 2)
        
        # A = Σ [λ_i * E(S_i²)]
        # Como E(S_i²) é o mesmo para todos, A = E(S²) * Σ(λ_i) = E(S²) * self.lam
        a = self.lam * e_s2
        
        r_sum_anterior = 0.0  # R_{k-1} = Σ_{i=1}^{k-1} ρ_i
        
        for i in range(len(self.lam_list)):
            lam_k = self.lam_list[i]
            rho_k = self.rho_list[i]
            
            # R_k = Σ_{i=1}^{k} ρ_i
            r_sum_atual = r_sum_anterior + rho_k
            
            # Wq_k = A / [2 * (1 - R_{k-1}) * (1 - R_k)]
            denominador = 2 * (1 - r_sum_anterior) * (1 - r_sum_atual)
            
            if denominador <= 0 or (1 - r_sum_atual) <= 0:
                # Sistema instável para esta classe de prioridade ou superior
                wq_k = float('inf')
                w_k = float('inf')
                lq_k = float('inf')
                l_k = float('inf')
            else:
                wq_k = a / denominador
                # W_k = Wq_k + E(S)
                w_k = wq_k + (1 / self.mi)
                # Lq_k = λ_k * Wq_k
                lq_k = lam_k * wq_k
                # L_k = λ_k * W_k
                l_k = lam_k * w_k
                
            resultados.append((lq_k, l_k, wq_k, w_k))
            
            # Atualiza R_{k-1} para a próxima iteração
            r_sum_anterior = r_sum_atual
            
        return resultados

    def mg1_print(self):
        """
        Exibe os resultados do modelo M/G/1 formatados no console.
        """
        if self.lam_list is None:  # Se não for modelo com prioridades
            try:
                rho, l, lq, w, wq = self.mg1()  # Calcula as métricas
                print(f"--- Modelo M/G/1 (Sem Prioridades) ---")
                print(f"Taxa de utilização (ρ): {rho:.4f}")
                print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
                print(f"Número médio de clientes no sistema (L): {l:.4f}")
                print(f"Tempo médio de espera na fila (Wq): {wq:.4f}")
                print(f"Tempo médio no sistema (W): {w:.4f}")
            except ValueError as e:
                print(e)
        else:  # Se for modelo com prioridades
            try:
                print(f"--- Modelo M/G/1 com Prioridades ({'COM' if self.interrupt else 'SEM'} Interrupção) ---")
                print(f"Taxa de utilização TOTAL (ρ_total): {self.rho:.4f}")
                
                resultados = self.mg1_prioridades()  # Calcula as métricas
                
                if resultados:
                    # Exibe os resultados para cada prioridade
                    for i, (lq_k, l, wq, w) in enumerate(resultados):
                        print(f"\nPrioridade {i+1} (λ_{i+1} = {self.lam_list[i]}, ρ_{i+1} = {self.rho_list[i]:.4f}):")
                        print(f"  Número médio na fila (Lq_{i+1}): {lq_k:.4f}")
                        print(f"  Número médio no sistema (L_{i+1}): {l:.4f}")
                        print(f"  Tempo médio na fila (Wq_{i+1}): {wq:.4f}")
                        print(f"  Tempo médio no sistema (W_{i+1}): {w:.4f}")
            except ValueError as e:
                print(e)


# Classe M/M/1 e M/M/s
class Mm:
    """
    Modelo de Fila M/M/1 e M/M/s (infinitos)
    ---------------------
    Fórmulas M/M/1 (Ref: PDF ...Modelo MMs... p. 38-39):
        ρ = λ / μ
        L = λ / (μ - λ)
        Lq = (λ²) / (μ(μ - λ))
        W = 1 / (μ - λ)
        Wq = λ / (μ(μ - λ))

    Fórmulas M/M/s (Ref: PDF ...Modelo MMs... p. 46, 48):
        ρ = λ / (sμ)
        P0 = 1 / [ (Σ_{n=0}^{s-1} (λ/μ)^n / n!) + ( (λ/μ)^s / s! ) * (1 / (1 - ρ)) ]
        Lq = (P0 * (λ/μ)^s * ρ) / (s! * (1 - ρ)²)
        Wq = Lq / λ
        W  = Wq + 1/μ
        L  = Lq + λ/μ
    """
    def __init__(self, lam, mi, s=1):
        """
        Inicializa o modelo M/M/1 ou M/M/s.
        
        Parâmetros:
        lam (float): Taxa média de chegada (λ).
        mi (float): Taxa média de atendimento (μ) por servidor.
        s (int, opcional): Número de servidores (default=1).
        """
        self.lam = lam  # Taxa de chegada (λ)
        self.mi = mi    # Taxa de atendimento (μ)
        self.s = s      # Número de servidores

        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        if s <= 0 or not isinstance(s, int):
            raise ValueError("s (número de servidores) deve ser um inteiro positivo.")

        # Fator de utilização (ρ)
        self.rho = lam / (mi * s)

        # Verificação de estabilidade
        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas de chegada, atendimento ou número de servidores.")

    def mm1(self):
        """
        Calcula as métricas do modelo M/M/1 (s=1).
        (Ref: PDF ...Modelo MMs... p. 38-39)
        
        Retorna:
        tuple: (P0, L, Lq, W, Wq)
        """
        # L = λ / (μ - λ)
        l = self.lam / (self.mi - self.lam)
        # Lq = λ² / (μ(μ - λ))
        lq = (math.pow(self.lam, 2) / (self.mi * (self.mi - self.lam)))
        # W = 1 / (μ - λ)
        w = 1 / (self.mi - self.lam)
        # Wq = λ / (μ(μ - λ))
        wq = self.lam / (self.mi * (self.mi - self.lam))
        
        # P0 = 1 - ρ
        return 1 - self.rho, l, lq, w, wq

    def mms(self):
        """
        Calcula as métricas do modelo M/M/s (s>1).
        (Ref: PDF ...Modelo MMs... p. 46, 48)

        Retorna:
        tuple: (P0, L, Lq, W, Wq)
        """
        
        r = self.lam / self.mi  # (λ/μ)
        
        # --- Cálculo de P0 ---
        # (Ref: PDF ...Modelo MMs... p. 46)
        soma_p0 = 0.0
        for n in range(self.s):
            soma_p0 += (math.pow(r, n) / factorial(n))
            
        termo_s = (math.pow(r, self.s) / factorial(self.s)) * (1 / (1 - self.rho))
        p0 = 1 / (soma_p0 + termo_s)
        
        # --- Cálculo de Lq ---
        # (Ref: PDF ...Modelo MMs... p. 48)
        # Lq = (P0 * (λ/μ)^s * ρ) / (s! * (1 - ρ)²)
        numerador_lq = p0 * math.pow(r, self.s) * self.rho
        denominador_lq = factorial(self.s) * math.pow(1 - self.rho, 2)
        lq = numerador_lq / denominador_lq
        
        # --- Outras métricas ---
        # (Ref: PDF ...Modelo MMs... p. 48)
        
        # Wq = Lq / λ
        wq = lq / self.lam
        
        # W = Wq + 1/μ
        w = wq + (1 / self.mi)
        
        # L = Lq + λ/μ
        l = lq + r
        
        return p0, l, lq, w, wq

    def resultado(self):
        """
        Exibe os resultados de M/M/1 ou M/M/s formatados no console.
        """
        try:
            if self.s == 1:
                p0, l, lq, w, wq = self.mm1()
                print(f"--- Modelo M/M/1 ---")
                print(f"Taxa de utilização (ρ): {self.rho:.4f}")
                print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
                print(f"Número médio de clientes no sistema (L): {l:.4f}")
                print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
                print(f"Tempo médio no sistema (W): {w:.4f}")
                print(f"Tempo médio na fila (Wq): {wq:.4f}")
            else:
                p0, l, lq, w, wq = self.mms()
                print(f"--- Modelo M/M/{self.s} ---")
                print(f"Taxa de utilização (ρ): {self.rho:.4f}")
                print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
                print(f"Número médio de clientes no sistema (L): {l:.4f}")
                print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
                print(f"Tempo médio no sistema (W): {w:.4f}")
                print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(e)


# Classe M/M/1/K
class Mm1k:
    """
    Modelo de Fila M/M/1/K (Capacidade Finita K)
    (Ref: PDF ...MMsK e MMsN... p. 5-6)
    """
    def __init__(self, lam, mi, k):
        """
        Inicializa o modelo M/M/1/K.
        
        Parâmetros:
        lam (float): Taxa média de chegada (λ).
        mi (float): Taxa média de atendimento (μ).
        k (int): Capacidade máxima do sistema (K).
        """
        self.lam = lam
        self.mi = mi
        self.k = k
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.rho = lam / mi # Taxa de tráfego (ρ = λ/μ)

    def mm1k(self):
        """
        Calcula as métricas do modelo M/M/1/K.
        (Ref: PDF ...MMsK e MMsN... p. 5-6)
        
        Retorna:
        tuple: (P0, Pk, L, Lq, W, Wq, λ_efetiva)
        """
        if self.rho == 1.0:
            # Caso especial ρ = 1
            p0 = 1 / (self.k + 1)
            pk = p0 # Pn = 1/(K+1) para todo n
            l = self.k / 2
        else:
            # P0 = (1-ρ) / (1 - ρ^(K+1))
            p0 = (1 - self.rho) / (1 - math.pow(self.rho, self.k + 1))
            # Pk = P0 * ρ^K
            pk = p0 * math.pow(self.rho, self.k)
            # L = [ρ / (1-ρ)] - [(K+1)ρ^(K+1) / (1-ρ^(K+1))]
            termo1 = self.rho / (1 - self.rho)
            termo2 = ((self.k + 1) * math.pow(self.rho, self.k + 1)) / (1 - math.pow(self.rho, self.k + 1))
            l = termo1 - termo2
        
        # λ_barra (taxa de chegada efetiva) = λ(1 - Pk)
        lam_efetiva = self.lam * (1 - pk)
        
        # Lq = L - (1 - P0)
        lq = l - (1 - p0)
        
        # W = L / λ_barra
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # Wq = Lq / λ_barra
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0

        return p0, pk, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """
        Exibe os resultados de M/M/1/K formatados no console.
        """
        print(f"--- Modelo M/M/1/K (K={self.k}) ---")
        print(f"Taxa de tráfego (ρ): {self.rho:.4f}")
        try:
            p0, pk, l, lq, w, wq, lam_efetiva = self.mm1k()
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Probabilidade do sistema estar cheio (Pk): {pk:.4f} (Prob. de perda)")
            print(f"Taxa de chegada efetiva (λ_barra): {lam_efetiva:.4f}")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f}")
            print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(e)


# Classe M/M/s/K
class Mmsk:
    """
    Modelo de Fila M/M/s/K (s servidores, Capacidade Finita K)
    (Ref: PDF ...MMsK e MMsN... p. 11-12)
    Requisito: K >= s
    """
    def __init__(self, lam, mi, s, k):
        """
        Inicializa o modelo M/M/s/K.
        
        Parâmetros:
        lam (float): Taxa média de chegada (λ).
        mi (float): Taxa média de atendimento (μ) por servidor.
        s (int): Número de servidores (s).
        k (int): Capacidade máxima do sistema (K).
        """
        if k < s:
            raise ValueError(f"K ({k}) deve ser maior ou igual a s ({s}).")
        self.lam = lam
        self.mi = mi
        self.s = s
        self.k = k
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.r = lam / mi      # λ/μ
        self.rho = lam / (s * mi)  # ρ = λ/(sμ)

    def mmsk(self):
        """
        Calcula as métricas do modelo M/M/s/K.
        (Ref: PDF ...MMsK e MMsN... p. 11-12)
        
        Retorna:
        tuple: (P0, Pk, L, Lq, W, Wq, λ_efetiva)
        """
        
        # --- Cálculo de P0 ---
        # 1/P0 = [ Σ_{n=0}^{s-1} (r^n / n!) ] + [ (r^s / s!) * Σ_{n=s}^{K} (r^n / (s! s^(n-s))) ]
        # Simplificado para: [ Σ_{n=0}^{s-1} (r^n / n!) ] + [ (r^s / s!) * Σ_{j=0}^{K-s} ρ^j ] (onde j=n-s)
        
        soma_p0_1 = 0.0
        for n in range(self.s):
            soma_p0_1 += math.pow(self.r, n) / factorial(n)
            
        soma_p0_2_geometrica = 0.0
        if self.rho == 1.0:
            # Caso especial ρ = 1 (soma de j=0 a K-s de 1)
            soma_p0_2_geometrica = self.k - self.s + 1
        else:
            # Soma de PG: a1 * (1 - q^n) / (1 - q)
            # Aqui: 1 * (1 - ρ^(K-s+1)) / (1 - ρ)
            soma_p0_2_geometrica = (1 - math.pow(self.rho, self.k - self.s + 1)) / (1 - self.rho)
            
        termo_s = (math.pow(self.r, self.s) / factorial(self.s)) * soma_p0_2_geometrica
        
        p0 = 1 / (soma_p0_1 + termo_s)
        
        # --- Pk (Probabilidade de perda) ---
        # Pk = (r^K / (s! * s^(K-s))) * P0
        pk = (math.pow(self.r, self.k) / (factorial(self.s) * math.pow(self.s, self.k - self.s))) * p0
        
        # --- Lq ---
        # Lq = [ (P0 * r^s * ρ) / (s! * (1-ρ)²) ] * [ 1 - ρ^(K-s) - (K-s)ρ^(K-s)(1-ρ) ]
        
        if self.rho == 1.0:
             # Caso especial ρ = 1, a fórmula de Lq acima falha (divisão por zero).
             # Lq = [ (P0 * r^s) / (s!) ] * [ ( (K-s)(K-s+1) ) / 2 ]
             lq = ( (p0 * math.pow(self.r, self.s)) / factorial(self.s) ) * ( ( (self.k - self.s) * (self.k - self.s + 1) ) / 2 )
        else:
            fator_comum = (p0 * math.pow(self.r, self.s) * self.rho) / (factorial(self.s) * math.pow(1 - self.rho, 2))
            termo_chaves = 1 - math.pow(self.rho, self.k - self.s) - (self.k - self.s) * math.pow(self.rho, self.k - self.s) * (1 - self.rho)
            lq = fator_comum * termo_chaves

        # --- Outras métricas ---
        # λ_barra (taxa de chegada efetiva) = λ(1 - Pk)
        lam_efetiva = self.lam * (1 - pk)
        
        # Wq = Lq / λ_barra
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # W = Wq + 1/μ
        w = wq + (1 / self.mi)
        
        # L = λ_barra * W
        l = lam_efetiva * w
        # (Alternativa L = Lq + λ_barra/μ)

        return p0, pk, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """
        Exibe os resultados de M/M/s/K formatados no console.
        """
        print(f"--- Modelo M/M/{self.s}/K (K={self.k}) ---")
        print(f"Taxa de tráfego (ρ): {self.rho:.4f} (r = {self.r:.4f})")
        try:
            p0, pk, l, lq, w, wq, lam_efetiva = self.mmsk()
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Probabilidade do sistema estar cheio (Pk): {pk:.4f} (Prob. de perda)")
            print(f"Taxa de chegada efetiva (λ_barra): {lam_efetiva:.4f}")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f}")
            print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(e)


# Classe M/M/1/N (População Finita N)
class Mm1n:
    """
    Modelo de Fila M/M/1/N (População Finita N)
    (Ref: PDF ...MMsK e MMsN... p. 16-17)
    """
    def __init__(self, lam_por_cliente, mi, n_pop):
        """
        Inicializa o modelo M/M/1/N.
        
        Parâmetros:
        lam_por_cliente (float): Taxa de chegada por cliente (λ).
        mi (float): Taxa média de atendimento (μ).
        n_pop (int): Tamanho da população (N).
        """
        self.lam_por_cliente = lam_por_cliente # λ por cliente
        self.mi = mi
        self.n_pop = n_pop # N
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.r = lam_por_cliente / mi # λ/μ

    def mm1n(self):
        """
        Calcula as métricas do modelo M/M/1/N.
        (Ref: PDF ...MMsK e MMsN... p. 16-17)
        
        Retorna:
        tuple: (P0, L, Lq, W, Wq, λ_efetiva)
        """

        # --- Cálculo de P0 ---
        # 1/P0 = Σ_{n=0}^{N} [ (N! / (N-n)!) * (λ/μ)^n ]
        soma_p0 = 0.0
        for n in range(self.n_pop + 1):
            termo_n = (factorial(self.n_pop) / factorial(self.n_pop - n)) * math.pow(self.r, n)
            soma_p0 += termo_n
        p0 = 1 / soma_p0

        # --- L (Número médio no sistema) ---
        # L = N - (μ/λ) * (1 - P0)
        l = self.n_pop - (self.mi / self.lam_por_cliente) * (1 - p0)
        
        # --- Lq (Número médio na fila) ---
        # Lq = N - [ (λ+μ)/λ ] * (1 - P0)
        lq = self.n_pop - ((self.lam_por_cliente + self.mi) / self.lam_por_cliente) * (1 - p0)
        
        # --- Outras métricas ---
        # λ_barra (taxa de chegada efetiva) = λ(N - L)
        lam_efetiva = self.lam_por_cliente * (self.n_pop - l)
        
        # W = L / λ_barra
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # Wq = Lq / λ_barra
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0
        
        return p0, l, lq, w, wq, lam_efetiva
        
    def resultado(self):
        """
        Exibe os resultados de M/M/1/N formatados no console.
        """
        print(f"--- Modelo M/M/1/N (População N={self.n_pop}) ---")
        try:
            p0, l, lq, w, wq, lam_efetiva = self.mm1n()
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Taxa de chegada efetiva (λ_barra): {lam_efetiva:.4f}")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f}")
            print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(e)
        

# Classe M/M/s/N (População Finita N)
class Mmsn:
    """
    Modelo de Fila M/M/s/N (s servidores, População Finita N)
    (Ref: PDF ...MMsK e MMsN... p. 21-22)
    Requisito: N >= s
    """
    def __init__(self, lam_por_cliente, mi, s, n_pop):
        """
        Inicializa o modelo M/M/s/N.
        
        Parâmetros:
        lam_por_cliente (float): Taxa de chegada por cliente (λ).
        mi (float): Taxa média de atendimento (μ) por servidor.
        s (int): Número de servidores (s).
        n_pop (int): Tamanho da população (N).
        """
        if n_pop < s:
            raise ValueError(f"N ({n_pop}) deve ser maior ou igual a s ({s}).")
        self.lam_por_cliente = lam_por_cliente # λ por cliente
        self.mi = mi
        self.s = s
        self.n_pop = n_pop # N
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.r = lam_por_cliente / mi # λ/μ
        
        self.p_list = [] # Lista para guardar Pn (P0, P1, ..., PN)

    def mmsn(self):
        """
        Calcula as métricas do modelo M/M/s/N.
        (Ref: PDF ...MMsK e MMsN... p. 21-22)
        
        Retorna:
        tuple: (P0, L, Lq, W, Wq, λ_efetiva)
        """

        # --- Cálculo de P0 ---
        # 1/P0 = [ Σ_{n=0}^{s-1} (N! / (N-n)! n!) * r^n ] + [ Σ_{n=s}^{N} (N! / (N-n)! s! s^(n-s)) * r^n ]
        soma_p0_1 = 0.0
        for n in range(self.s):
            # Usando (N C n) * n! = N! / (N-n)!
            # (N C n) = comb(N, n)
            comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(n))
            termo_n = comb * math.pow(self.r, n)
            soma_p0_1 += termo_n

        soma_p0_2 = 0.0
        for n in range(self.s, self.n_pop + 1):
            fator_comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(self.s))
            fator_pot = math.pow(self.s, n - self.s)
            termo_n = (fator_comb / fator_pot) * math.pow(self.r, n)
            soma_p0_2 += termo_n
            
        p0 = 1 / (soma_p0_1 + soma_p0_2)
        
        self.p_list = [p0]
        
        # --- L (Número médio no sistema) ---
        # L = Σ_{n=1}^{N} n * Pn
        # Precisamos calcular Pn para n=1..N
        
        l = 0.0
        # Pn para n < s (1 <= n <= s-1)
        for n in range(1, self.s):
            comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(n))
            pn = comb * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn
            
        # Pn para n >= s (s <= n <= N)
        for n in range(self.s, self.n_pop + 1):
            fator_comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(self.s))
            fator_pot = math.pow(self.s, n - self.s)
            pn = (fator_comb / fator_pot) * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn

        # --- Outras métricas ---
        # λ_barra (taxa de chegada efetiva) = λ(N - L)
        lam_efetiva = self.lam_por_cliente * (self.n_pop - l)
        
        # Lq = L - (λ_barra / μ)
        lq = l - (lam_efetiva / self.mi)
        
        # W = L / λ_barra
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # Wq = Lq / λ_barra
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0
        
        return p0, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """
        Exibe os resultados de M/M/s/N formatados no console.
        """
        print(f"--- Modelo M/M/{self.s}/N (População N={self.n_pop}) ---")
        try:
            p0, l, lq, w, wq, lam_efetiva = self.mmsn()
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Taxa de chegada efetiva (λ_barra): {lam_efetiva:.4f}")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f}")
            print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(e)
