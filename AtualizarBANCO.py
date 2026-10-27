# -*- coding: utf-8 -*-
"""
Limpa as movimentações do controle_instrumentos.db e atualiza a lista de funcionários.
 - Apaga TODAS as movimentações (e zera o contador de ID)
 - Mantém os instrumentos cadastrados (e volta o status de todos pra DISPONIVEL)
 - Substitui a lista de funcionários pela lista nova (ID = crachá)
 - Faz backup do banco antes de mexer em qualquer coisa
"""
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime

NOME_DB = "controle_instrumentos.db"

FUNCIONARIOS = [
    ("001685", "ADEMILSON GOMES"),
    ("001516", "ADRIANO E SILVA FREITAS"),
    ("900002", "AGNEZ BUENO CONSTANTINO DE OLIVEIRA"),
    ("001781", "ALBERTO JORGE DE OLIVEIRA"),
    ("001832", "ALESSANDRO NEVES DA SILVA"),
    ("001896", "ALEX AMANCIO DA SILVA"),
    ("001880", "ALEXSANDRO BARROS DE CARVALHO"),
    ("001874", "ALLYSON ALVES LEME DOS SANTOS"),
    ("001784", "ANDREIA SOARES DOS SANTOS PEREIRA"),
    ("001813", "CHARLES AGOSTINHO DA COSTA"),
    ("001721", "CLAUDIL DE ALMEIDA"),
    ("001888", "CLAUDIO ANTONIO GARCIA MORENO"),
    ("001271", "CLECIO REDIGOLO"),
    ("001895", "DANIEL CAETANO DA CRUZ"),
    ("801869", "DANIELLE BEZERRA DA SILVA"),
    ("001875", "DAVI DOS SANTOS COSTA"),
    ("001733", "DIEGO GRACIANO DOS SANTOS"),
    ("001560", "EDSON APARECIDO PEDRINI"),
    ("001839", "EDUARDO BERTUCCI LOURENCON GRAZIA"),
    ("001871", "EDUARDO SAMPAIO"),
    ("001717", "FABIO EDUARDO PEREIRA"),
    ("001491", "FELIPE DELEGA CINTRA"),
    ("001843", "FELIPE DOS ANJOS NASCIMENTO"),
    ("001803", "FELIPE OLIVEIRA RAMOS"),
    ("001811", "GEORGE DE OLIVEIRA ZOPPA"),
    ("001558", "GERALDO CLEMENTINO DA SILVA"),
    ("001879", "GERSON FERRARI"),
    ("001838", "GUILHERME REZENDE MONZILLO"),
    ("001867", "GUSTAVO DOS SANTOS BAIAO"),
    ("001876", "HENRIQUE ACACIO VICENTE"),
    ("001892", "HENRY EWANDER DOS SANTOS MIRANDA"),
    ("001852", "ICARO ANDRADE DA SILVA"),
    ("001772", "IGOR DANIEL TENORIO"),
    ("001894", "IURI TEIXEIRA VIEIRA"),
    ("001842", "JACKSON BATISTA DE SOUZA"),
    ("001723", "JAYRO STEK"),
    ("001863", "JOAO PEDRO PRADO VIEIRA"),
    ("001815", "JONATHAN DE SOUSA BISPO"),
    ("001429", "JOSE DA SILVA"),
    ("001280", "JURACI FRANCISCO SATELIS"),
    ("001704", "LEONARDO FERNANDES CERQUEIRA"),
    ("900001", "LEONARDO FERREIRA"),
    ("001592", "LUCIANO DOS SANTOS FERNANDES"),
    ("001804", "LUIZ FELIPE MORAIS ALVES"),
    ("001677", "MARCELA TOZZI DE SOUZA"),
    ("001681", "MARCELO MARQUES DA SILVA"),
    ("001653", "MARCELO SANTOS CORDEIRO"),
    ("001380", "MARCIO DONIZETI DA SILVA"),
    ("001897", "MATHEUS DA SILVA MARQUES"),
    ("001763", "MATHEUS HENRIQUE COSTA"),
    ("001828", "MAURICIO MANOEL DA SILVA"),
    ("001826", "MAURILIO ANTONIO DE OLIVEIRA"),
    ("001615", "MAYCON WELLINGTON GERMANO"),
    ("001868", "NATAN CRISTIAN LEME"),
    ("001773", "NATAN DE SOUZA NASCIMENTO FILHO"),
    ("001882", "NICOLAS DIAS LAURIANO DE FREITAS"),
    ("001825", "PATRICK DE SOUZA FRANCO"),
    ("001744", "PAULO MARCOS ALEXANDRINO"),
    ("001849", "PAULO ROBERTO DE LIMA"),
    ("001766", "PIETRO DE SOUZA FRANCO"),
    ("001856", "RAFAEL HENRIQUE AVELAR"),
    ("001621", "RAFAEL SILVA MENDES"),
    ("801871", "RHAIANNY STELA RIBEIRO MARTINS"),
    ("001120", "RICARDO OLIVEIRA DE BRITO"),
    ("001225", "RICARDO POLESI ALMIRALL"),
    ("001893", "RICIERI CELSO BRONZATTI"),
    ("001731", "ROBERTO CARLOS CALEGARI"),
    ("001898", "RODRIGO FABIANO FERNANDES VIEIRA"),
    ("001637", "RODRIGO FELIPE RAMOS"),
    ("001301", "RODRIGO FERREIRA DE SOUZA"),
    ("001795", "SAMUEL VITOR DOS SANTOS FERREIRA"),
    ("001820", "SANDRO RAMOS DA SILVA"),
    ("001805", "SAYMON FENIX CAMPOS DA SILVA"),
    ("001801", "SIDNEI FERRARI"),
    ("801870", "SOPHIA VIRGINIO CARVALHO"),
    ("001377", "THIAGO SOUZA SILVA"),
    ("001837", "TIAGO FRASI FERREIRA"),
    ("001886", "VINICIUS GABRIEL SANTOS SILVA"),
    ("001833", "VITOR TEODORO MARTINS"),
    ("001442", "VIVIANE APARECIDA MARTINS"),
    ("001481", "WELDER DE SOUZA LOPES"),
    ("001814", "WILSTON DOUGLAS TAVARES"),
]


