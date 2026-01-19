# views/funcionario_view.py
import streamlit as st
import html
import datetime
import requests
from babel.dates import format_datetime
from views.shared_components import (
    inject_canva_css, get_current_logo, render_kanban_component, 
    render_compromissos_component, render_banco_da_dino_tech,
    render_missoes_tapete, render_estrategia_robo, render_projeto_inovacao,
    render_controle_acompanhamento, render_roadmap,
    render_treino_apresentacao, render_registro_de_pecas, render_central_de_senhas,
    render_wiki, render_treinamento, render_gestao_riscos
)
from models.core_values import (
    listar_atividades_cv, listar_avaliacoes_cv, listar_conflitos_cv,
    atualizar_atividade_cv, excluir_atividade_cv, excluir_avaliacao_cv, excluir_conflito_cv
)
from models.momento import listar_momentos, upload_momento, excluir_momento
from models.reclamacao import listar_reclamacoes, marcar_reclamacao_como_lida, excluir_reclamacao
from models.votacao import (
    listar_votacoes_com_status, criar_votacao, atualizar_status_votacao,
    excluir_votacao, obter_resultados, obter_resultados_detalhados, registrar_voto, verificar_voto_integrante
)
from models.tarefa import (
    criar_tarefa, atualizar_status_tarefa, excluir_tarefa,
    listar_tarefas_por_status, obter_quadro_kanban
)
from models.integrante import listar_integrantes
import pandas as pd

# Importação condicional do gerador de PDF
try:
    from utils.pdf_generator import gerar_relatorio_completo
except ImportError:
    gerar_relatorio_completo = None

