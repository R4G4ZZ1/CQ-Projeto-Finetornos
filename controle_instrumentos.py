<<<<<<< HEAD
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import subprocess
import sys

# =========================
# CAMINHOS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "controle_instrumentos.db")

# =========================
# BANCO
# =========================
def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario TEXT PRIMARY KEY,
            nome TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS instrumentos (
            id_instrumento TEXT PRIMARY KEY,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario TEXT,
            id_instrumento TEXT,
            data_saida TEXT,
            data_devolucao TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

def seed():
    conn = conectar()
    c = conn.cursor()

    instrumentos = [
        "7.03.00164-N01",
        "7.03.00164-N02",
        "7.03.00164-N04",
        "7.03.00164-N05",
    ]

    for i in instrumentos:
        c.execute(
            "INSERT OR IGNORE INTO instrumentos VALUES (?, 'DISPONIVEL')", (i,)
        )

    funcionarios = [
        ("001803", "Felipe Ramos"),
        ("001641", "Marcelo Marques"),
    ]

    for f in funcionarios:
        c.execute(
            "INSERT OR IGNORE INTO funcionarios VALUES (?, ?)", f
        )

    conn.commit()
    conn.close()

# =========================
# EXCEL DINÂMICO
# =========================
def formatar_data(d):
    if not d:
        return ""
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")

def exportar_excel():
    conn = conectar()

    df_mov = pd.read_sql_query("""
        SELECT 
            f.nome AS Nome,
            m.id_funcionario AS Cracha,
            m.id_instrumento AS Instrumento,
            m.data_saida AS "Data Saída",
            m.data_devolucao AS "Data Devolução",
            m.status AS Status
        FROM movimentacoes m
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
    """, conn)

    df_mov["Data Saída"] = df_mov["Data Saída"].apply(formatar_data)
    df_mov["Data Devolução"] = df_mov["Data Devolução"].apply(formatar_data)

    df_inst = pd.read_sql_query("""
        SELECT id_instrumento AS Instrumento, status AS Status
        FROM instrumentos
    """, conn)

    conn.close()

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome_excel = f"controle_instrumentos_{agora}.xlsx"
    caminho_excel = os.path.join(BASE_DIR, nome_excel)

    with pd.ExcelWriter(caminho_excel, engine="openpyxl") as writer:
        df_mov.to_excel(writer, sheet_name="Movimentacoes", index=False)
        df_inst.to_excel(writer, sheet_name="Instrumentos", index=False)

    # Abrir automaticamente
    if sys.platform.startswith("win"):
        os.startfile(caminho_excel)
    elif sys.platform.startswith("linux"):
        subprocess.call(["xdg-open", caminho_excel])
    else:
        subprocess.call(["open", caminho_excel])

    messagebox.showinfo("Excel", "Planilha gerada com sucesso!")

# =========================
# LÓGICA
# =========================
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def processar_bip(func, inst):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT status FROM instrumentos WHERE id_instrumento=?", (inst,))
    r = c.fetchone()

    if not r:
        conn.close()
        return "❌ Instrumento não cadastrado"

    if r[0] == "DISPONIVEL":
        c.execute("""
            INSERT INTO movimentacoes
            (id_funcionario, id_instrumento, data_saida, status)
            VALUES (?, ?, ?, 'EM USO')
        """, (func, inst, agora()))

        c.execute("""
            UPDATE instrumentos SET status='EM USO'
            WHERE id_instrumento=?
        """, (inst,))

        conn.commit()
        conn.close()
        return "✅ Instrumento RETIRADO"

    c.execute("""
        SELECT id FROM movimentacoes
        WHERE id_instrumento=? AND status='EM USO'
        ORDER BY id DESC LIMIT 1
    """, (inst,))
    mov = c.fetchone()

    if mov:
        c.execute("""
            UPDATE movimentacoes
            SET data_devolucao=?, status='DEVOLVIDO'
            WHERE id=?
        """, (agora(), mov[0]))

        c.execute("""
            UPDATE instrumentos SET status='DISPONIVEL'
            WHERE id_instrumento=?
        """, (inst,))

        conn.commit()
        conn.close()
        return "🔁 Instrumento DEVOLVIDO"

    conn.close()
    return "⚠️ Erro"

# =========================
# UI
# =========================
def bipar(event=None):
    f = entry_func.get().strip()
    i = entry_inst.get().strip().upper()

    if not f or not i:
        return

    lbl_status.config(text=processar_bip(f, i))
    entry_func.delete(0, tk.END)
    entry_inst.delete(0, tk.END)
    entry_func.focus()

# =========================
# START
# =========================
inicializar_banco()
seed()

janela = tk.Tk()
janela.title("Controle de Instrumentos - CQ")
janela.geometry("420x280")
janela.resizable(False, False)

tk.Label(janela, text="Bipe o CRACHÁ").pack(pady=5)
entry_func = tk.Entry(janela, font=("Arial", 12))
entry_func.pack()

tk.Label(janela, text="Bipe o INSTRUMENTO").pack(pady=5)
entry_inst = tk.Entry(janela, font=("Arial", 12))
entry_inst.pack()
entry_inst.bind("<Return>", bipar)

lbl_status = tk.Label(janela, text="", font=("Arial", 10))
lbl_status.pack(pady=10)

tk.Button(
    janela,
    text="Exportar para Excel",
    bg="#1f6aa5",
    fg="white",
    font=("Arial", 11),
    command=exportar_excel
).pack(pady=5)

entry_func.focus()
janela.mainloop()
=======
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import subprocess
import sys

# =========================
# CAMINHOS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "controle_instrumentos.db")

# =========================
# BANCO
# =========================
def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario TEXT PRIMARY KEY,
            nome TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS instrumentos (
            id_instrumento TEXT PRIMARY KEY,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario TEXT,
            id_instrumento TEXT,
            data_saida TEXT,
            data_devolucao TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

def seed():
    conn = conectar()
    c = conn.cursor()

    instrumentos = [
        "7.03.00164-N01",
        "7.03.00164-N02",
        "7.03.00164-N04",
        "7.03.00164-N05",
    ]

    for i in instrumentos:
        c.execute(
            "INSERT OR IGNORE INTO instrumentos VALUES (?, 'DISPONIVEL')", (i,)
        )

    funcionarios = [
        ("001803", "Felipe Ramos"),
        ("001641", "Marcelo Marques"),
    ]

    for f in funcionarios:
        c.execute(
            "INSERT OR IGNORE INTO funcionarios VALUES (?, ?)", f
        )

    conn.commit()
    conn.close()

# =========================
# EXCEL DINÂMICO
# =========================
def formatar_data(d):
    if not d:
        return ""
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")

def exportar_excel():
    conn = conectar()

    df_mov = pd.read_sql_query("""
        SELECT 
            f.nome AS Nome,
            m.id_funcionario AS Cracha,
            m.id_instrumento AS Instrumento,
            m.data_saida AS "Data Saída",
            m.data_devolucao AS "Data Devolução",
            m.status AS Status
        FROM movimentacoes m
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
    """, conn)

    df_mov["Data Saída"] = df_mov["Data Saída"].apply(formatar_data)
    df_mov["Data Devolução"] = df_mov["Data Devolução"].apply(formatar_data)

    df_inst = pd.read_sql_query("""
        SELECT id_instrumento AS Instrumento, status AS Status
        FROM instrumentos
    """, conn)

    conn.close()

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome_excel = f"controle_instrumentos_{agora}.xlsx"
    caminho_excel = os.path.join(BASE_DIR, nome_excel)

    with pd.ExcelWriter(caminho_excel, engine="openpyxl") as writer:
        df_mov.to_excel(writer, sheet_name="Movimentacoes", index=False)
        df_inst.to_excel(writer, sheet_name="Instrumentos", index=False)

    # Abrir automaticamente
    if sys.platform.startswith("win"):
        os.startfile(caminho_excel)
    elif sys.platform.startswith("linux"):
        subprocess.call(["xdg-open", caminho_excel])
    else:
        subprocess.call(["open", caminho_excel])

    messagebox.showinfo("Excel", "Planilha gerada com sucesso!")

# =========================
# LÓGICA
# =========================
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def processar_bip(func, inst):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT status FROM instrumentos WHERE id_instrumento=?", (inst,))
    r = c.fetchone()

    if not r:
        conn.close()
        return "❌ Instrumento não cadastrado"

    if r[0] == "DISPONIVEL":
        c.execute("""
            INSERT INTO movimentacoes
            (id_funcionario, id_instrumento, data_saida, status)
            VALUES (?, ?, ?, 'EM USO')
        """, (func, inst, agora()))

        c.execute("""
            UPDATE instrumentos SET status='EM USO'
            WHERE id_instrumento=?
        """, (inst,))

        conn.commit()
        conn.close()
        return "✅ Instrumento RETIRADO"

    c.execute("""
        SELECT id FROM movimentacoes
        WHERE id_instrumento=? AND status='EM USO'
        ORDER BY id DESC LIMIT 1
    """, (inst,))
    mov = c.fetchone()

    if mov:
        c.execute("""
            UPDATE movimentacoes
            SET data_devolucao=?, status='DEVOLVIDO'
            WHERE id=?
        """, (agora(), mov[0]))

        c.execute("""
            UPDATE instrumentos SET status='DISPONIVEL'
            WHERE id_instrumento=?
        """, (inst,))

        conn.commit()
        conn.close()
        return "🔁 Instrumento DEVOLVIDO"

    conn.close()
    return "⚠️ Erro"

# =========================
# UI
# =========================
def bipar(event=None):
    f = entry_func.get().strip()
    i = entry_inst.get().strip().upper()

    if not f or not i:
        return

    lbl_status.config(text=processar_bip(f, i))
    entry_func.delete(0, tk.END)
    entry_inst.delete(0, tk.END)
    entry_func.focus()

# =========================
# START
# =========================
inicializar_banco()
seed()

janela = tk.Tk()
janela.title("Controle de Instrumentos - CQ")
janela.geometry("420x280")
janela.resizable(False, False)

tk.Label(janela, text="Bipe o CRACHÁ").pack(pady=5)
entry_func = tk.Entry(janela, font=("Arial", 12))
entry_func.pack()

tk.Label(janela, text="Bipe o INSTRUMENTO").pack(pady=5)
entry_inst = tk.Entry(janela, font=("Arial", 12))
entry_inst.pack()
entry_inst.bind("<Return>", bipar)

lbl_status = tk.Label(janela, text="", font=("Arial", 10))
lbl_status.pack(pady=10)

tk.Button(
    janela,
    text="Exportar para Excel",
    bg="#1f6aa5",
    fg="white",
    font=("Arial", 11),
    command=exportar_excel
).pack(pady=5)

entry_func.focus()
janela.mainloop()
>>>>>>> e7c3bf7ba42736141a14061e6d021af39ce282fd
