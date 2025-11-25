import math
from math import factorial

class Mmsk:
    # ... (Seu __init__ permanece inalterado)

    def __init__(self, lam, mi, s, k):
        if k < s:
            raise ValueError(f"K ({k}) deve ser maior ou igual a s ({s}).")
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")
            
        self.lam = lam
        self.mi = mi
        self.s = s
        self.k = k
        self.r = lam / mi      # r = λ/μ
        self.rho = lam / (s * mi)  # ρ = λ/(sμ)

    def prob_n_clientes(self, n: int, p0: float) -> float:
        """Calcula a probabilidade de haver EXATAMENTE 'n' clientes (Pn) para M/M/s/K."""
        if n < 0 or n > self.k:
            return 0.0
            
        r = self.lam / self.mi
        
        if n < self.s:
            # Pn = (r^n / n!) * P0
            return (math.pow(r, n) / factorial(n)) * p0
        else: # self.s <= n <= self.k
            # Pn = (r^s / s! * ρ^(n-s)) * P0
            rho_s = self.lam / (self.s * self.mi)
            
            termo_s = math.pow(r, self.s) / factorial(self.s)
            fator_rho = math.pow(rho_s, n - self.s)
            
            return termo_s * fator_rho * p0

    def mmsk(self):
        """Calcula as métricas do modelo M/M/s/K."""
        
        # --- 1. Cálculo de P0 (permanece inalterado e correto) ---
        soma_p0_1 = 0.0
        for n in range(self.s):
            soma_p0_1 += math.pow(self.r, n) / factorial(n)
            
        soma_p0_2_geometrica = 0.0
        if abs(self.rho - 1.0) < 1e-9:
            soma_p0_2_geometrica = self.k - self.s + 1
        else:
            soma_p0_2_geometrica = (1 - math.pow(self.rho, self.k - self.s + 1)) / (1 - self.rho)
            
        termo_s = (math.pow(self.r, self.s) / factorial(self.s)) * soma_p0_2_geometrica
        inverso_p0 = soma_p0_1 + termo_s
        p0 = 1 / inverso_p0
        
        # --- 2. Cálculo de L (Número Médio no Sistema) ---
        l = 0.0
        for n in range(self.k + 1):
            # L = Σ n * Pn. Chamamos a nova função auxiliar
            pn = self.prob_n_clientes(n, p0)
            l += n * pn
            
        # --- 3. Pk e Lq (Não altera) ---
        # Pk = Pn para n=K
        pk = self.prob_n_clientes(self.k, p0)
        
        # Lq (Permanecemos com a fórmula de Lq para M/M/s/K, pois a fórmula de soma é complexa)
        if abs(self.rho - 1.0) < 1e-9:
             lq = ( (p0 * math.pow(self.r, self.s)) / factorial(self.s) ) * ( ( (self.k - self.s) * (self.k - self.s + 1) ) / 2 )
        else:
            fator_comum = (p0 * math.pow(self.r, self.s) * self.rho) / (factorial(self.s) * math.pow(1 - self.rho, 2))
            termo_chaves = 1 - math.pow(self.rho, self.k - self.s) - (self.k - self.s) * math.pow(self.rho, self.k - self.s) * (1 - self.rho)
            lq = fator_comum * termo_chaves

        # --- 4. CÁLCULO DE W E Wq USANDO O L CORRETO ---
        
        # Métrica de chegada
        lam_efetiva = self.lam * (1 - pk) 
        l_perda = self.lam * pk 
        
        # W (Tempo Médio no Sistema)
        # W = L / λ_efetiva (Fórmula de Little, agora usando L calculado por soma)
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # Wq (Tempo Médio na Fila)
        # Wq = W - E(S)
        wq = w - (1 / self.mi)
        # Se Lq for calculado por fórmula analítica, podemos usar Wq = Lq / λ_efetiva

        # Verificação de consistência: Lq deve ser igual a λ_efetiva * Wq
        # Usaremos as definições baseadas em L e Lq (fórmula analítica)
        
        # Ajuste Final para consistência:
        # 1. L (Soma) -> W (Little)
        # 2. W -> Wq (Diferença)
        # 3. Lq (Fórmula analítica) -> OK
        
        return p0, pk, l, lq, w, wq, lam_efetiva, l_perda

    def resultado(self):
        """Exibe os resultados formatados no console, incluindo L_perda."""
        print(f"--- Modelo M/M/{self.s}/K (K={self.k}) ---")
        print(f"Taxa de tráfego (ρ): {self.rho:.4f} (r = {self.r:.4f})")
        try:
            p0, pk, l, lq, w, wq, lam_efetiva, l_perda = self.mmsk()
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Probabilidade do sistema estar cheio (Pk): {pk:.4f} (Prob. de perda)")
            print(f"Taxa de chegada efetiva (λ_barra): {lam_efetiva:.4f}")
            print(f"Número esperado de perdas (L_perda): {l_perda:.4f}") # NOVO
            print("--------------------------------------------------")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f}")
            print(f"Tempo médio na fila (Wq): {wq:.4f}")
        except ValueError as e:
            print(f"ERRO: {e}")