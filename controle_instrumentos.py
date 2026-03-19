import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import os

# =========================
# CAMINHO DO BANCO NA REDE
# =========================
DB_PATH = r"X:\CQ\BACKUP_masilva\CONTROLE DE INSTRUMENTOS _Sistema\controle_instrumentos.db"

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

    # Cria tabela base se nao existir (schema minimo compativel com banco original)
    c.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario  TEXT,
            id_instrumento  TEXT,
            data_saida      TEXT,
            data_devolucao  TEXT,
            status          TEXT
        )
    """)

    # Adiciona colunas extras que podem nao existir em bancos mais antigos
    colunas_extras = [
        ("nome_funcionario", "TEXT"),
        ("nome_instrumento", "TEXT"),
        ("devolvido_por",    "TEXT"),
        ("observacao",       "TEXT"),
    ]
    c.execute("PRAGMA table_info(movimentacoes)")
    colunas_existentes = {row[1] for row in c.fetchall()}
    for col, tipo in colunas_extras:
        if col not in colunas_existentes:
            c.execute(f"ALTER TABLE movimentacoes ADD COLUMN {col} {tipo}")

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
        SELECT id_funcionario, nome_funcionario
        FROM movimentacoes
        WHERE id_instrumento=? AND status='EM USO'
        ORDER BY id DESC LIMIT 1
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
        set_status("error", "Instrumento não cadastrado")
        limpar_campos()
        return

    nome_instrumento, status = dados
    instrumento_atual = codigo

    if status == "DISPONIVEL":
        acao_atual = "RETIRANDO"
        set_status("info",
            f"{nome_instrumento}  ({codigo})\n"
            "Status: DISPONÍVEL\n\n"
            "Bipe o crachá do funcionário"
        )
    else:
        acao_atual = "DEVOLVENDO"

        info = buscar_quem_esta_com_instrumento(codigo)
        if not info:
            set_status("error", "Erro de rastreabilidade")
            limpar_campos()
            return

        funcionario_retirou = info[0]
        nome_funcionario_retirou = info[1]

        set_status("warning",
            f"{nome_instrumento}  ({codigo})\n"
            "Status: EM USO\n\n"
            f"Em posse de: {nome_funcionario_retirou}\n\n"
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
        set_status("error", "Funcionário não cadastrado")
        limpar_campos()
        return

    nome_func = func[0]

    conn = conectar()
    c = conn.cursor()

    # ================= RETIRADA =================
    if acao_atual == "RETIRANDO":

        confirmar = messagebox.askokcancel(
            "Confirmar Retirada",
            f"Funcionário: {nome_func}\n"
            f"Ação: RETIRANDO\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})\n\n"
            "Confirma as informações?"
        )

        if not confirmar:
            conn.close()
            limpar_campos()
            return

        c.execute("""
            INSERT INTO movimentacoes
            (
                id_funcionario,
                nome_funcionario,
                id_instrumento,
                nome_instrumento,
                data_saida,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'EM USO')
        """, (
            cracha,
            nome_func,
            instrumento_atual,
            nome_instrumento,
            agora()
        ))

        c.execute("""
            UPDATE instrumentos SET status='EM USO'
            WHERE id_instrumento=?
        """, (instrumento_atual,))

        set_status("success",
            f"✅  RETIRADA REGISTRADA\n\n"
            f"Funcionário: {nome_func}\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})\n"
            f"Horário: {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}"
        )

    # ================= DEVOLUÇÃO =================
    else:

        if cracha != funcionario_retirou:
            conn.close()
            messagebox.showerror(
                "Acesso Negado",
                f"Este instrumento está com {nome_funcionario_retirou}.\n"
                "Somente quem retirou pode devolver."
            )
            limpar_campos()
            return

        confirmar = messagebox.askokcancel(
            "Confirmar Devolução",
            f"Funcionário: {nome_func}\n"
            f"Ação: DEVOLVENDO\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})\n\n"
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
                SET 
                    data_devolucao=?,
                    status='DEVOLVIDO',
                    devolvido_por=?
                WHERE id=?
            """, (
                agora(),
                nome_func,
                mov[0]
            ))

        c.execute("""
            UPDATE instrumentos SET status='DISPONIVEL'
            WHERE id_instrumento=?
        """, (instrumento_atual,))

        set_status("success",
            f"🔁  DEVOLUÇÃO REGISTRADA\n\n"
            f"Funcionário: {nome_func}\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})\n"
            f"Horário: {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}"
        )

    conn.commit()
    conn.close()
    limpar_campos()

def limpar_campos():
    global instrumento_atual, acao_atual, nome_instrumento
    global funcionario_retirou, nome_funcionario_retirou
    entry_inst.delete(0, tk.END)
    entry_func.delete(0, tk.END)
    instrumento_atual        = None
    acao_atual               = None
    nome_instrumento         = None
    funcionario_retirou      = None
    nome_funcionario_retirou = None
    entry_inst.focus()

# =========================
# HELPERS DE UI
# =========================
AZUL      = "#1B3F72"
AZUL_ESC  = "#122B52"
AZUL_MED  = "#2056A0"
CINZA     = "#9EA8B0"
CINZA_CLR = "#D6DCE1"
BRANCO    = "#FFFFFF"
FUNDO     = "#F0F3F6"

