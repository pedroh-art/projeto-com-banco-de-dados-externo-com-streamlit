from fpdf import FPDF
import datetime
from models.integrante import listar_integrantes, listar_atribuicoes
from models.tarefa import obter_quadro_kanban
from models.compromisso import listar_compromissos
from models.reclamacao import listar_reclamacoes
from models.momento import listar_momentos
from models.votacao import listar_votacoes_com_status, obter_resultados
from models.peca import listar_pecas
from models.banco import listar_itens, listar_transacoes, total_preco, totalizar_dinheiro_atual
from models.core_values import listar_atividades_cv, listar_avaliacoes_cv, listar_conflitos_cv
from models.planejamento import listar_marcos, listar_avaliacoes_treino
from models.missao import listar_missoes
from models.estrategia import obter_base_robo, listar_acessorios_por_missao
from models.codigo import listar_codigos_com_missao
from models.projeto_inovacao import obter_dados_pi, listar_arquivos_pi
from models.acompanhamento import listar_itens_checklist, listar_reunioes, listar_erros_solucoes

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Relatório Geral - Dino-Tech', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, safe_text(title), 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, safe_text(body))
        self.ln()

def safe_text(text):
    if text is None: return ""
    text = str(text)
    # Substituições simples para caracteres comuns que podem dar erro no latin-1 padrão do FPDF
    replacements = {
        '–': '-', '—': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        'ã': 'a', 'õ': 'o', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ç': 'c', 'Ã': 'A', 'Õ': 'O', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'Ç': 'C', 'à': 'a', 'À': 'A', 'â': 'a', 'ê': 'e', 'ô': 'o', 'Â': 'A', 'Ê': 'E', 'Ô': 'O'
    }
    # Tenta codificar para latin-1, substituindo caracteres não suportados por '?'
    return text.encode('latin-1', 'replace').decode('latin-1')

def gerar_relatorio_completo(conn, regras):
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Regras e Estrutura
    pdf.chapter_title("1. Estrutura e Regras")
    regras_texto = f"Título: {regras.get('titulo', 'N/A')}\n"
    regras_texto += f"Limite de Membros: {regras.get('limite_total_membros', 'N/A')}\n\n"
    
    regras_texto += "Setores:\n"
    for setor in regras.get("setores", []):
        regras_texto += f"- {setor['nome']} (Cap: {setor.get('capacidade')})\n"
        for func in setor.get("funcoes", []):
            regras_texto += f"  * {func['nome']} (Max: {func.get('max')})\n"
    
    pdf.chapter_body(regras_texto)
    
    # 2. Membros
    pdf.chapter_title("2. Membros e Atribuições")
    integrantes = listar_integrantes(conn)
    membros_texto = ""
    for uid, nome in integrantes:
        atribs = listar_atribuicoes(conn, uid)
        atribs_str = ", ".join([f"{s}/{f}" for s, f in atribs]) if atribs else "Sem atribuições"
        membros_texto += f"- {nome}: {atribs_str}\n"
    pdf.chapter_body(membros_texto)
    
    # 3. Kanban
    pdf.chapter_title("3. Tarefas (Kanban)")
    tarefas = obter_quadro_kanban(conn)
    kanban_texto = ""
    for status, titulo, desc, resp in tarefas:
        kanban_texto += f"[{status.upper()}] {titulo} ({resp})\n"
    pdf.chapter_body(kanban_texto)
    
    # 4. Compromissos
    pdf.chapter_title("4. Compromissos")
    comps = listar_compromissos(conn)
    comp_texto = ""
    for c in comps:
        # c: id, titulo, desc, data, inicio, fim
        comp_texto += f"{c[3]} {c[4]}-{c[5]}: {c[1]}\n"
    pdf.chapter_body(comp_texto)
    
    # 5. Acompanhamento
    pdf.chapter_title("5. Acompanhamento")
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, safe_text("Checklist"), 0, 1)
    pdf.set_font('Arial', '', 10)
    checklist = listar_itens_checklist(conn)
    check_txt = ""
    for item in checklist:
        status = "[X]" if item['status'] else "[ ]"
        resp = item.get('integrantes', {}).get('nome', 'N/A') if item.get('integrantes') else 'N/A'
        check_txt += f"{status} {item['item_texto']} ({resp})\n"
    pdf.multi_cell(0, 5, safe_text(check_txt))
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, safe_text("Reuniões"), 0, 1)
    pdf.set_font('Arial', '', 10)
    reunioes = listar_reunioes(conn)
    reuniao_txt = ""
    for r in reunioes:
        reuniao_txt += f"Data: {r['data_reuniao']}\nPauta: {r['pauta']}\nDecisões: {r['decisoes']}\n---\n"
    pdf.multi_cell(0, 5, safe_text(reuniao_txt))
    
    # 6. Core Values
    pdf.chapter_title("6. Core Values")
    atividades = listar_atividades_cv(conn)
    cv_txt = "Atividades:\n"
    for a in atividades:
        cv_txt += f"{a['data_atividade']}: {a['atividade']} - {a['aprendizado']}\n"
    
    conflitos = listar_conflitos_cv(conn)
    cv_txt += "\nConflitos Resolvidos:\n"
    for c in conflitos:
        cv_txt += f"Resumo: {c['resumo']}\nSolução: {c['solucao']}\n"
        
    pdf.chapter_body(cv_txt)
    
    # 7. Robô e Estratégia
    pdf.chapter_title("7. Robô e Estratégia")
    base = obter_base_robo(conn)
    robo_txt = ""
    if base:
        robo_txt += f"Base: {base['nome_base']}\nDesc: {base['descricao']}\n\n"
    
    missoes = listar_missoes(conn)
    robo_txt += "Missões:\n"
    for m in missoes:
        robo_txt += f"- {m['nome']} ({m['pontuacao']} pts) [{m['status']}]\n"
        
    pdf.chapter_body(robo_txt)
    
    # 8. Financeiro
    pdf.chapter_title("8. Financeiro")
    total_gasto = total_preco(conn)
    dinheiro = totalizar_dinheiro_atual(conn)
    fin_txt = f"Dinheiro Atual: R$ {dinheiro:.2f}\nTotal Gasto: R$ {total_gasto:.2f}\n\nTransações:\n"
    transacoes = listar_transacoes(conn)
    for t in transacoes:
        fin_txt += f"{t['data_criacao']} - {t['tipo']}: R$ {t['valor']} ({t['descricao']})\n"
    pdf.chapter_body(fin_txt)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')