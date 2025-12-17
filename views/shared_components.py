# views/shared_components.py
import streamlit as st
import datetime
from models.credencial import (
    criar_credencial, listar_credenciais, excluir_credencial
)
from models.peca import (
    registrar_peca, listar_pecas, atualizar_quantidade_peca, excluir_peca
)
from models.missao import (
    criar_missao, listar_missoes, atualizar_missao, atualizar_status_missao, excluir_missao
)
from models.estrategia import (
    salvar_base_robo, obter_base_robo, excluir_base_robo, adicionar_acessorio, listar_acessorios_por_missao, excluir_acessorio
)
from models.codigo import (
    salvar_codigo, listar_codigos_com_missao, excluir_codigo
)
from models.projeto_inovacao import (
    obter_dados_pi, salvar_dados_pi, adicionar_arquivo_pi, listar_arquivos_pi, excluir_arquivo_pi
)
from models.acompanhamento import (
    listar_itens_checklist, adicionar_item_checklist, atualizar_status_checklist, excluir_item_checklist,
    listar_reunioes, registrar_reuniao, excluir_reuniao,
    listar_erros_solucoes, registrar_erro_solucao, excluir_erro_solucao
)
from models.integrante import (
    listar_integrantes
)

def render_central_de_senhas(conn):
    """Renderiza a interface da Central de Senhas, que pode ser usada por admins e gestores."""
    st.markdown("<h2 style='color:#FF4500;'>🔑 Central de Senhas</h2>", unsafe_allow_html=True)
    st.warning("🔒 Esta área contém informações sensíveis. Acesso restrito.")

    with st.expander("➕ Adicionar Nova Credencial"):
        with st.form("form_nova_credencial", clear_on_submit=True):
            servico = st.text_input("Serviço (Ex: Instagram, Email da Equipe)")
            usuario = st.text_input("Usuário / Login / Email")
            senha = st.text_input("Senha", type="password")
            
            submitted = st.form_submit_button("💾 Salvar Credencial")
            if submitted:
                if servico.strip() and usuario.strip() and senha.strip():
                    if criar_credencial(conn, servico, usuario, senha):
                        st.success(f"✅ Credencial para '{servico}' salva com sucesso!")
                    else:
                        st.error("❌ Erro ao salvar a credencial.")
                else:
                    st.warning("⚠️ Todos os campos são obrigatórios.")

    st.markdown("---")
    st.subheader("🗂️ Credenciais Salvas")
    
    credenciais = listar_credenciais(conn)
    if not credenciais:
        st.info("Nenhuma credencial cadastrada ainda.")
    else:
        for cred in credenciais:
            with st.container(border=True):
                st.markdown(f"#### {cred['servico']}")

                # Campo de Usuário e botão de copiar
                col_user_input, col_user_btn = st.columns([0.7, 0.3])
                with col_user_input:
                    st.text_input("Usuário", value=cred['usuario'], key=f"user_display_{cred['id']}", disabled=True, label_visibility="collapsed")
                with col_user_btn:
                    if st.button("📋 Copiar Usuário", key=f"copy_user_btn_{cred['id']}"):
                        st.session_state[f"copy_user_value_{cred['id']}"] = cred['usuario']
                        st.rerun()

                if f"copy_user_value_{cred['id']}" in st.session_state:
                    st.markdown(f'<script>navigator.clipboard.writeText("{st.session_state[f"copy_user_value_{cred["id"]}"]}"); alert("Usuário copiado!");</script>', unsafe_allow_html=True)
                    del st.session_state[f"copy_user_value_{cred['id']}"]

                # Campo de Senha e botão de copiar
                col_pass_input, col_pass_btn = st.columns([0.7, 0.3])
                with col_pass_input:
                    st.text_input("Senha", value=cred['senha'], key=f"pass_display_{cred['id']}", disabled=True, type="password", label_visibility="collapsed")
                with col_pass_btn:
                    if st.button("📋 Copiar Senha", key=f"copy_pass_btn_{cred['id']}"):
                        st.session_state[f"copy_pass_value_{cred['id']}"] = cred['senha']
                        st.rerun()

                if f"copy_pass_value_{cred['id']}" in st.session_state:
                    st.markdown(f'<script>navigator.clipboard.writeText("{st.session_state[f"copy_pass_value_{cred["id"]}"]}"); alert("Senha copiada!");</script>', unsafe_allow_html=True)
                    del st.session_state[f"copy_pass_value_{cred['id']}"]

                if st.button("🗑️ Excluir Credencial", key=f"del_cred_{cred['id']}", type="primary"):
                    if excluir_credencial(conn, cred['id']):
                        st.success(f"✅ Credencial '{cred['servico']}' excluída.")
                        st.rerun()

