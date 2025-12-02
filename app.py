import customtkinter as ctk
from tkinter import messagebox
from typing import Any, Dict, List, Optional, Tuple, Callable, Iterable
from math import exp, factorial

# --- Configuração do CustomTkinter ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --- SEUS IMPORTS DE MODELOS ---
# Importações mantidas do seu código original
from modelos.mm1 import mm1
from modelos.mms import mms 
from modelos.mm1k import mm1k
from modelos.mmsk import mmsk
from modelos.mm1n import mm1n
from modelos.mmsn import mmsn
from modelos.mg1 import mg1
# OBS: O código assume que você alterou internamente nos seus modelos de prioridade 
# para somar L_class e Lq_class conforme sugerido anteriormente.
from modelos.mms_priority_preemptive import mms_priority_preemptive
from modelos.mms_priority_non_preemptive import mms_priority_non_preemptive


# Funções auxiliares (mantidas)
def _comb(n: int, k: int) -> int:
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    num = 1; den = 1
    for i in range(1, k + 1):
        num *= n - (k - i); den *= i
    return num // den

def erlang_c(lmbda: float, mu: float, s: int) -> float:
    a = lmbda / mu; rho = a / s
    if s == 0: return 0.0
    sum1 = sum(a**k / factorial(k) for k in range(s))
    if rho >= 1: return 1.0 
    p0 = 1.0 / (sum1 + (a**s / (factorial(s) * (1 - rho))))
    return (a**s / (factorial(s) * (1 - rho))) * p0


