import math
from math import factorial

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
