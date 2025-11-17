import math
from math import factorial

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