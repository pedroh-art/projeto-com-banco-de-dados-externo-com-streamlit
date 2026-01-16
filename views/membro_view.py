# views/membro_view.py
import streamlit as st
import datetime
import requests
import time
import html
from babel.dates import format_date
from collections import defaultdict 
from models.integrante import listar_integrantes, listar_atribuicoes
from utils.pushbullet_util import enviar_kanban_pushbullet
from models.tarefa import (
    criar_tarefa, atualizar_status_tarefa, excluir_tarefa,
    listar_tarefas_por_status, obter_quadro_kanban
)
from models.compromisso import (
    criar_compromisso, listar_compromissos, atualizar_compromisso, excluir_compromisso
)
from models.reclamacao import criar_reclamacao, listar_reclamacoes, marcar_reclamacao_como_lida, excluir_reclamacao
from models.momento import upload_momento, listar_momentos, excluir_momento
from models.votacao import (
    listar_votacoes_com_status, registrar_voto, verificar_voto_integrante,
    obter_resultados,
)
from views.shared_components import render_central_de_senhas, render_registro_de_pecas, render_missoes_tapete, render_estrategia_robo, render_biblioteca_codigos, render_projeto_inovacao, render_controle_acompanhamento, inject_canva_css, get_current_logo

def render_membro_view(conn, regras, usuario_logado):
    # Configura o locale para português do Brasil para formatar as datas
    HORARIOS_PADRAO = [f"{h:02d}:00" for h in range(8, 20)]

    st.set_page_config(page_title="Dino-Tech - Painel do Membro", page_icon="🦖", layout="wide")
    inject_canva_css()
    
    # Sidebar com informações do usuário e controles
    with st.sidebar:
        
        usuario_safe = html.escape(usuario_logado)
        st.markdown(f"<a style='margin-bottom:1rem; width:100%; text-align:center;' href='https://www.sesi.portaldaindustria.com.br/para-voce/robotica/first-lego-league-challenge#modal-robo'> <img src='https://cdn.brandfetch.io/idm_V4rm0p/theme/dark/logo.svg?c=1dxbfHSJFAPEGdCLU4o5B' class='simple-image' /> </a><div class='user-info' style='margin-bottom:1rem; width:100%; text-align:center;'>👤 <b>{usuario_safe}</b></div>", unsafe_allow_html=True)
        if st.button("🔄 Recarregar", key="recarregar_sidebar", help="Atualizar a página"):
            st.rerun()
        if st.button("🔒 Sair", key="sair_sidebar", help="Fazer logout"):
            st.session_state.usuario_logado = None
            st.session_state.tipo_usuario = None
            st.rerun()
        st.markdown("---")

    logo_src = get_current_logo()

    st.markdown(
        f"""
        <div style='text-align:center; margin-bottom:2.5rem;'>
            <a href='https://www.sesi.portaldaindustria.com.br/para-voce/robotica/first-lego-league-challenge#modal-robo'; style='display:inline-block; padding:0; margin:0; border: none; line-height:0; pointer-events:auto;'>
                <img src="{logo_src}" width="300" style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); border-radius:15px;" class='canva-images'; />
            </a>
            <div class="canva-title">Painel do Membro</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==============================================================================
    # IDENTIFICAR MEU ID
    # ==============================================================================
    integrantes_lista = listar_integrantes(conn)
    meu_id = None
    nome_login = usuario_logado.replace("_", " ").title()
    for id_, nome in integrantes_lista:
        if nome.lower() == nome_login.lower():
            meu_id = id_
            break
    if meu_id is None:
        for id_, nome in integrantes_lista:
            if usuario_logado in nome.lower().replace(" ", "_"):
                meu_id = id_
                break

    if meu_id is None:
        st.error("⚠️ Seu nome não foi encontrado na lista de membros. Contate o administrador.")
        st.stop()
    
    st.markdown("---")

    # Verifica as funções especiais do membro
    minhas_atribuicoes = listar_atribuicoes(conn, meu_id)
    is_gestor_redes = any(funcao == 'Gestor das Redes Sociais' for _, funcao in minhas_atribuicoes)
    is_responsavel_materiais = any(funcao == 'Responsável pelos Materiais' for _, funcao in minhas_atribuicoes)
    is_programador_robo = any(funcao == 'Programador do Robô' for _, funcao in minhas_atribuicoes)
    is_analista_missoes = any(funcao == 'Analista de Estratégia de Missões' for _, funcao in minhas_atribuicoes)
    is_engenheiro_construcao = any(funcao == 'Engenheiro de Construção' for _, funcao in minhas_atribuicoes)
    is_equipe_pi = any(setor == 'Projeto de Inovação (PI)' for setor, _ in minhas_atribuicoes)
    is_sr_core_values = any(funcao == 'Sr. core values' for _, funcao in minhas_atribuicoes)

    # Define as abas
    abas_nomes = [
        "📜 Meus Setores e Direitos",
        "📦 Registro de Peças",
        "🧩 Projeto de Inovação",
        "🤖 Robô e Programação",
        "📊 Kanban",
        "📅 Compromissos",
        "📈 Acompanhamento",
        "️🗣️ Enviar Feedback",
        "📸 Momentos da Equipe",
        "🗳️ Votações",
        "🔑 Trocar Senha",
        "🏦 Banco da Equipe"
    ]
    if is_gestor_redes:
        abas_nomes.insert(1, "🔑 Central de Senhas") # Adiciona a aba na segunda posição

    st.sidebar.title("Menu")
    aba_selecionada = st.sidebar.radio("Navegação", abas_nomes, label_visibility="collapsed")

    # ==============================================================================
    # ABA 1: MEUS SETORES, FUNÇÕES, RESPONSABILIDADES E DIREITOS EXCLUSIVOS
    # ==============================================================================
    if aba_selecionada == "📜 Meus Setores e Direitos":
        with st.container(border=True):
            st.markdown("## 📜 Meus Setores e Direitos")

            if minhas_atribuicoes:
                # Agrupa por setor
                atribuicoes_por_setor = defaultdict(list)
                for setor, funcao in minhas_atribuicoes:
                    atribuicoes_por_setor[setor].append(funcao)
                
                for setor_nome, funcoes in atribuicoes_por_setor.items():
                    st.markdown(f"#### 🏗️ **{setor_nome}**")
                    
                    # Buscar o setor nas regras
                    setor_regras = None
                    for s in regras.get("setores", []):
                        if s["nome"] == setor_nome:
                            setor_regras = s
                            break
                    
                    if setor_regras:
                        # Mostrar cada função com suas responsabilidades
                        for funcao in funcoes:
                            st.markdown(f"##### ⚡ **Função: `{funcao}`**")
                            
                            # Buscar responsabilidades dessa função
                            resp_list = []
                            for f in setor_regras.get("funcoes", []):
                                if f["nome"] == funcao:
                                    resp_list = f.get("responsabilidades", [])
                                    break
                            
                            if resp_list:
                                st.markdown("###### 📌 Responsabilidades:")
                                for r in resp_list:
                                    st.markdown(f"- {r}")
                            else:
                                st.info(f"Nenhuma responsabilidade definida para a função '{funcao}'.")
                    
                    else:
                        st.warning(f"Setor '{setor_nome}' não encontrado nas regras.")
                    
                    # Direitos exclusivos do setor (já existia)
                    direitos_setor = setor_regras.get("direitos_exclusivos", []) if setor_regras else []
                    if direitos_setor:
                        st.markdown("##### 🔑 Direitos exclusivos deste setor:")
                        for d in direitos_setor:
                            st.markdown(f"- ✅ {d}")
                    else:
                        st.info("Nenhum direito exclusivo definido para este setor.")
            else:
                st.info("Você ainda não foi atribuído a nenhum setor ou função.")

    # ==============================================================================
    # ABA EXTRA: Central de Senhas (se for gestor)
    # ==============================================================================
    if is_gestor_redes and aba_selecionada == "🔑 Central de Senhas":
        with st.container(border=True):
            render_central_de_senhas(conn)

    # ==============================================================================
    # ABA: REGISTRO DE PEÇAS
    # ==============================================================================
    if aba_selecionada == "📦 Registro de Peças":
        with st.container(border=True):
            # O componente decide se é modo de edição ou leitura
            render_registro_de_pecas(conn, read_only=not is_responsavel_materiais)

    # ==============================================================================
    # ABA: PROJETO DE INOVAÇÃO
    # ==============================================================================
    if aba_selecionada == "🧩 Projeto de Inovação":
        with st.container(border=True):
            # Permite edição para qualquer membro do setor de PI
            render_projeto_inovacao(conn, read_only=not is_equipe_pi)


    # ==============================================================================
    # ABA: ROBÔ E PROGRAMAÇÃO
    # ==============================================================================
    if aba_selecionada == "🤖 Robô e Programação":
        with st.container(border=True):
            st.markdown("<h2 style='color:#00BFFF;'>🤖 Robô e Programação</h2>", unsafe_allow_html=True)
            sub_tab_missoes, sub_tab_estrategia, sub_tab_codigos = st.tabs(["🎯 Missões", "🛠️ Estratégia", "🐍 Códigos"])
            
            with sub_tab_missoes:
                render_missoes_tapete(conn, read_only=not is_analista_missoes)
            
            with sub_tab_estrategia:
                render_estrategia_robo(conn, read_only=not is_engenheiro_construcao)
            
            with sub_tab_codigos:
                render_biblioteca_codigos(conn, read_only=not is_programador_robo)

    # ==============================================================================
    # ABA: KANBAN
    # ==============================================================================
    if aba_selecionada == "📊 Kanban":
        with st.container(border=True):
            st.markdown("<h2 style='color:#4B0082;'>📊 Quadro Kanban</h2>", unsafe_allow_html=True)
            # Verifica se o membro é 'Gerente de Tempo' para dar permissão de edição
            is_gerente_de_tempo = any(funcao == 'Gerente de Tempo' for _, funcao in minhas_atribuicoes)

            if is_gerente_de_tempo:
                st.subheader("➕ Nova Tarefa")
                integrantes_lista = listar_integrantes(conn)
                nomes_dict = {nome: id for id, nome in integrantes_lista}
                titulo_tarefa = st.text_input("Título da tarefa", key="kanban_titulo")
                desc_tarefa = st.text_area("Descrição (opcional)", key="kanban_desc")
                responsaveis = st.multiselect(
                    "Responsáveis",
                    list(nomes_dict.keys()),
                    key="kanban_resp"
                )
                if st.button("Criar Tarefa", key="kanban_criar"):
                    if not titulo_tarefa.strip():
                        st.warning("⚠️ O título não pode estar vazio.")
                    else:
                        # Pega o primeiro ID para o banco, mas lista todos na descrição
                        primary_id = nomes_dict[responsaveis[0]] if responsaveis else None
                        desc_final = desc_tarefa
                        if responsaveis:
                            desc_final = f"**Equipe:** {', '.join(responsaveis)}\n\n{desc_tarefa}"

                        if criar_tarefa(conn, titulo_tarefa, desc_final, primary_id):
                            st.success("✅ Tarefa criada!")
                            st.rerun()
                st.markdown("---")

            col_a_fazer, col_fazendo, col_feito = st.columns(3)
            for col, status, titulo_col in zip(
                [col_a_fazer, col_fazendo, col_feito],
                ["to_do", "doing", "done"],
                ["📝 A Fazer", "🔄 Fazendo", "✅ Feito"]
            ):
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
                                
                                if is_gerente_de_tempo:
                                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                                    if status != "to_do":
                                        with col_btn1:
                                            if st.button("← A Fazer", key=f"move_{t_id}_to_do", help="Mover para 'A Fazer'"):
                                                atualizar_status_tarefa(conn, t_id, "to_do")
                                                st.rerun()
                                    else:
                                        col_btn1.empty()
                                    if status != "doing":
                                        with col_btn2:
                                            if st.button("🔄 Fazendo", key=f"move_{t_id}_doing", help="Mover para 'Fazendo'"):
                                                atualizar_status_tarefa(conn, t_id, "doing")
                                                st.rerun()
                                    else:
                                        col_btn2.empty()
                                    if status != "done":
                                        with col_btn3:
                                            if st.button("✅ Feito", key=f"move_{t_id}_done", help="Mover para 'Feito'"):
                                                atualizar_status_tarefa(conn, t_id, "done")
                                                st.rerun()
                                    else:
                                        col_btn3.empty()
                                    with col_btn4:
                                        if st.button("🗑️ Excluir", key=f"del_tarefa_{t_id}", help="Excluir esta tarefa"):
                                            if excluir_tarefa(conn, t_id):
                                                st.success("✅ Tarefa excluída!")
                                                st.rerun()
            if is_gerente_de_tempo:
                st.markdown("---")
                st.subheader("📤 Enviar Quadro via Pushbullet")
                st.link_button("Pegue seu token aqui", "https://www.pushbullet.com/#settings/account", icon="🔗")
                token = st.text_input(f"Digite seu token do Pushbullet", type="password", key="push_token")
                if st.button("📤 Enviar Quadro Atual", key="push_enviar"):
                    tarefas_kanban = obter_quadro_kanban(conn)
                    if not tarefas_kanban:
                        st.warning("⚠️ Nenhuma tarefa no quadro para enviar.")
                    else:
                        sucesso, msg = enviar_kanban_pushbullet(tarefas_kanban, token)
                        if sucesso:
                            st.success("✅ Quadro enviado com sucesso via Pushbullet!")
                        else:
                            st.error(f"❌ {msg}")

    # ==============================================================================
    # ABA: COMPROMISSOS
    # ==============================================================================
    if aba_selecionada == "📅 Compromissos":
        with st.container(border=True):
            is_gerente_de_tempo = any(funcao == 'Gerente de Tempo' for _, funcao in minhas_atribuicoes)

            if is_gerente_de_tempo:
                st.markdown("<h2 style='color:#2E8B57;'>📅 Gerenciar Compromissos da Equipe</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#2E8B57;'>📅 Compromissos Oficiais da Equipe</h2>", unsafe_allow_html=True)

            compromissos = listar_compromissos(conn)
            if compromissos:
                comp_por_data = defaultdict(list)
                for cid, titulo, desc, data, inicio, fim in compromissos:
                    comp_por_data[data].append((cid, titulo, desc, inicio, fim))
                
                for data_str in sorted(comp_por_data.keys()):
                    data_obj = datetime.datetime.strptime(data_str, "%Y-%m-%d")
                    data_formatada = format_date(data_obj.date(), "d 'de' MMMM 'de' y", locale='pt_BR')
                    st.markdown(f"### 🗓️ {data_formatada}")
                    for cid, titulo, desc, inicio, fim in comp_por_data[data_str]:
                        with st.expander(f"📌 **{titulo}** — {inicio} a {fim}"):
                            if desc:
                                st.write(desc)
                            
                            if is_gerente_de_tempo:
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    if st.button("✏️ Editar", key=f"edit_{cid}", help="Editar este compromisso"):
                                        st.session_state.editando_compromisso = cid
                                        st.rerun()
                                with col2:
                                    if st.button("🗑️ Excluir", key=f"del_{cid}", help="Excluir este compromisso"):
                                        if excluir_compromisso(conn, cid):
                                            st.success("✅ Compromisso excluído!")
                                            st.rerun()
            else:
                st.info("Nenhum compromisso oficial agendado ainda.")

            if is_gerente_de_tempo:
                st.markdown("---")
                st.subheader("➕ Adicionar ou Editar Compromisso")
                
                editando_id = st.session_state.get("editando_compromisso", None)
                comp_edit = None
                if editando_id:
                    for c in compromissos:
                        if c[0] == editando_id:
                            comp_edit = c
                            break

                if comp_edit:
                    st.info(f"✏️ Editando: **{comp_edit[1]}**")
                    titulo_val = comp_edit[1]
                    desc_val = comp_edit[2]
                    data_val = datetime.datetime.strptime(comp_edit[3], "%Y-%m-%d").date()
                    inicio_val = comp_edit[4]
                    fim_val = comp_edit[5]
                else:
                    titulo_val = ""
                    desc_val = ""
                    data_val = datetime.date.today()
                    inicio_val = "09:00"
                    fim_val = "10:00"

                titulo = st.text_input("Título do compromisso", value=titulo_val, key="comp_titulo")
                descricao = st.text_area("Descrição (opcional)", value=desc_val, key="comp_desc")
                data = st.date_input("Data do compromisso", value=data_val, key="comp_data")
                inicio = st.selectbox(
                    "Horário de início",
                    HORARIOS_PADRAO,
                    index=HORARIOS_PADRAO.index(inicio_val),
                    key="comp_inicio"
                )
                fim_options = [h for h in HORARIOS_PADRAO if h > inicio]
                fim_index = fim_options.index(fim_val) if fim_val in fim_options else 0
                fim = st.selectbox("Horário de fim", fim_options, index=fim_index, key="comp_fim")

                if inicio >= fim:
                    st.warning("⚠️ O horário de fim deve ser depois do início.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Compromisso", key="comp_salvar"):
                        if not titulo.strip():
                            st.warning("⚠️ O título não pode estar vazio.")
                        elif inicio >= fim:
                            st.warning("⚠️ Corrija o horário.")
                        else:
                            data_str = data.strftime("%Y-%m-%d")
                            if comp_edit:
                                if atualizar_compromisso(conn, comp_edit[0], titulo, descricao, data_str, inicio, fim):
                                    st.success("✅ Compromisso atualizado!")
                                    st.session_state.editando_compromisso = None
                                    st.rerun()
                            else:
                                if criar_compromisso(conn, titulo, descricao, data_str, inicio, fim):
                                    st.success("✅ Compromisso criado!")
                                    st.rerun()
                with col2:
                    if comp_edit:
                        if st.button("❌ Cancelar edição", key="comp_cancelar"):
                            st.session_state.editando_compromisso = None
                            st.rerun()        

    # ==============================================================================
    # ABA: ACOMPANHAMENTO
    # ==============================================================================
    if aba_selecionada == "📈 Acompanhamento":
        with st.container(border=True):
            # Define permissões granulares
            is_gerente_de_tempo = any(funcao == 'Gerente de Tempo' for _, funcao in minhas_atribuicoes)
            
            render_controle_acompanhamento(
                conn,
                can_edit_checklist=(is_gerente_de_tempo or is_responsavel_materiais),
                can_edit_reunioes=is_gerente_de_tempo,
                can_edit_erros=is_gerente_de_tempo,
            )

    # ==============================================================================
    # ABA: ENVIAR FEEDBACK
    # ==============================================================================
    if aba_selecionada == "️🗣️ Enviar Feedback":
        with st.container(border=True):
            if is_sr_core_values:
                st.markdown("<h2 style='color:#FF6347;'>🗣️ Gerenciar Caixa de Feedback</h2>", unsafe_allow_html=True)
                st.info("Como 'Sr. core values', você pode visualizar e gerenciar os feedbacks enviados pela equipe.")

                reclamacoes = listar_reclamacoes(conn)

                if not reclamacoes:
                    st.success("✅ Nenhuma reclamação nova. Tudo em ordem!")
                else:
                    reclamacoes_novas = [r for r in reclamacoes if r['status'] == 'nova']
                    reclamacoes_lidas = [r for r in reclamacoes if r['status'] == 'lida']

                    st.markdown("### 📬 Novas")
                    if not reclamacoes_novas:
                        st.info("Nenhuma reclamação nova.")
                    for rec in reclamacoes_novas:
                        data_obj = datetime.datetime.fromisoformat(rec['data_criacao'])
                        try:
                            # Tenta formatar com hora
                            data_criacao = format_date(data_obj, "d MMM y, HH:mm", locale='pt_BR')
                        except AttributeError:
                            # Se falhar (não tem hora), formata sem hora
                            data_criacao = format_date(data_obj, "d MMM y", locale='pt_BR')
                        with st.expander(f"Feedback de **{rec.get('autor', 'N/A')}** - {data_criacao}"):
                            st.write(rec['texto'])
                            col1, col2 = st.columns(2)
                            if col1.button("Marcar como lida", key=f"ler_{rec['id']}", help="Mover para lidas"):
                                marcar_reclamacao_como_lida(conn, rec['id'])
                                st.rerun()
                            if col2.button("🗑️ Excluir", key=f"del_rec_{rec['id']}", help="Apagar esta reclamação"):
                                excluir_reclamacao(conn, rec['id'])
                                st.rerun()
                    
                    st.markdown("### 📖 Lidas")
                    for rec in reclamacoes_lidas:
                        data_obj = datetime.datetime.fromisoformat(rec['data_criacao'])
                        try:
                            # Tenta formatar com hora
                            data_criacao = format_date(data_obj, "d MMM y, HH:mm", locale='pt_BR')
                        except AttributeError:
                            # Se falhar (não tem hora), formata sem hora
                            data_criacao = format_date(data_obj, "d MMM y", locale='pt_BR')
                        with st.expander(f"Feedback lido de **{rec.get('autor', 'N/A')}** - {data_criacao}"):
                            st.write(rec['texto'])
                            if st.button("🗑️ Excluir", key=f"del_rec_lida_{rec['id']}", help="Apagar esta reclamação"):
                                excluir_reclamacao(conn, rec['id'])
                                st.rerun()
            else:
                st.markdown("<h2 style='color:#FF6347;'>🗣️ Caixa de Feedback e Reclamações</h2>", unsafe_allow_html=True)
                st.info("Use este espaço com responsabilidade para nos ajudar a melhorar. Você pode escolher se identificar ou enviar a mensagem anonimamente.")
                
                texto_reclamacao = st.text_area(
                    "Escreva sua reclamação ou sugestão aqui. Seja claro e objetivo.",
                    height=200,
                    key="texto_reclamacao"
                )
                
                enviar_anonimamente = st.checkbox("Quero enviar esta mensagem anonimamente", value=True, key="anonimo_check")
                
                if st.button("✉️ Enviar Mensagem", key="btn_enviar_reclamacao"):
                    if texto_reclamacao.strip():
                        # Se a caixa de anônimo estiver marcada, o ID enviado é None
                        id_do_autor = None if enviar_anonimamente else meu_id
                        
                        if criar_reclamacao(conn, texto_reclamacao, id_do_autor):
                            mensagem_sucesso = "Sua mensagem foi enviada com sucesso!"
                            st.toast(f"✅ {mensagem_sucesso}", icon="😁")
                            time.sleep(2) # Aguarda 2 segundos para o usuário ler a mensagem
                            st.rerun() # Recarrega a página, limpando o campo de texto
                        else:
                            st.error("❌ Ocorreu um erro ao enviar sua reclamação. Tente novamente.")
                    else:
                        st.warning("⚠️ O campo de texto não pode estar vazio.")

    if aba_selecionada == "📸 Momentos da Equipe":
        with st.container(border=True):
            st.markdown("<h2 style='color:#8A2BE2;'>📸 Momentos da Equipe</h2>", unsafe_allow_html=True)
            
            with st.form("upload_momento_form", clear_on_submit=True):
                st.subheader("📤 Envie uma foto de um momento especial")
                descricao_momento = st.text_input("Qual foi o momento? (Ex: Dia do campeonato, treino de sábado)")
                foto_momento = st.file_uploader("Selecione a foto", type=["jpg", "jpeg", "png"])
                
                submitted = st.form_submit_button("✨ Enviar Momento")
                if submitted:
                    if foto_momento and descricao_momento.strip():
                        with st.spinner("Enviando foto..."):
                            if upload_momento(conn, foto_momento, descricao_momento, meu_id):
                                st.success("✅ Foto enviada com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao enviar a foto. Tente novamente.")
                    else:
                        st.warning("⚠️ Por favor, adicione uma descrição e uma foto.")

            st.markdown("---")
            st.subheader("🖼️ Nossa Galeria")
            if is_sr_core_values:
                st.info("Como 'Sr. core values', você também pode excluir fotos da galeria.")

            momentos = listar_momentos(conn)
            if not momentos:
                st.info("Nenhuma foto foi enviada ainda.")
            else:
                for momento in momentos:
                    autor = momento.get("integrantes", {}).get("nome", "Equipe")
                    st.image(momento["url_imagem"], caption=f"'{momento['descricao']}' por {autor}", width=1365)

                    col1, col2 = st.columns([1, 5])
                    with col1:
                        try:
                            file_name = momento['url_imagem'].split('/')[-1]
                            st.download_button(
                                label="📥 Baixar",
                                data=requests.get(momento["url_imagem"]).content,
                                file_name=file_name,
                                mime="image/png",
                                key=f"download_momento_{momento['id']}"
                            )
                        except Exception as e:
                            st.error(f"Erro no download: {e}")
                    if is_sr_core_values:
                        with col2:
                            if st.button("🗑️ Excluir foto", key=f"del_momento_{momento['id']}", help="Remover esta foto da galeria"):
                                if excluir_momento(conn, momento['id'], momento['url_imagem']):
                                    st.success("✅ Foto excluída!")
                                    st.rerun()
                                    
                    st.markdown("---")

    if aba_selecionada == "🗳️ Votações":
        with st.container(border=True):
            st.markdown("<h2 style='color:#8A2BE2;'>🗳️ Votações da Equipe</h2>", unsafe_allow_html=True)
            
            votacoes = listar_votacoes_com_status(conn)
            if not votacoes:
                st.info("Nenhuma votação disponível no momento.")
            else:
                votacoes_abertas = [v for v in votacoes if v['status'] == 'aberta']
                votacoes_fechadas = [v for v in votacoes if v['status'] == 'fechada']

                st.markdown("### 🟢 Votações Abertas")
                if not votacoes_abertas:
                    st.info("Nenhuma votação aberta no momento.")
                for votacao in votacoes_abertas:
                    with st.expander(f"**{votacao['titulo']}**", expanded=True):
                        ja_votou = verificar_voto_integrante(conn, votacao['id'], meu_id)
                        if ja_votou:
                            st.success("✅ Você já votou nesta enquete. Obrigado por participar!")
                            # Mostra os resultados se o membro já votou
                            resultados = obter_resultados(conn, votacao['id'])
                            total_votos = sum(resultados.values())
                            st.write(f"Resultados parciais (total de **{total_votos}** votos):")
                            for opcao, contagem in resultados.items():
                                percentual = (contagem / total_votos * 100) if total_votos > 0 else 0
                                st.markdown(f"**{opcao}**: {contagem} voto(s)")
                                st.progress(percentual / 100)
                        else:
                            st.write("Escolha uma opção e clique para votar:")
                            # Adiciona aviso se a votação não for anônima
                            if votacao.get('tipo_votacao') == 'nao_anonima':
                                st.warning("⚠️ Esta é uma votação nominal. Seu voto será visível para o administrador.")

                            for opcao in votacao.get('opcoes_votacao', []):
                                if st.button(f"👉 {opcao['texto_opcao']}", key=f"votar_{votacao['id']}_{opcao['id']}"):
                                    sucesso, msg = registrar_voto(conn, votacao['id'], opcao['id'], meu_id)
                                    if sucesso:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                
                st.markdown("---")
                st.markdown("### 🔴 Votações Encerradas")
                if not votacoes_fechadas:
                    st.info("Nenhuma votação encerrada.")
                for votacao in votacoes_fechadas:
                     with st.expander(f"{votacao['titulo']}"):
                        resultados = obter_resultados(conn, votacao['id'])
                        total_votos = sum(resultados.values())
                        st.write(f"Resultado final (total de **{total_votos}** votos):")
                        for opcao, contagem in resultados.items():
                            percentual = (contagem / total_votos * 100) if total_votos > 0 else 0
                            st.markdown(f"**{opcao}**: {contagem} voto(s)")
                            st.progress(percentual / 100)

    if aba_selecionada == "🔑 Trocar Senha":
        with st.container(border=True):
            st.markdown("<h2 style='color:#FFD700;'>🔑 Trocar Minha Senha</h2>", unsafe_allow_html=True)
            
            with st.form("form_trocar_senha", clear_on_submit=True):
                senha_atual = st.text_input("Senha Atual", type="password")
                nova_senha = st.text_input("Nova Senha", type="password")
                confirmar_nova_senha = st.text_input("Confirmar Nova Senha", type="password")
                
                submitted = st.form_submit_button("💾 Alterar Senha")
                
                if submitted:
                    if not senha_atual or not nova_senha or not confirmar_nova_senha:
                        st.warning("⚠️ Todos os campos são obrigatórios.")
                    elif nova_senha != confirmar_nova_senha:
                        st.error("❌ As novas senhas não coincidem.")
                    elif nova_senha == senha_atual:
                        st.warning("⚠️ A nova senha deve ser diferente da senha atual.")
                    elif len(nova_senha) < 8:
                        st.warning("⚠️ A nova senha deve ter pelo menos 8 caracteres.")
                    else:
                        # A função trocar_senha_membro precisa ser importada
                        from models.integrante import trocar_senha_membro
                        sucesso, msg = trocar_senha_membro(conn, usuario_logado, senha_atual, nova_senha)
                        if sucesso:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
    if aba_selecionada == "🏦 Banco da Equipe":
        with st.container(border=True):
            st.markdown("<h2 style='color:#20B2AA;'>🏦 Banco da Equipe</h2>", unsafe_allow_html=True)
            # Componente do banco da equipe
            from views.shared_components import render_banco_da_dino_tech
            render_banco_da_dino_tech(conn)