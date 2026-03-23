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
# CORES  (definidas aqui para uso em toda a aplicação, inclusive no modal)
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
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_funcionario  TEXT,
            id_instrumento  TEXT,
            data_saida      TEXT,
            data_devolucao  TEXT,
            status          TEXT
        )
    """)

    # Migração automática de colunas extras
    colunas_inst = [("data_vencimento", "TEXT")]
    c.execute("PRAGMA table_info(instrumentos)")
    cols_inst = {row[1] for row in c.fetchall()}
    for col, tipo in colunas_inst:
        if col not in cols_inst:
            c.execute(f"ALTER TABLE instrumentos ADD COLUMN {col} {tipo}")

    colunas_mov = [
        ("nome_funcionario",  "TEXT"),
        ("nome_instrumento",  "TEXT"),
        ("devolvido_por",     "TEXT"),
        ("observacao",        "TEXT"),
        ("qtd_utilizacoes",   "INTEGER"),
    ]
    c.execute("PRAGMA table_info(movimentacoes)")
    cols_mov = {row[1] for row in c.fetchall()}
    for col, tipo in colunas_mov:
        if col not in cols_mov:
            c.execute(f"ALTER TABLE movimentacoes ADD COLUMN {col} {tipo}")

    conn.commit()
    conn.close()

# =========================
# FUNÇÕES AUXILIARES
# =========================
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

instrumento_atual        = None
acao_atual               = None
nome_instrumento         = None
familia_instrumento      = None
funcionario_retirou      = None
nome_funcionario_retirou = None

def buscar_instrumento(codigo):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT nome, status, familia, data_vencimento
        FROM instrumentos
        WHERE id_instrumento=?
    """, (codigo,))
    r = c.fetchone()
    conn.close()
    return r  # (nome, status, familia, data_vencimento)

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

def instrumento_esta_vencido(data_vencimento_str):
    """Retorna True se a data de vencimento já passou."""
    if not data_vencimento_str:
        return False
    try:
        dt_venc = datetime.strptime(data_vencimento_str, "%d/%m/%Y")
        return dt_venc < datetime.today()
    except ValueError:
        return False

