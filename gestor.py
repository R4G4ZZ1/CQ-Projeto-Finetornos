


import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# =========================
# BANCO
# =========================

DB_PATH = r"X:\CQ\BACKUP_masilva\CONTROLE DE INSTRUMENTOS _Sistema\controle_instrumentos.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS instrumentos (
            id_instrumento TEXT PRIMARY KEY,
            nome TEXT,
            familia TEXT,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario TEXT PRIMARY KEY,
            nome TEXT
        )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =========================
# FAMILIAS
# =========================

FAMILIAS = [
    "PAQUIMETRO",
    "MICROMETRO",
    "IMICRO",
    "CALIBRADOR TAMPAO ROSCA",
    "CALIBRADOR RAIO",
    "CALIBRADOR FOLGA",
    "SUBITO",
    "RELOGIO APALPADOR",
    "RELOGIO COMPARADOR",
    "CALIBRADOR ANEL LISO",
    "PINO DE REFERENCIA"
]

# =========================
# INSTRUMENTOS
# =========================

def cadastrar_instrumento():
    codigo = entry_codigo_inst.get().strip().upper()
    nome = entry_nome_inst.get().strip()
    familia = combo_familia.get()

    if not codigo or not nome or not familia:
        messagebox.showwarning("Atenção", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO instrumentos VALUES (?, ?, ?, 'DISPONIVEL')",
                  (codigo, nome, familia))
        conn.commit()
        messagebox.showinfo("Sucesso", "Instrumento cadastrado com sucesso")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já cadastrado")

    conn.close()
    limpar_campos_inst()
    listar_instrumentos()

def listar_instrumentos():
    for row in tree_inst.get_children():
        tree_inst.delete(row)

    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM instrumentos")
    for row in c.fetchall():
        status = row[3]
        tag = "em_uso" if status == "EM USO" else "disponivel"
        tree_inst.insert("", tk.END, values=row, tags=(tag,))
    conn.close()

def remover_instrumento():
    selecionado = tree_inst.selection()
    if not selecionado:
        return

    codigo = tree_inst.item(selecionado)["values"][0]

    confirmar = messagebox.askyesno("Confirmar", f"Remover instrumento {codigo}?")
    if not confirmar:
        return

    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM instrumentos WHERE id_instrumento=?", (codigo,))
    conn.commit()
    conn.close()

    listar_instrumentos()

def selecionar_inst(event):
    selecionado = tree_inst.selection()
    if selecionado:
        valores = tree_inst.item(selecionado)["values"]
        entry_codigo_inst.delete(0, tk.END)
        entry_codigo_inst.insert(0, valores[0])
        entry_nome_inst.delete(0, tk.END)
        entry_nome_inst.insert(0, valores[1])
        combo_familia.set(valores[2])

def limpar_campos_inst():
    entry_codigo_inst.delete(0, tk.END)
    entry_nome_inst.delete(0, tk.END)
    combo_familia.set("")

# =========================
# FUNCIONÁRIOS
# =========================

