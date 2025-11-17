import math
from math import factorial

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