# =========================
# MODAL — QUANTIDADE DE UTILIZAÇÕES
# Aparece somente para instrumentos da família "CALIBRADOR TAMPAO ROSCA"
# =========================
def pedir_quantidade_utilizacoes(nome_instr, codigo_instr):
    resultado = {"valor": None}

    dialogo = tk.Toplevel(janela)
    dialogo.title("Número de Utilizações")
    dialogo.geometry("420x280")
    dialogo.resizable(False, False)
    dialogo.configure(bg=FUNDO)
    dialogo.grab_set()
    dialogo.focus_force()

    dialogo.update_idletasks()
    x = janela.winfo_x() + (janela.winfo_width()  - 420) // 2
    y = janela.winfo_y() + (janela.winfo_height() - 280) // 2
    dialogo.geometry(f"+{x}+{y}")

    cab = tk.Frame(dialogo, bg=AZUL_MED, height=52)
    cab.pack(fill="x")
    cab.pack_propagate(False)
    tk.Label(cab, text="Calibrador Tampão Rosca — Nº de Utilizações",
             font=("Arial", 11, "bold"), fg=BRANCO, bg=AZUL_MED).pack(expand=True)

    corpo_dlg = tk.Frame(dialogo, bg=FUNDO, padx=26, pady=14)
    corpo_dlg.pack(fill="both", expand=True)

    tk.Label(corpo_dlg, text=f"{nome_instr}  ({codigo_instr})",
             font=("Arial", 9), fg=CINZA, bg=FUNDO, anchor="w").pack(fill="x")

    tk.Label(corpo_dlg, text="Quantas vezes o instrumento foi utilizado?",
             font=("Arial", 11), fg="#1A1A1A", bg=FUNDO,
             wraplength=360, justify="left").pack(anchor="w", pady=(10, 8))

    vcmd = dialogo.register(lambda val: val.isdigit() or val == "")
    frame_entry = tk.Frame(corpo_dlg, bg=BRANCO,
                           highlightbackground=AZUL_MED, highlightthickness=2)
    frame_entry.pack(fill="x", ipady=2)

    entry_qtd = tk.Entry(frame_entry, font=("Arial", 18, "bold"),
                         bd=0, relief="flat", bg=BRANCO, fg=AZUL,
                         insertbackground=AZUL, justify="center",
                         validate="key", validatecommand=(vcmd, "%P"))
    entry_qtd.pack(fill="x", ipady=8, padx=10)
    entry_qtd.focus_set()

    lbl_erro = tk.Label(corpo_dlg, text="", font=("Arial", 8), fg="#B71C1C", bg=FUNDO)
    lbl_erro.pack(anchor="w", pady=(2, 0))

    frame_btns = tk.Frame(dialogo, bg=FUNDO, pady=8, padx=26)
    frame_btns.pack(fill="x")

    def confirmar(event=None):
        valor = entry_qtd.get().strip()
        if not valor or int(valor) < 1:
            lbl_erro.config(text="⚠  Informe um número maior que zero.")
            entry_qtd.focus_set()
            return
        resultado["valor"] = int(valor)
        dialogo.destroy()

    def cancelar():
        dialogo.destroy()

    tk.Button(frame_btns, text="Confirmar", font=("Arial", 10, "bold"),
              bg=AZUL_MED, fg=BRANCO, activebackground=AZUL, activeforeground=BRANCO,
              relief="flat", cursor="hand2", padx=20, pady=6,
              command=confirmar).pack(side="right")

    tk.Button(frame_btns, text="Cancelar", font=("Arial", 10),
              bg=CINZA_CLR, fg="#333", activebackground=CINZA,
              relief="flat", cursor="hand2", padx=20, pady=6,
              command=cancelar).pack(side="right", padx=(0, 8))

    entry_qtd.bind("<Return>", confirmar)
    dialogo.wait_window()
    return resultado["valor"]

