import math
from math import factorial

class Mg1:
    """
    Modelo de Fila M/G/1 com e sem Prioridades 
    ---------------------
    Fórmulas sem prioridades (Pollaczek-Khintchine):
    (Ref: Teoria de Filas M/G/1)
        ρ  = λ / μ
        Lq = (λ² * E[S²]) / [2 * (1 - ρ)]
        L  = ρ + Lq
        Wq = Lq / λ
        W  = Wq + (1 / μ)
    
    Fórmulas com prioridades (NÃO PREEMPTIVO, M/G/1 - K classes, K >= 2):
        Wq_k = A / [2 * (1 - R_{k-1}) * (1 - R_k)]
        onde R_k = Σ_{i=1}^{k} ρ_i e A = Σ_{i=1}^{m} [λ_i * E[S_i²]]
        
    Esta implementação assume E[S] = 1/μ e Var[S] = var (σ²) são os mesmos 
    para TODAS as classes de prioridade.
    """

    def __init__(self, lam, mi, var, lam_list=None, interrupt=False):
        """
        Inicializa o modelo com seus parâmetros básicos.
        
        Parâmetros:
        lam (float): Taxa média de chegada total (λ). *Ignorado se lam_list for fornecido.*
        mi (float): Taxa média de atendimento (μ).
        var (float): Variância do tempo de atendimento (σ²). Deve ser >= 0.
        lam_list (list, opcional): Lista de taxas de chegada (λ_i) por classe de prioridade.
        interrupt (bool, opcional): Define se o modelo de prioridades é preemptivo (com interrupção).
                                     *AVISO: M/G/1 Preemptivo (com interrupção) não está implementado.*
        """
        self.mi = mi     # Taxa média de atendimento (μ)
        self.var = var    # Variância do tempo de atendimento (σ²)
        
        if self.mi <= 0:
            raise ValueError("mi (taxa de atendimento) deve ser um valor positivo.")
        if self.var < 0:
            raise ValueError("var (variância do tempo de atendimento, σ²) não pode ser negativa.")
            
        # Calcula E[S²] = Var[S] + E[S]² = σ² + (1/μ)²
        self.e_s2 = self.var + math.pow(1 / self.mi, 2)

        if lam_list and len(lam_list) > 1:  # Modelo com prioridades
            self.lam_list = lam_list
            self.lam = sum(lam_list)      # λ total é a soma das taxas
            # ρ para cada prioridade, assumindo μ único
            self.rho_list = [l / self.mi for l in lam_list]
        else: # Modelo sem prioridades ou prioridade única (tratado como sem)
            self.lam_list = None
            self.lam = lam                # usa o λ total fornecido
            self.rho_list = None

        self.rho = self.lam / self.mi # Fator de utilização global (ρ)

        if self.rho >= 1:
            raise ValueError(f"O sistema está instável (ρ = {self.rho:.4f} >= 1). Ajuste as taxas de chegada ou atendimento.")

        self.interrupt = interrupt

    def mg1(self):
        """
        Calcula as métricas do modelo M/G/1 (sem prioridades).
        Fórmulas de Pollaczek-Khintchine.
        
        Retorna:
        tuple: (rho, L, Lq, W, Wq, P0)
        """
        p0 = 1 - self.rho
        
        # Lq = (λ² * E[S²]) / [2 * (1 - ρ)]
        lq = (math.pow(self.lam, 2) * self.e_s2) / (2 * (1 - self.rho))
        
        # L = ρ + Lq 
        l = self.rho + lq
        
        # Wq = Lq / λ 
        wq = lq / self.lam if self.lam != 0 else 0.0
        
        # W = Wq + E[S] = Wq + (1 / μ) 
        w = wq + (1 / self.mi)
        
        return self.rho, l, lq, w, wq, p0

    def mg1_prioridades_nao_preemptivo(self):
        """
        Calcula as métricas do modelo M/G/1 com prioridades NÃO PREEMPTIVO.
        
        Assume E[S] e Var[S] são idênticos para TODAS as classes de prioridade.
        
        Retorna:
        list: Lista de tuplas [(Lq_k, L_k, Wq_k, W_k, rho_k), ...] para cada prioridade.
        """
        if self.lam_list is None:
            raise ValueError("lam_list deve ser fornecido para calcular prioridades.")

        resultados = []
        
        # A = Σ [λ_i * E(S_i²)] -> A = E[S²] * Σ(λ_i) = E[S²] * self.lam
        a = self.lam * self.e_s2
        
        r_sum_anterior = 0.0  # R_{k-1} = Σ_{i=1}^{k-1} ρ_i. R_0 = 0.
        
        for i in range(len(self.lam_list)):
            lam_k = self.lam_list[i]
            rho_k = self.rho_list[i]
            
            # R_k = Σ_{i=1}^{k} ρ_i
            r_sum_atual = r_sum_anterior + rho_k
            
            # Wq_k = A / [2 * (1 - R_{k-1}) * (1 - R_k)]
            denominador = 2 * (1 - r_sum_anterior) * (1 - r_sum_atual)
            
            # Validação de estabilidade local
            if (1 - r_sum_atual) < 1e-9: # Se R_k se aproxima de 1 ou o denominador é zero
                wq_k = float('inf')
                w_k = float('inf')
                lq_k = float('inf')
                l_k = float('inf')
            else:
                wq_k = a / denominador
                w_k = wq_k + (1 / self.mi) # W = Wq + E(S)
                lq_k = lam_k * wq_k          # Lq = λ * Wq
                l_k = lam_k * w_k            # L = λ * W
                
            resultados.append((lq_k, l_k, wq_k, w_k, rho_k))
            
            r_sum_anterior = r_sum_atual # Atualiza R_{k-1} para a próxima iteração
            
        return resultados

    def mg1_print(self):
        """
        Exibe os resultados do modelo M/G/1 formatados no console.
        
        Nota: Esta versão redireciona a saída para o widget Text usando a classe utilitária.
        """
        # A captura de saída é feita pela função wrapper 'capture_output' no App Tkinter.
        
        if self.lam_list is None:  # Se não for modelo com prioridades
            try:
                rho, l, lq, w, wq, p0 = self.mg1()
                print(f"--- Modelo M/G/1 (Sem Prioridades) ---")
                print(f"Taxa de chegada (λ): {self.lam:.4f}")
                print(f"Taxa de atendimento (μ): {self.mi:.4f}")
                print(f"Variância do tempo de atendimento (σ²): {self.var:.4f}")
                print(f"E[S²] (Momento de 2ª ordem): {self.e_s2:.4f}")
                print(f"----------------------------------------")
                print(f"Taxa de utilização (ρ): {rho:.4f} ({(rho*100):.2f}%)")
                print(f"Probabilidade de sistema vazio (P0): {p0:.4f} ({(p0*100):.2f}%)")
                print(f"Número médio de clientes na fila (Lq): {lq:.4f}")
                print(f"Número médio de clientes no sistema (L): {l:.4f}")
                print(f"Tempo médio de espera na fila (Wq): {wq:.4f}")
                print(f"Tempo médio no sistema (W): {w:.4f}")
            except ValueError as e:
                # O wrapper capture_output já lida com o erro, mas printamos para o TextRedirector
                print(f"ERRO: {e}")
            
        else:  # Se for modelo com prioridades
            if self.interrupt:
                print(f"--- Modelo M/G/1 com Prioridades (COM Interrupção) ---")
                print("AVISO: O cálculo para M/G/1 com prioridades PREEMPTIVAS (com interrupção)")
                print("       NÃO é fornecido por este método. As fórmulas M/G/1 Non-Preemptive serão usadas.")
            
            try:
                print(f"--- Modelo M/G/1 com Prioridades (SEM Interrupção) ---")
                print(f"Taxa de utilização TOTAL (ρ_total): {self.rho:.4f} ({(self.rho*100):.2f}%)")
                print(f"E[S²] (Momento de 2ª ordem): {self.e_s2:.4f}")
                
                resultados = self.mg1_prioridades_nao_preemptivo()
                
                if resultados:
                    for i, (lq_k, l, wq, w, rho_k) in enumerate(resultados):
                        print(f"\nPrioridade {i+1} (λ_{i+1} = {self.lam_list[i]}, ρ_{i+1} = {rho_k:.4f}):")
                        print(f"  Número médio na fila (Lq_{i+1}): {lq_k:.4f}")
                        print(f"  Número médio no sistema (L_{i+1}): {l:.4f}")
                        print(f"  Tempo médio na fila (Wq_{i+1}): {wq:.4f}")
                        print(f"  Tempo médio no sistema (W_{i+1}): {w:.4f}")
            except ValueError as e:
                print(f"ERRO: {e}")