class QueueingApp(ctk.CTk):
    
    OPTIONAL_FIELDS = {"n", "t"} 

    MODEL_PARAMS: Dict[str, List[Tuple[str, Optional[List[str]]]]] = {
        "M/M/1 (Infinito)": [("lambda", None), ("mu", None), ("n", None), ("t", None)],
        "M/M/s (Infinito)": [("lambda", None), ("mu", None), ("s", None), ("n", None), ("t", None)],
        "M/G/1 (FCFS)": [("lambda", None), ("mu", None), ("service_distribution", ["exponential", "deterministic", "poisson"]), ("n", None), ("t", None)],
        "M/M/1/K (Capacidade)": [("lambda", None), ("mu", None), ("K", None), ("n", None), ("t", None)],
        "M/M/s/K (Capacidade)": [("lambda", None), ("mu", None), ("s", None), ("K", None), ("n", None), ("t", None)],
        "M/M/1/N (Pop. Finita)": [("lambda", None), ("mu", None), ("N", None), ("n", None), ("t", None)],
        "M/M/s/N (Pop. Finita)": [("lambda", None), ("mu", None), ("s", None), ("N", None), ("n", None), ("t", None)],
        "Prioridade com Interrupção": [("mu", None), ("s", None), ("arrival_rates (Ex: 10,5; 5,2)", None)],
        "Prioridade sem Interrupção": [("mu", None), ("s", None), ("arrival_rates (Ex: 10,5; 5,2)", None)],
    }

    def __init__(self):
        super().__init__()
        self.title("Calculadora de Modelos de Filas")
        self.geometry("900x600")

        self.model_funcs: Dict[str, Callable] = {
            "M/M/1 (Infinito)": mm1, "M/M/s (Infinito)": mms,
            "M/M/1/K (Capacidade)": mm1k, "M/M/s/K (Capacidade)": mmsk,
            "M/M/1/N (Pop. Finita)": mm1n, "M/M/s/N (Pop. Finita)": mmsn,
            "M/G/1 (FCFS)": mg1,
            "Prioridade com Interrupção": mms_priority_preemptive,
            "Prioridade sem Interrupção": mms_priority_non_preemptive,
        }

        self.input_vars: Dict[str, ctk.StringVar] = {}
        self.selected_model = ctk.StringVar(value="M/M/1 (Infinito)")
        
        self.create_widgets()
        self.setup_parameters() 
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=0); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        logo_label = ctk.CTkLabel(self.sidebar_frame, text="Modelos de Fila", font=ctk.CTkFont(size=18, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        row_index = 1
        for model_name in self.model_funcs.keys():
            model_button = ctk.CTkRadioButton(self.sidebar_frame, text=model_name, command=self.on_model_change, variable=self.selected_model, value=model_name)
            model_button.grid(row=row_index, column=0, padx=20, pady=(10, 5), sticky="w")
            row_index += 1
        self.sidebar_frame.grid_rowconfigure(row_index, weight=1)

        # 2. Main Content
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_rowconfigure(1, weight=1); self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        # 2.1. Parâmetros de Entrada
        self.param_frame = ctk.CTkScrollableFrame(self.main_content_frame, corner_radius=8, label_text="Parâmetros de Entrada")
        self.param_frame.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.param_frame.grid_columnconfigure(1, weight=1)
        
        # 2.2. Botão de Cálculo
        calculate_button = ctk.CTkButton(self.main_content_frame, text="Calcular Métricas", command=self.calculate, font=ctk.CTkFont(size=14, weight="bold"))
        calculate_button.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        # 2.3. Resultados
        self.result_container_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=8)
        self.result_container_frame.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="nsew")
        self.result_container_frame.grid_columnconfigure(0, weight=1); self.result_container_frame.grid_rowconfigure(0, weight=1)
        
        self.result_text = ctk.CTkTextbox(self.result_container_frame, wrap="word", height=200, activate_scrollbars=True)
        self.result_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.result_text.configure(state="disabled", font=ctk.CTkFont(family="Consolas", size=12))

    def setup_parameters(self, event=None):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.input_vars = {}

        current_model = self.selected_model.get()
        params = self.MODEL_PARAMS.get(current_model, [])
        self.param_frame.configure(label_text=f"Parâmetros: {current_model}")

        row = 0
        for name, combo_values in params:
            label_text = f"{name} (*)" if name in self.OPTIONAL_FIELDS else name 
            label = ctk.CTkLabel(self.param_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, sticky="w", padx=(10, 5), pady=5)

            var = ctk.StringVar(value="")
            self.input_vars[name] = var

            if name == "service_distribution":
                combo_values_list = combo_values or ["exponential", "deterministic", "poisson"]
                combo = ctk.CTkComboBox(self.param_frame, variable=var, values=combo_values_list, state="readonly")
                combo.grid(row=row, column=1, sticky="ew", padx=(5, 10), pady=5)
                combo.set(combo_values_list[0])
            else:
                entry = ctk.CTkEntry(self.param_frame, textvariable=var)
                entry.grid(row=row, column=1, sticky="ew", padx=(5, 10), pady=5)
            row += 1
            
        legend_label = ctk.CTkLabel(self.param_frame, text="(*) Campos opcionais (n: prob. de N, t: prob. de tempo)", text_color="#A0A0A0", font=ctk.CTkFont(size=10))
        legend_label.grid(row=row, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        
    def on_model_change(self):
        self.setup_parameters()
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")

    def parse_inputs(self) -> Dict[str, Any]:
        """Tenta converter os valores de string para os tipos corretos."""
        args: Dict[str, Any] = {}
        for name, var in self.input_vars.items():
            value_str = var.get().strip() # Mantém a string original

            # 1. Lida com arrival_rates (lista de floats)
            if name.startswith("arrival_rates"):
                if not value_str: raise ValueError(f"O parâmetro '{name}' é obrigatório.")
                try:
                    # 1. Substitui a vírgula decimal (,) por ponto (.) em toda a string
                    rates_list_str = value_str.replace(',', '.') 
                    
                    # 2. Divide a string usando ponto e vírgula (;) como separador da LISTA
                    rates = [float(r.strip()) for r in rates_list_str.split(';') if r.strip()]
                    
                    if not rates: raise ValueError("A lista de taxas de chegada não pode estar vazia.")
                    args["arrival_rates"] = rates
                except ValueError:
                    raise ValueError(f"'{name}' inválido. **Use ponto e vírgula (;) para separar as taxas** e vírgula (,) para decimais. Ex: 10,5; 5,2; 3.")
                continue

            # 2. Lida com service_distribution (string)
            if name == "service_distribution":
                if not value_str: raise ValueError(f"O parâmetro '{name}' é obrigatório.")
                args[name] = value_str
                continue

            # 3. Lida com campos opcionais vazios ("n" e "t")
            if name in self.OPTIONAL_FIELDS and not value_str:
                args[name] = None
                continue
            
            # 4. Garante que campos obrigatórios não estão vazios
            if not value_str:
                raise ValueError(f"O parâmetro '{name}' é obrigatório.")
            
            # 5. Converte para float/int (para os campos MU, K, S, N, lambda, t)
            try:
                # Trata vírgula como decimal para campos de valor único
                clean_value_str = value_str.replace(',', '.') 
                
                if name in ["K", "s", "N", "n"]:
                    args[name] = int(clean_value_str)
                    if args[name] < 0 and name != "n": raise ValueError(f"'{name}' deve ser inteiro >= 0.")
                else: # lambda, mu, t
                    args[name] = float(clean_value_str)
                    if args[name] < 0: raise ValueError(f"'{name}' deve ser >= 0.")
            except ValueError:
                target_type = "inteiro" if name in ["K", "s", "N", "n"] else "decimal"
                raise ValueError(f"'{name}' inválido. Deve ser um número {target_type}. Use vírgula para decimais.")

        # 🌟 Correção Crítica para os modelos M/M/x: Renomear 'lambda' para 'lmbda'
        if "lambda" in args:
            args["lmbda"] = args.pop("lambda")
            
        return args

    # (Funções format_output e calculate permanecem iguais, pois a lógica crítica foi ajustada em parse_inputs)

    def format_output(self, results: Dict[str, Any]) -> str:
        output = []
        friendly_names = {
            "rho": "Utilização (ρ)", "p0": "Prob. 0 no Sistema (P0)", "L": "No. Médio no Sistema (L)",
            "Lq": "No. Médio na Fila (Lq)", "W": "Tempo Médio no Sistema (W)", "Wq": "Tempo Médio na Fila (Wq)",
            "lambda_eff": "Taxa Efetiva (λ_eff)", "pK": "P(N=K) / P(Bloqueio)",
            "pn": f"Prob. de N={results.get('n_input', 'n')}",
            "P(W>t)": f"Prob. W > {results.get('t_input', 't')}", "P(Wq>t)": f"Prob. Wq > {results.get('t_input', 't')}",
            "cs2": "Coef. de Variação² (Cs²)", "E[S]": "Tempo Médio de Serviço (E[S])", "E[S^2]": "E[S²]",
        }
        for name in self.OPTIONAL_FIELDS:
            if name in self.input_vars and self.input_vars[name].get().strip():
                try:
                    # Tratamento de decimal para exibição de input
                    results[f"{name}_input"] = int(self.input_vars[name].get().strip()) if name == 'n' else float(self.input_vars[name].get().strip().replace(',', '.'))
                except ValueError:
                    results[f"{name}_input"] = self.input_vars[name].get().strip()

        for key, value in results.items():
            if key in ["n_input", "t_input", "lambda_total", "service_in_progress", "L_operational"]:
                continue
            if key == "per_class":
                output.append("\n--- Métricas por Classe (Prioridade) ---")
                for item in value:
                    class_output = [f"  - Prioridade {item.get('priority', 'N/A')}:"]
                    for k, v in item.items():
                        if k not in ["priority", "lambda_cum", "L_cum", "Lq_cum", "base_factor", "L_class", "Lq_class"]:
                             k_name = friendly_names.get(k, k.replace('_', ' ').title())
                             try:
                                 class_output.append(f"    - {k_name.ljust(15)}: {v:.6f}")
                             except Exception:
                                 class_output.append(f"    - {k_name.ljust(15)}: {v}")
                    output.append("\n".join(class_output))
                continue
            
            display_key = friendly_names.get(key, key.replace('_', ' ').title())
            try:
                if isinstance(value, float):
                    output.append(f"• **{display_key.ljust(30)}**: {value:.6f}")
                elif isinstance(value, int):
                    output.append(f"• **{display_key.ljust(30)}**: {value}")
                else:
                    output.append(f"• **{display_key.ljust(30)}**: {value}")
            except Exception:
                output.append(f"• **{display_key.ljust(30)}**: {value}")
        return "\n".join(output)

    def calculate(self):
        model_name = self.selected_model.get()
        model_func = self.model_funcs.get(model_name)

        if not model_func:
            messagebox.showerror("Erro", "Modelo selecionado não encontrado.")
            return

        try:
            args = self.parse_inputs() 
            results = model_func(**args) 

            formatted_output = f"*** Modelo: {model_name} ***\n\n"
            formatted_output += self.format_output(results)

            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", formatted_output)
            self.result_text.configure(state="disabled")

        except ValueError as e:
            messagebox.showerror("Erro de Parâmetro/Estabilidade", str(e))
        except Exception as e:
            messagebox.showerror("Erro de Cálculo Inesperado", f"Ocorreu um erro interno. {e}")


if __name__ == "__main__":
    app = QueueingApp()
    app.mainloop()