def render_funcionario_view(conn, regras, usuario_logado, permissoes):
    """
    Renderiza a visão restrita para funcionários da escola.
    'permissoes' é uma lista de strings com os nomes das abas permitidas.
    """
    st.set_page_config(page_title="Acesso Escola - Dino-Tech", page_icon="🏫", layout="wide")
    inject_canva_css()

    # --- Sidebar ---
    with st.sidebar:
        usuario_safe = html.escape(usuario_logado)
        st.markdown(f"""
        <div class='user-info' style='margin-bottom:1rem; width:100%; text-align:center;'>
            🏫 <b>{usuario_safe}</b><br><span style='font-size:0.8em; opacity:0.8;'>Acesso Externo</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 Sair", key="sair_func"):
            st.session_state.usuario_logado = None
            st.session_state.tipo_usuario = None
            st.rerun()
        st.markdown("---")

    # --- Cabeçalho ---
    logo_src = get_current_logo()
    st.markdown(
        f"""
        <div style='text-align:center; margin-bottom:2rem;'>
            <img src="{logo_src}" width="200" style="border-radius:15px; margin-bottom:10px;" />
            <h2 style='color:var(--primary-color);'>Portal de Acompanhamento Escolar</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Processamento das Permissões (Compatibilidade com lista antiga ou dict novo) ---
    if isinstance(permissoes, list):
        abas_visiveis = permissoes
        abas_editaveis = []
    elif isinstance(permissoes, dict):
        abas_visiveis = permissoes.get("view", [])
        abas_editaveis = permissoes.get("edit", [])
    else:
        abas_visiveis = []
        abas_editaveis = []

    if not abas_visiveis:
        st.warning("⚠️ Seu usuário não possui permissões de visualização configuradas. Contate o administrador da equipe.")
        st.stop()

    # --- Navegação Dinâmica ---
    aba_selecionada = st.sidebar.radio("Navegação", abas_visiveis)
    
    # Verifica se tem permissão de edição na aba atual
    pode_editar = aba_selecionada in abas_editaveis
    if pode_editar:
        st.sidebar.success("✏️ Modo Edição Habilitado")

    # --- Renderização das Abas (Baseado na Permissão) ---
    
    if aba_selecionada == "📊 Kanban e Tarefas":
        with st.container(border=True):
            st.markdown("## 📊 Quadro de Tarefas")
            
            if pode_editar:
                st.subheader("➕ Nova Tarefa")
                integrantes_lista = listar_integrantes(conn)
                nomes_dict = {nome: id for id, nome in integrantes_lista}
                
                with st.form("form_nova_tarefa_func"):
                    titulo_tarefa = st.text_input("Título da tarefa")
                    desc_tarefa = st.text_area("Descrição")
                    responsaveis = st.multiselect("Responsáveis", list(nomes_dict.keys()))
                    
                    if st.form_submit_button("Criar Tarefa"):
                        if titulo_tarefa:
                            # Usa o ID do primeiro responsável ou None
                            primary_id = nomes_dict[responsaveis[0]] if responsaveis else None
                            desc_final = f"**Equipe:** {', '.join(responsaveis)}\n\n{desc_tarefa}" if responsaveis else desc_tarefa
                            
                            if criar_tarefa(conn, titulo_tarefa, desc_final, primary_id):
                                st.success("Tarefa criada!")
                                st.rerun()
                            else:
                                st.error("Erro ao criar.")
                        else:
                            st.warning("Título obrigatório.")
            
            # Exibição do Kanban (Lógica completa igual ao Admin)
            col_a_fazer, col_fazendo, col_feito = st.columns(3)
            for col, status, titulo_col in zip([col_a_fazer, col_fazendo, col_feito], ["to_do", "doing", "done"], ["📝 A Fazer", "🔄 Fazendo", "✅ Feito"]):
                with col:
                    st.markdown(f"### {titulo_col}")
                    tarefas = listar_tarefas_por_status(conn, status)
                    if not tarefas:
                        st.info("Nenhuma tarefa.")
                    else:
                        for t_id, titulo, desc, int_id, nome_resp in tarefas:
                            with st.expander(f"📌 {titulo}"):
                                st.markdown(f"**Responsáveis:** {nome_resp or 'Ninguém'}")
                                if desc:
                                    st.write(desc)
                                
                                if pode_editar:
                                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                                    if status != "to_do":
                                        with col_btn1:
                                            if st.button("←", key=f"move_{t_id}_to_do", help="Mover para 'A Fazer'"):
                                                atualizar_status_tarefa(conn, t_id, "to_do")
                                                st.rerun()
                                    else:
                                        col_btn1.empty()
                                    if status != "doing":
                                        with col_btn2:
                                            if st.button("🔄", key=f"move_{t_id}_doing", help="Mover para 'Fazendo'"):
                                                atualizar_status_tarefa(conn, t_id, "doing")
                                                st.rerun()
                                    else:
                                        col_btn2.empty()
                                    if status != "done":
                                        with col_btn3:
                                            if st.button("✅", key=f"move_{t_id}_done", help="Mover para 'Feito'"):
                                                atualizar_status_tarefa(conn, t_id, "done")
                                                st.rerun()
                                    else:
                                        col_btn3.empty()
                                    with col_btn4:
                                        if st.button("🗑️", key=f"del_tarefa_{t_id}", help="Excluir esta tarefa"):
                                            excluir_tarefa(conn, t_id)
                                            st.rerun()

    if aba_selecionada == "� Cronograma":
        with st.container(border=True):
            # Agora passamos o 'admin' como 'pode_editar' para liberar os botões
            render_compromissos_component(conn, admin=pode_editar)

    if aba_selecionada == "💰 Financeiro":
        with st.container(border=True):
            render_banco_da_dino_tech(conn, pode_editar=pode_editar)

    if aba_selecionada == "❤️ Core Values":
        with st.container(border=True):
            st.markdown("## ❤️ Cultura e Valores")
            tab1, tab2, tab3 = st.tabs(["Atividades Registradas", "Avaliações da Equipe", "🤝 Conflitos Resolvidos"])
            
            with tab1:
                atividades = listar_atividades_cv(conn)
                if atividades:
                    integrantes_lista = listar_integrantes(conn)
                    nomes_integrantes = [nome for _, nome in integrantes_lista]
                    
                    for a in atividades:
                        # Se pode editar, mostra o formulário completo como no Admin
                        if pode_editar:
                            with st.expander(f"📝 {a['data_atividade']} - {a['atividade']}"):
                                with st.form(key=f"form_edit_cv_{a['id']}"):
                                    nova_atividade = st.text_input("Atividade", value=a['atividade'])
                                    try:
                                        d_str = str(a['data_atividade'])
                                        data_val = datetime.datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                                    except Exception:
                                        data_val = datetime.date.today()
                                    nova_data = st.date_input("Data", value=data_val, key=f"date_cv_{a['id']}")
                                    
                                    parts = a.get('participantes', [])
                                    if isinstance(parts, str):
                                        import ast
                                        try: parts = ast.literal_eval(parts)
                                        except: parts = [parts] if parts else []
                                    elif parts is None: parts = []
                                    default_parts = [p for p in parts if p in nomes_integrantes]
                                    
                                    novos_participantes = st.multiselect("Participantes", options=nomes_integrantes, default=default_parts)
                                    novo_aprendizado = st.text_area("Aprendizado", value=a['aprendizado'])
                                    
                                    if st.form_submit_button("💾 Salvar Alterações"):
                                        if atualizar_atividade_cv(conn, a['id'], nova_atividade, nova_data, novos_participantes, novo_aprendizado):
                                            st.success("Atividade atualizada!")
                                            st.rerun()
                                        else:
                                            st.error("Erro ao atualizar.")
                                
                                if st.button("🗑️ Excluir Atividade", key=f"del_cv_act_{a['id']}"):
                                    if excluir_atividade_cv(conn, a['id']):
                                        st.success("Atividade excluída!")
                                        st.rerun()
                        else:
                            # Modo leitura
                            st.info(f"**{a['data_atividade']}**: {a['atividade']} (Aprendizado: {a['aprendizado']})")
                else:
                    st.write("Nenhuma atividade registrada.")

            with tab2:
                avals = listar_avaliacoes_cv(conn)
                if avals:
                    st.markdown("### 📊 Avaliações da Equipe")
                    integrantes_lista = listar_integrantes(conn)
                    mapa_nomes = {id_: nome for id_, nome in integrantes_lista}

                    for av in avals:
                        autor_nome = mapa_nomes.get(av.get('autor_id'), "Membro Desconhecido")
                        try:
                            raw_date = av.get('data_registro', '')
                            if raw_date and isinstance(raw_date, str):
                                if raw_date.endswith('Z'): raw_date = raw_date.replace('Z', '+00:00')
                                data_obj = datetime.datetime.fromisoformat(raw_date)
                            else: data_obj = datetime.datetime.now()
                            data_fmt = format_datetime(data_obj, "d 'de' MMM 'às' HH:mm", locale='pt_BR')
                        except Exception:
                            data_fmt = str(av.get('data_registro', 'Data inválida'))

                        with st.expander(f"👤 {autor_nome} - {data_fmt}"):
                            st.write(f"Descoberta: {av.get('descoberta')}/5 | Inovação: {av.get('inovacao')}/5 | Impacto: {av.get('impacto')}/5")
                            st.write(f"Inclusão: {av.get('inclusao')}/5 | Equipe: {av.get('trabalho_equipe')}/5 | Diversão: {av.get('diversao')}/5")
                            
                            if pode_editar:
                                st.markdown("---")
                                if st.button("🗑️ Excluir Avaliação", key=f"del_cv_aval_{av['id']}"):
                                    if excluir_avaliacao_cv(conn, av['id']):
                                        st.success("Avaliação excluída!")
                                        st.rerun()
                else:
                    st.info("Nenhuma avaliação registrada.")

            with tab3:
                conflitos = listar_conflitos_cv(conn)
                if conflitos:
                    st.markdown("### 🕊️ Histórico de Resoluções")
                    for c in conflitos:
                        try:
                            raw_date = c.get('data_registro', '')
                            if raw_date and isinstance(raw_date, str):
                                if raw_date.endswith('Z'): raw_date = raw_date.replace('Z', '+00:00')
                                data_obj = datetime.datetime.fromisoformat(raw_date)
                            else: data_obj = datetime.datetime.now()
                            data_fmt = format_datetime(data_obj, "d 'de' MMM 'às' HH:mm", locale='pt_BR')
                        except: data_fmt = "Data desconhecida"

                        with st.expander(f"⚔️ {c.get('resumo', 'Sem título')} - {data_fmt}"):
                            st.markdown(f"**Solução:**\n{c.get('solucao')}")
                            if pode_editar:
                                st.markdown("---")
                                if st.button("🗑️ Excluir Registro", key=f"del_conf_{c['id']}"):
                                    if excluir_conflito_cv(conn, c['id']):
                                        st.success("Conflito excluído!")
                                        st.rerun()
                else:
                    st.info("Nenhum conflito registrado.")
            

    if aba_selecionada == "🤖 Robô e Estratégia":
        with st.container(border=True):
            # Passa read_only invertido (se pode editar, read_only é False)
            render_missoes_tapete(conn, read_only=not pode_editar)
            st.markdown("---")
            render_estrategia_robo(conn, read_only=not pode_editar)

    if aba_selecionada == "🧩 Projeto de Inovação":
        with st.container(border=True):
            render_projeto_inovacao(conn, read_only=not pode_editar)

    if aba_selecionada == "📄 Relatórios PDF":
        with st.container(border=True):
            st.markdown("## 📄 Exportar Relatórios")
            if gerar_relatorio_completo:
                pdf = gerar_relatorio_completo(conn, regras)
                st.download_button("📥 Baixar Relatório Completo", pdf, "relatorio_escola.pdf", "application/pdf")
            else:
                st.error("Gerador de PDF indisponível.")

    if aba_selecionada == "📈 Acompanhamento":
        with st.container(border=True):
            # Se pode editar, passa True para todas as permissões de edição do componente
            render_controle_acompanhamento(
                conn,
                can_edit_checklist=pode_editar,
                can_edit_reunioes=pode_editar,
                can_edit_erros=pode_editar
            )

    if aba_selecionada == "🗣️ Reclamações":
        with st.container(border=True):
            st.markdown("<h2 style='color:#FF6347;'>🗣️ Caixa de Feedback</h2>", unsafe_allow_html=True)
            reclamacoes = listar_reclamacoes(conn)
            if not reclamacoes:
                st.success("✅ Nenhuma reclamação.")
            else:
                reclamacoes_novas = [r for r in reclamacoes if r['status'] == 'nova']
                reclamacoes_lidas = [r for r in reclamacoes if r['status'] == 'lida']

                st.markdown("### 📬 Novas")
                if not reclamacoes_novas: st.info("Nenhuma nova.")
                for rec in reclamacoes_novas:
                    with st.expander(f"Feedback de **{rec.get('autor', 'N/A')}**"):
                        st.write(rec['texto'])
                        if pode_editar:
                            c1, c2 = st.columns(2)
                            if c1.button("Marcar lida", key=f"ler_{rec['id']}"):
                                marcar_reclamacao_como_lida(conn, rec['id'])
                                st.rerun()
                            if c2.button("🗑️ Excluir", key=f"del_rec_{rec['id']}"):
                                excluir_reclamacao(conn, rec['id'])
                                st.rerun()
                
                st.markdown("### 📖 Lidas")
                for rec in reclamacoes_lidas:
                    with st.expander(f"Lida - **{rec.get('autor', 'N/A')}**"):
                        st.write(rec['texto'])
                        if pode_editar and st.button("🗑️ Excluir", key=f"del_rec_lida_{rec['id']}"):
                            excluir_reclamacao(conn, rec['id'])
                            st.rerun()

    if aba_selecionada == "📸 Momentos":
        with st.container(border=True):
            st.markdown("<h2 style='color:#8A2BE2;'>📸 Galeria da Equipe</h2>", unsafe_allow_html=True)
            
            if pode_editar:
                with st.form("upload_momento_func", clear_on_submit=True):
                    st.subheader("📤 Enviar Foto")
                    desc = st.text_input("Descrição")
                    foto = st.file_uploader("Foto", type=["jpg", "png"])
                    if st.form_submit_button("Enviar"):
                        if foto and desc:
                            # Usa ID 0 ou busca um ID genérico se necessário, aqui usaremos None ou tratar no backend
                            # Como o funcionário não é um "integrante" na tabela integrantes, o upload pode falhar se tiver FK constraint
                            # Idealmente o funcionário deveria ter um ID de integrante ou o campo ser nullable.
                            # Assumindo nullable ou que o sistema aceita:
                            if upload_momento(conn, foto, f"[Funcionario] {desc}", None):
                                st.success("Foto enviada!")
                                st.rerun()
                            else:
                                st.error("Erro ao enviar.")
            
            momentos = listar_momentos(conn)
            if momentos:
                for m in momentos:
                    st.image(m["url_imagem"], caption=m['descricao'])
                    if pode_editar:
                        if st.button("🗑️ Excluir", key=f"del_mom_{m['id']}"):
                            excluir_momento(conn, m['id'], m['url_imagem'])
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("Nenhuma foto.")

    if aba_selecionada == "🗳️ Votação":
        with st.container(border=True):
            st.markdown("<h2 style='color:#8A2BE2;'>🗳️ Votações</h2>", unsafe_allow_html=True)
            
            if pode_editar:
                with st.expander("➕ Criar Votação"):
                    titulo = st.text_input("Título")
                    opcoes = st.text_area("Opções (uma por linha)")
                    tipo = st.radio("Tipo", ('anonima', 'nao_anonima'))
                    if st.button("Criar"):
                        opts = [o.strip() for o in opcoes.split('\n') if o.strip()]
                        if titulo and len(opts) >= 2:
                            criar_votacao(conn, titulo, opts, tipo)
                            st.success("Criada!")
                            st.rerun()
            
            votacoes = listar_votacoes_com_status(conn)
            if votacoes:
                for v in votacoes:
                    status_icon = "🟢" if v['status'] == 'aberta' else "🔴"
                    with st.expander(f"{status_icon} {v['titulo']}"):
                        res = obter_resultados(conn, v['id'])
                        total = sum(res.values())
                        st.write(f"Total: {total}")
                        for op, count in res.items():
                            st.write(f"{op}: {count}")
                            st.progress((count/total) if total > 0 else 0)
                        
                        if pode_editar:
                            c1, c2 = st.columns(2)
                            if v['status'] == 'aberta':
                                if c1.button("🔒 Fechar", key=f"close_{v['id']}"):
                                    atualizar_status_votacao(conn, v['id'], 'fechada')
                                    st.rerun()
                            else:
                                if c1.button("🔓 Reabrir", key=f"open_{v['id']}"):
                                    atualizar_status_votacao(conn, v['id'], 'aberta')
                                    st.rerun()
                            if c2.button("🗑️ Excluir", key=f"del_vot_{v['id']}"):
                                excluir_votacao(conn, v['id'])
                                st.rerun()
            else:
                st.info("Nenhuma votação.")

    if aba_selecionada == "📦 Registro de Peças":
        with st.container(border=True):
            # Se pode editar, read_only é False
            render_registro_de_pecas(conn, read_only=not pode_editar)

    if aba_selecionada == "🗺️ Roadmap":
        with st.container(border=True):
            # Se pode editar, admin é True
            render_roadmap(conn, admin=pode_editar)

    if aba_selecionada == "🎤 Treino Apresentação":
        with st.container(border=True):
            # Se pode editar, admin é True
            render_treino_apresentacao(conn, admin=pode_editar)

    if aba_selecionada == "📂 Regras e Setores":
        with st.container(border=True):
            st.markdown("## 📂 Regras e Estrutura da Equipe")
            
            # Visualização dos Setores
            setores = regras.get("setores", [])
            if setores:
                tabs = st.tabs([s['nome'] for s in setores])
                for i, setor in enumerate(setores):
                    with tabs[i]:
                        st.markdown(f"### {setor['nome']}")
                        st.write(f"**Capacidade:** {setor.get('capacidade')} pessoas")
                        for func in setor.get("funcoes", []):
                            st.markdown(f"**{func['nome']}** (Max: {func.get('max')})")
                            for r in func.get("responsabilidades", []):
                                st.write(f"- {r}")
                        
                        if pode_editar:
                            st.info("⚠️ Para editar a estrutura de setores e regras, contate o Administrador Principal.")
            
            st.markdown("---")
            st.markdown("### 📜 Direitos e Regras Gerais")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Direitos Gerais**")
                for d in regras.get("direitos_gerais", []):
                    st.write(f"✅ {d}")
            with c2:
                st.markdown("**Regras Gerais**")
                for r in regras.get("regras_gerais", []):
                    st.write(f"⚖️ {r}")

    if aba_selecionada == "📚 Wiki & Conhecimento":
        with st.container(border=True):
            # Se pode editar, libera funções de admin (excluir artigos)
            render_wiki(conn, usuario_logado, admin=pode_editar)

    if aba_selecionada == "🧑‍🏫 Capacitação":
        with st.container(border=True):
            # usuario_id=None pois funcionários não validam progresso pessoal, apenas gerenciam ou visualizam
            render_treinamento(conn, usuario_id=None, admin=pode_editar)

    if aba_selecionada == "🚨 Gestão de Risco":
        with st.container(border=True):
            # Renderiza a matriz de riscos
            render_gestao_riscos(conn, usuario_logado)

    if aba_selecionada == "🔑 Central de Senhas":
        with st.container(border=True):
            # Renderiza a central de senhas
            render_central_de_senhas(conn)