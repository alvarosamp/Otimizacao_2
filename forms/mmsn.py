import math
from math import factorial

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