def render_registro_de_pecas(conn, read_only=False):
    """Renderiza a interface de Registro de Peças, com modo de edição ou somente leitura."""
    st.markdown("<h2 style='color:#008080;'>📦 Registro de Peças e Equipamentos</h2>", unsafe_allow_html=True)
    
    if not read_only:
        st.info("Use este painel para controlar o inventário de peças do robô e outros materiais.")
        with st.expander("➕ Registrar Nova Peça"):
            with st.form("form_nova_peca", clear_on_submit=True):
                nome_peca = st.text_input("Nome da Peça (Ex: Motor Grande, Sensor de Cor)")
                qtd_peca = st.number_input("Quantidade Inicial", min_value=0, step=1)
                
                submitted = st.form_submit_button("📥 Registrar Peça")
                if submitted:
                    if nome_peca.strip():
                        if registrar_peca(conn, nome_peca, qtd_peca):
                            st.success(f"✅ Peça '{nome_peca}' registrada com sucesso!")
                        else:
                            st.error("❌ Erro ao registrar a peça. Verifique se ela já não existe.")
                    else:
                        st.warning("⚠️ O nome da peça é obrigatório.")
    else:
        st.info("Este é o inventário de peças e equipamentos da equipe. Apenas o 'Responsável pelos Materiais' pode fazer alterações.")

    st.markdown("---")
    st.subheader("📋 Inventário Atual")
    
    pecas = listar_pecas(conn)
    if not pecas:
        st.info("Nenhuma peça registrada no inventário.")
    else:
        # Cabeçalho da tabela
        col1, col2, _ = st.columns([2, 1, 1])
        col1.markdown("**Peça**")
        col2.markdown("**Quantidade**")

        for peca in pecas:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{peca['nome']}**")
            with col2:
                if read_only:
                    st.markdown(f"{peca['quantidade']}")
                else:
                    nova_qtd = st.number_input("Qtd.", value=peca['quantidade'], min_value=0, step=1, key=f"qtd_{peca['id']}", label_visibility="collapsed")
                    if nova_qtd != peca['quantidade']:
                        atualizar_quantidade_peca(conn, peca['id'], nova_qtd)
                        st.rerun()
            with col3:
                if not read_only:
                    if st.button("🗑️", key=f"del_peca_{peca['id']}", help="Excluir peça"):
                        excluir_peca(conn, peca['id'])
                        st.rerun()

def render_missoes_tapete(conn, read_only=False):
    """Renderiza a interface para gerenciamento de missões do tapete."""
    st.markdown("### 🎯 Missões do Tapete")
    
    status_map = {
        "nao_iniciada": "🔴 Não Iniciada",
        "em_teste": "🟡 Em Teste",
        "concluida": "🟢 Concluída"
    }
    status_options = list(status_map.keys())

    if not read_only:
        with st.expander("➕ Adicionar Nova Missão"):
            with st.form("form_nova_missao", clear_on_submit=True):
                nome = st.text_input("Nome da Missão")
                pontuacao = st.number_input("Pontuação", min_value=0, step=5)
                descricao = st.text_area("Descrição/Requisitos")
                
                submitted = st.form_submit_button("📥 Registrar Missão")
                if submitted:
                    if nome.strip():
                        if criar_missao(conn, nome, pontuacao, descricao):
                            st.success(f"✅ Missão '{nome}' registrada!")
                        else:
                            st.error("❌ Erro ao registrar missão. Verifique se o nome já existe.")
                    else:
                        st.warning("⚠️ O nome da missão é obrigatório.")

    missoes = listar_missoes(conn)
    if not missoes:
        st.info("Nenhuma missão cadastrada ainda.")
    else:
        total_pontos = sum(m['pontuacao'] for m in missoes if m['status'] == 'concluida')
        st.metric("Pontuação Total (Missões Concluídas)", f"{total_pontos} pontos")
        st.markdown("---")

        for missao in missoes:
            with st.container(border=True):
                col_nome, col_pontos, col_status = st.columns([2, 1, 1.5])
                
                with col_nome:
                    st.markdown(f"**{missao['nome']}**")
                    if missao['descricao']:
                        st.caption(missao['descricao'])
                
                with col_pontos:
                    st.markdown(f"**{missao['pontuacao']} pts**")

                with col_status:
                    if read_only:
                        st.markdown(status_map.get(missao['status'], "Desconhecido"))
                    else:
                        # Encontra o índice do status atual para o selectbox
                        current_status_index = status_options.index(missao['status']) if missao['status'] in status_options else 0
                        novo_status = st.selectbox(
                            "Status",
                            options=status_options,
                            format_func=lambda x: status_map[x],
                            index=current_status_index,
                            key=f"status_{missao['id']}",
                            label_visibility="collapsed"
                        )
                        if novo_status != missao['status']:
                            atualizar_status_missao(conn, missao['id'], novo_status)
                            st.rerun()
                
                if not read_only:
                    if st.button("🗑️ Excluir", key=f"del_missao_{missao['id']}", type="primary"):
                        excluir_missao(conn, missao['id'])
                        st.rerun()

