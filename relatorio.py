import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime

# matplotlib embutido no tkinter
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =========================
# BANCO
# =========================
DB_PATH = r"X:\CQ\BACKUP_masilva\CONTROLE DE INSTRUMENTOS _Sistema\controle_instrumentos.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# =========================
# CORES — FINETORNOS
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
LARANJA   = "#8A5000"
LARANJA_BG= "#FFF5E6"
VERM      = "#B71C1C"
VERM_BG   = "#FDECEA"

# paleta para gráficos
CHART_COLORS = ["#1B3F72","#2056A0","#9EA8B0","#3A7BD5","#6FA3EF",
                "#122B52","#D6DCE1","#4C8CB5","#7FAECC","#B3CDE0"]

# =========================
# QUERIES
# =========================

def query_movimentacoes(filtros=None):
    """Retorna todas as movimentações com JOIN em nomes."""
    conn = conectar()
    c = conn.cursor()

    sql = """
        SELECT
            m.id,
            m.id_funcionario,
            COALESCE(m.nome_funcionario, f.nome, m.id_funcionario) AS nome_funcionario,
            m.id_instrumento,
            COALESCE(m.nome_instrumento, i.nome, m.id_instrumento) AS nome_instrumento,
            i.familia,
            m.data_saida,
            m.data_devolucao,
            COALESCE(m.devolvido_por, '') AS devolvido_por,
            m.status
        FROM movimentacoes m
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
        LEFT JOIN instrumentos i ON i.id_instrumento = m.id_instrumento
        WHERE 1=1
    """
    params = []

    if filtros:
        if filtros.get("busca"):
            termo = f"%{filtros['busca']}%"
            sql += """ AND (
                m.id_funcionario LIKE ? OR
                COALESCE(m.nome_funcionario, f.nome, '') LIKE ? OR
                m.id_instrumento LIKE ? OR
                COALESCE(m.nome_instrumento, i.nome, '') LIKE ? OR
                i.familia LIKE ?
            )"""
            params += [termo, termo, termo, termo, termo]

        if filtros.get("status") and filtros["status"] != "TODOS":
            sql += " AND m.status = ?"
            params.append(filtros["status"])

        if filtros.get("familia") and filtros["familia"] != "TODAS":
            sql += " AND i.familia = ?"
            params.append(filtros["familia"])

        if filtros.get("data_ini"):
            sql += " AND m.data_saida >= ?"
            params.append(filtros["data_ini"] + " 00:00:00")

        if filtros.get("data_fim"):
            sql += " AND m.data_saida <= ?"
            params.append(filtros["data_fim"] + " 23:59:59")

    sql += " ORDER BY m.id DESC"
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return rows

def query_status_atual():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM instrumentos GROUP BY status")
    r = dict(c.fetchall())
    conn.close()
    return r

def query_top_funcionarios(limit=10):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(m.nome_funcionario, f.nome, m.id_funcionario), COUNT(*) as total
        FROM movimentacoes m
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
        GROUP BY m.id_funcionario
        ORDER BY total DESC LIMIT ?
    """, (limit,))
    r = c.fetchall()
    conn.close()
    return r

def query_top_instrumentos(limit=10):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(m.nome_instrumento, i.nome, m.id_instrumento), COUNT(*) as total
        FROM movimentacoes m
        LEFT JOIN instrumentos i ON i.id_instrumento = m.id_instrumento
        GROUP BY m.id_instrumento
        ORDER BY total DESC LIMIT ?
    """, (limit,))
    r = c.fetchall()
    conn.close()
    return r

def query_por_familia():
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(i.familia, 'Sem família'), COUNT(*) as total
        FROM movimentacoes m
        LEFT JOIN instrumentos i ON i.id_instrumento = m.id_instrumento
        GROUP BY i.familia
        ORDER BY total DESC
    """)
    r = c.fetchall()
    conn.close()
    return r

def query_por_dia(limit=30):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT substr(data_saida,1,10) as dia, COUNT(*) as total
        FROM movimentacoes
        WHERE data_saida IS NOT NULL
        GROUP BY dia
        ORDER BY dia DESC LIMIT ?
    """, (limit,))
    r = c.fetchall()
    conn.close()
    return list(reversed(r))

def query_familias_disponiveis():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT DISTINCT familia FROM instrumentos WHERE familia IS NOT NULL ORDER BY familia")
    r = [row[0] for row in c.fetchall()]
    conn.close()
    return r