def cadastrar_funcionario():
    codigo = entry_codigo_func.get().strip().upper()
    nome = entry_nome_func.get().strip()

    if not codigo or not nome:
        messagebox.showwarning("Atenção", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO funcionarios VALUES (?, ?)", (codigo, nome))
        conn.commit()
        messagebox.showinfo("Sucesso", "Funcionário cadastrado com sucesso")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já cadastrado")

    conn.close()
    limpar_campos_func()
    listar_funcionarios()

def listar_funcionarios():
    for row in tree_func.get_children():
        tree_func.delete(row)

    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM funcionarios")
    for row in c.fetchall():
        tree_func.insert("", tk.END, values=row)
    conn.close()

def remover_funcionario():
    selecionado = tree_func.selection()
    if not selecionado:
        return

    codigo = tree_func.item(selecionado)["values"][0]

    confirmar = messagebox.askyesno("Confirmar", f"Remover funcionário {codigo}?")
    if not confirmar:
        return

    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM funcionarios WHERE id_funcionario=?", (codigo,))
    conn.commit()
    conn.close()

    listar_funcionarios()

def selecionar_func(event):
    selecionado = tree_func.selection()
    if selecionado:
        valores = tree_func.item(selecionado)["values"]
        entry_codigo_func.delete(0, tk.END)
        entry_codigo_func.insert(0, valores[0])
        entry_nome_func.delete(0, tk.END)
        entry_nome_func.insert(0, valores[1])

def limpar_campos_func():
    entry_codigo_func.delete(0, tk.END)
    entry_nome_func.delete(0, tk.END)

# =========================
# CORES / TEMA FINETORNOS
# =========================

AZUL      = "#1B3F72"
AZUL_ESC  = "#122B52"
AZUL_MED  = "#2056A0"
CINZA     = "#9EA8B0"
CINZA_CLR = "#D6DCE1"
BRANCO    = "#FFFFFF"
FUNDO     = "#F0F3F6"
VERDE     = "#1A6E35"
VERDE_BG  = "#E6F4EC"
VERM      = "#B71C1C"
VERM_BG   = "#FDECEA"

# =========================
# HELPERS DE UI
# =========================

def make_label(parent, text, bold=False):
    font = ("Arial", 8, "bold") if bold else ("Arial", 8)
    return tk.Label(parent, text=text, font=font, fg=CINZA, bg=FUNDO, anchor="w")

def make_entry(parent):
    frame = tk.Frame(parent, bg=BRANCO, highlightbackground=CINZA_CLR, highlightthickness=1)
    entry = tk.Entry(
        frame,
        font=("Arial", 11),
        bd=0, relief="flat",
        bg=BRANCO, fg="#1A1A1A",
        insertbackground=AZUL,
    )
    entry.pack(fill="x", expand=True, ipady=7, padx=8)
    entry.bind("<FocusIn>",  lambda e: frame.config(highlightbackground=AZUL))
    entry.bind("<FocusOut>", lambda e: frame.config(highlightbackground=CINZA_CLR))
    return frame, entry

def make_button(parent, text, command, color=AZUL):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 9, "bold"),
        bg=color,
        fg=BRANCO,
        activebackground=AZUL_MED,
        activeforeground=BRANCO,
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=7,
        bd=0,
    )
    return btn

def style_treeview(tree, alternating=True):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
        background=BRANCO,
        foreground="#1A1A1A",
        rowheight=28,
        fieldbackground=BRANCO,
        bordercolor=CINZA_CLR,
        font=("Arial", 9),
    )
    style.configure("Custom.Treeview.Heading",
        background=AZUL,
        foreground=BRANCO,
        font=("Arial", 9, "bold"),
        relief="flat",
        padding=6,
    )
    style.map("Custom.Treeview",
        background=[("selected", AZUL_MED)],
        foreground=[("selected", BRANCO)],
    )
    style.map("Custom.Treeview.Heading",
        background=[("active", AZUL_ESC)],
    )
    tree.configure(style="Custom.Treeview")

    if alternating:
        tree.tag_configure("odd",  background="#EEF2F7")
        tree.tag_configure("even", background=BRANCO)

# =========================
# INTERFACE PRINCIPAL
# =========================

root = tk.Tk()
root.title("Painel do Gestor — Finetornos")
root.geometry("1020x680")
root.resizable(True, True)
root.configure(bg=FUNDO)

# ---------- Header ----------
header = tk.Frame(root, bg=AZUL, height=70)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="FINETORNOS", font=("Arial Black", 20, "bold"),
         fg=BRANCO, bg=AZUL).pack(side="left", padx=20, pady=10)

tk.Label(header, text="Painel do Gestor — Controle de Qualidade",
         font=("Arial", 9), fg=CINZA_CLR, bg=AZUL).place(x=22, y=46)

tk.Frame(root, bg=AZUL_MED, height=4).pack(fill="x")

# ---------- Notebook ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("FT.TNotebook",
    background=FUNDO,
    borderwidth=0,
    tabmargins=[0, 6, 0, 0],
)
style.configure("FT.TNotebook.Tab",
    background=CINZA_CLR,
    foreground="#444",
    font=("Arial", 9, "bold"),
    padding=[18, 8],
    borderwidth=0,
)
style.map("FT.TNotebook.Tab",
    background=[("selected", AZUL), ("active", AZUL_MED)],
    foreground=[("selected", BRANCO), ("active", BRANCO)],
)

