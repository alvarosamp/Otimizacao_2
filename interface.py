"""
interface.py

Pequena interface em linha de comando para testar os modelos implementados em
`formulas.py`. Permite selecionar um modelo, entrar parâmetros (com valores
default) e visualizar resultados no console.

Uso: python interface.py
"""

import os
import sys

# Garante que o diretório deste arquivo (raiz do repositório) esteja no sys.path
# — assim, se alguém executar o script a partir de outra pasta, o import funcionará.
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

# Indica se o arquivo formulas.py existe no mesmo diretório
FORMULAS_PRESENT = os.path.exists(os.path.join(REPO_ROOT, "formulas.py"))

try:
	from formulas import Mg1, Mm, Mm1k, Mmsk, Mm1n, Mmsn
except Exception as e:
	# Mensagem clara caso o import falhe — útil para quem baixar o repo e tentar rodar sem ajustar PATH
	print(f"ERRO: Não foi possível importar 'formulas.py' a partir de {REPO_ROOT}: {e}")
	raise


def input_float(prompt, default=None):
	while True:
		raw = input(f"{prompt} " + (f"[default={default}] " if default is not None else ""))
		if raw.strip() == "" and default is not None:
			return float(default)
		try:
			return float(raw)
		except ValueError:
			print("Valor inválido — digite um número (ex: 2.5) ou ENTER para usar o default.")


def input_int(prompt, default=None):
	while True:
		raw = input(f"{prompt} " + (f"[default={default}] " if default is not None else ""))
		if raw.strip() == "" and default is not None:
			return int(default)
		try:
			return int(raw)
		except ValueError:
			print("Valor inválido — digite um inteiro (ex: 3) ou ENTER para usar o default.")


def input_list_floats(prompt, default=None):
	raw = input(f"{prompt} " + (f"[default={default}] " if default is not None else "(use vírgula para separar) "))
	if raw.strip() == "" and default is not None:
		return default
	try:
		items = [float(x.strip()) for x in raw.split(",") if x.strip() != ""]
		return items
	except ValueError:
		print("Entrada inválida — use números separados por vírgula, ex: 1,0.5,2")
		return input_list_floats(prompt, default)


def print_separator():
	print("\n" + "-" * 60 + "\n")


