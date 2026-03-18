import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import os

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
            nome TEXT,
            familia TEXT,
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

# =========================
# FUNÇÕES AUXILIARES
# =========================
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

instrumento_atual = None
acao_atual = None
nome_instrumento = None
funcionario_retirou = None
nome_funcionario_retirou = None

def buscar_instrumento(codigo):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT nome, status 
        FROM instrumentos 
        WHERE id_instrumento=?
    """, (codigo,))
    r = c.fetchone()
    conn.close()
    return r

def buscar_funcionario(cracha):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT nome FROM funcionarios WHERE id_funcionario=?", (cracha,))
    r = c.fetchone()
    conn.close()
    return r

def buscar_quem_esta_com_instrumento(codigo):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT m.id_funcionario, f.nome
        FROM movimentacoes m
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
        WHERE m.id_instrumento=? AND m.status='EM USO'
        ORDER BY m.id DESC LIMIT 1
    """, (codigo,))
    r = c.fetchone()
    conn.close()
    return r

# =========================
# FLUXO
# =========================
def bipar_instrumento(event=None):
    global instrumento_atual, acao_atual
    global nome_instrumento, funcionario_retirou, nome_funcionario_retirou

    codigo = entry_inst.get().strip().upper()
    if not codigo:
        return

    dados = buscar_instrumento(codigo)

    if not dados:
        lbl_status.config(text="❌ Instrumento não cadastrado")
        limpar_campos()
        return

    nome_instrumento, status = dados
    instrumento_atual = codigo

    if status == "DISPONIVEL":
        acao_atual = "RETIRANDO"
        lbl_status.config(
            text=f"✅ {nome_instrumento} ({codigo})\n"
                 "Status: DISPONÍVEL\n\n"
                 "Bipe o crachá"
        )
    else:
        acao_atual = "DEVOLVENDO"

        info = buscar_quem_esta_com_instrumento(codigo)
        if not info:
            lbl_status.config(text="⚠️ Erro de rastreabilidade")
            limpar_campos()
            return

        funcionario_retirou = info[0]
        nome_funcionario_retirou = info[1]

        lbl_status.config(
            text=f"🔒 {nome_instrumento} ({codigo})\n"
                 "Status: EM USO\n\n"
                 f"👤 Está com: {nome_funcionario_retirou}\n\n"
                 "Bipe o crachá para devolver"
        )

    entry_func.focus()

def bipar_funcionario(event=None):
    global instrumento_atual, acao_atual
    global nome_instrumento, funcionario_retirou, nome_funcionario_retirou

    cracha = entry_func.get().strip()
    if not cracha or not instrumento_atual:
        return

    func = buscar_funcionario(cracha)

    if not func:
        lbl_status.config(text="❌ Funcionário não cadastrado")
        limpar_campos()
        return

    nome_func = func[0]

    conn = conectar()
    c = conn.cursor()

    # ================= RETIRADA =================
    if acao_atual == "RETIRANDO":

        confirmar = messagebox.askokcancel(
            "Confirmar",
            f"{nome_func} está RETIRANDO\n"
            f"{nome_instrumento} ({instrumento_atual}).\n\n"
            "Confirma as informações?"
        )

        if not confirmar:
            conn.close()
            limpar_campos()
            return

        c.execute("""
            INSERT INTO movimentacoes
            (id_funcionario, id_instrumento, data_saida, status)
            VALUES (?, ?, ?, 'EM USO')
        """, (cracha, instrumento_atual, agora()))

        c.execute("""
            UPDATE instrumentos SET status='EM USO'
            WHERE id_instrumento=?
        """, (instrumento_atual,))

        msg = "✅ Instrumento RETIRADO"

    # ================= DEVOLUÇÃO =================
    else:

        if cracha != funcionario_retirou:
            conn.close()
            messagebox.showerror(
                "Erro",
                f"Este instrumento está com {nome_funcionario_retirou}.\n"
                "Somente quem retirou pode devolver."
            )
            limpar_campos()
            return

        confirmar = messagebox.askokcancel(
            "Confirmar",
            f"{nome_func} está DEVOLVENDO\n"
            f"{nome_instrumento} ({instrumento_atual}).\n\n"
            "Confirma as informações?"
        )

        if not confirmar:
            conn.close()
            limpar_campos()
            return

        c.execute("""
            SELECT id FROM movimentacoes
            WHERE id_instrumento=? AND status='EM USO'
            ORDER BY id DESC LIMIT 1
        """, (instrumento_atual,))
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
        """, (instrumento_atual,))

        msg = "🔁 Instrumento DEVOLVIDO"

    conn.commit()
    conn.close()

    lbl_status.config(text=msg)
    limpar_campos()

def limpar_campos():
    global instrumento_atual, funcionario_retirou, nome_funcionario_retirou
    entry_inst.delete(0, tk.END)
    entry_func.delete(0, tk.END)
    instrumento_atual = None
    funcionario_retirou = None
    nome_funcionario_retirou = None
    entry_inst.focus()

# =========================
# UI
# =========================
inicializar_banco()

janela = tk.Tk()
janela.title("Controle de Instrumentos - Funcionário")
janela.geometry("480x340")
janela.resizable(False, False)

tk.Label(janela, text="Bipe o INSTRUMENTO").pack(pady=5)
entry_inst = tk.Entry(janela, font=("Arial", 12))
entry_inst.pack()
entry_inst.bind("<Return>", bipar_instrumento)

tk.Label(janela, text="Bipe o CRACHÁ").pack(pady=5)
entry_func = tk.Entry(janela, font=("Arial", 12))
entry_func.pack()
entry_func.bind("<Return>", bipar_funcionario)

lbl_status = tk.Label(janela, text="", font=("Arial", 10))
lbl_status.pack(pady=15)

entry_inst.focus()
janela.mainloop()