import tkinter as tk
from tkinter import ttk, messagebox
import sys
import io

try:
    from forms.mg1 import Mg1
    from forms.mm import Mm
    from forms.mm1k import Mm1k
    from forms.mmsk import Mmsk
    from forms.mm1n import Mm1n
    from forms.mmsn import Mmsn
    from forms.prioridadesInterrupcao import MMSPrioridadeComInterrupcaoModelo
    from forms.prioridadesSemInterrup import MMSPrioridadeSemInterrupcaoModelo
    from ListaExercicios import rodar_testes
except ImportError as e:
    print("Erro crítico: Certifique-se de que 'formulas.py' e 'ListaExercicios.py' estão na mesma pasta.")
    print(f"Detalhe: {e}")
    sys.exit(1)

class TextRedirector(object):
    """Classe utilitária para redirecionar o stdout (print) para um widget de Texto do Tkinter."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_val):
        self.widget.configure(state='normal')
        self.widget.insert("end", str_val)
        self.widget.see("end")
        self.widget.configure(state='disabled')

    def flush(self):
        pass

class FilaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Teoria das Filas")
        self.root.geometry("800x600")
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Container principal (Abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Criar as abas
        self.create_tab_mms()
        self.create_tab_mg1()
        self.create_tab_finite_k() # M/M/1/K e M/M/s/K
        self.create_tab_finite_n() # M/M/1/N e M/M/s/N
        self.create_tab_lista_exercicios()
        self.criar_aba_prioridade_interrupcao()
        self.criar_aba_prioridade_sem_interrupcao()


    def create_output_area(self, parent):
        """Cria uma área de texto scrollável para mostrar os resultados."""
        frame = ttk.LabelFrame(parent, text="Resultados", padding=10)
        frame.pack(side='bottom', expand=True, fill='both', padx=5, pady=5)
        
        text_area = tk.Text(frame, height=10, state='disabled', font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        text_area.pack(side='left', expand=True, fill='both')
        
        # Botão limpar
        btn_clean = ttk.Button(frame, text="Limpar Tela", command=lambda: self.clear_text(text_area))
        btn_clean.pack(side='top', anchor='ne', pady=2)
        
        return text_area

    def clear_text(self, text_widget):
        text_widget.configure(state='normal')
        text_widget.delete(1.0, tk.END)
        text_widget.configure(state='disabled')

    def capture_output(self, func, text_widget, *args):
        """Executa uma função capturando seus prints para a widget de texto."""
        old_stdout = sys.stdout
        sys.stdout = TextRedirector(text_widget)
        try:
            text_widget.configure(state='normal')
            text_widget.insert(tk.END, "\n>>> Calculando...\n")
            text_widget.configure(state='disabled')
            func(*args)
        except Exception as e:
            text_widget.configure(state='normal')
            text_widget.insert(tk.END, f"\nERRO: {str(e)}\n")
            text_widget.configure(state='disabled')
            messagebox.showerror("Erro no Cálculo", str(e))
        finally:
            sys.stdout = old_stdout

    # --- ABA 1: M/M/1 e M/M/s ---
    def create_tab_mms(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="M/M/s (Infinito)")
        
        # Inputs Frame
        input_frame = ttk.Frame(tab, padding=10)
        input_frame.pack(fill='x')
        
        # Linha 0: Lambda
        ttk.Label(input_frame, text="Taxa de Chegada (λ):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ent_lam = ttk.Entry(input_frame)
        ent_lam.grid(row=0, column=1, padx=5, pady=5)
        
        # Linha 1: Mu
        ttk.Label(input_frame, text="Taxa de Atendimento (μ):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ent_mi = ttk.Entry(input_frame)
        ent_mi.grid(row=1, column=1, padx=5, pady=5)
        
        # Linha 2: Servidores (s)
        ttk.Label(input_frame, text="Número de Servidores (s):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ent_s = ttk.Entry(input_frame)
        ent_s.insert(0, "1")
        ent_s.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Separator(input_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)

        # Linha 4: Tempo N para Probabilidade W>t e Wq>t
        ttk.Label(input_frame, text="Tempo t (em Minutos) para P(W>t) e P(Wq>t):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        ent_t_minutos = ttk.Entry(input_frame)
        ent_t_minutos.insert(0, "60") 
        ent_t_minutos.grid(row=4, column=1, padx=5, pady=5)
        
        # --- NOVO CAMPO ---
        # Linha 5: Número n de clientes para Pn
        ttk.Label(input_frame, text="Número n de Clientes para Pn:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        ent_n_clientes = ttk.Entry(input_frame)
        ent_n_clientes.insert(0, "5") # Exemplo: probabilidade de 5 clientes estarem no sistema
        ent_n_clientes.grid(row=5, column=1, padx=5, pady=5)
        # --- FIM NOVO CAMPO ---
        
        # Área de Output
        out_text = self.create_output_area(tab)
        
        def run():
            # 1. Captura e validação de entradas
            l = float(ent_lam.get())
            m = float(ent_mi.get())
            s = int(ent_s.get())
            t_min = float(ent_t_minutos.get()) 
            t_horas = t_min / 60.0 # Converte t para horas

            # --- NOVO VALOR ---
            n_clientes = int(ent_n_clientes.get())
            # ------------------
            
            modelo = Mm(lam=l, mi=m, s=s)
            
            # 2. Imprime as métricas básicas (L, Lq, W, Wq, P0, etc)
            modelo.resultado() 
            
            # 3. Imprime as probabilidades
            print("-" * 30)
            print("--- Cálculos de Probabilidade ---")
            
            # Pn
            prob_n = modelo.prob_n_clientes(n=n_clientes)
            print(f"P({n_clientes}) (Prob. de {n_clientes} clientes no sistema): {prob_n:.4f} ({prob_n*100:.2f}%)")

            # P(Wq > t)
            prob_wq = modelo.prob_wq_maior_que_t(t=t_horas)
            print(f"P(Wq > {t_min:.2f} min) (Esperar na Fila): {prob_wq:.4f} ({prob_wq*100:.2f}%)")

            # P(W > t)
            if s == 1:
                prob_w = modelo.prob_w_maior_que_t(t=t_horas)
                print(f"P(W > {t_min:.2f} min) (Ficar no Sistema): {prob_w:.4f} ({prob_w*100:.2f}%)")
            else:
                print(f"P(W > {t_min:.2f} min) (Ficar no Sistema): Fórmula simplificada P(W>t) indisponível para M/M/{modelo.s} (s>1).")


        # Botão Calcular
        ttk.Button(input_frame, text="Calcular", command=lambda: self.capture_output(run, out_text)).grid(row=6, column=0, columnspan=2, pady=10)

    # --- ABA 2: M/G/1 e Prioridades ---
    def create_tab_mg1(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="M/G/1 e Prioridades")
        
        input_frame = ttk.Frame(tab, padding=10)
        input_frame.pack(fill='x')
        
        # Variaveis de controle
        mode_var = tk.StringVar(value="simple") # simple, priority_nopreempt, priority_preempt
        
        # Radio buttons para modo
        ttk.Label(input_frame, text="Modo:").grid(row=0, column=0, sticky='w')
        rb_simple = ttk.Radiobutton(input_frame, text="M/G/1 Simples", variable=mode_var, value="simple")
        rb_simple.grid(row=0, column=1, sticky='w')
        rb_prio_np = ttk.Radiobutton(input_frame, text="Prioridade (Sem Interrupção)", variable=mode_var, value="priority_nopreempt")
        rb_prio_np.grid(row=1, column=1, sticky='w')
        rb_prio_p = ttk.Radiobutton(input_frame, text="Prioridade (Com Interrupção - M/M/1)", variable=mode_var, value="priority_preempt")
        rb_prio_p.grid(row=2, column=1, sticky='w')

        ttk.Separator(input_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)

        # Campos
        ttk.Label(input_frame, text="Taxa de Chegada (λ):").grid(row=4, column=0, sticky='w')
        ent_lam = ttk.Entry(input_frame)
        ent_lam.grid(row=4, column=1, padx=5, pady=2)
        ttk.Label(input_frame, text="* Para prioridades, use lista ex: 2, 4, 2", font=("Arial", 8)).grid(row=5, column=1, sticky='w')

        ttk.Label(input_frame, text="Taxa de Atendimento (μ):").grid(row=6, column=0, sticky='w')
        ent_mi = ttk.Entry(input_frame)
        ent_mi.grid(row=6, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Variância (σ²) [Só M/G/1]:").grid(row=7, column=0, sticky='w')
        ent_var = ttk.Entry(input_frame)
        ent_var.insert(0, "0")
        ent_var.grid(row=7, column=1, padx=5, pady=2)

        out_text = self.create_output_area(tab)

        def run():
            mi = float(ent_mi.get())
            mode = mode_var.get()
            
            if mode == "simple":
                lam = float(ent_lam.get())
                var = float(ent_var.get())
                # Chama a classe Mg1 para M/G/1 simples (sem lista de lambda)
                modelo = Mg1(lam=lam, mi=mi, var=var)
                modelo.mg1_print()
            
            elif mode == "priority_nopreempt":
                # Parse list
                lam_str = ent_lam.get()
                lam_list = [float(x.strip()) for x in lam_str.split(',') if x.strip()]
                var = float(ent_var.get())
                # Chama a classe Mg1 para prioridade não preemptiva (com lista de lambda)
                modelo = Mg1(lam=0, mi=mi, var=var, lam_list=lam_list, interrupt=False)
                modelo.mg1_print()
                
            elif mode == "priority_preempt":
                try:
                    Mm1PrioridadePreemptiva
                except NameError:
                    raise ValueError("A classe Mm1PrioridadePreemptiva não foi importada corretamente.")
                
                lam_str = ent_lam.get()
                lam_list = [float(x.strip()) for x in lam_str.split(',') if x.strip()]
                # Classe especifica Mm1PrioridadePreemptiva
                modelo = Mm1PrioridadePreemptiva(lam_list=lam_list, mi=mi)
                modelo.resultado()

        ttk.Button(input_frame, text="Calcular", command=lambda: self.capture_output(run, out_text)).grid(row=8, column=0, columnspan=2, pady=10)
    
    def criar_aba_prioridade_interrupcao(notebook):
        aba = ttk.Frame(notebook)
        notebook.add(aba, text="Prioridade c/ Interrupção")

        # ---------- Layout ----------
        frm = ttk.Frame(aba, padding=10)
        frm.pack(fill="both", expand=True)

        # λ_i
        ttk.Label(frm, text="λᵢ (separados por vírgula):").grid(row=0, column=0, sticky="w")
        entrada_lambda = ttk.Entry(frm, width=40)
        entrada_lambda.grid(row=0, column=1, padx=5, pady=5)

        # μ
        ttk.Label(frm, text="μ (taxa de atendimento):").grid(row=1, column=0, sticky="w")
        entrada_mi = ttk.Entry(frm, width=20)
        entrada_mi.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # servidores
        ttk.Label(frm, text="Número de servidores (s):").grid(row=2, column=0, sticky="w")
        entrada_servidores = ttk.Entry(frm, width=20)
        entrada_servidores.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ---------- Caixa de Resultado ----------
        caixa_frame = ttk.Frame(frm)
        caixa_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

        frm.rowconfigure(4, weight=1)
        frm.columnconfigure(1, weight=1)

        texto_resultado = tk.Text(caixa_frame, height=20, wrap="word")
        texto_resultado.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(caixa_frame, orient="vertical", command=texto_resultado.yview)
        scroll.pack(side="right", fill="y")
        texto_resultado.configure(yscrollcommand=scroll.set)

        # ---------- Função de Cálculo ----------
        def calcular():
            lambdas = entrada_lambda.get()
            mi = entrada_mi.get()
            servidores = entrada_servidores.get()

            if not lambdas or not mi or not servidores:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            try:
                modelo = MMSPrioridadeComInterrupcaoModelo()
                res = modelo.calcular(
                    lambdas_=lambdas,
                    mi=mi,
                    servidores=servidores,
                )
            except Exception as e:
                messagebox.showerror("Erro ao calcular", str(e))
                return

            texto_resultado.delete("1.0", tk.END)

            if isinstance(res, dict) and "Erro" in res:
                texto_resultado.insert(tk.END, f"Erro: {res['Erro']}")
                return

            for classe, valores in res.items():
                texto_resultado.insert(tk.END, f"{classe}\n")
                for key, val in valores.items():
                    texto_resultado.insert(tk.END, f"  {key}: {val}\n")
                texto_resultado.insert(tk.END, "\n-------------------------\n")

        # ---------- Botão Calcular ----------
        ttk.Button(frm, text="Calcular", command=calcular).grid(
            row=3, column=0, columnspan=2, pady=10
        )
        return aba
    
    def criar_aba_prioridade_sem_interrupcao(notebook):
        aba = ttk.Frame(notebook)
        notebook.add(aba, text="Prioridade s/ Interrupção")

        # ---------- Layout ----------
        frm = ttk.Frame(aba, padding=10)
        frm.pack(fill="both", expand=True)

        # λ_i
        ttk.Label(frm, text="λᵢ (separados por vírgula):").grid(row=0, column=0, sticky="w")
        entrada_lambda = ttk.Entry(frm, width=40)
        entrada_lambda.grid(row=0, column=1, padx=5, pady=5)

        # μ
        ttk.Label(frm, text="μ (taxa de atendimento):").grid(row=1, column=0, sticky="w")
        entrada_mi = ttk.Entry(frm, width=20)
        entrada_mi.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # servidores
        ttk.Label(frm, text="Número de servidores (s):").grid(row=2, column=0, sticky="w")
        entrada_servidores = ttk.Entry(frm, width=20)
        entrada_servidores.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ---------- Caixa de Resultado ----------
        caixa_frame = ttk.Frame(frm)
        caixa_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

        frm.rowconfigure(4, weight=1)
        frm.columnconfigure(1, weight=1)

        texto_resultado = tk.Text(caixa_frame, height=20, wrap="word")
        texto_resultado.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(caixa_frame, orient="vertical", command=texto_resultado.yview)
        scroll.pack(side="right", fill="y")
        texto_resultado.configure(yscrollcommand=scroll.set)

        # ---------- Função de Cálculo ----------
        def calcular():
            lambdas = entrada_lambda.get()
            mi = entrada_mi.get()
            servidores = entrada_servidores.get()

            if not lambdas or not mi or not servidores:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            try:
                modelo = MMSPrioridadeSemInterrupcaoModelo()
                res = modelo.calcular(
                    lambdas_=lambdas,
                    mi=mi,
                    servidores=servidores,
                )
            except Exception as e:
                messagebox.showerror("Erro ao calcular", str(e))
                return

            texto_resultado.delete("1.0", tk.END)

            if isinstance(res, dict) and "Erro" in res:
                texto_resultado.insert(tk.END, f"Erro: {res['Erro']}")
                return

            for classe, valores in res.items():
                texto_resultado.insert(tk.END, f"{classe}\n")
                for key, val in valores.items():
                    texto_resultado.insert(tk.END, f"  {key}: {val}\n")
                texto_resultado.insert(tk.END, "\n-------------------------\n")

        # ---------- Botão Calcular ----------
        ttk.Button(frm, text="Calcular", command=calcular).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        return aba

        

    # --- ABA 3: Fila Finita (K) ---
    def create_tab_finite_k(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Capacidade Finita (K)")
        
        input_frame = ttk.Frame(tab, padding=10)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="Taxa de Chegada (λ):").grid(row=0, column=0, sticky='w')
        ent_lam = ttk.Entry(input_frame)
        ent_lam.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Taxa de Atendimento (μ):").grid(row=1, column=0, sticky='w')
        ent_mi = ttk.Entry(input_frame)
        ent_mi.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Número de Servidores (s):").grid(row=2, column=0, sticky='w')
        ent_s = ttk.Entry(input_frame)
        ent_s.insert(0, "1")
        ent_s.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Capacidade do Sistema (K):").grid(row=3, column=0, sticky='w')
        ent_k = ttk.Entry(input_frame)
        ent_k.grid(row=3, column=1, padx=5, pady=5)
        
        out_text = self.create_output_area(tab)
        
        def run():
            l = float(ent_lam.get())
            m = float(ent_mi.get())
            s = int(ent_s.get())
            k = int(ent_k.get())
            
            if s == 1:
                modelo = Mm1k(lam=l, mi=m, k=k)
                modelo.resultado()
            else:
                modelo = Mmsk(lam=l, mi=m, s=s, k=k)
                modelo.resultado()

        ttk.Button(input_frame, text="Calcular", command=lambda: self.capture_output(run, out_text)).grid(row=4, column=0, columnspan=2, pady=10)

    # --- ABA 4: População Finita (N) ---
    def create_tab_finite_n(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="População Finita (N)")
        
        input_frame = ttk.Frame(tab, padding=10)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="λ por cliente:").grid(row=0, column=0, sticky='w')
        ent_lam = ttk.Entry(input_frame)
        ent_lam.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Taxa de Atendimento (μ):").grid(row=1, column=0, sticky='w')
        ent_mi = ttk.Entry(input_frame)
        ent_mi.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Número de Servidores (s):").grid(row=2, column=0, sticky='w')
        ent_s = ttk.Entry(input_frame)
        ent_s.insert(0, "1")
        ent_s.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Tamanho da População (N):").grid(row=3, column=0, sticky='w')
        ent_n = ttk.Entry(input_frame)
        ent_n.grid(row=3, column=1, padx=5, pady=5)
        
        out_text = self.create_output_area(tab)
        
        def run():
            l = float(ent_lam.get())
            m = float(ent_mi.get())
            s = int(ent_s.get())
            n_pop = int(ent_n.get())
            
            if s == 1:
                modelo = Mm1n(lam_por_cliente=l, mi=m, n_pop=n_pop)
                modelo.resultado()
            else:
                modelo = Mmsn(lam_por_cliente=l, mi=m, s=s, n_pop=n_pop)
                modelo.resultado()

        ttk.Button(input_frame, text="Calcular", command=lambda: self.capture_output(run, out_text)).grid(row=4, column=0, columnspan=2, pady=10)

    # --- ABA 5: Resolver Lista ---
    def create_tab_lista_exercicios(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Resolver Lista Exercícios")
        
        desc = ttk.Label(tab, text="Esta função executa os testes definidos em 'ListaExercicios.py'\ne exibe os resultados abaixo.", justify="center", padding=20)
        desc.pack()
        
        out_text = self.create_output_area(tab)
        
        # Botão Grande para rodar a lista
        btn_run_list = ttk.Button(tab, text="RODAR LISTA DE EXERCÍCIOS", command=lambda: self.capture_output(rodar_testes, out_text))
        btn_run_list.pack(pady=10, ipadx=20, ipady=10)
    
    

if __name__ == "__main__":
    root = tk.Tk()
    app = FilaApp(root)
    root.mainloop()