def query_resumo():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM instrumentos")
    total_inst = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM instrumentos WHERE status='EM USO'")
    em_uso = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM instrumentos WHERE status='DISPONIVEL'")
    disponivel = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM movimentacoes")
    total_mov = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM funcionarios")
    total_func = c.fetchone()[0]
    conn.close()
    return total_inst, em_uso, disponivel, total_mov, total_func

# =========================
# FORMATADORES
# =========================

def fmt_dt(val):
    if not val:
        return "—"
    try:
        dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y  %H:%M")
    except:
        return val

def fmt_duracao(saida, devolucao):
    if not saida or not devolucao:
        return "—"
    try:
        s = datetime.strptime(saida,     "%Y-%m-%d %H:%M:%S")
        d = datetime.strptime(devolucao, "%Y-%m-%d %H:%M:%S")
        delta = d - s
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m = rem // 60
        return f"{h}h {m:02d}m"
    except:
        return "—"

# =========================
# JANELA PRINCIPAL
# =========================

root = tk.Tk()
root.title("Relatório de Instrumentos — Finetornos")
root.geometry("1280x780")
root.minsize(1100, 680)
root.configure(bg=FUNDO)

# ---------- Header ----------
header = tk.Frame(root, bg=AZUL, height=70)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="FINETORNOS", font=("Arial Black", 20, "bold"),
         fg=BRANCO, bg=AZUL).pack(side="left", padx=20, pady=8)

tk.Label(header, text="Dashboard · Controle de Instrumentos",
         font=("Arial", 9), fg=CINZA_CLR, bg=AZUL).place(x=22, y=46)

# cards de resumo no header
frame_cards = tk.Frame(header, bg=AZUL)
frame_cards.pack(side="right", padx=20, pady=8)

card_labels = {}
def make_card(parent, titulo, valor, cor_val=BRANCO):
    f = tk.Frame(parent, bg=AZUL_ESC, padx=12, pady=4)
    f.pack(side="left", padx=4)
    tk.Label(f, text=titulo, font=("Arial", 7), fg=CINZA_CLR, bg=AZUL_ESC).pack()
    lbl = tk.Label(f, text=str(valor), font=("Arial", 14, "bold"), fg=cor_val, bg=AZUL_ESC)
    lbl.pack()
    return lbl

lbl_card_total    = make_card(frame_cards, "INSTRUMENTOS", "—")
lbl_card_uso      = make_card(frame_cards, "EM USO",       "—", "#FFB347")
lbl_card_disp     = make_card(frame_cards, "DISPONÍVEIS",  "—", "#6FCF97")
lbl_card_mov      = make_card(frame_cards, "MOVIMENTAÇÕES","—")
lbl_card_func     = make_card(frame_cards, "FUNCIONÁRIOS", "—")

tk.Frame(root, bg=AZUL_MED, height=4).pack(fill="x")

# ---------- Notebook de abas ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("FT.TNotebook", background=FUNDO, borderwidth=0, tabmargins=[0, 6, 0, 0])
style.configure("FT.TNotebook.Tab",
    background=CINZA_CLR, foreground="#444",
    font=("Arial", 9, "bold"), padding=[18, 8], borderwidth=0)
style.map("FT.TNotebook.Tab",
    background=[("selected", AZUL), ("active", AZUL_MED)],
    foreground=[("selected", BRANCO), ("active", BRANCO)])

notebook = ttk.Notebook(root, style="FT.TNotebook")
notebook.pack(fill="both", expand=True)

# ============================================================
# ABA 1 — TABELA DE MOVIMENTAÇÕES
# ============================================================

aba_tabela = tk.Frame(notebook, bg=FUNDO)
notebook.add(aba_tabela, text="  📋  Movimentações  ")

# --- barra de filtros ---
barra = tk.Frame(aba_tabela, bg=BRANCO, pady=10, padx=16)
barra.pack(fill="x")
tk.Frame(barra, bg=AZUL_MED, height=2).pack(fill="x", side="bottom")

def lbl_filtro(parent, text):
    tk.Label(parent, text=text, font=("Arial", 8, "bold"),
             fg=CINZA, bg=BRANCO).pack(side="left", padx=(10, 2))

# Busca geral
lbl_filtro(barra, "🔍 BUSCA")
entry_busca = tk.Entry(barra, font=("Arial", 10), bd=1, relief="solid",
                       bg=BRANCO, fg="#1A1A1A", insertbackground=AZUL, width=22)
