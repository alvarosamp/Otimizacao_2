import math
from math import factorial

# --- FUNÇÕES AUXILIARES ---

def arredondar(valor, casas=6):
    """Função auxiliar para arredondar valores."""
    if isinstance(valor, float):
        return round(valor, casas)
    if isinstance(valor, dict):
        # Arredonda chaves/valores de nível superior (exceto a lista Pn)
        return {k: arredondar(v, casas) if k != 'Distribuição de Probabilidade (Pn)' else v for k, v in valor.items()}
    if isinstance(valor, list):
        return [arredondar(v, casas) for v in valor]
    return valor

# ----------------------------------------------------------------------

class Mmsn:
    """
    Modelo de Fila M/M/s/N (s servidores, População Finita N).
    A classe contém um método para calcular as métricas (mmsn) e um 
    método para formatar e exibir (resultado).
    """
    def __init__(self, lam_por_cliente, mi, s, n_pop):
        if n_pop < s:
            raise ValueError(f"N ({n_pop}) deve ser maior ou igual a s ({s}).")
        if mi == 0:
            raise ValueError("mi (taxa de atendimento) não pode ser zero.")

        self.lam_por_cliente = lam_por_cliente # λ por cliente
        self.mi = mi
        self.s = s
        self.n_pop = n_pop # N
        self.r = lam_por_cliente / mi # λ/μ
        self.p_list = [] # Lista para guardar Pn (P0, P1, ..., PN)

    def mmsn(self):
        """Calcula as métricas do modelo M/M/s/N e retorna um dicionário."""

        # --- Cálculo de P0 ---
        soma_p0_1 = 0.0
        # n vai de 0 até s-1
        for n in range(self.s):
            comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(n))
            termo_n = comb * math.pow(self.r, n)
            soma_p0_1 += termo_n

        soma_p0_2 = 0.0
        # n vai de s até N
        for n in range(self.s, self.n_pop + 1):
            fator_comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(self.s))
            fator_pot = math.pow(self.s, n - self.s)
            termo_n = (fator_comb / fator_pot) * math.pow(self.r, n)
            soma_p0_2 += termo_n
            
        p0 = 1 / (soma_p0_1 + soma_p0_2)
        
        self.p_list = [p0]
        l = 0.0
        
        # --- Cálculo de L (Número médio no sistema) e Pn para n >= 1 ---
        
        # Pn para 1 <= n <= s-1
        for n in range(1, self.s):
            comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(n))
            pn = comb * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn
            
        # Pn para s <= n <= N
        for n in range(self.s, self.n_pop + 1):
            fator_comb = factorial(self.n_pop) / (factorial(self.n_pop - n) * factorial(self.s))
            fator_pot = math.pow(self.s, n - self.s)
            pn = (fator_comb / fator_pot) * math.pow(self.r, n) * p0
            self.p_list.append(pn)
            l += n * pn

        # --- Métricas (Lei de Little para População Finita) ---
        lam_efetiva = self.lam_por_cliente * (self.n_pop - l) 
        
        # Número médio de clientes em serviço (Ls) - Ocupação Total
        l_servico = lam_efetiva / self.mi 
        
        # Lq = L - Ls
        lq = l - l_servico        
        w = l / lam_efetiva if lam_efetiva != 0 else 0.0
        wq = lq / lam_efetiva if lam_efetiva != 0 else 0.0
        
        # --- MÉTRICAS ADICIONAIS ---
        
        # 1. Número médio de clientes fora do sistema (N - L)
        l_parado = self.n_pop - l
        
        # 2. Tempo médio de um cliente fora do sistema (W_parado)
        if lam_efetiva == 0:
            w_parado = 0.0
        else:
             w_parado = (self.n_pop / lam_efetiva) - w

        # 3. Ocupação por Servidor (Rho')
        rho_por_servidor = lam_efetiva / (self.s * self.mi) if self.s * self.mi != 0 else 0.0
        ocioso_servidor_perc = 1.0 - rho_por_servidor

        # Estrutura de Resultados
        resultados = {
            "Probabilidade do sistema vazio (P0)": p0,
            "Taxa de chegada efetiva (λ_efetiva)": lam_efetiva,
            "Número médio no sistema (L)": l,
            "Número médio na fila (Lq)": lq,
            "Tempo médio no sistema (W)": w,
            "Tempo médio na fila (Wq)": wq,
            
            # MÉTRICAS DE OCUPAÇÃO E OCIOSIDADE
            "Número médio de clientes em serviço (Ls)": l_servico,
            "Ocupação por servidor (ρ)": rho_por_servidor,
            "Porcentagem de tempo ocioso por servidor": ocioso_servidor_perc,
            
            # MÉTRICAS DA POPULAÇÃO
            "Número médio de clientes fora do sistema (L_parado)": l_parado,
            "Tempo médio que o cliente passa fora do sistema (W_parado)": w_parado,
            
            "Distribuição de Probabilidade (Pn)": arredondar(self.p_list)
        }

        # Aplica arredondamento e retorna
        return arredondar(resultados)

    def resultado(self):
        """Exibe os resultados formatados no console (útil para self.capture_output)."""
        
        # Tenta executar o cálculo principal
        try:
            resultados = self.mmsn()
        except ValueError as e:
            print(f"ERRO DE CONFIGURAÇÃO: {e}"); return
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}"); return

        print(f"\n" + "="*60)
        print(f"--- RESULTADOS M/M/{self.s}/{self.n_pop} (POPULAÇÃO FINITA) ---")
        print(f"λ/cliente: {self.lam_por_cliente:.4f} | µ: {self.mi:.4f} | Servidores: {self.s} | População: {self.n_pop}")
        print("="*60)
        
        # Verifica se houve erro
        if "Erro" in resultados:
            print(f"ERRO: {resultados['Erro']}"); return
            
        # --- MÉTRICAS GERAIS ---
        print(f"Probabilidade do sistema vazio (P0): {resultados['Probabilidade do sistema vazio (P0)']:.6f}")
        print(f"Taxa de chegada efetiva (λ_efetiva): {resultados['Taxa de chegada efetiva (λ_efetiva)']:.6f}")
        
        # --- MÉTRICAS DO CLIENTE (Sistema) ---
        print("\n--- MÉTRICAS DO CLIENTE (Sistema) ---")
        print(f"Número médio no sistema (L): {resultados['Número médio no sistema (L)']:.6f}")
        print(f"Número médio na fila (Lq): {resultados['Número médio na fila (Lq)']:.6f}")
        print(f"Tempo médio no sistema (W): {resultados['Tempo médio no sistema (W)']:.6f}")
        print(f"Tempo médio na fila (Wq): {resultados['Tempo médio na fila (Wq)']:.6f}")

        # --- MÉTRICAS DE OCUPAÇÃO E POPULAÇÃO ---
        print("\n--- MÉTRICAS DE OCUPAÇÃO E POPULAÇÃO ---")
        print(f"Número médio de servidores ocupados (Ls): {resultados['Número médio de clientes em serviço (Ls)']:.6f}")
        print(f"Ocupação por servidor (ρ'): {resultados['Ocupação por servidor (ρ)'] * 100:.2f}%")
        print(f"Porcentagem de tempo ocioso por servidor: {resultados['Porcentagem de tempo ocioso por servidor'] * 100:.2f}%")
        
        print(f"Número médio de clientes FORA do sistema (L_parado): {resultados['Número médio de clientes fora do sistema (L_parado)']:.6f}")
        print(f"Tempo médio que o cliente passa FORA do sistema (W_parado): {resultados['Tempo médio que o cliente passa fora do sistema (W_parado)']:.6f}")