# =========================
# FLUXO PRINCIPAL
# =========================
def bipar_instrumento(event=None):
    global instrumento_atual, acao_atual
    global nome_instrumento, familia_instrumento
    global funcionario_retirou, nome_funcionario_retirou

    codigo = entry_inst.get().strip().upper()
    if not codigo:
        return

    dados = buscar_instrumento(codigo)

    if not dados:
        set_status("error", "Instrumento não cadastrado")
        limpar_campos()
        return

    nome_instrumento, status, familia_instrumento, data_vencimento = dados
    instrumento_atual = codigo

    # ── NOVO: bloqueia retirada se instrumento estiver vencido ──────────
    if status != "EM USO" and instrumento_esta_vencido(data_vencimento):
        # Garante que o status no banco esteja como VENCIDO
        conn = conectar()
        conn.execute("UPDATE instrumentos SET status='VENCIDO' WHERE id_instrumento=?", (codigo,))
        conn.commit()
        conn.close()
        set_status("error",
            f"⛔  INSTRUMENTO VENCIDO\n\n"
            f"{nome_instrumento}  ({codigo})\n"
            f"Vencimento: {data_vencimento}\n\n"
            "Favor avisar ao líder do CQ.\n"
            "A retirada não é permitida."
        )
        limpar_campos()
        return
    # ────────────────────────────────────────────────────────────────────

    if status in ("DISPONIVEL",):
        acao_atual = "RETIRANDO"

        # Alerta se vence em breve (≤ 30 dias) mas ainda não venceu
        aviso_venc = ""
        if data_vencimento:
            try:
                dt_venc = datetime.strptime(data_vencimento, "%d/%m/%Y")
                delta = (dt_venc - datetime.today()).days
                if 0 <= delta <= 30:
                    aviso_venc = f"\n⚠  Atenção: vence em {delta} dia(s)!"
            except ValueError:
                pass

        set_status("info",
            f"{nome_instrumento}  ({codigo})\n"
            f"Status: DISPONÍVEL{aviso_venc}\n\n"
            "Bipe o crachá do funcionário"
        )
    elif status == "VENCIDO":
        set_status("error",
            f"⛔  INSTRUMENTO VENCIDO\n\n"
            f"{nome_instrumento}  ({codigo})\n"
            f"Vencimento: {data_vencimento or '—'}\n\n"
            "Favor avisar ao líder do CQ.\n"
            "A retirada não é permitida."
        )
        limpar_campos()
        return
    else:
        # EM USO — fluxo de devolução
        acao_atual = "DEVOLVENDO"

        info = buscar_quem_esta_com_instrumento(codigo)
        if not info:
            set_status("error", "Erro de rastreabilidade")
            limpar_campos()
            return

        funcionario_retirou      = info[0]
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
    global nome_instrumento, familia_instrumento
    global funcionario_retirou, nome_funcionario_retirou

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
            (id_funcionario, nome_funcionario, id_instrumento, nome_instrumento,
             data_saida, status)
            VALUES (?, ?, ?, ?, ?, 'EM USO')
        """, (cracha, nome_func, instrumento_atual, nome_instrumento, agora()))

        c.execute("UPDATE instrumentos SET status='EM USO' WHERE id_instrumento=?",
                  (instrumento_atual,))

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

        # Pergunta quantas vezes foi usado, se for Calibrador Tampão Rosca
        qtd_utilizacoes = None
        eh_calibrador_rosca = (
            familia_instrumento is not None
            and familia_instrumento.strip().upper() == "CALIBRADOR TAMPAO ROSCA"
        )

        if eh_calibrador_rosca:
            conn.close()
            qtd_utilizacoes = pedir_quantidade_utilizacoes(nome_instrumento, instrumento_atual)
            if qtd_utilizacoes is None:
                limpar_campos()
                return
            conn = conectar()
            c = conn.cursor()

        linha_qtd = f"Utilizações realizadas: {qtd_utilizacoes}\n" if qtd_utilizacoes else ""
        confirmar = messagebox.askokcancel(
            "Confirmar Devolução",
            f"Funcionário: {nome_func}\n"
            f"Ação: DEVOLVENDO\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})\n"
            f"{linha_qtd}"
            "\nConfirma as informações?"
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
                SET data_devolucao=?, status='DEVOLVIDO', devolvido_por=?, qtd_utilizacoes=?
                WHERE id=?
            """, (agora(), nome_func, qtd_utilizacoes, mov[0]))

        # Após devolução, verifica se já está vencido para definir o status correto
        c.execute("SELECT data_vencimento FROM instrumentos WHERE id_instrumento=?",
                  (instrumento_atual,))
        row = c.fetchone()
        data_venc = row[0] if row else None
        novo_status = "VENCIDO" if instrumento_esta_vencido(data_venc) else "DISPONIVEL"

        c.execute("UPDATE instrumentos SET status=? WHERE id_instrumento=?",
                  (novo_status, instrumento_atual))

        aviso_venc = (
            "\n\n⚠  Instrumento devolvido como VENCIDO.\nAvise o líder do CQ."
            if novo_status == "VENCIDO" else ""
        )
        msg_qtd_dev = f"\nUtilizações realizadas: {qtd_utilizacoes}" if qtd_utilizacoes else ""
        set_status("success",
            f"🔁  DEVOLUÇÃO REGISTRADA\n\n"
            f"Funcionário: {nome_func}\n"
            f"Instrumento: {nome_instrumento} ({instrumento_atual})"
            f"{msg_qtd_dev}\n"
            f"Horário: {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}"
            f"{aviso_venc}"
        )

    conn.commit()
    conn.close()
    limpar_campos()

def limpar_campos():
    global instrumento_atual, acao_atual, nome_instrumento, familia_instrumento
    global funcionario_retirou, nome_funcionario_retirou
    entry_inst.delete(0, tk.END)
    entry_func.delete(0, tk.END)
    instrumento_atual        = None
    acao_atual               = None
    nome_instrumento         = None
    familia_instrumento      = None
    funcionario_retirou      = None
    nome_funcionario_retirou = None
    entry_inst.focus()

