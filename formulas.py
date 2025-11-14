import math
from math import factorial

# Classe M/G/1
class Mg1:
    """
    Modelo de Fila M/G/1 com e sem Prioridades 
    ---------------------
    Fórmulas sem prioridades (Pollaczek-Khintchine):
    (Ref: Teoria... MG1... p. 5) [cite: 91, 92, 93]
        ρ  = λ / μ
        Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)]
        L  = ρ + Lq
        Wq = Lq / λ
        W  = Wq + (1 / μ)

    Fórmulas com prioridades (NÃO PREEMPTIVO, M/G/1):
    (Ref: Teoria... MG1... p. 19, Ex. 2) [cite: 241, 242]
        Assume E(S) e V(S) podem ser diferentes por classe (mi_list, var_list)
        OU E(S)=1/μ e V(S)=var para todas (mi, var únicos)
    
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
                                     *AVISO: M/G/1 Preemptivo não está implementado.*
        """
        self.mi = mi      # taxa média de atendimento (μ)
        self.var = var    # variância do tempo de atendimento (σ²)
        
        if self.mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero")

        if lam_list:  # Modelo com prioridades
            self.lam_list = lam_list
            self.lam = sum(lam_list)  # λ total é a soma das taxas
            # ρ para cada prioridade, assumindo μ único
            self.rho_list = [l / self.mi for l in lam_list]
        else: # Modelo sem prioridades
            self.lam_list = None
            self.lam = lam  # usa o λ total fornecido
            self.rho_list = None

        self.rho = self.lam / self.mi # Fator de utilização global (ρ)

        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas de chegada ou atendimento.")

        self.interrupt = interrupt

    def mg1(self):
        """
        Calcula as métricas do modelo M/G/1 (sem prioridades).
        Fórmulas de Pollaczek-Khintchine (Ref: Teoria... MG1... p. 5) [cite: 91, 92, 93]
        
        Retorna:
        tuple: (rho, L, Lq, W, Wq)
        """
        p0 = 1 - self.rho
        
        # Lq = (λ² * σ² + ρ²) / [2 * (1 - ρ)] [cite: 91]
        lq = (math.pow(self.lam, 2) * self.var + math.pow(self.rho, 2)) / (2 * (1 - self.rho))
        
        # L = ρ + Lq [cite: 93]
        l = self.rho + lq
        
        # Wq = Lq / λ [cite: 92]
        wq = lq / self.lam if self.lam != 0 else 0.0
        
        # W = Wq + (1 / μ) [cite: 93]
        w = wq + (1 / self.mi)
        
        return self.rho, l, lq, w, wq

    def mg1_prioridades_nao_preemptivo(self):
        """
        Calcula as métricas do modelo M/G/1 com prioridades NÃO PREEMPTIVO.
        (Ref: Teoria... MG1... p. 19, Ex. 2) [cite: 241, 242]
        
        Esta implementação assume E(S) = 1/μ e Var(S) = self.var (únicos) 
        para TODAS as classes de prioridade.
        
        Retorna:
        list: Lista de tuplas [(Lq_k, L_k, Wq_k, W_k), ...] para cada prioridade.
        """
        resultados = []
        
        # E(S²) = V(S) + E(S)²
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
            
            # Wq_k = A / [2 * (1 - R_{k-1}) * (1 - R_k)] [cite: 241, 242]
            denominador = 2 * (1 - r_sum_anterior) * (1 - r_sum_atual)
            
            if denominador <= 0 or (1 - r_sum_atual) <= 0:
                wq_k = float('inf')
                w_k = float('inf')
                lq_k = float('inf')
                l_k = float('inf')
            else:
                wq_k = a / denominador
                w_k = wq_k + (1 / self.mi) # W = Wq + E(S)
                lq_k = lam_k * wq_k       # Lq = λ * Wq
                l_k = lam_k * w_k         # L = λ * W
                
            resultados.append((lq_k, l_k, wq_k, w_k))
            
            r_sum_anterior = r_sum_atual # Atualiza R_{k-1} para a próxima iteração
            
        return resultados

    def mg1_print(self):
        """
        Exibe os resultados do modelo M/G/1 formatados no console.
        """
        if self.lam_list is None:  # Se não for modelo com prioridades
            try:
                rho, l, lq, w, wq = self.mg1()
                print(f"--- Modelo M/G/1 (Sem Prioridades) ---")
                print(f"Taxa de utilização (ρ): {rho:.4f}")
                print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
                print(f"Número médio de clientes no sistema (L): {l:.4f}")
                print(f"Tempo médio de espera na fila (Wq): {wq:.4f}")
                print(f"Tempo médio no sistema (W): {w:.4f}")
            except ValueError as e:
                print(e)
        else:  # Se for modelo com prioridades
            if self.interrupt:
                print(f"--- Modelo M/G/1 com Prioridades (COM Interrupção) ---")
                print("AVISO: O cálculo para M/G/1 com prioridades PREEMPTIVAS (com interrupção)")
                print("       não está implementado nesta classe, pois requer fórmulas M/M/1.")
                return

            try:
                print(f"--- Modelo M/G/1 com Prioridades (SEM Interrupção) ---")
                print(f"Taxa de utilização TOTAL (ρ_total): {self.rho:.4f}")
                
                resultados = self.mg1_prioridades_nao_preemptivo()
                
                if resultados:
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
    (Ref: Teoria... Modelo MMs... p. 38-39, 46, 48) [cite: 793, 795, 800, 802, 873, 891, 892, 893, 894]
    """
    def __init__(self, lam, mi, s=1):
        self.lam = lam
        self.mi = mi
        self.s = s

        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        if s <= 0 or not isinstance(s, int):
            raise ValueError("s (número de servidores) deve ser um inteiro positivo.")

        self.rho = lam / (mi * s) # Fator de utilização [cite: 868]

        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas de chegada, atendimento ou número de servidores.")

    def mm1(self):
        """Métricas M/M/1 (s=1)"""
        # (Ref: Teoria... Modelo MMs... p. 38-39) [cite: 793, 795, 800, 802]
        l = self.lam / (self.mi - self.lam)                   # [cite: 793]
        lq = (math.pow(self.lam, 2) / (self.mi * (self.mi - self.lam))) # [cite: 795]
        w = 1 / (self.mi - self.lam)                          # [cite: 800]
        wq = self.lam / (self.mi * (self.mi - self.lam))      # [cite: 802]
        return 1 - self.rho, l, lq, w, wq                     # P0 = 1 - rho [cite: 771]

    def mms(self):
        """Métricas M/M/s (s>1)"""
        # (Ref: Teoria... Modelo MMs... p. 46, 48) [cite: 873, 891, 892, 893, 894]
        
        r = self.lam / self.mi  # (λ/μ)
        
        # --- Cálculo de P0 --- [cite: 873]
        soma_p0 = 0.0
        for n in range(self.s):
            soma_p0 += (math.pow(r, n) / factorial(n))
        termo_s = (math.pow(r, self.s) / factorial(self.s)) * (1 / (1 - self.rho))
        p0 = 1 / (soma_p0 + termo_s)
        
        # --- Cálculo de Lq --- [cite: 891]
        numerador_lq = p0 * math.pow(r, self.s) * self.rho
        denominador_lq = factorial(self.s) * math.pow(1 - self.rho, 2)
        lq = numerador_lq / denominador_lq
        
        # --- Outras métricas --- [cite: 892, 893, 894]
        wq = lq / self.lam        # [cite: 892]
        w = wq + (1 / self.mi)    # [cite: 894]
        l = lq + r                # [cite: 893]
        
        return p0, l, lq, w, wq

    def resultado(self):
        """Exibe os resultados formatados no console."""
        try:
            if self.s == 1:
                p0, l, lq, w, wq = self.mm1()
                print(f"--- Modelo M/M/1 ---")
                print(f"Taxa de utilização (ρ): {self.rho:.4f}")
                print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
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
    (Ref: Teoria... MMsK e MMsN... p. 5-6) [cite: 1031, 1034, 1039, 1041, 1042]
    """
    def __init__(self, lam, mi, k):
        self.lam = lam
        self.mi = mi
        self.k = k
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.rho = lam / mi # Taxa de tráfego (ρ = λ/μ) [cite: 1032]

    def mm1k(self):
        """Calcula as métricas do modelo M/M/1/K."""
        if self.rho == 1.0:
            p0 = 1 / (self.k + 1)
            pk = p0
            l = self.k / 2
        else:
            # P0 = (1-ρ) / (1 - ρ^(K+1)) [cite: 1031]
            p0 = (1 - self.rho) / (1 - math.pow(self.rho, self.k + 1))
            # Pk = P0 * ρ^K [cite: 1034]
            pk = p0 * math.pow(self.rho, self.k)
            # L = [ρ / (1-ρ)] - [(K+1)ρ^(K+1) / (1-ρ^(K+1))] [cite: 1042]
            termo1 = self.rho / (1 - self.rho)
            termo2 = ((self.k + 1) * math.pow(self.rho, self.k + 1)) / (1 - math.pow(self.rho, self.k + 1))
            l = termo1 - termo2
        
        # λ_barra (taxa de chegada efetiva) = λ(1 - Pk) [cite: 1041]
        lam_efetiva = self.lam * (1 - pk)
        
        # Lq = L - (1 - P0) [cite: 1039]
        lq = l - (1 - p0)
        
        # W = L / λ_barra [cite: 1044]
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # Wq = Lq / λ_barra [cite: 1041]
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0

        return p0, pk, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """Exibe os resultados formatados no console."""
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
    (Ref: Teoria... MMsK e MMsN... p. 11-12) [cite: 1105, 1109, 1112, 1118, 1119, 1120]
    Requisito: K >= s
    """
    def __init__(self, lam, mi, s, k):
        if k < s:
            raise ValueError(f"K ({k}) deve ser maior ou igual a s ({s}).")
        self.lam = lam
        self.mi = mi
        self.s = s
        self.k = k
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.r = lam / mi      # λ/μ
        self.rho = lam / (s * mi)  # ρ = λ/(sμ) [cite: 1110]

    def mmsk(self):
        """Calcula as métricas do modelo M/M/s/K."""
        
        # --- Cálculo de P0 --- [cite: 1105]
        # 1/P0 = [ Σ_{n=0}^{s-1} (r^n / n!) ] + [ (r^s / s!) * Σ_{j=0}^{K-s} ρ^j ]
        soma_p0_1 = 0.0
        for n in range(self.s):
            soma_p0_1 += math.pow(self.r, n) / factorial(n)
            
        soma_p0_2_geometrica = 0.0
        if self.rho == 1.0:
            soma_p0_2_geometrica = self.k - self.s + 1
        else:
            soma_p0_2_geometrica = (1 - math.pow(self.rho, self.k - self.s + 1)) / (1 - self.rho)
        termo_s = (math.pow(self.r, self.s) / factorial(self.s)) * soma_p0_2_geometrica
        p0 = 1 / (soma_p0_1 + termo_s)
        
        # --- Pk (Probabilidade de perda) --- [cite: 1112]
        # Pk = (r^K / (s! * s^(K-s))) * P0
        pk = (math.pow(self.r, self.k) / (factorial(self.s) * math.pow(self.s, self.k - self.s))) * p0
        
        # --- Lq --- [cite: 1118]
        if self.rho == 1.0:
             # Caso especial ρ = 1
             lq = ( (p0 * math.pow(self.r, self.s)) / factorial(self.s) ) * ( ( (self.k - self.s) * (self.k - self.s + 1) ) / 2 )
        else:
            fator_comum = (p0 * math.pow(self.r, self.s) * self.rho) / (factorial(self.s) * math.pow(1 - self.rho, 2))
            termo_chaves = 1 - math.pow(self.rho, self.k - self.s) - (self.k - self.s) * math.pow(self.rho, self.k - self.s) * (1 - self.rho)
            lq = fator_comum * termo_chaves

        # --- Outras métricas --- [cite: 1119, 1120, 1124]
        lam_efetiva = self.lam * (1 - pk)   # [cite: 1119]
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0 # [cite: 1119]
        w = wq + (1 / self.mi)            # W = Wq + E(S)
        l = lam_efetiva * w               # L = λ_barra * W [cite: 1124]

        return p0, pk, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """Exibe os resultados formatados no console."""
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
    (Ref: Teoria... MMsK e MMsN... p. 16-17) [cite: 1173, 1176, 1180]
    """
    def __init__(self, lam_por_cliente, mi, n_pop):
        self.lam_por_cliente = lam_por_cliente # λ por cliente
        self.mi = mi
        self.n_pop = n_pop # N
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
        self.r = lam_por_cliente / mi # λ/μ

    def mm1n(self):
        """Calcula as métricas do modelo M/M/1/N."""
        # (Ref: Teoria... MMsK e MMsN... p. 16-17) [cite: 1173, 1176, 1180]

        # --- Cálculo de P0 --- [cite: 1173]
        soma_p0 = 0.0
        for n in range(self.n_pop + 1):
            termo_n = (factorial(self.n_pop) / factorial(self.n_pop - n)) * math.pow(self.r, n)
            soma_p0 += termo_n
        p0 = 1 / soma_p0

        # --- L (Número médio no sistema) --- [cite: 1180]
        l = self.n_pop - (self.mi / self.lam_por_cliente) * (1 - p0)
        
        # --- Lq (Número médio na fila) --- [cite: 1180]
        lq = self.n_pop - ((self.lam_por_cliente + self.mi) / self.lam_por_cliente) * (1 - p0)
        
        # --- Outras métricas --- [cite: 1180]
        lam_efetiva = self.lam_por_cliente * (self.n_pop - l) # [cite: 1180]
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0
        
        return p0, l, lq, w, wq, lam_efetiva
        
    def resultado(self):
        """Exibe os resultados formatados no console."""
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
    (Ref: Teoria... MMsK e MMsN... p. 21-22) [cite: 1218, 1224, 1229, 1230, 1231, 1232]
    Requisito: N >= s
    """
    def __init__(self, lam_por_cliente, mi, s, n_pop):
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
        """Calcula as métricas do modelo M/M/s/N."""
        # (Ref: Teoria... MMsK e MMsN... p. 21-22) [cite: 1218, 1224, 1229, 1230, 1231, 1232]

        # --- Cálculo de P0 --- [cite: 1218]
        soma_p0_1 = 0.0
        for n in range(self.s):
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
        l = 0.0
        
        # --- L (Número médio no sistema) --- [cite: 1231]
        # L = Σ_{n=1}^{N} n * Pn
        # Pn para n < s (1 <= n <= s-1) [cite: 1224]
        for n in range(1, self.s):
            comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(n))
            pn = comb * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn
            
        # Pn para n >= s (s <= n <= N) [cite: 1224]
        for n in range(self.s, self.n_pop + 1):
            fator_comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(self.s))
            fator_pot = math.pow(self.s, n - self.s)
            pn = (fator_comb / fator_pot) * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn

        # --- Outras métricas --- [cite: 1229, 1230, 1232]
        lam_efetiva = self.lam_por_cliente * (self.n_pop - l) # [cite: 1230]
        lq = l - (lam_efetiva / self.mi)        # [cite: 1229]
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0  # [cite: 1232]
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0# [cite: 1230]
        
        return p0, l, lq, w, wq, lam_efetiva

    def resultado(self):
        """Exibe os resultados formatados no console."""
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


# Classe M/M/1 Prioridade Preemptiva (COM Interrupção)
class Mm1PrioridadePreemptiva:
    """
    Modelo de Fila M/M/1 com Prioridades COM Interrupção (Preemptivo)
    (Ref: Teoria... MG1... p. 13, Ex. 1, S=1) 
    """
    def __init__(self, lam_list, mi):
        self.lam_list = lam_list
        self.mi = mi
        self.n_classes = len(lam_list)
        
        # ρ para cada prioridade
        self.rho_list = [l / self.mi for l in lam_list]
        # ρ total
        self.rho_total = sum(self.rho_list)
        
        if self.rho_total >= 1:
            raise ValueError(f"O sistema está instável (ρ_total = {self.rho_total:.4f} >= 1).")
            
    def calcular_metricas(self):
        """
        Calcula as métricas W, Wq, L, Lq para cada classe.
        Usa as fórmulas simplificadas para S=1 do Exemplo 1 
        """
        resultados = []
        lam_acumulada = 0.0
        
        for i in range(self.n_classes):
            lam_i = self.lam_list[i]
            
            # Cálculo de W_k (Tempo no sistema)
            # W_k = μ / [ (μ - Σλ_{j=1}^{k-1}) * (μ - Σλ_{j=1}^{k}) ]
            
            # Termo (μ - Σλ_{j=1}^{k-1})
            denominador_1 = self.mi - lam_acumulada
            
            # Atualiza λ acumulada para esta classe
            lam_acumulada += lam_i
            
            # Termo (μ - Σλ_{j=1}^{k})
            denominador_2 = self.mi - lam_acumulada
            
            if denominador_1 <= 0 or denominador_2 <= 0:
                w_k = float('inf')
                wq_k = float('inf')
                l_k = float('inf')
                lq_k = float('inf')
            else:
                if i == 0:
                     # W_1 = 1 / (μ - λ_1) [cite: 171]
                    w_k = 1 / denominador_2
                else:
                    # W_k = μ / (denominador_1 * denominador_2) [cite: 174, 175]
                    w_k = self.mi / (denominador_1 * denominador_2)
            
                # Métricas derivadas
                wq_k = w_k - (1 / self.mi) # Wq = W - E(S) [cite: 172]
                l_k = lam_i * w_k         # L = λ * W [cite: 173]
                lq_k = lam_i * wq_k
            
            resultados.append((lq_k, l_k, wq_k, w_k))
            
        return resultados

    def resultado(self):
        """Exibe os resultados formatados no console."""
        print(f"--- Modelo M/M/1 com Prioridades (COM Interrupção) ---")
        print(f"Taxa de utilização TOTAL (ρ_total): {self.rho_total:.4f}")
        try:
            resultados = self.calcular_metricas()
            for i, (lq_k, l, wq, w) in enumerate(resultados):
                print(f"\nPrioridade {i+1} (λ_{i+1} = {self.lam_list[i]}, ρ_{i+1} = {self.rho_list[i]:.4f}):")
                print(f"  Número médio na fila (Lq_{i+1}): {lq_k:.4f}")
                print(f"  Número médio no sistema (L_{i+1}): {l:.4f}")
                print(f"  Tempo médio na fila (Wq_{i+1}): {wq:.4f}")
                print(f"  Tempo médio no sistema (W_{i+1}): {w:.4f}")
        except ValueError as e:
            print(e)