entry_busca.pack(side="left", ipady=4, padx=(0, 8))

# Status
lbl_filtro(barra, "STATUS")
combo_status = ttk.Combobox(barra, values=["TODOS", "EM USO", "DEVOLVIDO"],
                             state="readonly", width=12, font=("Arial", 9))
combo_status.set("TODOS")
combo_status.pack(side="left", padx=(0, 8), ipady=3)

# Família
familias_lista = ["TODAS"] + query_familias_disponiveis()
lbl_filtro(barra, "FAMÍLIA")
combo_fam_filtro = ttk.Combobox(barra, values=familias_lista,
                                 state="readonly", width=22, font=("Arial", 9))
combo_fam_filtro.set("TODAS")
combo_fam_filtro.pack(side="left", padx=(0, 8), ipady=3)

# Datas
lbl_filtro(barra, "DE")
entry_data_ini = tk.Entry(barra, font=("Arial", 10), bd=1, relief="solid",
                           bg=BRANCO, fg="#1A1A1A", width=11)
entry_data_ini.pack(side="left", ipady=4, padx=(0, 4))
entry_data_ini.insert(0, "AAAA-MM-DD")
entry_data_ini.bind("<FocusIn>",  lambda e: entry_data_ini.delete(0, tk.END)
                    if entry_data_ini.get() == "AAAA-MM-DD" else None)

lbl_filtro(barra, "ATÉ")
entry_data_fim = tk.Entry(barra, font=("Arial", 10), bd=1, relief="solid",
                           bg=BRANCO, fg="#1A1A1A", width=11)
entry_data_fim.pack(side="left", ipady=4, padx=(0, 10))
entry_data_fim.insert(0, "AAAA-MM-DD")
entry_data_fim.bind("<FocusIn>",  lambda e: entry_data_fim.delete(0, tk.END)
                    if entry_data_fim.get() == "AAAA-MM-DD" else None)

# Botões filtro
def btn_style(parent, text, cmd, cor=AZUL):
    b = tk.Button(parent, text=text, command=cmd,
                  font=("Arial", 9, "bold"), bg=cor, fg=BRANCO,
                  activebackground=AZUL_MED, activeforeground=BRANCO,
                  relief="flat", cursor="hand2", padx=12, pady=4, bd=0)
    b.pack(side="left", padx=3)
    return b

btn_style(barra, "Filtrar",  lambda: aplicar_filtros())
btn_style(barra, "Limpar",   lambda: limpar_filtros(), CINZA)

# --- contador de resultados ---
frame_info_tabela = tk.Frame(aba_tabela, bg=FUNDO, pady=4, padx=16)
frame_info_tabela.pack(fill="x")

lbl_contagem = tk.Label(frame_info_tabela, text="",
                         font=("Arial", 8), fg=CINZA, bg=FUNDO)
lbl_contagem.pack(side="left")

# --- tabela ---
COLUNAS = ("ID", "Crachá", "Funcionário", "Cód. Instrumento",
           "Instrumento", "Família", "Retirada", "Devolução", "Duração", "Status")

style.configure("FT.Treeview",
    background=BRANCO, foreground="#1A1A1A",
    rowheight=26, fieldbackground=BRANCO,
    font=("Arial", 9))
style.configure("FT.Treeview.Heading",
    background=AZUL, foreground=BRANCO,
    font=("Arial", 9, "bold"), relief="flat", padding=5)
style.map("FT.Treeview",
    background=[("selected", AZUL_MED)],
    foreground=[("selected", BRANCO)])
style.map("FT.Treeview.Heading",
    background=[("active", AZUL_ESC)])

frame_tree = tk.Frame(aba_tabela, bg=FUNDO)
frame_tree.pack(fill="both", expand=True, padx=16, pady=(0, 10))

tree = ttk.Treeview(frame_tree, columns=COLUNAS, show="headings", style="FT.Treeview")

larguras = {"ID": 40, "Crachá": 60, "Funcionário": 140, "Cód. Instrumento": 120,
            "Instrumento": 160, "Família": 130, "Retirada": 130,
            "Devolução": 130, "Duração": 80, "Status": 90}

for col in COLUNAS:
    tree.heading(col, text=col)
    tree.column(col, width=larguras[col], minwidth=40, anchor="center"
                if col in ("ID","Duração","Status") else "w")