notebook = ttk.Notebook(root, style="FT.TNotebook")
notebook.pack(fill="both", expand=True, padx=0, pady=0)

# ============================================================
# ABA INSTRUMENTOS
# ============================================================

frame_inst = tk.Frame(notebook, bg=FUNDO)
notebook.add(frame_inst, text="  🔧  Instrumentos  ")

# --- painel esquerdo (formulário) ---
painel_form_inst = tk.Frame(frame_inst, bg=FUNDO, width=280)
painel_form_inst.pack(side="left", fill="y", padx=(20, 10), pady=20)
painel_form_inst.pack_propagate(False)

tk.Label(painel_form_inst, text="CADASTRO DE INSTRUMENTO",
         font=("Arial", 10, "bold"), fg=AZUL, bg=FUNDO).pack(anchor="w", pady=(0, 12))

tk.Frame(painel_form_inst, bg=AZUL_MED, height=2).pack(fill="x", pady=(0, 14))

make_label(painel_form_inst, "CÓDIGO", bold=True).pack(fill="x", pady=(0, 3))
frame_cod_inst, entry_codigo_inst = make_entry(painel_form_inst)
frame_cod_inst.pack(fill="x", pady=(0, 10))

make_label(painel_form_inst, "NOME", bold=True).pack(fill="x", pady=(0, 3))
frame_nom_inst, entry_nome_inst = make_entry(painel_form_inst)
frame_nom_inst.pack(fill="x", pady=(0, 10))

make_label(painel_form_inst, "FAMÍLIA", bold=True).pack(fill="x", pady=(0, 3))

style.configure("FT.TCombobox",
    fieldbackground=BRANCO,
    background=BRANCO,
    foreground="#1A1A1A",
    bordercolor=CINZA_CLR,
    arrowcolor=AZUL,
    padding=6,
)
combo_familia = ttk.Combobox(painel_form_inst, values=FAMILIAS,
                              state="readonly", style="FT.TCombobox",
                              font=("Arial", 10))
combo_familia.pack(fill="x", pady=(0, 18))

btn_frame_inst = tk.Frame(painel_form_inst, bg=FUNDO)
btn_frame_inst.pack(fill="x", pady=(0, 6))

make_button(btn_frame_inst, "Cadastrar", cadastrar_instrumento, AZUL).pack(fill="x", pady=(0, 6))
make_button(btn_frame_inst, "Remover selecionado", remover_instrumento, VERM).pack(fill="x")

# separador vertical
tk.Frame(frame_inst, bg=CINZA_CLR, width=1).pack(side="left", fill="y", pady=16)

# --- painel direito (tabela) ---
painel_tree_inst = tk.Frame(frame_inst, bg=FUNDO)
painel_tree_inst.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)

tk.Label(painel_tree_inst, text="INSTRUMENTOS CADASTRADOS",
         font=("Arial", 10, "bold"), fg=AZUL, bg=FUNDO).pack(anchor="w", pady=(0, 12))
tk.Frame(painel_tree_inst, bg=AZUL_MED, height=2).pack(fill="x", pady=(0, 8))

frame_tree_inst = tk.Frame(painel_tree_inst, bg=FUNDO)
frame_tree_inst.pack(fill="both", expand=True)

tree_inst = ttk.Treeview(frame_tree_inst,
                          columns=("Código", "Nome", "Família", "Status"),
                          show="headings")

for col, w in (("Código", 110), ("Nome", 200), ("Família", 180), ("Status", 100)):
    tree_inst.heading(col, text=col)
    tree_inst.column(col, width=w, minwidth=60)

tree_inst.tag_configure("em_uso",    background="#FFF5E6", foreground="#8A5000")
tree_inst.tag_configure("disponivel", background=VERDE_BG,  foreground=VERDE)

style_treeview(tree_inst, alternating=False)

