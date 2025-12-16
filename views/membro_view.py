# views/membro_view.py
import streamlit as st
import datetime
from babel.dates import format_date
from collections import defaultdict
from models.integrante import listar_integrantes, listar_atribuicoes
from models.tarefa import listar_tarefas_por_status
from models.compromisso import listar_compromissos
from utils.pushbullet_util import enviar_kanban_pushbullet
from models.tarefa import (
    criar_tarefa, atualizar_status_tarefa, excluir_tarefa,
    listar_tarefas_por_status, obter_quadro_kanban
)
from models.compromisso import (
    criar_compromisso, listar_compromissos, atualizar_compromisso, excluir_compromisso
)
def render_membro_view(conn, regras, usuario_logado):
    # Configura o locale para português do Brasil para formatar as datas
    HORARIOS_PADRAO = [f"{h:02d}:00" for h in range(8, 20)]
<<<<<<< HEAD
    import locale

    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'C')

=======
>>>>>>> 7cf68b6 (Corrige erro de locale no Streamlit Cloud)

    st.set_page_config(page_title="Dino-Tech - Painel do Membro", layout="wide")
    st.markdown("<h1 style='color:#4B0082; text-align:center;'>👤 Painel do Membro - Dino-Tech</h1>", unsafe_allow_html=True)
    if st.button("Recarregar página", key="recarregar_pagina_membro"):
        st.rerun()
    st.markdown(f"👤 Logado como: **{usuario_logado}** (membro)")
    
    if st.button("🔒 Sair", key="sair_membro"):
        st.session_state.usuario_logado = None
        st.session_state.tipo_usuario = None
        st.rerun()

    st.markdown("---")

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

    # ==============================================================================
    # MEUS SETORES, FUNÇÕES, RESPONSABILIDADES E DIREITOS EXCLUSIVOS
    # ==============================================================================
    st.markdown("### 👥 Meus Setores e Funções")
    minhas_atribuicoes = listar_atribuicoes(conn, meu_id)
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

    st.markdown("---")

    # ==============================================================================
    # COMPROMISSOS OFICIAIS
    # ==============================================================================
    st.markdown("### 📅 Compromissos Oficiais da Equipe")
    compromissos = listar_compromissos(conn)
    if compromissos:
        comp_por_data = defaultdict(list)
        for cid, titulo, desc, data, inicio, fim in compromissos:
            comp_por_data[data].append((titulo, desc, inicio, fim))
        
        for data_str in sorted(comp_por_data.keys()):
            data_obj = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            data_formatada = format_date(data_obj, "d 'de' MMMM 'de' y", locale='pt_BR')
            st.markdown(f"#### 🗓️ {data_formatada}")
            for titulo, desc, inicio, fim in comp_por_data[data_str]:
                with st.expander(f"📌 **{titulo}** — {inicio} a {fim}"):
                    if desc:
                        st.write(desc)
    else:
        st.info("Nenhum compromisso oficial agendado ainda.")

    st.markdown("---")

    # ==============================================================================
    # KANBAN (SOMENTE LEITURA)
    # ==============================================================================
    atribuicoes_do_integrante = listar_atribuicoes(conn, meu_id)
    if any(funcao == 'Gerente de Tempo' for setor, funcao in atribuicoes_do_integrante):
        st.markdown("<h2 style='color:#4B0082;'>📊 Quadro Kanban</h2>", unsafe_allow_html=True)
        st.subheader("➕ Nova Tarefa")
        integrantes_lista = listar_integrantes(conn)
        nomes_dict = {nome: id for id, nome in integrantes_lista}
        titulo_tarefa = st.text_input("Título da tarefa", key="kanban_titulo")
        desc_tarefa = st.text_area("Descrição (opcional)", key="kanban_desc")
        responsavel = st.selectbox(
            "Responsável",
            ["(Nenhum)"] + list(nomes_dict.keys()),
            key="kanban_resp"
        )
        if st.button("Criar Tarefa", key="kanban_criar"):
            if not titulo_tarefa.strip():
                st.warning("⚠️ O título não pode estar vazio.")
            else:
                integrante_id = nomes_dict.get(responsavel) if responsavel != "(Nenhum)" else None
                if criar_tarefa(conn, titulo_tarefa, desc_tarefa, integrante_id):
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
                            st.markdown(f"**Responsável:** {nome_resp or 'Ninguém'}")
                            if desc:
                                st.write(desc)
                            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                            if status != "to_do":
                                with col_btn1:
                                    if st.button("← A Fazer", key=f"move_{t_id}_to_do"):
                                        atualizar_status_tarefa(conn, t_id, "to_do")
                                        st.rerun()
                            else:
                                col_btn1.empty()
                            if status != "doing":
                                with col_btn2:
                                    if st.button("🔄 Fazendo", key=f"move_{t_id}_doing"):
                                        atualizar_status_tarefa(conn, t_id, "doing")
                                        st.rerun()
                            else:
                                col_btn2.empty()
                            if status != "done":
                                with col_btn3:
                                    if st.button("✅ Feito", key=f"move_{t_id}_done"):
                                        atualizar_status_tarefa(conn, t_id, "done")
                                        st.rerun()
                            else:
                                col_btn3.empty()
                            with col_btn4:
                                if st.button("🗑️ Excluir", key=f"del_tarefa_{t_id}"):
                                    if excluir_tarefa(conn, t_id):
                                        st.success("✅ Tarefa excluída!")
                                        st.rerun()
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
        st.markdown("<h2 style='color:#2E8B57;'>📅 Compromissos Oficiais da Equipe</h2>", unsafe_allow_html=True)
        compromissos = listar_compromissos(conn)
        if compromissos:
            comp_por_data = defaultdict(list)
            for cid, titulo, desc, data, inicio, fim in compromissos:
                comp_por_data[data].append((cid, titulo, desc, inicio, fim))
            for data_str in sorted(comp_por_data.keys()):
                data_obj = datetime.datetime.strptime(data_str, "%Y-%m-%d")
                data_formatada = format_date(data_obj, "d 'de' MMMM 'de' y", locale='pt_BR')
                st.markdown(f"### 🗓️ {data_formatada}")
                for cid, titulo, desc, inicio, fim in comp_por_data[data_str]:
                    with st.expander(f"📌 **{titulo}** — {inicio} a {fim}"):
                        if desc:
                            st.write(desc)
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("✏️ Editar", key=f"edit_{cid}"):
                                st.session_state.editando_compromisso = cid
                        with col2:
                            if st.button("🗑️ Excluir", key=f"del_{cid}"):
                                if excluir_compromisso(conn, cid):
                                    st.success("✅ Compromisso excluído!")
                                    st.rerun()
        else:
            st.info("Nenhum compromisso oficial agendado ainda.")

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
    
    else:
        st.markdown("### 📊 Quadro Kanban (visão somente leitura)")

        col_a_fazer, col_fazendo, col_feito = st.columns(3)

        for col, status, titulo_col in zip(
            [col_a_fazer, col_fazendo, col_feito],
            ["to_do", "doing", "done"],
            ["📝 A Fazer", "🔄 Fazendo", "✅ Feito"]
        ):
            with col:
                st.markdown(f"#### {titulo_col}")
                tarefas = listar_tarefas_por_status(conn, status)
                if not tarefas:
                    st.info("Nenhuma tarefa.")
                else:
                    for t_id, titulo, desc, int_id, nome_resp in tarefas:
                        st.markdown(f"**📌 {titulo}**")
                        st.markdown(f"**Responsável:** {nome_resp or 'Não atribuído'}")
                        if desc:
                            st.markdown(f"> {desc}")
                        st.markdown("")
    