def pasta_do_programa():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def pausar():
    try:
        input("\nAperte ENTER pra fechar...")
    except EOFError:
        pass


def main():
    pasta = pasta_do_programa()
    caminho_db = os.path.join(pasta, NOME_DB)

    print("=" * 60)
    print(" LIMPEZA DO BANCO - CONTROLE DE INSTRUMENTOS")
    print("=" * 60)

    if not os.path.isfile(caminho_db):
        print(f"\n[ERRO] Não achei '{NOME_DB}' na pasta:\n  {pasta}")
        print("Coloque o script na mesma pasta do banco e tente de novo.")
        pausar()
        return

    con = sqlite3.connect(caminho_db)
    cur = con.cursor()
    qtd_mov = cur.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0]
    qtd_ins = cur.execute("SELECT COUNT(*) FROM instrumentos").fetchone()[0]
    qtd_fun = cur.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0]
    con.close()

    print(f"\nBanco: {caminho_db}")
    print(f"  Movimentações hoje : {qtd_mov}  -> serão APAGADAS")
    print(f"  Instrumentos       : {qtd_ins}  -> serão mantidos")
    print(f"  Funcionários hoje  : {qtd_fun}  -> serão substituídos por {len(FUNCIONARIOS)}")
    print("\nUm backup será criado antes de qualquer alteração.")

    resp = input("\nDigite SIM pra continuar: ").strip().upper()
    if resp != "SIM":
        print("Cancelado. Nada foi alterado.")
        pausar()
        return

    # Backup
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(pasta, f"controle_instrumentos_BACKUP_{carimbo}.db")
    shutil.copy2(caminho_db, backup)
    print(f"\nBackup criado: {backup}")

    con = sqlite3.connect(caminho_db)
    try:
        cur = con.cursor()
        cur.execute("BEGIN")

        # 1) Movimentações
        cur.execute("DELETE FROM movimentacoes")
        cur.execute("DELETE FROM sqlite_sequence WHERE name = 'movimentacoes'")

        # 2) Instrumentos continuam, todos voltam como disponíveis
        cur.execute("UPDATE instrumentos SET status = 'DISPONIVEL'")

        # 3) Funcionários: troca pela lista nova
        cur.execute("DELETE FROM funcionarios")
        vistos = set()
        for cracha, nome in FUNCIONARIOS:
            nome = re.sub(r"\s+", " ", nome).strip()
            if cracha in vistos:
                continue
            vistos.add(cracha)
            cur.execute(
                "INSERT INTO funcionarios (id_funcionario, nome) VALUES (?, ?)",
                (cracha, nome),
            )

        con.commit()
        cur.execute("VACUUM")
    except Exception as e:
        con.rollback()
        print(f"\n[ERRO] Algo deu errado, nada foi alterado: {e}")
        print(f"Seu backup continua em: {backup}")
        con.close()
        pausar()
        return

    cur = con.cursor()
    print("\nPronto! Resultado final:")
    print(f"  Movimentações : {cur.execute('SELECT COUNT(*) FROM movimentacoes').fetchone()[0]}")
    print(f"  Instrumentos  : {cur.execute('SELECT COUNT(*) FROM instrumentos').fetchone()[0]}")
    print(f"  Funcionários  : {cur.execute('SELECT COUNT(*) FROM funcionarios').fetchone()[0]}")
    con.close()
    pausar()


if __name__ == "__main__":
    main()