def run_mg1():
	print_separator()
	print("Modelo M/G/1 — parâmetros:")
	has_prior = input("Deseja informar uma lista de taxas por prioridade? (s/n) [n]: ").strip().lower() or "n"
	if has_prior.startswith("s"):
		lam_list = input_list_floats("Informe λ_i separados por vírgula:", default=[1.0, 1.0])
		lam_total = sum(lam_list)
		mi = input_float("μ (taxa de atendimento):", default=1.0)
		var = input_float("Var(S) (variância do tempo de serviço):", default=0.0)
		try:
			modelo = Mg1(lam=lam_total, mi=mi, var=var, lam_list=lam_list, interrupt=False)
			print(f"ρ total = {modelo.rho:.4f}")
			resultados = modelo.mg1_prioridades()
			if resultados:
				for i, (lq_k, l_k, wq_k, w_k) in enumerate(resultados):
					print(f"Prioridade {i+1}: λ={modelo.lam_list[i]}, ρ={modelo.rho_list[i]:.4f}")
					print(f"  Lq={lq_k:.6g}, L={l_k:.6g}, Wq={wq_k:.6g}, W={w_k:.6g}")
		except Exception as e:
			print(f"Erro ao calcular M/G/1 prioridades: {e}")
	else:
		lam = input_float("λ (taxa de chegada):", default=1.0)
		mi = input_float("μ (taxa de atendimento):", default=1.0)
		var = input_float("Var(S) (variância do tempo de serviço):", default=0.0)
		try:
			modelo = Mg1(lam=lam, mi=mi, var=var)
			rho, l, lq, w, wq = modelo.mg1()
			print(f"ρ={rho:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
		except Exception as e:
			print(f"Erro ao calcular M/G/1: {e}")


def run_mm1_or_mms():
	print_separator()
	lam = input_float("λ (taxa de chegada):", default=1.0)
	mi = input_float("μ (taxa de atendimento):", default=1.0)
	s = input_int("Número de servidores s (1 para M/M/1):", default=1)
	try:
		modelo = Mm(lam=lam, mi=mi, s=s)
		if s == 1:
			p0, l, lq, w, wq = modelo.mm1()
			print(f"P0={p0:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
		else:
			p0, l, lq, w, wq = modelo.mms()
			print(f"P0={p0:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
	except Exception as e:
		print(f"Erro ao calcular M/M/s: {e}")


def run_mm1k():
	print_separator()
	lam = input_float("λ (taxa de chegada):", default=1.0)
	mi = input_float("μ (taxa de atendimento):", default=1.0)
	k = input_int("Capacidade K (inteiro):", default=5)
	try:
		modelo = Mm1k(lam=lam, mi=mi, k=k)
		p0, pk, l, lq, w, wq, lam_eff = modelo.mm1k()
		print(f"P0={p0:.6g}, Pk={pk:.6g}, λ_barra={lam_eff:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
	except Exception as e:
		print(f"Erro ao calcular M/M/1/K: {e}")


def run_mmsk():
	print_separator()
	lam = input_float("λ (taxa de chegada):", default=1.0)
	mi = input_float("μ (taxa de atendimento):", default=1.0)
	s = input_int("Número de servidores s:", default=1)
	k = input_int("Capacidade K (K >= s):", default=max(5, s))
	try:
		modelo = Mmsk(lam=lam, mi=mi, s=s, k=k)
		p0, pk, l, lq, w, wq, lam_eff = modelo.mmsk()
		print(f"P0={p0:.6g}, Pk={pk:.6g}, λ_barra={lam_eff:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
	except Exception as e:
		print(f"Erro ao calcular M/M/s/K: {e}")


def run_mm1n():
	print_separator()
	lam_c = input_float("λ por cliente (λ_por_cliente):", default=0.01)
	mi = input_float("μ (taxa de atendimento):", default=1.0)
	n = input_int("População N (inteiro):", default=10)
	try:
		modelo = Mm1n(lam_por_cliente=lam_c, mi=mi, n_pop=n)
		p0, l, lq, w, wq, lam_eff = modelo.mm1n()
		print(f"P0={p0:.6g}, λ_barra={lam_eff:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
	except Exception as e:
		print(f"Erro ao calcular M/M/1/N: {e}")


def run_mmsn():
	print_separator()
	lam_c = input_float("λ por cliente (λ_por_cliente):", default=0.01)
	mi = input_float("μ (taxa de atendimento):", default=1.0)
	s = input_int("Número de servidores s:", default=1)
	n = input_int("População N (inteiro):", default=max(10, s))
	try:
		modelo = Mmsn(lam_por_cliente=lam_c, mi=mi, s=s, n_pop=n)
		p0, l, lq, w, wq, lam_eff = modelo.mmsn()
		print(f"P0={p0:.6g}, λ_barra={lam_eff:.6g}, L={l:.6g}, Lq={lq:.6g}, W={w:.6g}, Wq={wq:.6g}")
	except Exception as e:
		print(f"Erro ao calcular M/M/s/N: {e}")


def run_examples():
	print_separator()
	print("Executando os exemplos embutidos em formulas.py (equivalente ao bloco __main__):")
	# Reuse the examples present in formulas.py by instantiating similar objects
	try:
		m1 = Mg1(lam=2, mi=5, var=0.04)
		print("M/G/1 (sem prioridades):")
		print(m1.mg1())
	except Exception as e:
		print(f"Erro exemplo M/G/1: {e}")

	try:
		mp = Mg1(lam=3, mi=6, var=0.05, lam_list=[1,1,1], interrupt=False)
		print("M/G/1 (prioridades):")
		print(mp.mg1_prioridades())
	except Exception as e:
		print(f"Erro exemplo M/G/1 prioridades: {e}")

	try:
		mm1 = Mm(lam=2, mi=5, s=1)
		print("M/M/1:")
		print(mm1.mm1())
	except Exception as e:
		print(f"Erro exemplo M/M/1: {e}")

	try:
		mms = Mm(lam=4, mi=3, s=2)
		print("M/M/s:")
		print(mms.mms())
	except Exception as e:
		print(f"Erro exemplo M/M/s: {e}")


def main_loop():
	actions = {
		"1": ("M/G/1", run_mg1),
		"2": ("M/M/1 or M/M/s", run_mm1_or_mms),
		"3": ("M/M/1/K", run_mm1k),
		"4": ("M/M/s/K", run_mmsk),
		"5": ("M/M/1/N", run_mm1n),
		"6": ("M/M/s/N", run_mmsn),
		"7": ("Executar exemplos rápidos", run_examples),
	}

	while True:
		print_separator()
		print("Escolha um modelo para testar (ou 0 para sair):")
		for k, (name, _) in actions.items():
			print(f"  {k}. {name}")
		print("  0. Sair")
		choice = input("Opção: ").strip()
		if choice == "0":
			print("Saindo...")
			break
		action = actions.get(choice)
		if action:
			try:
				action[1]()
			except Exception as e:
				print(f"Erro ao executar ação: {e}")
		else:
			print("Opção inválida — escolha novamente.")


if __name__ == "__main__":
	print("Interface simples para testes de modelos de filas. Pressione Ctrl+C para sair a qualquer momento.")
	try:
		main_loop()
	except KeyboardInterrupt:
		print("\nInterrompido pelo usuário. Saindo...")
