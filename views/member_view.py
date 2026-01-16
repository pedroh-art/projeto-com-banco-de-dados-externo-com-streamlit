# views/member_view.py
import streamlit as st
from models.reclamacao import criar_reclamacao

def render_member_view(conn, regras):
    """
    Renderiza a interface para membros logados.
    """
    st.set_page_config(page_title="Painel do Membro - Dino-Tech", page_icon="🦖", layout="centered")
    st.markdown(f"<h1 style='color:#FFD700; text-align:center;'>🚀 Painel do Membro - Dino-Tech 🚀</h1>", unsafe_allow_html=True)
    
    st.markdown(f"👤 Logado como: **{st.session_state.usuario_logado}**")
    if st.button("🔒 Sair", key="sair_membro"):
        st.session_state.usuario_logado = None
        st.session_state.tipo_usuario = None
        st.rerun()

    # Abas para a visão do membro
    tab1, tab2 = st.tabs([
        "📜 Regras e Direitos", 
        "🗣️ Enviar Reclamação Anônima"
    ])

    # ==============================================================================
    # ABA 1: Regras e Direitos
    # ==============================================================================
    with tab1:
        st.markdown("<h2 style='color:#32CD32;'>📜 Direitos gerais da equipe</h2>", unsafe_allow_html=True)
        direitos = regras.get("direitos_gerais", [])
        if direitos:
            for d in direitos:
                st.markdown(f"✅ {d}")
        else:
            st.info("Nenhum direito geral definido.")

        st.markdown("---")
        st.markdown("<h2 style='color:#1E90FF;'>📑 Regras gerais da equipe</h2>", unsafe_allow_html=True)
        regras_gerais = regras.get("regras_gerais", [])
        if regras_gerais:
            for r in regras_gerais:
                st.markdown(f"⚖️ {r}")
        else:
            st.info("Nenhuma regra geral definida.")

    # ==============================================================================
    # ABA 2: Enviar Reclamação Anônima
    # ==============================================================================
    with tab2:
        st.markdown("<h2 style='color:#FF6347;'>🗣️ Caixa de Reclamações Anônimas</h2>", unsafe_allow_html=True)
        st.warning("**Atenção:** Sua identidade será mantida em sigilo. Use este espaço com responsabilidade para nos ajudar a melhorar.")
        
        texto_reclamacao = st.text_area(
            "Escreva sua reclamação ou sugestão aqui. Seja claro e objetivo.",
            height=200,
            key="texto_reclamacao"
        )
        
        if st.button("✉️ Enviar Reclamação Anônima", key="btn_enviar_reclamacao"):
            if texto_reclamacao.strip():
                if criar_reclamacao(conn, texto_reclamacao):
                    st.success("✅ Sua reclamação foi enviada com sucesso e anonimamente!")
                else:
                    st.error("❌ Ocorreu um erro ao enviar sua reclamação. Tente novamente.")
            else:
                st.warning("⚠️ O campo de texto não pode estar vazio.")