def render_estrategia_robo(conn, read_only=False):
    """Renderiza a interface para a estratégia do robô."""
    
    # --- Seção da Base do Robô ---
    st.markdown("### 🛠️ Base Utilizada")
    base_robo = obter_base_robo(conn)

    if not read_only:
        with st.form("form_base_robo"):
            nome_base = st.text_input("Nome da Base", value=base_robo['nome_base'] if base_robo else "")
            desc_base = st.text_area("Descrição da Base", value=base_robo['descricao'] if base_robo else "")
            foto_base = st.file_uploader("Foto da Base (opcional)", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("💾 Salvar Base"):
                if salvar_base_robo(conn, nome_base, desc_base, foto_base):
                    st.success("✅ Base do robô salva com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar a base do robô.")

    if base_robo:
        st.markdown(f"**Nome:** {base_robo['nome_base']}")
        if base_robo['descricao']:
            st.markdown(f"**Descrição:** {base_robo['descricao']}")
        if base_robo['foto_url']:
            st.image(base_robo['foto_url'], width=400)
        
        if not read_only:
            st.markdown("---")
            if st.button("🗑️ Excluir Base do Robô", type="primary"):
                if excluir_base_robo(conn):
                    st.success("✅ Base do robô excluída com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao excluir a base do robô.")
    else:
        st.info("Nenhuma base de robô foi definida ainda.")

    st.markdown("---")

    # --- Seção de Acessórios por Missão ---
    st.markdown("### 🧩 Acessórios por Missão")
    missoes = listar_missoes(conn)

    if not read_only:
        with st.expander("➕ Adicionar Novo Acessório"):
            with st.form("form_novo_acessorio", clear_on_submit=True):
                if not missoes:
                    st.warning("Cadastre as missões primeiro para poder adicionar acessórios.")
                else:
                    missao_selecionada_id = st.selectbox(
                        "Para qual missão é este acessório?",
                        options=[m['id'] for m in missoes],
                        format_func=lambda x: next((m['nome'] for m in missoes if m['id'] == x), "N/A")
                    )
                    nome_acessorio = st.text_input("Nome do Acessório")
                    desc_acessorio = st.text_area("Descrição do Acessório")
                    foto_acessorio = st.file_uploader("Foto do Acessório (opcional)", type=["jpg", "jpeg", "png"])

                    if st.form_submit_button("📥 Adicionar Acessório"):
                        if nome_acessorio.strip() and missao_selecionada_id:
                            if adicionar_acessorio(conn, nome_acessorio, desc_acessorio, missao_selecionada_id, foto_acessorio):
                                st.success("✅ Acessório adicionado!")
                            else:
                                st.error("❌ Erro ao adicionar acessório.")
                        else:
                            st.warning("⚠️ O nome e a missão são obrigatórios.")
    
    acessorios = listar_acessorios_por_missao(conn)
    if not acessorios:
        st.info("Nenhum acessório cadastrado.")
    else:
        for acessorio in acessorios:
            missao_nome = acessorio.get("missoes_tapete", {}).get("nome", "Missão Desconhecida")
            with st.expander(f"**{acessorio['nome']}** (para: *{missao_nome}*)"):
                if acessorio['descricao']:
                    st.write(acessorio['descricao'])
                if acessorio['foto_url']:
                    st.image(acessorio['foto_url'], width=300)
                if not read_only:
                    if st.button("🗑️ Excluir Acessório", key=f"del_acessorio_{acessorio['id']}", type="primary"):
                        excluir_acessorio(conn, acessorio['id'])
                        st.rerun()

def render_biblioteca_codigos(conn, read_only=False):
    """Renderiza a interface para a biblioteca de códigos."""
    st.markdown("### 🐍 Biblioteca de Códigos")
    missoes = listar_missoes(conn)

    if not read_only:
        with st.expander("➕ Adicionar Novo Código"):
            with st.form("form_novo_codigo", clear_on_submit=True):
                nome_codigo = st.text_input("Nome do Programa (Ex: Saída da Base, Missão 5)")
                
                missao_opcoes = {m['id']: m['nome'] for m in missoes}
                missao_opcoes[None] = "(Nenhuma)" # Adiciona opção para não vincular
                
                missao_selecionada_id = st.selectbox(
                    "Vincular a qual missão? (opcional)",
                    options=list(missao_opcoes.keys()),
                    format_func=lambda x: missao_opcoes[x]
                )

                desc_codigo = st.text_area("Descrição (o que este código faz?)")
                codigo_python = st.text_area("Cole o código Python aqui", height=300, placeholder="import spike\n\n...")
                video_teste = st.file_uploader("Vídeo/GIF de teste (opcional)", type=["mp4", "mov", "gif"])

                if st.form_submit_button("💾 Salvar Código"):
                    if nome_codigo.strip() and codigo_python.strip():
                        if salvar_codigo(conn, nome_codigo, desc_codigo, codigo_python, missao_selecionada_id, video_teste):
                            st.success("✅ Código salvo na biblioteca!")
                        else:
                            st.error("❌ Erro ao salvar o código.")
                    else:
                        st.warning("⚠️ O nome e o código são obrigatórios.")

    codigos = listar_codigos_com_missao(conn)
    if not codigos:
        st.info("Nenhum código foi adicionado à biblioteca ainda.")
    else:
        for codigo in codigos:
            missao_nome = codigo.get("missoes_tapete", {}).get("nome")
            expander_title = f"**{codigo['nome']}**"
            if missao_nome:
                expander_title += f" (para: *{missao_nome}*)"

            with st.expander(expander_title):
                if codigo['descricao']:
                    st.markdown("**Descrição:**")
                    st.write(codigo['descricao'])
                
                st.markdown("**Código:**")
                st.code(codigo['codigo'], language='python')

                if codigo['video_url']:
                    st.markdown("**Vídeo de Teste:**")
                    st.video(codigo['video_url'])
                
                if not read_only:
                    if st.button("🗑️ Excluir Código", key=f"del_codigo_{codigo['id']}", type="primary"):
                        if excluir_codigo(conn, codigo['id']):
                            st.success("✅ Código excluído com sucesso!")
                            st.rerun()

def render_projeto_inovacao(conn, read_only=False):
    """Renderiza a interface para o Projeto de Inovação."""
    st.markdown("<h2 style='color:#FF69B4;'>🧩 Projeto de Inovação</h2>", unsafe_allow_html=True)
    
    dados_pi = obter_dados_pi(conn) or {}

    # Campos de texto para as seções do projeto
    campos = {
        "tema_temporada": "🌟 Tema da Temporada",
        "problema_identificado": "❓ Problema Identificado",
        "solucao_proposta": "💡 Solução Proposta",
        "pesquisa_realizada": "📚 Pesquisa Realizada",
        "feedback_especialistas": "🗣️ Feedback de Especialistas",
        "evolucao_projeto": "📈 Evolução do Projeto (Versionamento)"
    }

    dados_editados = {}
    for chave, titulo in campos.items():
        valor_atual = dados_pi.get(chave, "")
        if read_only:
            with st.expander(titulo, expanded=True):
                st.markdown(valor_atual if valor_atual else "_Não preenchido_")
        else:
            with st.expander(titulo, expanded=True):
                dados_editados[chave] = st.text_area(
                    "Conteúdo", 
                    value=valor_atual, 
                    key=f"pi_{chave}", 
                    height=200,
                    label_visibility="collapsed"
                )

    if not read_only:
        if st.button("💾 Salvar Alterações no Projeto", type="primary"):
            if salvar_dados_pi(conn, dados_editados):
                st.success("✅ Projeto de Inovação atualizado!")
                st.rerun()
            else:
                st.error("❌ Erro ao salvar o projeto.")

    st.markdown("---")

    # Seção de Arquivos
    st.markdown("### 📂 Arquivos do Projeto")
    if not read_only:
        with st.expander("➕ Adicionar Novo Arquivo"):
            with st.form("form_novo_arquivo_pi", clear_on_submit=True):
                nome_arquivo = st.text_input("Nome do Arquivo (Ex: Apresentação V1, Artigo Científico)")
                desc_arquivo = st.text_area("Descrição (opcional)")
                arquivo_upload = st.file_uploader("Selecione o arquivo (PDF, PPTX, DOCX, PNG, JPG)", type=["pdf", "pptx", "docx", "png", "jpg", "jpeg"])

                if st.form_submit_button("📤 Enviar Arquivo"):
                    if nome_arquivo.strip() and arquivo_upload:
                        if adicionar_arquivo_pi(conn, nome_arquivo, desc_arquivo, arquivo_upload):
                            st.success("✅ Arquivo enviado com sucesso!")
                        else:
                            st.error("❌ Erro ao enviar o arquivo.")
                    else:
                        st.warning("⚠️ O nome e o arquivo são obrigatórios.")

    arquivos = listar_arquivos_pi(conn)
    if not arquivos:
        st.info("Nenhum arquivo foi adicionado ao projeto ainda.")
    else:
        for arq in arquivos:
            st.markdown(f"**[{arq['nome_arquivo']}]({arq['url_arquivo']})**")
            if arq['descricao']:
                st.caption(arq['descricao'])
            if not read_only:
                if st.button("🗑️ Excluir Arquivo", key=f"del_arq_{arq['id']}", type="primary"):
                    if excluir_arquivo_pi(conn, arq['id'], arq['url_arquivo']):
                        st.success("✅ Arquivo excluído!")
                        st.rerun()
            st.markdown("---")

def render_controle_acompanhamento(conn, can_edit_checklist=False, can_edit_reunioes=False, can_edit_erros=False):
    """Renderiza a interface para o módulo de Controle e Acompanhamento."""
    st.markdown("<h2 style='color:#6A5ACD;'>📊 Controle e Acompanhamento</h2>", unsafe_allow_html=True)

    tab_check, tab_reuniao, tab_erros = st.tabs([
        "📋 Checklist da Competição", 
        "🤝 Registro de Reuniões", 
        "🐞 Lista de Erros e Soluções"
    ])

    integrantes_lista = listar_integrantes(conn)
    nomes_dict = {nome: id for id, nome in integrantes_lista}

    # --- Checklist da Competição ---
    with tab_check:
        st.markdown("### 📋 Checklist da Competição")
        if can_edit_checklist:
            with st.expander("➕ Adicionar Item ao Checklist"):
                with st.form("form_novo_item_check", clear_on_submit=True):
                    texto_item = st.text_input("Novo item para o checklist")
                    responsavel = st.selectbox("Responsável (opcional)", ["(Ninguém)"] + list(nomes_dict.keys()))
                    
                    if st.form_submit_button("📥 Adicionar Item"):
                        if texto_item.strip():
                            resp_id = nomes_dict.get(responsavel)
                            if adicionar_item_checklist(conn, texto_item, resp_id):
                                st.success("✅ Item adicionado ao checklist!")
                            else:
                                st.error("❌ Erro ao adicionar item.")
                        else:
                            st.warning("⚠️ O texto do item é obrigatório.")
        
        itens = listar_itens_checklist(conn)
        if not itens:
            st.info("Nenhum item no checklist ainda.")
        else:
            for item in itens:
                col1, col2, col3 = st.columns([0.1, 2, 0.5])
                with col1:
                    novo_status = st.checkbox("", value=item['status'], key=f"check_{item['id']}", disabled=not can_edit_checklist)
                    if novo_status != item['status']:
                        atualizar_status_checklist(conn, item['id'], novo_status)
                        st.rerun()
                with col2:
                    integrante_info = item.get('integrantes')
                    responsavel_nome = integrante_info.get('nome', 'Ninguém') if integrante_info else 'Ninguém'
                    st.markdown(f"**{item['item_texto']}** (Responsável: *{responsavel_nome}*)")
                with col3:
                    if can_edit_checklist:
                        if st.button("🗑️", key=f"del_check_{item['id']}", help="Excluir item"):
                            excluir_item_checklist(conn, item['id'])
                            st.rerun()

    # --- Registro de Reuniões ---
    with tab_reuniao:
        st.markdown("### 🤝 Registro de Reuniões")
        if can_edit_reunioes:
            with st.expander("➕ Registrar Nova Reunião"):
                with st.form("form_nova_reuniao", clear_on_submit=True):
                    data_reuniao = st.date_input("Data da Reunião")
                    pauta = st.text_area("Pauta da Reunião")
                    participantes_nomes = [nome for _, nome in integrantes_lista]
                    participantes = st.multiselect("Participantes", options=participantes_nomes)
                    decisoes = st.text_area("Decisões Tomadas e Próximos Passos")

                    if st.form_submit_button("💾 Registrar Reunião"):
                        if registrar_reuniao(conn, data_reuniao, pauta, ", ".join(participantes), decisoes):
                            st.success("✅ Reunião registrada com sucesso!")
                        else:
                            st.error("❌ Erro ao registrar reunião.")
        
        reunioes = listar_reunioes(conn)
        if not reunioes:
            st.info("Nenhuma reunião registrada.")
        else:
            for reuniao in reunioes:
                data_formatada = datetime.datetime.strptime(reuniao['data_reuniao'], "%Y-%m-%d").strftime("%d/%m/%Y")
                with st.expander(f"**Reunião de {data_formatada}**"):
                    st.markdown(f"**Participantes:** {reuniao.get('participantes', 'N/A')}")
                    st.markdown(f"**Pauta:**\n{reuniao.get('pauta', 'N/A')}")
                    st.markdown(f"**Decisões:**\n{reuniao.get('decisoes', 'N/A')}")
                    if can_edit_reunioes:
                        if st.button("🗑️ Excluir Registro", key=f"del_reuniao_{reuniao['id']}", type="primary"):
                            excluir_reuniao(conn, reuniao['id'])
                            st.rerun()

    # --- Lista de Erros e Soluções ---
    with tab_erros:
        st.markdown("### 🐞 Lista de Erros e Soluções")
        if can_edit_erros:
            with st.expander("➕ Registrar Novo Erro/Solução"):
                with st.form("form_novo_erro", clear_on_submit=True):
                    data_erro = st.date_input("Data da Ocorrência")
                    erro_desc = st.text_area("Descrição do Erro (O que aconteceu?)")
                    solucao_desc = st.text_area("Solução Aplicada (Como foi resolvido?)")
                    responsavel = st.selectbox("Quem resolveu? (opcional)", ["(Ninguém)"] + list(nomes_dict.keys()))

                    if st.form_submit_button("💾 Registrar"):
                        if erro_desc.strip():
                            resp_id = nomes_dict.get(responsavel)
                            if registrar_erro_solucao(conn, erro_desc, solucao_desc, resp_id, data_erro):
                                st.success("✅ Registro de erro/solução salvo!")
                            else:
                                st.error("❌ Erro ao salvar registro.")
                        else:
                            st.warning("⚠️ A descrição do erro é obrigatória.")

        erros = listar_erros_solucoes(conn)
        if not erros:
            st.info("Nenhum erro registrado. Ótimo trabalho!")
        else:
            for erro in erros:
                data_formatada = datetime.datetime.strptime(erro['data_ocorrido'], "%Y-%m-%d").strftime("%d/%m/%Y")
                integrante_info = erro.get('integrantes')
                responsavel_nome = integrante_info.get('nome', 'N/A') if integrante_info else 'N/A'
                with st.expander(f"**{data_formatada}** - Resolvido por: *{responsavel_nome}*"):
                    st.error(f"**Erro:** {erro['erro_descricao']}")
                    st.success(f"**Solução:** {erro['solucao_aplicada']}")
                    if can_edit_erros:
                        if st.button("🗑️ Excluir Registro", key=f"del_erro_{erro['id']}", type="primary"):
                            excluir_erro_solucao(conn, erro['id'])
                            st.rerun()