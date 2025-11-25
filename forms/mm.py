import math
from math import factorial

class Mm:
    # ... (Métodos __init__, mm1, mms permanecem como no código anterior) ...
    # IMPORTANTE: A sua implementação de 'mms' já calcula P0 corretamente,
    # que é essencial para o método 'prob_n_clientes'.

    def __init__(self, lam: float, mi: float, s: int = 1):
        self.lam = lam
        self.mi = mi
        self.s = s

        if mi <= 0:
            raise ValueError("A taxa de atendimento (μ) deve ser um valor positivo e não-nulo.")
        if s <= 0 or not isinstance(s, int):
            raise ValueError("O número de servidores (s) deve ser um inteiro positivo.")

        self.rho = self.lam / (self.mi * self.s)

        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas ou o número de servidores.")

    def mm1(self) -> tuple[float, float, float, float, float]:
        """Calcula as métricas de desempenho para o Modelo M/M/1 (s=1)."""
        rho1 = self.lam / self.mi
        
        p0 = 1 - rho1
        l = self.lam / (self.mi - self.lam)
        lq = math.pow(self.lam, 2) / (self.mi * (self.mi - self.lam))
        w = 1 / (self.mi - self.lam)
        wq = self.lam / (self.mi * (self.mi - self.lam))
        
        return p0, l, lq, w, wq

    def mms(self) -> tuple[float, float, float, float, float]:
        """Calcula as métricas de desempenho para o Modelo M/M/s (s > 1)."""
        r = self.lam / self.mi  # Razão r = (λ/μ)
        
        # --- Cálculo de P0 ---
        soma_p0 = 0.0
        for n in range(self.s):
            soma_p0 += (math.pow(r, n) / math.factorial(n))
            
        termo_s = (math.pow(r, self.s) / math.factorial(self.s)) * (1 / (1 - self.rho))
        p0 = 1 / (soma_p0 + termo_s)
        
        # --- Cálculo de Lq ---
        numerador_lq = p0 * math.pow(r, self.s) * self.rho
        denominador_lq = math.factorial(self.s) * math.pow(1 - self.rho, 2)
        lq = numerador_lq / denominador_lq
        
        # --- Outras métricas ---
        wq = lq / self.lam
        w = wq + (1 / self.mi)
        l = lq + r
        
        return p0, l, lq, w, wq

    def prob_n_clientes(self, n: int) -> float:
        """
        Calcula a probabilidade de haver exatamente 'n' clientes no sistema (Pn).
        Válido para M/M/1 (n >= 0) e M/M/s (n >= 0).
        """
        if n < 0:
            return 0.0

        # Obter P0. Se s=1, usa mm1; se s>1, usa mms.
        if self.s == 1:
            p0, _, _, _, _ = self.mm1()
            # Fórmula M/M/1: Pn = ρ^n * P0
            if n == 0:
                return p0
            return math.pow(self.rho, n) * p0
        else: # M/M/s
            p0, _, _, _, _ = self.mms()
            r = self.lam / self.mi # r = λ/μ
            
            if n < self.s:
                # Se n < s: Pn = (r^n / n!) * P0
                return (math.pow(r, n) / math.factorial(n)) * p0
            else:
                # Se n >= s: Pn = (r^s / s! * ρ^(n-s)) * P0
                # Onde ρ = λ/(sμ)
                
                # Termo de Pn = (r^s / s!)
                termo_s = math.pow(r, self.s) / math.factorial(self.s)
                
                # Termo de ρ^(n-s)
                fator_rho = math.pow(self.rho, n - self.s)
                
                return termo_s * fator_rho * p0


    def prob_wq_maior_que_t(self, t: float) -> float:
        """
        Calcula a probabilidade de o tempo de espera na fila ser maior que t: P(Wq > t).
        """
        if self.rho >= 1:
            return 1.0
            
        if self.s == 1: 
            # Fórmula M/M/1: P(Wq > t) = ρ * e^-(μ - λ)t
            rho1 = self.lam / self.mi
            return rho1 * math.exp(-(self.mi - self.lam) * t)
        else:
            # Fórmula M/M/s: P(Wq > t) = P(Wq > 0) * e^-(sμ(1-ρ)t)
            p0, _, lq, _, _ = self.mms()
            r = self.lam / self.mi
            pwq0 = lq / r
            
            return pwq0 * math.exp(-(self.mi * self.s * (1 - self.rho)) * t)

    def prob_w_maior_que_t(self, t: float) -> float:
        """
        Calcula a probabilidade de o tempo total no sistema (W) ser maior que t: P(W > t).
        Válido para M/M/1 e M/M/s (ρ < 1).
        """
        # 1. Checagem de Estabilidade
        if self.s * self.mi <= self.lam: # sμ <= λ
            return 1.0
            
        # 2. Requer que as métricas (principalmente P0) sejam calculadas
        p0, _, _, _, _ = self.mms()
        
        if self.s == 1:
            # M/M/1: P(W > t) = e^-(μ - λ)t
            return math.exp(-(self.mi - self.lam) * t)
            
        else: # M/M/s (s > 1)
            # --- NOVO CÁLCULO DE P(Wq > 0) USANDO ERLANG C ---
            
            r = self.lam / self.mi # r = λ/μ
            rho_s = self.lam / (self.s * self.mi) # ρ = λ / sμ
            
            # 1. Calcule P(Wq > 0) (Fator de Erlang C)
            try:
                # Numerador: (r^s / s!)
                termo_erlang_numerador = math.pow(r, self.s) / math.factorial(self.s)
                
                # Denominador: (1 - ρ)
                termo_erlang_denominador = (1.0 - rho_s)
                
                # P(Wq > 0) = [P0 * (r^s / s!)] / (1 - ρ)
                pwq0_maior = (p0 * termo_erlang_numerador) / termo_erlang_denominador
                
            except ValueError: # Captura erros como math.factorial de números grandes
                # Pode ser necessário um cálculo mais robusto para n! (e.g., função auxiliar)
                # Neste caso, vamos assumir que o erro é grave e retornar 0 ou levantar a exceção.
                return 0.0 # Ou levantar a exceção
            
            # Garante que P(Wq > 0) está no intervalo [0, 1]
            pwq0_maior = max(0.0, min(1.0, pwq0_maior))

            # 2. Calcule P(Wq = 0)
            pwq0_igual = 1.0 - pwq0_maior
            
            # 3. Fórmula P(W > t) = P(Wq=0) * e^-(μt) + P(Wq>0) * e^-(sμ(1-ρ)t)
            
            # Termo 1: Cliente é atendido imediatamente (Taxa: μ)
            termo1 = pwq0_igual * math.exp(-self.mi * t)
            
            # Termo 2: Cliente espera na fila (Taxa: sμ(1-ρ))
            taxa_do_termo2 = self.mi * self.s * (1 - rho_s)
            termo2 = pwq0_maior * math.exp(-taxa_do_termo2 * t)
            
            # P(W > t) = Termo 1 + Termo 2
            return termo1 + termo2
            
    def resultado(self):
        """Exibe os resultados formatados no console."""
        try:
            if self.s == 1:
                p0, l, lq, w, wq = self.mm1()
                modelo = "M/M/1"
            else:
                p0, l, lq, w, wq = self.mms()
                modelo = f"M/M/{self.s}"
            
            print(f"--- Modelo {modelo} ---")
            print(f"Taxa de chegada (λ): {self.lam:.4f}")
            print(f"Taxa de atendimento por servidor (μ): {self.mi:.4f}")
            print(f"Número de servidores (s): {self.s}")
            print(f"Taxa de utilização do sistema (ρ): {self.rho:.4f}")
            print(f"Probabilidade do sistema estar vazio (P0): {p0:.4f}")
            print(f"Número médio de clientes no sistema (L): {l:.4f}")
            print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
            print(f"Tempo médio no sistema (W): {w:.4f} horas ({w*60:.2f} minutos)")
            print(f"Tempo médio na fila (Wq): {wq:.4f} horas ({wq*60:.2f} minutos)")
            
        except ValueError as e:
            raise e