tree.tag_configure("em_uso",    background=LARANJA_BG, foreground=LARANJA)
tree.tag_configure("devolvido", background=VERDE_BG,   foreground=VERDE)

sb_y = ttk.Scrollbar(frame_tree, orient="vertical",   command=tree.yview)
sb_x = ttk.Scrollbar(frame_tree, orient="horizontal",  command=tree.xview)
tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

sb_y.pack(side="right",  fill="y")
sb_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

def carregar_tabela(filtros=None):
    for row in tree.get_children():
        tree.delete(row)

    dados = query_movimentacoes(filtros)
    for r in dados:
        id_, cracha, nome_func, cod_inst, nome_inst, familia, \
            data_s, data_d, dev_por, status = r

        duracao = fmt_duracao(data_s, data_d)
        tag = "em_uso" if status == "EM USO" else "devolvido"

        tree.insert("", tk.END, values=(
            id_,
            cracha,
            nome_func,
            cod_inst,
            nome_inst,
            familia or "—",
            fmt_dt(data_s),
            fmt_dt(data_d),
            duracao,
            status,
        ), tags=(tag,))

    lbl_contagem.config(text=f"{len(dados)} registro(s) encontrado(s)")

def aplicar_filtros():
    di = entry_data_ini.get().strip()
    df = entry_data_fim.get().strip()
    filtros = {
        "busca":    entry_busca.get().strip(),
        "status":   combo_status.get(),
        "familia":  combo_fam_filtro.get(),
        "data_ini": di if di not in ("", "AAAA-MM-DD") else "",
        "data_fim": df if df not in ("", "AAAA-MM-DD") else "",
    }
    carregar_tabela(filtros)

def limpar_filtros():
    entry_busca.delete(0, tk.END)
    combo_status.set("TODOS")
    combo_fam_filtro.set("TODAS")
    entry_data_ini.delete(0, tk.END)
    entry_data_ini.insert(0, "AAAA-MM-DD")
    entry_data_fim.delete(0, tk.END)
    entry_data_fim.insert(0, "AAAA-MM-DD")
    carregar_tabela()

# busca em tempo real
entry_busca.bind("<Return>", lambda e: aplicar_filtros())

# ============================================================
# ABA 2 — STATUS ATUAL DOS INSTRUMENTOS
# ============================================================

aba_status = tk.Frame(notebook, bg=FUNDO)
notebook.add(aba_status, text="  🔧  Status Atual  ")

frame_status_top = tk.Frame(aba_status, bg=FUNDO, padx=16, pady=10)
frame_status_top.pack(fill="x")

tk.Label(frame_status_top, text="STATUS ATUAL DOS INSTRUMENTOS",
         font=("Arial", 10, "bold"), fg=AZUL, bg=FUNDO).pack(side="left")
tk.Frame(aba_status, bg=AZUL_MED, height=2).pack(fill="x", padx=16, pady=(0,8))

style.configure("Status.Treeview",
    background=BRANCO, foreground="#1A1A1A",
    rowheight=28, fieldbackground=BRANCO, font=("Arial", 9))
style.configure("Status.Treeview.Heading",
    background=AZUL, foreground=BRANCO,
    font=("Arial", 9, "bold"), relief="flat", padding=5)
style.map("Status.Treeview",
    background=[("selected", AZUL_MED)],
    foreground=[("selected", BRANCO)])

frame_tree_status = tk.Frame(aba_status, bg=FUNDO)
frame_tree_status.pack(fill="both", expand=True, padx=16, pady=(0,10))

COLS_STATUS = ("Cód.", "Nome", "Família", "Status", "Último Usuário", "Última Saída")
tree_status = ttk.Treeview(frame_tree_status, columns=COLS_STATUS,
                            show="headings", style="Status.Treeview")

largs_status = {"Cód.": 120, "Nome": 200, "Família": 160,
                "Status": 100, "Último Usuário": 160, "Última Saída": 130}
for col in COLS_STATUS:
    tree_status.heading(col, text=col)
    tree_status.column(col, width=largs_status[col], minwidth=60,
                       anchor="center" if col in ("Status",) else "w")

tree_status.tag_configure("em_uso",    background=LARANJA_BG, foreground=LARANJA)
tree_status.tag_configure("disponivel", background=VERDE_BG,  foreground=VERDE)

sb_status = ttk.Scrollbar(frame_tree_status, orient="vertical", command=tree_status.yview)
tree_status.configure(yscrollcommand=sb_status.set)
sb_status.pack(side="right", fill="y")
tree_status.pack(fill="both", expand=True)

