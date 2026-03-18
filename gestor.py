<<<<<<< Updated upstream
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# =========================
# BANCO
# =========================

def conectar():
    return sqlite3.connect("controle_instrumentos.db")

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
        messagebox.showwarning("Erro", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO instrumentos VALUES (?, ?, ?, 'DISPONIVEL')",
                  (codigo, nome, familia))
        conn.commit()
        messagebox.showinfo("Sucesso", "Instrumento cadastrado")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já existe")

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
        tree_inst.insert("", tk.END, values=row)
    conn.close()

def remover_instrumento():
    selecionado = tree_inst.selection()
    if not selecionado:
        return

    codigo = tree_inst.item(selecionado)["values"][0]

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
        messagebox.showwarning("Erro", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO funcionarios VALUES (?, ?)", (codigo, nome))
        conn.commit()
        messagebox.showinfo("Sucesso", "Funcionário cadastrado")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já existe")

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
# INTERFACE
# =========================

root = tk.Tk()
root.title("Painel do Gestor")
root.geometry("1000x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# =========================
# ABA INSTRUMENTOS
# =========================

frame_inst = tk.Frame(notebook)
notebook.add(frame_inst, text="Instrumentos")

tk.Label(frame_inst, text="Código").pack()
entry_codigo_inst = tk.Entry(frame_inst)
entry_codigo_inst.pack()

tk.Label(frame_inst, text="Nome").pack()
entry_nome_inst = tk.Entry(frame_inst)
entry_nome_inst.pack()

tk.Label(frame_inst, text="Família").pack()
combo_familia = ttk.Combobox(frame_inst, values=FAMILIAS, state="readonly")
combo_familia.pack()

tk.Button(frame_inst, text="Cadastrar", command=cadastrar_instrumento).pack(pady=5)
tk.Button(frame_inst, text="Remover", command=remover_instrumento).pack(pady=5)

tree_inst = ttk.Treeview(frame_inst,
                         columns=("Código", "Nome", "Família", "Status"),
                         show="headings")

for col in ("Código", "Nome", "Família", "Status"):
    tree_inst.heading(col, text=col)

tree_inst.pack(fill="both", expand=True)
tree_inst.bind("<<TreeviewSelect>>", selecionar_inst)

# =========================
# ABA FUNCIONÁRIOS
# =========================

frame_func = tk.Frame(notebook)
notebook.add(frame_func, text="Funcionários")

tk.Label(frame_func, text="Código do Funcionário").pack()
entry_codigo_func = tk.Entry(frame_func)
entry_codigo_func.pack()

tk.Label(frame_func, text="Nome").pack()
entry_nome_func = tk.Entry(frame_func)
entry_nome_func.pack()

tk.Button(frame_func, text="Cadastrar", command=cadastrar_funcionario).pack(pady=5)
tk.Button(frame_func, text="Remover", command=remover_funcionario).pack(pady=5)

tree_func = ttk.Treeview(frame_func,
                         columns=("Código", "Nome"),
                         show="headings")

tree_func.heading("Código", text="Código")
tree_func.heading("Nome", text="Nome")

tree_func.pack(fill="both", expand=True)
tree_func.bind("<<TreeviewSelect>>", selecionar_func)

# =========================

listar_instrumentos()
listar_funcionarios()

=======
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# =========================
# BANCO
# =========================

def conectar():
    return sqlite3.connect("controle_instrumentos.db")

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
        messagebox.showwarning("Erro", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO instrumentos VALUES (?, ?, ?, 'DISPONIVEL')",
                  (codigo, nome, familia))
        conn.commit()
        messagebox.showinfo("Sucesso", "Instrumento cadastrado")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já existe")

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
        tree_inst.insert("", tk.END, values=row)
    conn.close()

def remover_instrumento():
    selecionado = tree_inst.selection()
    if not selecionado:
        return

    codigo = tree_inst.item(selecionado)["values"][0]

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
        messagebox.showwarning("Erro", "Preencha todos os campos")
        return

    conn = conectar()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO funcionarios VALUES (?, ?)", (codigo, nome))
        conn.commit()
        messagebox.showinfo("Sucesso", "Funcionário cadastrado")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Código já existe")

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
# INTERFACE
# =========================

root = tk.Tk()
root.title("Painel do Gestor")
root.geometry("1000x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# =========================
# ABA INSTRUMENTOS
# =========================

frame_inst = tk.Frame(notebook)
notebook.add(frame_inst, text="Instrumentos")

tk.Label(frame_inst, text="Código").pack()
entry_codigo_inst = tk.Entry(frame_inst)
entry_codigo_inst.pack()

tk.Label(frame_inst, text="Nome").pack()
entry_nome_inst = tk.Entry(frame_inst)
entry_nome_inst.pack()

tk.Label(frame_inst, text="Família").pack()
combo_familia = ttk.Combobox(frame_inst, values=FAMILIAS, state="readonly")
combo_familia.pack()

tk.Button(frame_inst, text="Cadastrar", command=cadastrar_instrumento).pack(pady=5)
tk.Button(frame_inst, text="Remover", command=remover_instrumento).pack(pady=5)

tree_inst = ttk.Treeview(frame_inst,
                         columns=("Código", "Nome", "Família", "Status"),
                         show="headings")

for col in ("Código", "Nome", "Família", "Status"):
    tree_inst.heading(col, text=col)

tree_inst.pack(fill="both", expand=True)
tree_inst.bind("<<TreeviewSelect>>", selecionar_inst)

# =========================
# ABA FUNCIONÁRIOS
# =========================

frame_func = tk.Frame(notebook)
notebook.add(frame_func, text="Funcionários")

tk.Label(frame_func, text="Código do Funcionário").pack()
entry_codigo_func = tk.Entry(frame_func)
entry_codigo_func.pack()

tk.Label(frame_func, text="Nome").pack()
entry_nome_func = tk.Entry(frame_func)
entry_nome_func.pack()

tk.Button(frame_func, text="Cadastrar", command=cadastrar_funcionario).pack(pady=5)
tk.Button(frame_func, text="Remover", command=remover_funcionario).pack(pady=5)

tree_func = ttk.Treeview(frame_func,
                         columns=("Código", "Nome"),
                         show="headings")

tree_func.heading("Código", text="Código")
tree_func.heading("Nome", text="Nome")

tree_func.pack(fill="both", expand=True)
tree_func.bind("<<TreeviewSelect>>", selecionar_func)

# =========================

listar_instrumentos()
listar_funcionarios()

>>>>>>> Stashed changes
root.mainloop()