scroll_inst = ttk.Scrollbar(frame_tree_inst, orient="vertical", command=tree_inst.yview)
tree_inst.configure(yscrollcommand=scroll_inst.set)
scroll_inst.pack(side="right", fill="y")
tree_inst.pack(fill="both", expand=True)
tree_inst.bind("<<TreeviewSelect>>", selecionar_inst)

# ============================================================
# ABA FUNCIONÁRIOS
# ============================================================

frame_func = tk.Frame(notebook, bg=FUNDO)
notebook.add(frame_func, text="  👤  Funcionários  ")

# --- painel esquerdo (formulário) ---
painel_form_func = tk.Frame(frame_func, bg=FUNDO, width=280)
painel_form_func.pack(side="left", fill="y", padx=(20, 10), pady=20)
painel_form_func.pack_propagate(False)

tk.Label(painel_form_func, text="CADASTRO DE FUNCIONÁRIO",
         font=("Arial", 10, "bold"), fg=AZUL, bg=FUNDO).pack(anchor="w", pady=(0, 12))

tk.Frame(painel_form_func, bg=AZUL_MED, height=2).pack(fill="x", pady=(0, 14))

make_label(painel_form_func, "CÓDIGO / CRACHÁ", bold=True).pack(fill="x", pady=(0, 3))
frame_cod_func, entry_codigo_func = make_entry(painel_form_func)
frame_cod_func.pack(fill="x", pady=(0, 10))

make_label(painel_form_func, "NOME COMPLETO", bold=True).pack(fill="x", pady=(0, 3))
frame_nom_func, entry_nome_func = make_entry(painel_form_func)
frame_nom_func.pack(fill="x", pady=(0, 18))

btn_frame_func = tk.Frame(painel_form_func, bg=FUNDO)
btn_frame_func.pack(fill="x")

make_button(btn_frame_func, "Cadastrar", cadastrar_funcionario, AZUL).pack(fill="x", pady=(0, 6))
make_button(btn_frame_func, "Remover selecionado", remover_funcionario, VERM).pack(fill="x")

# separador vertical
tk.Frame(frame_func, bg=CINZA_CLR, width=1).pack(side="left", fill="y", pady=16)

# --- painel direito (tabela) ---
painel_tree_func = tk.Frame(frame_func, bg=FUNDO)
painel_tree_func.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)

tk.Label(painel_tree_func, text="FUNCIONÁRIOS CADASTRADOS",
         font=("Arial", 10, "bold"), fg=AZUL, bg=FUNDO).pack(anchor="w", pady=(0, 12))
tk.Frame(painel_tree_func, bg=AZUL_MED, height=2).pack(fill="x", pady=(0, 8))

frame_tree_func = tk.Frame(painel_tree_func, bg=FUNDO)
frame_tree_func.pack(fill="both", expand=True)

tree_func = ttk.Treeview(frame_tree_func,
                          columns=("Código", "Nome"),
                          show="headings")

tree_func.heading("Código", text="Código")
tree_func.column("Código", width=140, minwidth=80)
tree_func.heading("Nome", text="Nome")
tree_func.column("Nome", width=320, minwidth=120)

style_treeview(tree_func)

scroll_func = ttk.Scrollbar(frame_tree_func, orient="vertical", command=tree_func.yview)
tree_func.configure(yscrollcommand=scroll_func.set)
scroll_func.pack(side="right", fill="y")
tree_func.pack(fill="both", expand=True)
tree_func.bind("<<TreeviewSelect>>", selecionar_func)

# ---------- Footer ----------
tk.Frame(root, bg=CINZA_CLR, height=1).pack(fill="x", side="bottom")
footer = tk.Frame(root, bg=AZUL_ESC, height=30)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

from datetime import datetime
tk.Label(footer, text=f"CQ · {datetime.now().strftime('%d/%m/%Y')}",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="right", padx=16, pady=6)
tk.Label(footer, text="Sistema de Gestão de Instrumentos",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="left", padx=16, pady=6)

# =========================

listar_instrumentos()
listar_funcionarios()
root.mainloop()