def set_status(tipo, texto):
    bg, fg = STATUS_CORES.get(tipo, (FUNDO, "#333"))
    lbl_status.config(text=texto, bg=bg, fg=fg)
    frame_status.config(bg=bg)

# =========================
# UI — JANELA PRINCIPAL
# =========================
if not os.path.exists(DB_PATH):
    messagebox.showerror("Erro", "Banco de dados não encontrado na rede.")
    exit()

inicializar_banco()

janela = tk.Tk()
janela.title("Controle de Instrumentos — Finetornos")
janela.geometry("500x620")
janela.resizable(False, False)
janela.configure(bg=FUNDO)

# ---------- header ----------
header = tk.Frame(janela, bg=AZUL, height=80)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="FINETORNOS", font=("Arial Black", 22, "bold"),
         fg=BRANCO, bg=AZUL).pack(side="left", padx=20, pady=18)

tk.Label(header, text="Controle de Qualidade", font=("Arial", 9),
         fg=CINZA_CLR, bg=AZUL).place(x=22, y=50)

tk.Frame(janela, bg=AZUL_MED, height=4).pack(fill="x")

# ---------- corpo ----------
corpo = tk.Frame(janela, bg=FUNDO, padx=28, pady=20)
corpo.pack(fill="both", expand=True)

# --- Instrumento ---
tk.Label(corpo, text="INSTRUMENTO", font=("Arial", 8, "bold"),
         fg=CINZA, bg=FUNDO, anchor="w").pack(fill="x", pady=(0, 4))

frame_inst = tk.Frame(corpo, bg=BRANCO, highlightbackground=CINZA_CLR, highlightthickness=1)
frame_inst.pack(fill="x", ipady=2)

tk.Label(frame_inst, text="  🔧", bg=BRANCO, font=("Arial", 13)).pack(side="left")

entry_inst = tk.Entry(frame_inst, font=("Arial", 13), bd=0, relief="flat",
                      bg=BRANCO, fg="#1A1A1A", insertbackground=AZUL)
entry_inst.pack(side="left", fill="x", expand=True, ipady=8, padx=(4, 10))
entry_inst.bind("<Return>", bipar_instrumento)
entry_inst.bind("<FocusIn>",  lambda e: frame_inst.config(highlightbackground=AZUL))
entry_inst.bind("<FocusOut>", lambda e: frame_inst.config(highlightbackground=CINZA_CLR))

tk.Label(corpo, bg=FUNDO, height=1).pack()

# --- Crachá ---
tk.Label(corpo, text="CRACHÁ DO FUNCIONÁRIO", font=("Arial", 8, "bold"),
         fg=CINZA, bg=FUNDO, anchor="w").pack(fill="x", pady=(0, 4))

frame_func = tk.Frame(corpo, bg=BRANCO, highlightbackground=CINZA_CLR, highlightthickness=1)
frame_func.pack(fill="x", ipady=2)

tk.Label(frame_func, text="  👤", bg=BRANCO, font=("Arial", 13)).pack(side="left")

entry_func = tk.Entry(frame_func, font=("Arial", 13), bd=0, relief="flat",
                      bg=BRANCO, fg="#1A1A1A", insertbackground=AZUL)
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
    fg=CINZA, bg=FUNDO,
    justify="center",
    wraplength=420,
    pady=14, padx=16,
)
lbl_status.pack(fill="x")

# ---------- footer ----------
tk.Frame(janela, bg=CINZA_CLR, height=1).pack(fill="x", side="bottom", before=corpo)

footer = tk.Frame(janela, bg=AZUL_ESC, height=34)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

tk.Label(footer, text=f"CQ · {datetime.now().strftime('%d/%m/%Y')}",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="right", padx=16, pady=8)

tk.Label(footer, text="Sistema de Movimentação",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="left", padx=16, pady=8)

entry_inst.focus()
janela.mainloop()