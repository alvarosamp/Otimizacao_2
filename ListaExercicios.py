import math
# Importa todas as classes do seu script principal
from forms.mg1 import Mg1
from forms.mm import Mm
from forms.mm1k import Mm1k
from forms.mmsk import Mmsk
from forms.mm1n import Mm1n
from forms.mmsn import Mmsn

def imprimir_titulo(titulo):
    """Auxiliar para formatar a saída"""
    print("\n" + "="*60)
    print(f" {titulo} ".center(60, "="))
    print("="*60)

def rodar_testes():
    """
    Executa os testes baseados nas listas de exercícios fornecidas.
    """

    # --- 1. Lista de exercícios Modelo MMs --- [cite: 315]
    imprimir_titulo("Lista de Exercícios: M/M/1 e M/M/s")

    try:
        print("\n--- Ex. 5 (M/M/1) ---")
        # λ = 3 caminhões/hora [cite: 354]
        # T_s = 15 min => μ = (1 / 15 min) * 60 min/hora = 4 caminhões/hora [cite: 355]
        # Respostas esperadas: Lq=2.25, L=3, Wq=0.75, W=1 [cite: 357, 358, 359, 361]
        modelo_mm1_ex5 = Mm(lam=3, mi=4, s=1)
        modelo_mm1_ex5.resultado()
    except Exception as e:
        print(f"Erro ao processar Ex. 5: {e}")

    try:
        print("\n--- Ex. 7 (M/M/1) - 1 médico ---")
        # λ = 1 / (1/2 hora) = 2 pacientes/hora [cite: 387]
        # T_s = 20 min => μ = (1 / 20 min) * 60 min/hora = 3 pacientes/hora [cite: 388]
        # s = 1 [cite: 389]
        # Respostas esperadas: ρ=2/3, L=2, Lq=4/3, P0=1/3, Wq=2/3, W=1 [cite: 390, 391, 392, 393, 397, 399]
        modelo_mm1_ex7 = Mm(lam=2, mi=3, s=1)
        modelo_mm1_ex7.resultado()
    except Exception as e:
        print(f"Erro ao processar Ex. 7 (s=1): {e}")

    try:
        print("\n--- Ex. 7 (M/M/s) - 2 médicos ---")
        # λ = 2 pacientes/hora [cite: 387]
        # μ = 3 pacientes/hora [cite: 388]
        # s = 2 [cite: 389]
        # Respostas esperadas: ρ=1/3, L=3/4, Lq=1/12, P0=1/2, Wq=1/24, W=3/8 [cite: 390, 391, 392, 393, 397, 399]
        modelo_mms_ex7 = Mm(lam=2, mi=3, s=2)
        modelo_mms_ex7.resultado()
    except Exception as e:
        print(f"Erro ao processar Ex. 7 (s=2): {e}")

    try:
        print("\n--- Ex. 15 (M/M/s) - Caso A (Atual) ---")
        # λ = 2 /min [cite: 468], T_s = 1 min => μ = 1 /min [cite: 470], s=4 [cite: 467]
        # Respostas esperadas: Lq=0.1739 [cite: 473]
        modelo_mms_ex15a = Mm(lam=2, mi=1, s=4)
        modelo_mms_ex15a.resultado()
    except Exception as e:
        print(f"Erro ao processar Ex. 15 (s=4, λ=2): {e}")

    try:
        print("\n--- Ex. 15 (M/M/s) - Caso B (Daqui a 1 ano) ---")
        # λ = 3 /min [cite: 469], T_s = 1 min => μ = 1 /min [cite: 470], s=4 [cite: 467]
        # Respostas esperadas: Lq=1.5283 [cite: 475]
        modelo_mms_ex15b = Mm(lam=3, mi=1, s=4)
        modelo_mms_ex15b.resultado()
    except Exception as e:
        print(f"Erro ao processar Ex. 15 (s=4, λ=3): {e}")


    # --- 2. Lista de exercícios Modelo MG1 e com prioridades --- [cite: 264]
    imprimir_titulo("Lista de Exercícios: M/G/1 e Prioridades")

    try:
        print("\n--- Ex. 1 (M/G/1) ---")
        # λ=0.2, μ=0.25[cite: 264]. Testar var = 16, 9, 4, 1, 0 (σ² = var) [cite: 265]
        # Respostas (σ=4, var=16): Lq=3.200, L=4.000, Wq=16.000, W=20.000 [cite: 270]
        # Respostas (σ=0, var=0): Lq=1.600, L=2.400, Wq=8.000, W=12.000 [cite: 270]
        params_mg1 = [
            {"sigma": 4, "var": 16},
            {"sigma": 3, "var": 9},
            {"sigma": 2, "var": 4},
            {"sigma": 1, "var": 1},
            {"sigma": 0, "var": 0},
        ]
        for p in params_mg1:
            print(f"\nTestando com σ={p['sigma']} (var=σ²={p['var']}):")
            modelo_mg1_ex1 = Mg1(lam=0.2, mi=0.25, var=p['var'])
            modelo_mg1_ex1.mg1_print()
    except Exception as e:
        print(f"Erro ao processar M/G/1 Ex. 1: {e}")

    try:
        print("\n--- Ex. 6a (M/M/1 - FIFO) ---")
        # λ_total = 8 (2+4+2)[cite: 305]. T_s = 0.1 dia => μ = 10 . s=1.
        # Resposta esperada: W=0.5 dias [cite: 308]
        modelo_ex6a = Mm(lam=8, mi=10, s=1)
        modelo_ex6a.resultado()
    except Exception as e:
        print(f"Erro ao processar M/G/1 Ex. 6a: {e}")

    try:
        print("\n--- Ex. 6b (M/M/1 - Prioridade SEM Interrupção) ---")
        # λ_list = [2, 4, 2][cite: 305]. μ = 10.
        # Modelo M/M/1 é M/G/1 com var = (1/μ)² = (0.1)² = 0.01 
        # Respostas esperadas: W1=0.2, W2=0.35, W3=1.1 
        modelo_ex6b = Mg1(lam=8, mi=10, var=0.01, lam_list=[2, 4, 2], interrupt=False)
        modelo_ex6b.mg1_print()
    except Exception as e:
        print(f"Erro ao processar M/G/1 Ex. 6b: {e}")

    try:
        print("\n--- Ex. 6c (M/M/1 - Prioridade COM Interrupção) ---")
        # λ_list = [2, 4, 2][cite: 305]. μ = 10.
        # Respostas esperadas: W1=0.125, W2=0.3125, W3=1.25 
        modelo_ex6c = Mm1PrioridadePreemptiva(lam_list=[2, 4, 2], mi=10)
        modelo_ex6c.resultado()
    except Exception as e:
        print(f"Erro ao processar M/G/1 Ex. 6c: {e}")


    # --- 3. Lista de exercícios Modelo MMsK --- [cite: 1]
    imprimir_titulo("Lista de Exercícios: M/M/1/K e M/M/s/K")

    try:
        print("\n--- Ex. 1 (M/M/1/K) ---")
        # λ=2 /min [cite: 1], T_s = 0.25 min => μ = 1 / 0.25 = 4 /min [cite: 2], K=5 [cite: 3]
        # Respostas esperadas: P0=0.5079, L=0.9048, Lq=0.4127, W=0.4597, Wq=0.2097 [cite: 4, 5, 6, 8, 9]
        modelo_mm1k_ex1 = Mm1k(lam=2, mi=4, k=5)
        modelo_mm1k_ex1.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/1/K Ex. 1: {e}")

    try:
        print("\n--- Ex. 4 (M/M/s/K) ---")
        # λ = 1/4 min = 0.25 /min [cite: 25]
        # T_s = 3 min => μ = 1/3 min [cite: 28]
        # s=2 [cite: 25], K = 2 (serviço) + 3 (espera) = 5 [cite: 27]
        # Respostas esperadas: Lq=0.0848, Wq=0.3455 [cite: 30, 31]
        modelo_mmsk_ex4 = Mmsk(lam=0.25, mi=(1/3), s=2, k=5)
        modelo_mmsk_ex4.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/s/K Ex. 4: {e}")

    try:
        print("\n--- Ex. 5 (M/M/s/K) ---")
        # λ=1 /hora [cite: 35]
        # T_s = 45 min = 0.75 hora => μ = 1 / 0.75 hora [cite: 36]
        # s=2 [cite: 33], K=5 [cite: 34]
        # Respostas esperadas: L=0.8212, Wq=0.0864 [cite: 37, 39]
        modelo_mmsk_ex5 = Mmsk(lam=1, mi=(1/0.75), s=2, k=5)
        modelo_mmsk_ex5.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/s/K Ex. 5: {e}")


    # --- 4. Lista de exercícios Modelo MMsN --- [cite: 943]
    imprimir_titulo("Lista de Exercícios: M/M/1/N e M/M/s/N")

    try:
        print("\n--- Ex. 3 (M/M/1/N) ---")
        # N=2 [cite: 961]
        # TBF = 10 horas => λ_cliente = 1/10 = 0.1 [cite: 962]
        # T_s = 8 horas => μ = 1/8 = 0.125 [cite: 963]
        # Respostas esperadas: P0=0.2577, L=1.072, Lq=0.330, W=11.556, Wq=3.556 [cite: 964, 965]
        modelo_mm1n_ex3 = Mm1n(lam_por_cliente=0.1, mi=0.125, n_pop=2)
        modelo_mm1n_ex3.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/1/N Ex. 3: {e}")

    try:
        print("\n--- Ex. 4d (M/M/s/N) ---")
        # N=3 [cite: 968], s=2 [cite: 976]
        # TBF = 9 horas => λ_cliente = 1/9 [cite: 969]
        # T_s = 2 horas => μ = 1/2 = 0.5 [cite: 970]
        # Respostas esperadas: L=0.5528 [cite: 977]
        modelo_mmsn_ex4d = Mmsn(lam_por_cliente=(1/9), mi=0.5, s=2, n_pop=3)
        modelo_mmsn_ex4d.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/s/N Ex. 4d: {e}")

    try:
        print("\n--- Ex. 6 (M/M/s/N) ---")
        # N=4 [cite: 985], s=2 [cite: 985]
        # TBF = 100 horas => λ_cliente = 1/100 = 0.01 [cite: 985]
        # T_s = 10 horas => μ = 1/10 = 0.1 [cite: 985]
        # Respostas esperadas: P0=0.6820, L=0.3677, Lq=0.0045, W=10.1239, Wq=0.1239 [cite: 986, 987]
        modelo_mmsn_ex6 = Mmsn(lam_por_cliente=0.01, mi=0.1, s=2, n_pop=4)
        modelo_mmsn_ex6.resultado()
    except Exception as e:
        print(f"Erro ao processar M/M/s/N Ex. 6: {e}")


if __name__ == "__main__":
    rodar_testes()