STATUS_CORES = {
    "info":    ("#E8EFF8", AZUL),
    "success": ("#E6F4EC", "#1A6E35"),
    "warning": ("#FFF5E6", "#8A5000"),
    "error":   ("#FDECEA", "#B71C1C"),
}

def set_status(tipo, texto):
    bg, fg = STATUS_CORES.get(tipo, (FUNDO, "#333"))
    lbl_status.config(text=texto, bg=bg, fg=fg)
    frame_status.config(bg=bg)

# =========================
# UI
# =========================
if not os.path.exists(DB_PATH):
    messagebox.showerror("Erro", "Banco de dados não encontrado na rede.")
    exit()

inicializar_banco()

# ---------- janela principal ----------
janela = tk.Tk()
janela.title("Controle de Instrumentos — Finetornos")
janela.geometry("500x600")
janela.resizable(False, False)
janela.configure(bg=FUNDO)

# ---------- header ----------
header = tk.Frame(janela, bg=AZUL, height=80)
header.pack(fill="x")
header.pack_propagate(False)

lbl_empresa = tk.Label(
    header,
    text="FINETORNOS",
    font=("Arial Black", 22, "bold"),
    fg=BRANCO,
    bg=AZUL,
)
lbl_empresa.pack(side="left", padx=20, pady=18)

lbl_subtitulo = tk.Label(
    header,
    text="Controle de Qualidade",
    font=("Arial", 9),
    fg=CINZA_CLR,
    bg=AZUL
)
lbl_subtitulo.place(x=22, y=50)

# linha decorativa
tk.Frame(janela, bg=AZUL_MED, height=4).pack(fill="x")

# ---------- corpo ----------
corpo = tk.Frame(janela, bg=FUNDO, padx=28, pady=20)
corpo.pack(fill="both", expand=True)

# --- Instrumento ---
tk.Label(
    corpo,
    text="INSTRUMENTO",
    font=("Arial", 8, "bold"),
    fg=CINZA,
    bg=FUNDO,
    anchor="w"
).pack(fill="x", pady=(0, 4))

frame_inst = tk.Frame(corpo, bg=BRANCO, highlightbackground=CINZA_CLR,
                      highlightthickness=1)
frame_inst.pack(fill="x", ipady=2)

lbl_icon_inst = tk.Label(frame_inst, text="  🔧", bg=BRANCO,
                          font=("Arial", 13))
lbl_icon_inst.pack(side="left")

entry_inst = tk.Entry(
    frame_inst,
    font=("Arial", 13),
    bd=0, relief="flat",
    bg=BRANCO, fg="#1A1A1A",
    insertbackground=AZUL,
)
entry_inst.pack(side="left", fill="x", expand=True, ipady=8, padx=(4, 10))
entry_inst.bind("<Return>", bipar_instrumento)
entry_inst.bind("<FocusIn>",  lambda e: frame_inst.config(highlightbackground=AZUL))
entry_inst.bind("<FocusOut>", lambda e: frame_inst.config(highlightbackground=CINZA_CLR))

tk.Label(corpo, bg=FUNDO, height=1).pack()   # espaço

# --- Crachá ---
tk.Label(
    corpo,
    text="CRACHÁ DO FUNCIONÁRIO",
    font=("Arial", 8, "bold"),
    fg=CINZA,
    bg=FUNDO,
    anchor="w"
).pack(fill="x", pady=(0, 4))

frame_func = tk.Frame(corpo, bg=BRANCO, highlightbackground=CINZA_CLR,
                      highlightthickness=1)
frame_func.pack(fill="x", ipady=2)

lbl_icon_func = tk.Label(frame_func, text="  👤", bg=BRANCO,
                          font=("Arial", 13))
lbl_icon_func.pack(side="left")

entry_func = tk.Entry(
    frame_func,
    font=("Arial", 13),
    bd=0, relief="flat",
    bg=BRANCO, fg="#1A1A1A",
    insertbackground=AZUL,
)
entry_func.pack(side="left", fill="x", expand=True, ipady=8, padx=(4, 10))
entry_func.bind("<Return>", bipar_funcionario)
entry_func.bind("<FocusIn>",  lambda e: frame_func.config(highlightbackground=AZUL))
entry_func.bind("<FocusOut>", lambda e: frame_func.config(highlightbackground=CINZA_CLR))

# --- Status ---
tk.Label(corpo, bg=FUNDO, height=1).pack()

frame_status = tk.Frame(corpo, bg=FUNDO)
frame_status.pack(fill="x")

lbl_status = tk.Label(
    frame_status,
    text="Aguardando leitura...",
    font=("Arial", 10),
    fg=CINZA,
    bg=FUNDO,
    justify="center",
    wraplength=420,
    pady=14,
    padx=16
)
lbl_status.pack(fill="x")

# ---------- footer ----------
separador = tk.Frame(janela, bg=CINZA_CLR, height=1)
separador.pack(fill="x", side="bottom", before=corpo)

footer = tk.Frame(janela, bg=AZUL_ESC, height=34)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

tk.Label(
    footer,
    text=f"CQ · {datetime.now().strftime('%d/%m/%Y')}",
    font=("Arial", 8),
    fg=CINZA,
    bg=AZUL_ESC
).pack(side="right", padx=16, pady=8)

tk.Label(
    footer,
    text="Sistema de Movimentação",
    font=("Arial", 8),
    fg=CINZA,
    bg=AZUL_ESC
).pack(side="left", padx=16, pady=8)

entry_inst.focus()
janela.mainloop()
