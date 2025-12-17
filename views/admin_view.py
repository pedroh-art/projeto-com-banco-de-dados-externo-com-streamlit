# views/admin_view.py
import streamlit as st
import datetime
import copy
from collections import defaultdict
from models.integrante import (
    listar_integrantes, cadastrar_integrante, cadastrar_login_membro,
    atribuir_setor_funcao, listar_atribuicoes, remover_atribuicao,
    remover_integrante_completo, contar_total_integrantes,
    contar_atribuidos_por_funcao, contar_setores_unicos_por_integrante,
    contar_total_funcoes_por_integrante, listar_logins_membros, resetar_senha_admin
)
from models.tarefa import (
    criar_tarefa, atualizar_status_tarefa, excluir_tarefa,
    listar_tarefas_por_status, obter_quadro_kanban
)
import requests
from models.compromisso import (
    criar_compromisso, listar_compromissos, atualizar_compromisso, excluir_compromisso
)
from models.reclamacao import (
    listar_reclamacoes, marcar_reclamacao_como_lida, excluir_reclamacao
)
from models.momento import (
    listar_momentos, excluir_momento
)
from models.votacao import (
    criar_votacao, listar_votacoes_com_status, atualizar_status_votacao,
    excluir_votacao, obter_resultados, obter_resultados_detalhados
)
from models.credencial import (
    criar_credencial, listar_credenciais, excluir_credencial
)
from views.shared_components import render_central_de_senhas, render_registro_de_pecas, render_missoes_tapete, render_estrategia_robo, render_biblioteca_codigos, render_projeto_inovacao, render_controle_acompanhamento
from services.regras_service import salvar_regras
from utils.pushbullet_util import enviar_kanban_pushbullet
from babel.dates import format_date
import time
# Horários padrão
HORARIOS_PADRAO = [f"{h:02d}:00" for h in range(8, 20)]