def carregar_status():
    for row in tree_status.get_children():
        tree_status.delete(row)

    conn = conectar()
    c = conn.cursor()
    c.execute("""
        SELECT
            i.id_instrumento,
            i.nome,
            i.familia,
            i.status,
            COALESCE(m.nome_funcionario, f.nome, m.id_funcionario, '—') AS ultimo_usuario,
            m.data_saida
        FROM instrumentos i
        LEFT JOIN (
            SELECT id_instrumento, id_funcionario, nome_funcionario, data_saida
            FROM movimentacoes
            WHERE id IN (
                SELECT MAX(id) FROM movimentacoes GROUP BY id_instrumento
            )
        ) m ON m.id_instrumento = i.id_instrumento
        LEFT JOIN funcionarios f ON f.id_funcionario = m.id_funcionario
        ORDER BY i.status DESC, i.nome
    """)
    rows = c.fetchall()
    conn.close()

    for r in rows:
        cod, nome, fam, status, usuario, data_s = r
        tag = "em_uso" if status == "EM USO" else "disponivel"
        tree_status.insert("", tk.END, values=(
            cod, nome, fam or "—", status,
            usuario, fmt_dt(data_s)
        ), tags=(tag,))

# ============================================================
# ABA 3 — GRÁFICOS
# ============================================================

aba_graficos = tk.Frame(notebook, bg=FUNDO)
notebook.add(aba_graficos, text="  📊  Gráficos  ")

# Seletor de gráfico
barra_graf = tk.Frame(aba_graficos, bg=BRANCO, pady=8, padx=16)
barra_graf.pack(fill="x")
tk.Frame(barra_graf, bg=AZUL_MED, height=2).pack(fill="x", side="bottom")

tk.Label(barra_graf, text="VISUALIZAÇÃO:", font=("Arial", 8, "bold"),
         fg=CINZA, bg=BRANCO).pack(side="left", padx=(0, 8))

GRAFICOS = [
    "Retiradas por dia",
    "Movimentações por família",
    "Top funcionários (retiradas)",
    "Top instrumentos (retiradas)",
    "Status atual (pizza)",
]

combo_grafico = ttk.Combobox(barra_graf, values=GRAFICOS,
                              state="readonly", width=30, font=("Arial", 9))
combo_grafico.set(GRAFICOS[0])
combo_grafico.pack(side="left", padx=(0, 10), ipady=4)

btn_style(barra_graf, "Gerar Gráfico", lambda: gerar_grafico())

# Frame do canvas
frame_canvas = tk.Frame(aba_graficos, bg=FUNDO)
frame_canvas.pack(fill="both", expand=True, padx=16, pady=10)

canvas_widget = [None]

def limpar_canvas():
    for w in frame_canvas.winfo_children():
        w.destroy()

