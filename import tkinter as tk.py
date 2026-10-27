import tkinter as tk
from tkinter import ttk, messagebox
import math

# ---------------- Config / Percentuais ----------------
PERC_FELIPE = 0.2233
PERC_IARA   = 0.3398
PERC_JULIO  = 0.4369

PERC_IARA_LUZ  = 3500 / 8000
PERC_JULIO_LUZ = 4500 / 8000

ALUGUEL_CASA     = 2537.93
INTERNET_CASA    = 100.00

ALUGUEL_PESSOAL  = 531.45
FACULDADE_PESSOAL= 200.00
INTERNET_PESSOAL = 33.00
INGLES_PESSOAL   = 130.00

# ---------------- Helpers ----------------
def parse_val(value_str):
    try:
        return float(value_str.strip().replace(",", "."))
    except Exception:
        raise ValueError("Valor inválido. Use números (ex: 123,45 ou 123.45).")

def fmt(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- Paleta ----------------
C = {
    "bg":         "#0D0D14",
    "surface":    "#13131F",
    "card":       "#1A1A2A",
    "border":     "#2A2A40",
    "border2":    "#3A3A55",
    "fg":         "#F0F0FF",
    "fg2":        "#9090B0",
    "fg3":        "#5A5A7A",
    "green":      "#00E5A0",
    "green_d":    "#00B880",
    "blue":       "#4D8AFF",
    "blue_d":     "#2D6ADF",
    "yellow":     "#FFD166",
    "yellow_d":   "#E0B040",
    "red":        "#FF6B6B",
    "purple":     "#A78BFA",
    "iara":       "#FF8FAB",
    "julio":      "#60D0FF",
    "felipe":     "#A8FF78",
}

PESSOAS = {
    "Iara":   {"cor": C["iara"],   "perc": PERC_IARA,   "emoji": "🌸"},
    "Júlio":  {"cor": C["julio"],  "perc": PERC_JULIO,  "emoji": "🌊"},
    "Felipe": {"cor": C["felipe"], "perc": PERC_FELIPE, "emoji": "🌿"},
}

# ============================================================
class GestorContasApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Ragazzi · Gestor de Contas")
        self.geometry("760x680")
        self.minsize(700, 600)
        self.configure(bg=C["bg"])
        self.extras = []

        self._build_ui()

    # -------- UI Principal --------
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(hdr, text="💰", font=("Segoe UI Emoji", 28),
                 bg=C["bg"], fg=C["fg"]).pack(side="left")
        tk.Label(hdr, text="Gestor de Contas", font=("Georgia", 22, "bold"),
                 bg=C["bg"], fg=C["fg"]).pack(side="left", padx=(10, 0))
        tk.Label(hdr, text="Ragazzi", font=("Georgia", 22, "italic"),
                 bg=C["bg"], fg=C["purple"]).pack(side="left", padx=(6, 0))

        sep = tk.Frame(self, bg=C["border"], height=1)
        sep.pack(fill="x", padx=24, pady=(14, 0))

        # Tab bar custom
        self.tab_frame = tk.Frame(self, bg=C["bg"])
        self.tab_frame.pack(fill="x", padx=24, pady=(12, 0))

        self.pages = {}
        self.active_tab = tk.StringVar(value="casa")

        self._make_tab("casa",    "🏠  Casa",           self._page_casa)
        self._make_tab("pessoal", "👤  Pessoal (Felipe)", self._page_pessoal)

        # Container das páginas
        self.container = tk.Frame(self, bg=C["bg"])
        self.container.pack(fill="both", expand=True, padx=24, pady=12)

        self._show_tab("casa")

    def _make_tab(self, key, label, builder):
        btn = tk.Label(self.tab_frame, text=label,
                       font=("Segoe UI", 11, "bold"),
                       bg=C["bg"], fg=C["fg2"],
                       padx=18, pady=8, cursor="hand2")
        btn.pack(side="left")
        btn.bind("<Button-1>", lambda e, k=key: self._show_tab(k))
        self.pages[key] = {"btn": btn, "builder": builder, "frame": None}

    def _show_tab(self, key):
        self.active_tab.set(key)
        for k, p in self.pages.items():
            if k == key:
                p["btn"].config(fg=C["fg"],
                                relief="flat",
                                bg=C["card"],
                                bd=0)
            else:
                p["btn"].config(fg=C["fg2"], bg=C["bg"])

        # Destrói frames antigos
        for widget in self.container.winfo_children():
            widget.destroy()

        # Reconstrói a página ativa
        self.pages[key]["builder"]()

    # ============================================================
    # PÁGINA CASA
    # ============================================================
    def _page_casa(self):
        outer = tk.Frame(self.container, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        # -- Inputs --
        card_in = self._card(outer, "Valores do Mês")
        card_in.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(card_in, bg=C["card"])
        row1.pack(fill="x", padx=16, pady=(4, 10))

        self.entry_agua_casa = self._labeled_entry(row1, "💧 Água (R$)", side="left", expand=True)
        tk.Frame(row1, bg=C["card"], width=16).pack(side="left")
        self.entry_luz_casa  = self._labeled_entry(row1, "⚡ Luz (R$)",  side="left", expand=True)

        self._btn(card_in, "Calcular Divisão da Casa", self.calcular_casa,
                  C["green"], "#000", pady=10)

        # -- Resultado --
        self.frame_resultado_casa = tk.Frame(outer, bg=C["bg"])
        self.frame_resultado_casa.pack(fill="both", expand=True)

    def calcular_casa(self):
        try:
            agua = parse_val(self.entry_agua_casa.get() or "0")
            luz  = parse_val(self.entry_luz_casa.get()  or "0")
        except ValueError as e:
            messagebox.showerror("Erro", str(e)); return

        # Cálculos
        contas = {
            "Aluguel":  {
                "total": ALUGUEL_CASA,
                "Iara":   ALUGUEL_CASA * PERC_IARA,
                "Júlio":  ALUGUEL_CASA * PERC_JULIO,
                "Felipe": ALUGUEL_CASA * PERC_FELIPE,
                "obs": None,
            },
            "Internet": {
                "total": INTERNET_CASA,
                "Iara":   INTERNET_CASA * PERC_IARA,
                "Júlio":  INTERNET_CASA * PERC_JULIO,
                "Felipe": INTERNET_CASA * PERC_FELIPE,
                "obs": None,
            },
            "Água": {
                "total": agua,
                "Iara":   agua * PERC_IARA,
                "Júlio":  agua * PERC_JULIO,
                "Felipe": agua * PERC_FELIPE,
                "obs": None,
            },
            "Luz": {
                "total": luz,
                "Iara":   luz * PERC_IARA_LUZ,
                "Júlio":  luz * PERC_JULIO_LUZ,
                "Felipe": 0.0,
                "obs": "Felipe não paga luz",
            },
        }

        totais = {
            "Iara":   sum(c["Iara"]   for c in contas.values()),
            "Júlio":  sum(c["Júlio"]  for c in contas.values()),
            "Felipe": sum(c["Felipe"] for c in contas.values()),
        }
        total_geral = ALUGUEL_CASA + INTERNET_CASA + agua + luz

        # Limpa resultado anterior
        for w in self.frame_resultado_casa.winfo_children():
            w.destroy()

        # === Cards de resumo por pessoa ===
        row_cards = tk.Frame(self.frame_resultado_casa, bg=C["bg"])
        row_cards.pack(fill="x", pady=(0, 10))

        for nome, info in PESSOAS.items():
            val = totais[nome]
            pct = (val / total_geral * 100) if total_geral else 0
            self._resumo_card(row_cards, nome, info, val, pct, total_geral)

        # === Tabela detalhada ===
        card_tab = self._card(self.frame_resultado_casa, "Detalhamento por Conta")
        card_tab.pack(fill="both", expand=True)

        # Header da tabela
        hdr = tk.Frame(card_tab, bg=C["border"])
        hdr.pack(fill="x", padx=12, pady=(4, 0))

        cols = [("Conta", 120, "w"), ("Total", 90, "center"),
                ("🌸 Iara", 110, "center"), ("🌊 Júlio", 110, "center"), ("🌿 Felipe", 110, "center")]
        for txt, w, anchor in cols:
            tk.Label(hdr, text=txt, width=w//7, font=("Segoe UI", 9, "bold"),
                     bg=C["border"], fg=C["fg2"], anchor=anchor, pady=6).pack(side="left", fill="x",
                     expand=(txt=="Conta"))

        # Linhas
        for i, (nome_conta, c) in enumerate(contas.items()):
            bg = C["card"] if i % 2 == 0 else C["surface"]
            linha = tk.Frame(card_tab, bg=bg)
            linha.pack(fill="x", padx=12)

            tk.Label(linha, text=nome_conta, font=("Segoe UI", 10, "bold"),
                     bg=bg, fg=C["fg"], anchor="w", pady=8, padx=6).pack(side="left", fill="x", expand=True)

            tk.Label(linha, text=fmt(c["total"]), font=("Consolas", 10),
                     bg=bg, fg=C["fg2"], width=12, anchor="center").pack(side="left")

            for pessoa in ["Iara", "Júlio", "Felipe"]:
                cor = PESSOAS[pessoa]["cor"]
                val_p = c[pessoa]
                txt_p = fmt(val_p) if val_p > 0 else "—"
                tk.Label(linha, text=txt_p, font=("Consolas", 10),
                         bg=bg, fg=cor if val_p > 0 else C["fg3"],
                         width=13, anchor="center").pack(side="left")

            if c["obs"]:
                tk.Label(linha, text=f"  ⚠ {c['obs']}", font=("Segoe UI", 8),
                         bg=bg, fg=C["yellow"]).pack(side="left", padx=4)

        # Linha de total
        tot_linha = tk.Frame(card_tab, bg=C["border2"])
        tot_linha.pack(fill="x", padx=12, pady=(2, 8))

        tk.Label(tot_linha, text="TOTAL GERAL", font=("Segoe UI", 10, "bold"),
                 bg=C["border2"], fg=C["fg"], anchor="w", pady=8, padx=6).pack(side="left", fill="x", expand=True)
        tk.Label(tot_linha, text=fmt(total_geral), font=("Consolas", 10, "bold"),
                 bg=C["border2"], fg=C["fg"], width=12, anchor="center").pack(side="left")

        for nome in ["Iara", "Júlio", "Felipe"]:
            cor = PESSOAS[nome]["cor"]
            tk.Label(tot_linha, text=fmt(totais[nome]), font=("Consolas", 10, "bold"),
                     bg=C["border2"], fg=cor, width=13, anchor="center").pack(side="left")

    def _resumo_card(self, parent, nome, info, valor, pct, total):
        cor = info["cor"]
        card = tk.Frame(parent, bg=C["card"],
                        highlightbackground=cor,
                        highlightthickness=2)
        card.pack(side="left", fill="both", expand=True, padx=4)

        # Barra colorida no topo
        barra = tk.Frame(card, bg=cor, height=4)
        barra.pack(fill="x")

        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill="both", padx=14, pady=10)

        # Nome + emoji
        tk.Label(inner, text=f"{info['emoji']}  {nome}",
                 font=("Georgia", 12, "bold"),
                 bg=C["card"], fg=cor).pack(anchor="w")

        # Valor principal
        tk.Label(inner, text=fmt(valor),
                 font=("Consolas", 16, "bold"),
                 bg=C["card"], fg=C["fg"]).pack(anchor="w", pady=(6, 2))

        # Percentual
        tk.Label(inner, text=f"{pct:.1f}% do total",
                 font=("Segoe UI", 9),
                 bg=C["card"], fg=C["fg2"]).pack(anchor="w")

        # Mini barra de progresso
        bar_bg = tk.Frame(inner, bg=C["border"], height=5)
        bar_bg.pack(fill="x", pady=(8, 0))
        bar_bg.update_idletasks()
        w = bar_bg.winfo_width() or 160
        fill_w = int(w * pct / 100)
        bar_fill = tk.Frame(bar_bg, bg=cor, height=5, width=fill_w)
        bar_fill.place(x=0, y=0)

    # ============================================================
    # PÁGINA PESSOAL
    # ============================================================
    def _page_pessoal(self):
        outer = tk.Frame(self.container, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        # Inputs variáveis
        card_var = self._card(outer, "Valores Variáveis do Mês")
        card_var.pack(fill="x", pady=(0, 10))

        row_var = tk.Frame(card_var, bg=C["card"])
        row_var.pack(fill="x", padx=16, pady=(4, 10))
        self.entry_agua_p = self._labeled_entry(row_var, "💧 Água (R$)", side="left", expand=True)
        tk.Frame(row_var, bg=C["card"], width=16).pack(side="left")
        self.entry_luz_p  = self._labeled_entry(row_var, "⚡ Luz (R$)",  side="left", expand=True)

        # Fixos (visual somente)
        card_fix = self._card(outer, "Gastos Fixos Mensais")
        card_fix.pack(fill="x", pady=(0, 10))

        fixos = [
            ("🏠 Aluguel Pessoal", ALUGUEL_PESSOAL),
            ("🎓 Faculdade",        FACULDADE_PESSOAL),
            ("📡 Internet",         INTERNET_PESSOAL),
            ("🇬🇧 Inglês",          INGLES_PESSOAL),
        ]
        row_fix = tk.Frame(card_fix, bg=C["card"])
        row_fix.pack(fill="x", padx=16, pady=(4, 12))
        for i, (label, val) in enumerate(fixos):
            f = tk.Frame(row_fix, bg=C["surface"],
                         highlightbackground=C["border2"],
                         highlightthickness=1)
            f.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(f, text=label, font=("Segoe UI", 9),
                     bg=C["surface"], fg=C["fg2"], pady=4).pack()
            tk.Label(f, text=fmt(val), font=("Consolas", 11, "bold"),
                     bg=C["surface"], fg=C["felipe"], pady=2).pack()

        # Extras
        card_ext = self._card(outer, "Despesas Extras")
        card_ext.pack(fill="x", pady=(0, 10))

        row_ext = tk.Frame(card_ext, bg=C["card"])
        row_ext.pack(fill="x", padx=16, pady=(4, 8))

        self.entry_extra_nome  = self._labeled_entry(row_ext, "📝 Nome",     side="left", expand=True)
        tk.Frame(row_ext, bg=C["card"], width=12).pack(side="left")
        self.entry_extra_valor = self._labeled_entry(row_ext, "💵 Valor (R$)", side="left", expand=False, w=14)
        tk.Frame(row_ext, bg=C["card"], width=12).pack(side="left")

        self._btn(row_ext, "+ Adicionar", self.adicionar_extra,
                  C["yellow"], "#000", pady=0, padx=4, side="left")

        # Lista de extras
        self.frame_lista_extras = tk.Frame(card_ext, bg=C["card"])
        self.frame_lista_extras.pack(fill="x", padx=16, pady=(0, 4))
        self._render_extras()

        # Botão calcular
        btn_frame = tk.Frame(outer, bg=C["bg"])
        btn_frame.pack(fill="x")
        self._btn(btn_frame, "Calcular Total Pessoal", self.calcular_pessoal,
                  C["blue"], C["fg"], pady=10)

        # Resultado
        self.frame_resultado_pessoal = tk.Frame(outer, bg=C["bg"])
        self.frame_resultado_pessoal.pack(fill="both", expand=True, pady=(10, 0))

    def _render_extras(self):
        for w in self.frame_lista_extras.winfo_children():
            w.destroy()

        if not self.extras:
            tk.Label(self.frame_lista_extras, text="Nenhuma despesa extra adicionada.",
                     font=("Segoe UI", 9, "italic"),
                     bg=C["card"], fg=C["fg3"], pady=4).pack(anchor="w")
            return

        for i, (nome, val) in enumerate(self.extras):
            row = tk.Frame(self.frame_lista_extras, bg=C["card"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"  ·  {nome}", font=("Segoe UI", 10),
                     bg=C["card"], fg=C["fg"], anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=fmt(val), font=("Consolas", 10),
                     bg=C["card"], fg=C["yellow"]).pack(side="left", padx=8)
            tk.Button(row, text="✕", font=("Segoe UI", 9),
                      bg=C["card"], fg=C["red"], bd=0, cursor="hand2",
                      activebackground=C["card"], activeforeground=C["red"],
                      command=lambda idx=i: self._remover_extra(idx)).pack(side="left", padx=4)

        # Total extras
        tot = tk.Frame(self.frame_lista_extras, bg=C["border"])
        tot.pack(fill="x", pady=(4, 0))
        tk.Label(tot, text="  Total extras:", font=("Segoe UI", 9, "bold"),
                 bg=C["border"], fg=C["fg2"], pady=3).pack(side="left")
        tk.Label(tot, text=fmt(sum(v for _, v in self.extras)), font=("Consolas", 10, "bold"),
                 bg=C["border"], fg=C["yellow"]).pack(side="right", padx=8)

        btn_limpar = tk.Label(self.frame_lista_extras, text="🗑  Limpar tudo",
                              font=("Segoe UI", 9), bg=C["card"], fg=C["red"],
                              cursor="hand2", pady=4)
        btn_limpar.pack(anchor="e")
        btn_limpar.bind("<Button-1>", lambda e: self.limpar_extras())

    def _remover_extra(self, idx):
        self.extras.pop(idx)
        self._render_extras()

    def adicionar_extra(self):
        nome = self.entry_extra_nome.get().strip()
        valor_str = self.entry_extra_valor.get().strip()
        if not nome or not valor_str:
            messagebox.showwarning("Aviso", "Preencha nome e valor antes de adicionar."); return
        try:
            valor = parse_val(valor_str)
        except ValueError as e:
            messagebox.showerror("Erro", str(e)); return

        self.extras.append((nome, valor))
        self.entry_extra_nome.delete(0, tk.END)
        self.entry_extra_valor.delete(0, tk.END)
        self._render_extras()

    def limpar_extras(self):
        self.extras.clear()
        self._render_extras()

    def calcular_pessoal(self):
        try:
            agua = parse_val(self.entry_agua_p.get() or "0")
            luz  = parse_val(self.entry_luz_p.get()  or "0")
        except ValueError as e:
            messagebox.showerror("Erro", str(e)); return

        total_extras = sum(v for (_, v) in self.extras)
        fixos_total  = ALUGUEL_PESSOAL + FACULDADE_PESSOAL + INTERNET_PESSOAL + INGLES_PESSOAL
        total        = fixos_total + agua + luz + total_extras

        for w in self.frame_resultado_pessoal.winfo_children():
            w.destroy()

        card = self._card(self.frame_resultado_pessoal, "Resumo Pessoal — Felipe 🌿")
        card.pack(fill="both", expand=True)

        linhas = [
            ("🏠 Aluguel Pessoal",  ALUGUEL_PESSOAL,  False),
            ("🎓 Faculdade",         FACULDADE_PESSOAL, False),
            ("📡 Internet",          INTERNET_PESSOAL,  False),
            ("🇬🇧 Inglês",           INGLES_PESSOAL,    False),
            ("💧 Água",              agua,              True),
            ("⚡ Luz",               luz,               True),
        ]

        for i, (label, val, variavel) in enumerate(linhas):
            bg = C["card"] if i % 2 == 0 else C["surface"]
            r = tk.Frame(card, bg=bg)
            r.pack(fill="x", padx=12)
            cor_val = C["yellow"] if variavel else C["felipe"]
            tag = " (variável)" if variavel else " (fixo)"
            tk.Label(r, text=label, font=("Segoe UI", 10),
                     bg=bg, fg=C["fg"], anchor="w", pady=7, padx=8).pack(side="left", fill="x", expand=True)
            tk.Label(r, text=tag, font=("Segoe UI", 8),
                     bg=bg, fg=C["fg3"]).pack(side="left")
            tk.Label(r, text=fmt(val), font=("Consolas", 11, "bold"),
                     bg=bg, fg=cor_val, padx=12).pack(side="right")

        if self.extras:
            sep2 = tk.Frame(card, bg=C["yellow"], height=1)
            sep2.pack(fill="x", padx=12, pady=4)
            tk.Label(card, text="  Despesas Extras", font=("Segoe UI", 9, "bold"),
                     bg=C["card"], fg=C["yellow"], anchor="w").pack(fill="x", padx=12)
            for i, (nome, val) in enumerate(self.extras):
                bg = C["card"] if i % 2 == 0 else C["surface"]
                r = tk.Frame(card, bg=bg)
                r.pack(fill="x", padx=12)
                tk.Label(r, text=f"  · {nome}", font=("Segoe UI", 10),
                         bg=bg, fg=C["fg"], anchor="w", pady=6, padx=8).pack(side="left", fill="x", expand=True)
                tk.Label(r, text=fmt(val), font=("Consolas", 11, "bold"),
                         bg=bg, fg=C["yellow"], padx=12).pack(side="right")

        # Linha total
        tot = tk.Frame(card, bg=C["blue_d"])
        tot.pack(fill="x", padx=12, pady=(6, 8))
        tk.Label(tot, text="  TOTAL PESSOAL", font=("Georgia", 12, "bold"),
                 bg=C["blue_d"], fg=C["fg"], pady=10, padx=4).pack(side="left")
        tk.Label(tot, text=fmt(total), font=("Consolas", 16, "bold"),
                 bg=C["blue_d"], fg=C["fg"], padx=12).pack(side="right")

    # ============================================================
    # Widgets auxiliares
    # ============================================================
    def _card(self, parent, titulo):
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        # sem outer.pack — quem chama decide
        inner = tk.Frame(outer, bg=C["card"])
        inner.pack(fill="both", expand=True)

        hdr = tk.Frame(inner, bg=C["surface"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=titulo, font=("Georgia", 11, "bold"),
                 bg=C["surface"], fg=C["fg"], anchor="w",
                 padx=14, pady=9).pack(fill="x")

        sep = tk.Frame(inner, bg=C["border"], height=1)
        sep.pack(fill="x")

        # Retorna o inner pra widgets serem colocados dentro
        return inner

    def _labeled_entry(self, parent, label, side="top", expand=False, w=20):
        frame = tk.Frame(parent, bg=C["card"])
        frame.pack(side=side, fill="x", expand=expand)

        tk.Label(frame, text=label, font=("Segoe UI", 9),
                 bg=C["card"], fg=C["fg2"], pady=3).pack(anchor="w")

        entry = tk.Entry(frame, bg=C["surface"], fg=C["fg"],
                         insertbackground=C["fg"],
                         highlightbackground=C["border2"],
                         highlightcolor=C["blue"],
                         highlightthickness=1,
                         relief="flat",
                         font=("Consolas", 12),
                         width=w)
        entry.pack(fill="x" if expand else None, ipady=6, padx=2)
        return entry

    def _btn(self, parent, texto, cmd, bg, fg, pady=6, padx=0, side="top"):
        btn = tk.Button(parent, text=texto, command=cmd,
                        bg=bg, fg=fg, activebackground=bg,
                        activeforeground=fg,
                        font=("Segoe UI", 11, "bold"),
                        relief="flat", bd=0,
                        cursor="hand2",
                        padx=padx or 10)
        btn.pack(side=side, fill="x" if side == "top" else None,
                 ipady=pady, pady=4, padx=4 if side == "left" else 0)
        # Hover
        def on_enter(e): btn.config(bg=self._lighten(bg))
        def on_leave(e): btn.config(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _lighten(self, hex_color):
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02X}{g:02X}{b:02X}"
        except:
            return hex_color

# -------- Run --------
if __name__ == "__main__":
    app = GestorContasApp()
    app.mainloop()