def render_admin_view(conn, regras):
    # Faz uma cópia profunda das regras no início para detectar mudanças
    regras_originais = copy.deepcopy(regras)

    st.set_page_config(page_title="Banco De Dados Da Dino-Tech", layout="wide")
    st.markdown(f"<h1 style='color:#FFD700; text-align:center;'>🚀 Banco De Dados Da Dino-Tech 🚀</h1>", unsafe_allow_html=True)
    if st.button("Recarregar página", key="recarregar_pagina_admin"):
        st.rerun()
    st.markdown(f"👤 Logado como: **{st.session_state.usuario_logado}** (administrador)")
    if st.button("🔒 Sair", key="sair_admin"):
        st.session_state.usuario_logado = None
        st.session_state.tipo_usuario = None
        st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18 = st.tabs([
        "📂 Setores", "📜 Direitos gerais", "🔑 Direitos por Setor", "📑 Regras gerais",
        "💡 Por quê", "👥 Membros", "⚙️ Editar regras", "🧩 Projeto de Inovação", "🤖 Robô e Programação", "📊 Kanban", "📅 Compromissos", "📈 Acompanhamento", "🗣️ Reclamações", "📸 Momentos",
        "🗳️ Votação", "🔑 Central de Senhas", "👤 Usuários e Senhas", "📦 Registro de Peças"
    ])

    # ==============================================================================
    # ABA 1: Setores
    # ==============================================================================
    with tab1:
        setores = regras.get("setores", [])
        if not setores:
            st.warning("⚠️ Nenhum setor definido nas regras.")
        else:
            sub_tabs = st.tabs([f"🏗️ {s['nome']}" for s in setores])
            for i, setor in enumerate(setores):
                with sub_tabs[i]:
                    st.markdown(f"<h2 style='color:#00CED1;'>✨ {setor['nome']} ✨</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size:18px; color:#FF69B4;'>Capacidade máxima: <b>{setor.get('capacidade', 'N/A')}</b> pessoas</p>", unsafe_allow_html=True)
                    for func in setor.get("funcoes", []):
                        st.markdown(f"<h4 style='color:#FF4500;'>⚡ {func['nome']} (máximo {func.get('max', 'N/A')} pessoas)</h4>", unsafe_allow_html=True)
                        for r in func.get("responsabilidades", []):
                            st.markdown(f"👉 {r}")
                    direitos_exclusivos = setor.get("direitos_exclusivos", [])
                    st.markdown("### 🔑 Direitos exclusivos deste setor")
                    if direitos_exclusivos:
                        for d in direitos_exclusivos:
                            st.markdown(f"✅ {d}")
                    else:
                        st.info("Nenhum direito exclusivo definido para este setor.")
                    try:
                        res = conn.table("atribuicoes").select("funcao, integrantes(nome)").eq("setor", setor["nome"]).order("integrantes(nome)").execute()
                        atribs = []
                        if res.data:
                            for item in res.data:
                                nome_integrante = item.get("integrantes", {}).get("nome") if item.get("integrantes") else "Desconhecido"
                                atribs.append((nome_integrante, item["funcao"]))
                    except Exception as e:
                        st.error(f"Erro ao carregar membros do setor: {e}")
                        atribs = []
                    st.write("### 👥 Membros nesse setor")
                    if atribs:
                        for nome, funcao in atribs:
                            st.markdown(f"- {nome} → {funcao}")
                    else:
                        st.info("Nenhum membro atribuído ainda.")

    # ==============================================================================
    # ABA 2: Direitos gerais
    # ==============================================================================
    with tab2:
        st.markdown("<h2 style='color:#32CD32;'>📜 Direitos gerais da equipe</h2>", unsafe_allow_html=True)
        direitos = regras.get("direitos_gerais", [])
        if direitos:
            for d in direitos:
                st.markdown(f"✅ {d}")
        else:
            st.info("Nenhum direito geral definido.")

    # ==============================================================================
    # ABA 3: Direitos por Setor
    # ==============================================================================
    with tab3:
        st.markdown("<h2 style='color:#9932CC;'>🔑 Direitos Exclusivos por Setor</h2>", unsafe_allow_html=True)
        for setor in regras.get("setores", []):
            if "direitos_exclusivos" not in setor:
                setor["direitos_exclusivos"] = []
        for setor in regras.get("setores", []):
            with st.expander(f"🏗️ {setor['nome']}", expanded=False):
                direitos = setor.setdefault("direitos_exclusivos", [])
                for idx in range(len(direitos.copy())):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        novo_direito = st.text_area(
                            f"Direito exclusivo {idx+1}",
                            value=direitos[idx],
                            key=f"dir_setor_{setor['nome']}_{idx}"
                        )
                        direitos[idx] = novo_direito
                    with col2:
                        if st.button("❌", key=f"del_dir_setor_{setor['nome']}_{idx}"):
                            direitos.pop(idx)
                            st.rerun()
                novo_dir = st.text_input(
                    f"Novo direito exclusivo para {setor['nome']}",
                    key=f"novo_dir_setor_{setor['nome']}"
                )
                if st.button(f"➕ Adicionar a {setor['nome']}", key=f"add_dir_setor_{setor['nome']}"):
                    if novo_dir.strip():
                        direitos.append(novo_dir.strip())
                        st.rerun()
                if direitos:
                    st.markdown("#### ✅ Direitos exclusivos:")
                    for d in direitos:
                        st.markdown(f"- {d}")
                else:
                    st.info("Nenhum direito exclusivo definido para este setor.")

    # ==============================================================================
    # ABA 4: Regras gerais
    # ==============================================================================
    with tab4:
        st.markdown("<h2 style='color:#1E90FF;'>📑 Regras gerais da equipe</h2>", unsafe_allow_html=True)
        regras_gerais = regras.get("regras_gerais", [])
        if regras_gerais:
            for r in regras_gerais:
                st.markdown(f"⚖️ {r}")
        else:
            st.info("Nenhuma regra geral definida.")

    # ==============================================================================
    # ABA 5: Justificativas
    # ==============================================================================
    with tab5:
        st.markdown("<h2 style='color:#FF1493;'>💡 Por que estas regras</h2>", unsafe_allow_html=True)
        por_que = regras.get("por_que", {})
        if por_que:
            for chave, valor in por_que.items():
                st.markdown(f"🔹 **{chave.capitalize()}:** {valor}")
        else:
            st.info("Nenhuma justificativa definida.")

    # ==============================================================================
    # ABA 6: Membros
    # ==============================================================================
    with tab6:
        st.markdown("<h2 style='color:#FFA500;'>👥 Cadastro e atribuições dos membros</h2>", unsafe_allow_html=True)
        novo_nome = st.text_input("Nome do integrante", key="novo_integrante")
        total = contar_total_integrantes(conn)
        limite_total = regras.get("limite_total_membros", 6)
        if st.button("Cadastrar integrante", key="btn_cadastrar_integrante"):
            if not novo_nome.strip():
                st.warning("⚠️ O nome não pode estar vazio.")
            elif total >= limite_total:
                st.error(f"❌ Limite total de {limite_total} membros já foi atingido!")
            else:
                if cadastrar_integrante(conn, novo_nome):
                    user, pwd = cadastrar_login_membro(conn, novo_nome)
                    if user:
                        st.toast(f"✅ Integrante '{novo_nome}' cadastrado! Login: **{user}** / Senha: **{pwd}**", icon="✅")
                        print(f"Login criado para {novo_nome} → Usuário: {user} | Senha: {pwd}")
                        credenciais = f"Usuário: {user}\nSenha: {pwd}\n\n(Obs: Guarde este arquivo em local seguro!)"
                        
                
                        
                    else:
                        st.success(f"✅ Integrante '{novo_nome}' cadastrado!")
                    if st.download_button(
                            label="📥 Baixar credenciais (clique para salvar)",
                            data=credenciais,
                            file_name=f"credenciais_{user}.txt",
                            mime="text/plain",
                            key=f"download_{user}"
                        ):
                        st.rerun()
                    st.stop()
        st.markdown(f"📊 Total de integrantes: **{total} / {limite_total}**")
        if total >= limite_total:
            st.warning(f"⚠️ Limite máximo de {limite_total} membros atingido!")
        integrantes = listar_integrantes(conn)
        if integrantes:
            for integrante_id, nome in integrantes:
                setores_count = contar_setores_unicos_por_integrante(conn, integrante_id)
                funcoes_count = contar_total_funcoes_por_integrante(conn, integrante_id)
                st.markdown(f"### 👤 {nome} (`Setores: {setores_count}/4` • `Funções: {funcoes_count}/5`)")
                if st.button(f"❌ Remover {nome}", key=f"rem_integrante_{integrante_id}"):
                    if remover_integrante_completo(conn, integrante_id):
                        st.success(f"🗑️ Integrante '{nome}' removido com sucesso!")
                        st.rerun()
                setor_escolhido = st.selectbox(
                    f"Setor para {nome}",
                    [s["nome"] for s in regras.get("setores", [])],
                    key=f"setor_{integrante_id}"
                )
                funcoes_do_setor = []
                for s in regras.get("setores", []):
                    if s["nome"] == setor_escolhido:
                        funcoes_do_setor = s.get("funcoes", [])
                        break
                if funcoes_do_setor:
                    funcao_escolhida = st.selectbox(
                        f"Função em {setor_escolhido}",
                        [f["nome"] for f in funcoes_do_setor],
                        key=f"funcao_{integrante_id}"
                    )
                    funcao_info = next((f for f in funcoes_do_setor if f["nome"] == funcao_escolhida), {})
                    max_funcao = funcao_info.get("max", 999)
                    atual_funcao = contar_atribuidos_por_funcao(conn, setor_escolhido, funcao_escolhida)
                    if st.button(f"➕ Atribuir {nome} a {setor_escolhido}/{funcao_escolhida}", key=f"btn_atribuir_{integrante_id}"):
                        if atual_funcao >= max_funcao:
                            st.error(f"❌ Limite atingido para '{funcao_escolhida}' ({max_funcao} pessoas).")
                        else:
                            atribs_existentes = listar_atribuicoes(conn, integrante_id)
                            ja_esta_nesse_setor = any(s == setor_escolhido for s, f in atribs_existentes)
                            setores_atuais = contar_setores_unicos_por_integrante(conn, integrante_id)
                            novo_total_setores = setores_atuais if ja_esta_nesse_setor else setores_atuais + 1
                            if novo_total_setores > 4:
                                st.error("❌ Este integrante já está em 4 setores diferentes! Limite atingido.")
                            else:
                                total_funcoes = contar_total_funcoes_por_integrante(conn, integrante_id)
                                if total_funcoes >= 5:
                                    st.error("❌ Este integrante já tem 5 funções atribuídas! Limite atingido.")
                                else:
                                    if atribuir_setor_funcao(conn, integrante_id, setor_escolhido, funcao_escolhida):
                                        st.success(f"✅ {nome} atribuído(a) a {setor_escolhido} como {funcao_escolhida}!")
                                        st.rerun()
                else:
                    st.warning(f"Nenhuma função definida para o setor '{setor_escolhido}'.")
                atribs = listar_atribuicoes(conn, integrante_id)
                if atribs:
                    st.write("📌 Atribuições atuais:")
                    for idx_atrib, (setor, funcao) in enumerate(atribs):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"- {setor} / {funcao}")
                        with col2:
                            if st.button("❌", key=f"rem_atrib_{integrante_id}_{idx_atrib}", help="Remover atribuição"):
                                if remover_atribuicao(conn, integrante_id, setor, funcao):
                                    st.success(f"✅ Atribuição removida!")
                                    st.rerun()
                else:
                    st.info("Nenhuma atribuição ainda.")
        else:
            st.info("Nenhum integrante cadastrado ainda.")

    # ==============================================================================
    # ABA 7: Editar regras
    # ==============================================================================
    with tab7:
            
        st.markdown("<h2 style='color:#8A2BE2;'>⚙️ Editar limites e textos das regras</h2>", unsafe_allow_html=True)
        for setor in regras.get("setores", []):
            with st.expander(f"🏗️ {setor['nome']} — capacidade atual: {setor.get('capacidade', 'N/A')} pessoas", expanded=False):
                novo_cap = st.slider(
                    f"Capacidade máxima do setor {setor['nome']}",
                    min_value=1, max_value=6, value=setor.get("capacidade", 6),
                    key=f"cap_{setor['nome']}"
                )
                setor["capacidade"] = novo_cap
                for func in setor.get("funcoes", []):
                    st.markdown(f"<h4 style='color:#FF4500;'>⚡ {func['nome']}</h4>", unsafe_allow_html=True)
                    novo_max = st.slider(
                        f"Máximo de pessoas para {func['nome']}",
                        min_value=1, max_value=6, value=func.get("max", 3),
                        key=f"max_{setor['nome']}_{func['nome']}"
                    )
                    func["max"] = novo_max
                    with st.expander(f"✏️ Responsabilidades de {func['nome']}", expanded=False):
                        resp_list = func.get("responsabilidades", [])
                        for idx, r in enumerate(resp_list.copy()):
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                novo_texto = st.text_area(
                                    f"Responsabilidade {idx+1}",
                                    value=r,
                                    key=f"resp_{setor['nome']}_{func['nome']}_{idx}"
                                )
                                resp_list[idx] = novo_texto
                            with col2:
                                if st.button("❌", key=f"del_resp_{setor['nome']}_{func['nome']}_{idx}"):
                                    resp_list.pop(idx)
                                    func["responsabilidades"] = resp_list
                                    st.rerun()
                        nova_resp = st.text_input(
                            f"Nova responsabilidade para {func['nome']}",
                            key=f"nova_resp_{setor['nome']}_{func['nome']}"
                        )
                        if st.button(f"➕ Adicionar", key=f"btn_resp_{setor['nome']}_{func['nome']}"):
                            if nova_resp.strip():
                                resp_list.append(nova_resp.strip())
                                func["responsabilidades"] = resp_list
                                st.rerun()
        with st.expander("📜 Direitos gerais da equipe", expanded=False):
            direitos = regras.setdefault("direitos_gerais", [])
            for idx in range(len(direitos.copy())):
                col1, col2 = st.columns([4, 1])
                with col1:
                    novo_d = st.text_area(f"Direito {idx+1}", value=direitos[idx], key=f"dir_global_{idx}")
                    direitos[idx] = novo_d
                with col2:
                    if st.button("❌", key=f"del_dir_{idx}"):
                        direitos.pop(idx)
                        regras["direitos_gerais"] = direitos
                        st.rerun()
            novo_dir = st.text_input("Novo direito geral", key="novo_dir_global")
            if st.button("➕ Adicionar direito geral", key="btn_add_dir_global"):
                if novo_dir.strip():
                    direitos.append(novo_dir.strip())
                    st.rerun()
        with st.expander("📑 Regras gerais da equipe", expanded=False):
            regras_gerais = regras.setdefault("regras_gerais", [])
            for idx in range(len(regras_gerais.copy())):
                col1, col2 = st.columns([4, 1])
                with col1:
                    novo_r = st.text_area(f"Regra {idx+1}", value=regras_gerais[idx], key=f"reg_global_{idx}")
                    regras_gerais[idx] = novo_r
                with col2:
                    if st.button("❌", key=f"del_reg_{idx}"):
                        regras_gerais.pop(idx)
                        regras["regras_gerais"] = regras_gerais
                        st.rerun()
            nova_regra = st.text_input("Nova regra geral", key="nova_regra_global")
            if st.button("➕ Adicionar regra geral", key="btn_add_reg_global"):
                if nova_regra.strip():
                    regras_gerais.append(nova_regra.strip())
                    st.rerun()
        with st.expander("💡 Justificativas", expanded=False):
            por_que = regras.setdefault("por_que", {})
            chaves = list(por_que.keys())
            for idx, chave in enumerate(chaves):
                col1, col2 = st.columns([4, 1])
                with col1:
                    novo_texto = st.text_area(f"'{chave}'", value=por_que[chave], key=f"just_{idx}")
                    por_que[chave] = novo_texto
                with col2:
                    if st.button("❌", key=f"del_just_{idx}"):
                        por_que.pop(chave)
                        st.rerun()
            nova_chave = st.text_input("Nova justificativa: nome curto", key="nova_just_chave")
            nova_valor = st.text_area("Texto da justificativa", key="nova_just_valor")
            if st.button("➕ Adicionar justificativa", key="btn_add_just"):
                if nova_chave.strip() and nova_valor.strip():
                    por_que[nova_chave.strip()] = nova_valor.strip()
                    st.rerun()
        with st.expander("👥 Limite total de membros da equipe", expanded=False):
            limite_atual = regras.get("limite_total_membros", 6)
            novo_limite = st.number_input(
                "Número máximo de integrantes permitidos na equipe",
                min_value=1,
                max_value=6,
                value=int(limite_atual),
                step=1,
                key="limite_total"
            )
            regras["limite_total_membros"] = int(novo_limite)

        # Lógica de salvamento automático
        if regras != regras_originais:
            salvar_regras(conn, regras)
            st.toast("💾 Alterações feitas foram salvas automaticamente!", icon="✅", duration="short")
            with st.sidebar:
                if st.button("💾 Recarregar para aplicar mudanças", key="recarregar_apos_salvar_regras"):
                    st.rerun()
            st.stop()
               

    # ==============================================================================
    # ABA 8: Projeto de Inovação
    # ==============================================================================
    with tab8:
        render_projeto_inovacao(conn, read_only=False)

    # ==============================================================================
    # ABA 8: Robô e Programação
    # ==============================================================================
    with tab9:
        st.markdown("<h2 style='color:#00BFFF;'>🤖 Robô e Programação</h2>", unsafe_allow_html=True)
        sub_tab_missoes, sub_tab_estrategia, sub_tab_codigos = st.tabs(["🎯 Missões", "🛠️ Estratégia", "🐍 Códigos"])
        
        with sub_tab_missoes:
            # Admin tem acesso completo (read_only=False)
            render_missoes_tapete(conn, read_only=False)
        
        with sub_tab_estrategia:
            render_estrategia_robo(conn, read_only=False)
        
        with sub_tab_codigos:
            render_biblioteca_codigos(conn, read_only=False)

    # ==============================================================================
    # ABA 8: Kanban
    # ==============================================================================
    with tab10:
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

    # ==============================================================================
    # ABA 9: Compromissos
    # ==============================================================================
    with tab11:
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

    # ==============================================================================
    # ABA 12: Acompanhamento
    # ==============================================================================
    with tab12:
        render_controle_acompanhamento(
            conn, 
            can_edit_checklist=True, 
            can_edit_reunioes=True, 
            can_edit_erros=True
        )

    # ==============================================================================
    # ABA 13: Reclamações Anônimas
    # ==============================================================================
    with tab13:
        st.markdown("<h2 style='color:#FF6347;'>🗣️ Caixa de Feedback</h2>", unsafe_allow_html=True)
        st.info("Este espaço é para visualizar feedbacks e reclamações enviadas pelos membros da equipe.")

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
                    if col1.button("Marcar como lida", key=f"ler_{rec['id']}"):
                        marcar_reclamacao_como_lida(conn, rec['id'])
                        st.rerun()
                    if col2.button("🗑️ Excluir", key=f"del_rec_{rec['id']}"):
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
                    if st.button("🗑️ Excluir", key=f"del_rec_lida_{rec['id']}"):
                        excluir_reclamacao(conn, rec['id'])
                        st.rerun()

    # ==============================================================================
    # ABA 14: Momentos da Equipe
    # ==============================================================================
    with tab14:
        st.markdown("<h2 style='color:#8A2BE2;'>📸 Gerenciar Momentos da Equipe</h2>", unsafe_allow_html=True)
        st.info("Visualize e gerencie as fotos enviadas pelos membros da equipe.")

        momentos = listar_momentos(conn)
        if not momentos:
            st.info("Nenhuma foto foi enviada ainda.")
        else:
            for momento in momentos:
                autor = momento.get("integrantes", {}).get("nome", "Equipe")
                st.image(momento["url_imagem"], caption=f"'{momento['descricao']}'", width=1365)
                if st.button("🗑️ Excluir esta foto", key=f"del_momento_{momento['id']}"):
                    if excluir_momento(conn, momento['id'], momento['url_imagem']):
                        st.success("✅ Foto excluída com sucesso!")
                        st.rerun()
                try:
                    file_name = momento['url_imagem'].split('/')[-1]
                    st.download_button(
                        label="📥 Baixar",
                        data=requests.get(momento["url_imagem"]).content,
                        file_name=file_name, # type: ignore
                        mime="image/png",
                        key=f"download_momento_{momento['id']}"
                   )
                except Exception as e:
                    st.error(f"Erro no download: {e}")        
                st.markdown("---")

    # ==============================================================================
    # ABA 15: Votação
    # ==============================================================================
    with tab15:
        st.markdown("<h2 style='color:#8A2BE2;'>🗳️ Votações da Equipe</h2>", unsafe_allow_html=True)

        with st.expander("➕ Criar Nova Votação", expanded=False):
            titulo_votacao = st.text_input("Título da votação", key="votacao_titulo")
            opcoes_votacao = st.text_area(
                "Opções (uma por linha)",
                key="votacao_opcoes",
                help="Digite cada opção em uma nova linha."
            )
            tipo_votacao = st.radio(
                "Tipo de Votação",
                ('anonima', 'nao_anonima'),
                format_func=lambda x: "Anônima (só mostra o total)" if x == 'anonima' else "Nominal (mostra quem votou em quê)",
                key="tipo_votacao"
            )
            if st.button("🚀 Criar Votação", key="votacao_criar"):
                opcoes_lista = [opt.strip() for opt in opcoes_votacao.split('\n') if opt.strip()]
                if not titulo_votacao.strip():
                    st.warning("⚠️ O título da votação não pode estar vazio.")
                elif len(opcoes_lista) < 2:
                    st.warning("⚠️ A votação precisa ter pelo menos duas opções.")
                else:
                    if criar_votacao(conn, titulo_votacao, opcoes_lista, tipo_votacao):
                        st.success(f"✅ Votação '{titulo_votacao}' criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao criar a votação.")

        st.markdown("---")
        st.subheader("📋 Votações em Andamento e Encerradas")

        votacoes = listar_votacoes_com_status(conn)
        if not votacoes:
            st.info("Nenhuma votação foi criada ainda.")
        else:
            for votacao in votacoes:
                status_emoji = "🟢" if votacao['status'] == 'aberta' else "🔴"
                tipo_texto = "Anônima" if votacao.get('tipo_votacao', 'anonima') == 'anonima' else "Nominal"
                with st.expander(f"{status_emoji} {votacao['titulo']} ({votacao['status'].capitalize()} - {tipo_texto})"):
                    st.markdown("#### Resultados Atuais")
                    resultados = obter_resultados(conn, votacao['id'])
                    total_votos = sum(resultados.values())
                    st.write(f"Total de votos: **{total_votos}**")

                    # Mostra resultados anônimos (barra de progresso)
                    for opcao, contagem in resultados.items():
                        percentual = (contagem / total_votos * 100) if total_votos > 0 else 0
                        st.markdown(f"**{opcao}**: {contagem} voto(s)")
                        st.progress(percentual / 100)
                    
                    # Se a votação for não anônima, mostra os detalhes
                    if votacao.get('tipo_votacao') == 'nao_anonima':
                        st.markdown("##### Votos por integrante:")
                        resultados_detalhados = obter_resultados_detalhados(conn, votacao['id'])
                        for opcao, integrantes in resultados_detalhados.items():
                            st.markdown(f"**{opcao}**: {', '.join(integrantes)}")

                    st.markdown("---")
                    st.markdown("##### Gerenciar Votação")
                    col1, col2, col3 = st.columns(3)
                    if votacao['status'] == 'aberta':
                        if col1.button("🔒 Fechar Votação", key=f"fechar_vot_{votacao['id']}"):
                            atualizar_status_votacao(conn, votacao['id'], 'fechada')
                            st.rerun()
                    else:
                        if col1.button("🔓 Reabrir Votação", key=f"reabrir_vot_{votacao['id']}"):
                            atualizar_status_votacao(conn, votacao['id'], 'aberta')
                            st.rerun()
                    if col3.button("🗑️ Excluir Votação", key=f"excluir_vot_{votacao['id']}", type="primary"):
                        if excluir_votacao(conn, votacao['id']):
                            st.success("✅ Votação excluída com sucesso!")
                            st.rerun()

    # ==============================================================================
    # ABA 16: Central de Senhas
    # ==============================================================================
    with tab16:
        render_central_de_senhas(conn)

    # ==============================================================================
    # ABA 17: Usuários e Senhas
    # ==============================================================================
    with tab17:
        st.markdown("<h2 style='color:#DC143C;'>👤 Usuários e Senhas dos Membros</h2>", unsafe_allow_html=True)
        st.warning("🔒 Esta área expõe as senhas dos usuários. Use com extrema cautela.")

        logins = listar_logins_membros(conn)

        if not logins:
            st.info("Nenhum login de membro encontrado.")
        else:
            for login in logins:
                with st.container(border=True):
                    st.markdown(f"#### {login['usuario']}")
                    
                    # Campo de Usuário e botão de copiar
                    col_user_input, col_user_btn = st.columns([0.7, 0.3])
                    with col_user_input:
                        st.text_input("Usuário", value=login['usuario'], key=f"login_user_display_{login['id']}", disabled=True, label_visibility="collapsed")
                    with col_user_btn:
                        if st.button("📋 Copiar Usuário", key=f"copy_login_user_btn_{login['id']}"):
                            st.session_state[f"copy_login_user_value_{login['id']}"] = login['usuario']
                            st.rerun()

                    if f"copy_login_user_value_{login['id']}" in st.session_state:
                        st.markdown(f'<script>navigator.clipboard.writeText("{st.session_state[f"copy_login_user_value_{login["id"]}"]}");</script>', unsafe_allow_html=True)
                        st.toast("Usuário copiado!", icon="📋")
                        del st.session_state[f"copy_login_user_value_{login['id']}"]

                    # Campo de Senha e botão de copiar
                    col_pass_input, col_pass_btn = st.columns([0.7, 0.3])
                    with col_pass_input:
                        st.text_input("Senha", value=login['senha'], key=f"login_pass_display_{login['id']}", disabled=True, type="password", label_visibility="collapsed")
                    with col_pass_btn:
                        if st.button("📋 Copiar Senha", key=f"copy_login_pass_btn_{login['id']}"):
                            st.session_state[f"copy_login_pass_value_{login['id']}"] = login['senha']
                            st.rerun()

                    if f"copy_login_pass_value_{login['id']}" in st.session_state:
                        st.markdown(f'<script>navigator.clipboard.writeText("{st.session_state[f"copy_login_pass_value_{login["id"]}"]}");</script>', unsafe_allow_html=True)
                        st.toast("Senha copiada!", icon="📋")
                        del st.session_state[f"copy_login_pass_value_{login['id']}"]

                    # Botão para resetar a senha
                    if st.button("🔄 Resetar Senha", key=f"reset_pass_btn_{login['id']}", type="primary"):
                        nova_senha = resetar_senha_admin(conn, login['id'])
                        if nova_senha:
                            # Guarda a nova senha em texto para exibir na mensagem de sucesso
                            st.session_state[f"nova_senha_{login['id']}"] = nova_senha
                            # Força o recarregamento da página para buscar os dados atualizados do banco
                            st.rerun()

                    # Exibe a nova senha gerada após o reset
                    if f"nova_senha_{login['id']}" in st.session_state:
                        st.success(f"Nova senha para **{login['usuario']}**: `{st.session_state[f'nova_senha_{login["id"]}']}` (copie e guarde em local seguro)")
                        # Limpa a chave da sessão para não mostrar a mensagem novamente
                        del st.session_state[f"nova_senha_{login['id']}"]

    # ==============================================================================
    # ABA 18: Registro de Peças
    # ==============================================================================
    with tab18:
        render_registro_de_pecas(conn)