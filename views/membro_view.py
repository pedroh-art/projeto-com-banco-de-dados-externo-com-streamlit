# views/membro_view.py
import streamlit as st
import datetime
from collections import defaultdict
from models.integrante import listar_integrantes, listar_atribuicoes
from models.tarefa import listar_tarefas_por_status
from models.compromisso import listar_compromissos

def render_membro_view(conn, regras, usuario_logado):
    st.set_page_config(page_title="Dino-Tech - Painel do Membro", layout="wide")
    st.markdown("<h1 style='color:#4B0082; text-align:center;'>👤 Painel do Membro - Dino-Tech</h1>", unsafe_allow_html=True)
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
            data_formatada = data_obj.strftime("%d de %B de %Y")
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