def gerar_grafico():
    limpar_canvas()
    escolha = combo_grafico.get()

    fig = Figure(figsize=(10, 5), dpi=100, facecolor=FUNDO)
    ax  = fig.add_subplot(111)
    ax.set_facecolor(BRANCO)
    for spine in ax.spines.values():
        spine.set_edgecolor(CINZA_CLR)
    ax.tick_params(colors=CINZA, labelsize=8)
    ax.title.set_color(AZUL)
    ax.xaxis.label.set_color(CINZA)
    ax.yaxis.label.set_color(CINZA)

    if escolha == "Retiradas por dia":
        dados = query_por_dia(30)
        if not dados:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=CINZA, fontsize=12)
        else:
            dias   = [r[0] for r in dados]
            totais = [r[1] for r in dados]
            bars = ax.bar(dias, totais, color=AZUL_MED, edgecolor=AZUL, linewidth=0.5)
            ax.set_title("Retiradas por Dia (últimos 30 dias)", fontsize=11, fontweight="bold", pad=12)
            ax.set_xlabel("Data", fontsize=8)
            ax.set_ylabel("Quantidade", fontsize=8)
            ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)
            for bar, val in zip(bars, totais):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(val), ha="center", va="bottom", fontsize=7, color=AZUL)

    elif escolha == "Movimentações por família":
        dados = query_por_familia()
        if not dados:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=CINZA, fontsize=12)
        else:
            familias = [r[0] for r in dados]
            totais   = [r[1] for r in dados]
            cores    = CHART_COLORS[:len(familias)]
            bars = ax.barh(familias, totais, color=cores, edgecolor=BRANCO, linewidth=0.5)
            ax.set_title("Movimentações por Família de Instrumento", fontsize=11, fontweight="bold", pad=12)
            ax.set_xlabel("Quantidade", fontsize=8)
            ax.invert_yaxis()
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            for bar, val in zip(bars, totais):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                        str(val), va="center", fontsize=8, color=AZUL)

    elif escolha == "Top funcionários (retiradas)":
        dados = query_top_funcionarios(10)
        if not dados:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=CINZA, fontsize=12)
        else:
            nomes  = [r[0] for r in dados]
            totais = [r[1] for r in dados]
            cores  = CHART_COLORS[:len(nomes)]
            bars = ax.barh(nomes, totais, color=cores, edgecolor=BRANCO, linewidth=0.5)
            ax.set_title("Top Funcionários por Número de Retiradas", fontsize=11, fontweight="bold", pad=12)
            ax.set_xlabel("Quantidade de retiradas", fontsize=8)
            ax.invert_yaxis()
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            for bar, val in zip(bars, totais):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                        str(val), va="center", fontsize=8, color=AZUL)

    elif escolha == "Top instrumentos (retiradas)":
        dados = query_top_instrumentos(10)
        if not dados:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=CINZA, fontsize=12)
        else:
            nomes  = [r[0] for r in dados]
            totais = [r[1] for r in dados]
            cores  = CHART_COLORS[:len(nomes)]
            bars = ax.barh(nomes, totais, color=cores, edgecolor=BRANCO, linewidth=0.5)
            ax.set_title("Top Instrumentos por Número de Retiradas", fontsize=11, fontweight="bold", pad=12)
            ax.set_xlabel("Quantidade de retiradas", fontsize=8)
            ax.invert_yaxis()
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            for bar, val in zip(bars, totais):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                        str(val), va="center", fontsize=8, color=AZUL)

    elif escolha == "Status atual (pizza)":
        dados = query_status_atual()
        if not dados:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=CINZA, fontsize=12)
        else:
            labels = list(dados.keys())
            sizes  = list(dados.values())
            cores_pizza = []
            for l in labels:
                if l == "EM USO":       cores_pizza.append("#FFB347")
                elif l == "DISPONIVEL": cores_pizza.append("#6FCF97")
                else:                   cores_pizza.append(CINZA)

            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=cores_pizza,
                autopct="%1.1f%%", startangle=90,
                wedgeprops=dict(edgecolor=BRANCO, linewidth=2),
                textprops=dict(color=AZUL, fontsize=9)
            )
            for at in autotexts:
                at.set_color(AZUL_ESC)
                at.set_fontsize(9)
                at.set_fontweight("bold")
            ax.set_title("Status Atual dos Instrumentos", fontsize=11, fontweight="bold", pad=12)

    fig.tight_layout(pad=2)

    canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas_widget[0] = canvas

# ============================================================
# FOOTER
# ============================================================

tk.Frame(root, bg=CINZA_CLR, height=1).pack(fill="x", side="bottom")
footer = tk.Frame(root, bg=AZUL_ESC, height=30)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

tk.Label(footer, text=f"CQ · {datetime.now().strftime('%d/%m/%Y  %H:%M')}",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="right", padx=16, pady=6)
tk.Label(footer, text="Leitura em tempo real · controle_instrumentos.db",
         font=("Arial", 8), fg=CINZA, bg=AZUL_ESC).pack(side="left", padx=16, pady=6)

# botão atualizar no footer
def atualizar_tudo():
    carregar_tabela()
    carregar_status()
    t, u, d, m, f = query_resumo()
    lbl_card_total.config(text=str(t))
    lbl_card_uso.config(text=str(u))
    lbl_card_disp.config(text=str(d))
    lbl_card_mov.config(text=str(m))
    lbl_card_func.config(text=str(f))
    familias_lista[:] = ["TODAS"] + query_familias_disponiveis()
    combo_fam_filtro["values"] = familias_lista

tk.Button(footer, text="⟳  Atualizar", command=atualizar_tudo,
          font=("Arial", 8, "bold"), bg=AZUL_MED, fg=BRANCO,
          activebackground=AZUL, activeforeground=BRANCO,
          relief="flat", cursor="hand2", padx=10, pady=2, bd=0
          ).pack(side="right", padx=4, pady=4)

# =========================
# CARGA INICIAL
# =========================

atualizar_tudo()

root.mainloop()
