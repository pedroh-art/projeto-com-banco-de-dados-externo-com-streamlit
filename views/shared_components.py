# views/shared_components.py
import streamlit as st
import base64
import os
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
from models.banco import (
    listar_itens, adicionar_item, excluir_item, total_preco, totalizar_dinheiro_atual, atualizar_dinheiro_atual, registrar_transacao, listar_transacoes, excluir_transacao
)

def carregar_imagem_local(caminho_arquivo):
    """
    Lê uma imagem local do repositório e converte para Base64 para uso em tags HTML <img>.
    Exemplo de uso: <img src="{carregar_imagem_local('assets/logo.png')}" />
    """
    if not os.path.exists(caminho_arquivo):
        return ""
    
    with open(caminho_arquivo, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
        
    ext = caminho_arquivo.split('.')[-1].lower()
    mime_type = f"image/{ext}" if ext != 'svg' else "image/svg+xml"
    
    return f"data:{mime_type};base64,{encoded}"

# --- Configuração de Logos e Temporadas ---
# Fallback logo (Dino Tech) - Base64 padrão caso a imagem local não exista


# Tenta carregar o logo local, se não existir, usa o base64 padrão (fallback)
LOGO_LOCAL = carregar_imagem_local("images/LOGO DO TIME.png")
LOGO_DINO_TECH = LOGO_LOCAL
UNEARTHED = carregar_imagem_local("images/UNEARTHED.png")
MASTERPIECE = carregar_imagem_local("images/MASTERPIECE.png")
SUPERPOWERED = carregar_imagem_local("images/SUPERPOWERED.png") or "https://firstinspiresst01.blob.core.windows.net/first-energize/fll-challenge/fll-challenge-superpowered-logo-horiz-rgb.png"
CARGO_CONNECT = carregar_imagem_local("images/CARGO CONNECT.jpg")
RePLAY = carregar_imagem_local("images/RePLAY.png")
CITY_SHAPER = carregar_imagem_local("images/CITY SHAPER.png")
INTO_ORBIT = carregar_imagem_local("images/INTO ORBIT.png")
HYDRO_DYNAMICS = carregar_imagem_local("images/HYDRO DYNAMICS.png")
ANIMAL_ALLIES = carregar_imagem_local("images/ANIMAL ALLIES.png")
TRASH_TREK = carregar_imagem_local("images/TRASH TREK.png")
submerged = carregar_imagem_local("images/submerged logo.png")

LOGOS_TEMPORADAS = {
    "UNEARTHED (2025-2026)": f"{UNEARTHED}",
    "SUBMERGED (2024-2025)": f"{submerged}",
    "MASTERPIECE (2023-2024)": f"{MASTERPIECE}",
    "SUPERPOWERED (2022-2023)": f"{SUPERPOWERED}",
    "CARGO CONNECT (2021-2022)": f"{CARGO_CONNECT}",
    "RePLAY (2020-2021)": f"{RePLAY}",
    "CITY SHAPER (2019-2020)": f"{CITY_SHAPER}",
    "INTO ORBIT (2018-2019)": f"{INTO_ORBIT}",
    "HYDRO DYNAMICS (2017-2018)": f"{HYDRO_DYNAMICS}",
    "ANIMAL ALLIES (2016-2017)": f"{ANIMAL_ALLIES}",
    "TRASH TREK (2015-2016)": f"{TRASH_TREK}"
}

def get_current_logo():
    """Retorna a URL do logo atual baseado no estado da sessão (Modo Equipe ou Temporada)."""
    # Se o modo equipe estiver ativo, força o logo da Dino Tech
    if st.session_state.get("modo_equipe"):
        return LOGO_DINO_TECH
    
    # Se o modo temporada estiver ativo, retorna o logo da temporada selecionada
    if st.session_state.get("modo_temporada_ativo"):
        tema = st.session_state.get("tema_fll_selecionado")
        return LOGOS_TEMPORADAS.get(tema, LOGO_DINO_TECH)
    
    # Padrão
    return LOGO_DINO_TECH

def inject_canva_css():
    """Injeta CSS global estilo Canva AI e gerencia os Modos Visuais (Equipe e Todas as Temporadas FLL)."""
    
    # --- Inicialização de Estados ---
    if "modo_equipe" not in st.session_state:
        st.session_state.modo_equipe = False
    if "modo_temporada_ativo" not in st.session_state:
        st.session_state.modo_temporada_ativo = False
    if "tema_fll_selecionado" not in st.session_state:
        st.session_state.tema_fll_selecionado = "SUBMERGED (2024-2025)"

    # --- Definição das Temporadas (Pesquisa Completa FLL) ---
    # Dicionário com paletas de cores baseadas na identidade visual de cada temporada
    TEMPORADAS = {
        "UNEARTHED (2025-2026)": {
            "primary": "#4DB6AC", "secondary": "#8D6E63", "highlight": "#FF7043",
            "bg": "#1B1816", "card": "#2E2824", "sidebar": "#120F0E",
            "gradient": "linear-gradient(135deg, #1B1816 0%, #2E2824 100%)"
        },
        "SUBMERGED (2024-2025)": {
            "primary": "#0097D7", "secondary": "#005EB8", "highlight": "#FF0066",
            "bg": "#001233", "card": "#002244", "sidebar": "#000A1F", 
            "gradient": "linear-gradient(180deg, #001233 0%, #003366 100%)"
        },
        "MASTERPIECE (2023-2024)": {
            "primary": "#F05A28", "secondary": "#632CA6", "highlight": "#00AEEF",
            "bg": "#1A1A1A", "card": "#2D2D2D", "sidebar": "#121212", 
            "gradient": "linear-gradient(135deg, #1A1A1A 0%, #2D1030 100%)"
        },
        "SUPERPOWERED (2022-2023)": {
            "primary": "#FDB913", "secondary": "#00AEEF", "highlight": "#ED1C24",
            "bg": "#2C2C2C", "card": "#383838", "sidebar": "#202020", 
            "gradient": "repeating-linear-gradient(45deg, #2C2C2C, #2C2C2C 10px, #333333 10px, #333333 20px)"
        },
        "CARGO CONNECT (2021-2022)": {
            "primary": "#00A651", "secondary": "#005EB8", "highlight": "#FDB913",
            "bg": "#0D1F2D", "card": "#1A2F3D", "sidebar": "#051019", 
            "gradient": "linear-gradient(135deg, #0D1F2D 0%, #1A2F3D 100%)"
        },
        "RePLAY (2020-2021)": {
            "primary": "#ED1C24", "secondary": "#00AEEF", "highlight": "#8DC63F",
            "bg": "#1E1E1E", "card": "#252525", "sidebar": "#151515", 
            "gradient": "linear-gradient(to right, #1E1E1E, #2A2A2A)"
        },
        "CITY SHAPER (2019-2020)": {
            "primary": "#A6CE39", "secondary": "#58595B", "highlight": "#FDB913",
            "bg": "#202020", "card": "#303030", "sidebar": "#181818", 
            "gradient": "linear-gradient(135deg, #202020 0%, #303030 100%)"
        },
        "INTO ORBIT (2018-2019)": {
            "primary": "#662D91", "secondary": "#FDB913", "highlight": "#00AEEF",
            "bg": "#0B0B15", "card": "#151525", "sidebar": "#05050A", 
            "gradient": "radial-gradient(circle at center, #151525 0%, #0B0B15 100%)"
        },
        "HYDRO DYNAMICS (2017-2018)": {
            "primary": "#00AEEF", "secondary": "#005EB8", "highlight": "#FDB913",
            "bg": "#001525", "card": "#002535", "sidebar": "#000A15", 
            "gradient": "linear-gradient(180deg, #001525 0%, #002535 100%)"
        },
        "ANIMAL ALLIES (2016-2017)": {
            "primary": "#8DC63F", "secondary": "#FDB913", "highlight": "#5D4037",
            "bg": "#1A2515", "card": "#253020", "sidebar": "#10150A", 
            "gradient": "linear-gradient(135deg, #1A2515 0%, #253020 100%)"
        },
        "TRASH TREK (2015-2016)": {
            "primary": "#00A651", "secondary": "#005EB8", "highlight": "#FDB913",
            "bg": "#102015", "card": "#1A3020", "sidebar": "#0A150A", 
            "gradient": "linear-gradient(135deg, #102015 0%, #1A3020 100%)"
        }
    }

    with st.sidebar:
        st.markdown("### 🎨 Personalização")
        
        # Modo Equipe (Override)
        st.session_state.modo_equipe = st.toggle(
            "🦖 Modo Equipe: Dino Tech", 
            value=st.session_state.modo_equipe
        )
        
        st.markdown("#### 🏆 Temporadas FLL")
        
        # Toggle Geral de Temporada
        st.session_state.modo_temporada_ativo = st.toggle(
            "🌍 Modo Temporada FLL", 
            value=st.session_state.modo_temporada_ativo
        )
        
        if st.session_state.modo_temporada_ativo:
            st.session_state.tema_fll_selecionado = st.selectbox(
                "Escolha a Temporada:",
                options=list(TEMPORADAS.keys()),
                index=list(TEMPORADAS.keys()).index(st.session_state.tema_fll_selecionado) if st.session_state.tema_fll_selecionado in TEMPORADAS else 0
            )
        
        st.markdown("---")

    # --- Definição das Variáveis CSS ---
    if st.session_state.modo_equipe:
        # Paleta Dino Tech (Modo Equipe)
        vars_css = """
            --primary-color: #0057FF;    /* Azul Elétrico */
            --secondary-color: #00D4FF;  /* Ciano Tecnológico */
            --highlight-color: #0057FF;  /* Branco */
            --bg-color: #0A0E17;         /* Fundo Escuro Profundo */
            --card-bg: #111625;          /* Card Escuro */
            --text-color: #F0F6FC;       /* Texto Claro */
            --text-secondary: #8B949E;
            --border-radius: 16px;
            --shadow-color: rgba(0, 87, 255, 0.25);
            --sidebar-bg: #050910;       /* Sidebar Escura Dino */
            
            /* Variáveis Legadas FLL (Mapeadas) */
            --fll-dark-blue: #0057FF;
            --fll-light-blue: #00D4FF;
            --fll-red: #FF2E2E;
        """
        bg_gradient = "radial-gradient(circle at 15% 50%, rgba(0, 87, 255, 0.08) 0%, transparent 25%), radial-gradient(circle at 85% 30%, rgba(0, 212, 255, 0.08) 0%, transparent 25%)"
    elif st.session_state.modo_temporada_ativo:
        tema = TEMPORADAS[st.session_state.tema_fll_selecionado]
        vars_css = f"""
            --primary-color: {tema['primary']};
            --secondary-color: {tema['secondary']};
            --highlight-color: {tema['highlight']};
            --bg-color: {tema['bg']};
            --card-bg: {tema['card']};
            --text-color: #FFFFFF;
            --text-secondary: #E0E0E0;
            --border-radius: 16px;
            --shadow-color: rgba(0, 0, 0, 0.3);
            --sidebar-bg: {tema['sidebar']};
            
            /* Variáveis Legadas FLL */
            --fll-dark-blue: {tema['secondary']};
            --fll-light-blue: {tema['primary']};
            --fll-red: {tema['highlight']};
        """
        bg_gradient = tema['gradient']
    else:
        # Default FLL Dark
        vars_css = """
            --primary-color: #00AEEF;    /* Azul Claro FLL */
            --secondary-color: #003A8F;  /* Azul FLL */
            --highlight-color: #ED1C24;  /* Vermelho FLL */
            --bg-color: #001A3D;         /* Azul Escuro Profundo (FLL Dark) */
            --card-bg: #002855;          /* Azul Marinho Card */
            --text-color: #FFFFFF;       /* Texto Branco */
            --text-secondary: #E0E0E0;
            --border-radius: 12px;
            --shadow-color: rgba(0, 0, 0, 0.3);
            --sidebar-bg: #000F24;       /* Sidebar Escura Padrão */
            
            /* Variáveis Legadas FLL */
            --fll-dark-blue: #003A8F;
            --fll-light-blue: #00AEEF;
            --fll-red: #ED1C24;
        """
        bg_gradient = "linear-gradient(135deg, #001A3D 0%, #002855 100%)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {{
        {vars_css}
        --shadow-sm: 0 4px 6px var(--shadow-color);
        --shadow-md: 0 10px 15px var(--shadow-color);
    }}

    /* Global Reset */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: var(--text-color);
        background-color: var(--bg-color);
    }}

    /* Background Principal */
    .stApp {{
        background-color: var(--bg-color);
        background-image: {bg_gradient};
        background-attachment: fixed;
    }}

    /* Headings (Alto Contraste) */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: var(--primary-color);
        font-weight: 700;
    }}
    
    h1 {{
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Cards e Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        padding: 24px;
        margin-bottom: 20px;
    }}
    
    .stExpander {{
        background-color: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1rem;
    }}

    .streamlit-expanderHeader {{
        background-color: rgba(255, 255, 255, 0.05);
        color: var(--text-color) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .streamlit-expanderHeader:hover {{
        color: var(--primary-color) !important;
    }}

    /* Inputs (Dark Mode Force) */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {{
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: var(--text-color) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
    }}
    
    /* Labels */
    label, .stText, p {{
        color: var(--text-color) !important;
    }}

    /* Botões */
    .stButton > button {{
        background-color: var(--highlight-color);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        font-weight: 600;
        transition: transform 0.2s;
        box-shadow: var(--shadow-sm);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        background-color: var(--primary-color);
        box-shadow: var(--shadow-md);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg);
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    
    section[data-testid="stSidebar"] * {{
        color: var(--text-color) !important;
    }}

    /* Sidebar Radio Buttons (Navigation Cards) */
    section[data-testid="stSidebar"] .stRadio label {{
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        width: 100%;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }}

    section[data-testid="stSidebar"] .stRadio label:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        border-color: var(--primary-color);
        transform: translateX(5px);
    }}

    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
        background-color: var(--primary-color);
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px var(--shadow-color);
        border-color: var(--primary-color);
        font-weight: bold;
    }}
    
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) * {{
        color: #FFFFFF !important;
    }}

    /* Hide the radio circle */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.05);
        color: var(--text-secondary);
        border-radius: 8px 8px 0 0;
        border: none;
        padding: 8px 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: var(--primary-color) !important;
        color: #000 !important;
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: var(--highlight-color) !important;
    }}
    
    /* Custom Classes */
    .canva-title {{
        background: linear-gradient(90deg, var(--primary-color), var(--highlight-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 1rem;
    }}
    
    .user-info {{
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: var(--text-color);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        backdrop-filter: blur(5px);
    }}
    
    .simple-image {{
        display: block;
        margin: 20px auto;
        border-radius: 8px;
        max-width: 80%;
        transition: transform 0.3s;
    }}
    .simple-image:hover {{
        transform: scale(1.02);
    }}
    
    .canva-images {{
        display: block;
        margin: 0 auto;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        max-width: 90%;
        border: 2px solid var(--primary-color);
        padding: 5px;
        background: rgba(255,255,255,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

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

                if st.button("🗑️ Excluir Credencial", key=f"del_cred_{cred['id']}", type="primary", help="Remover esta credencial permanentemente"):
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
                    if st.button("🗑️", key=f"del_peca_{peca['id']}", help="Excluir esta peça do inventário"):
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
                    if st.button("🗑️ Excluir", key=f"del_missao_{missao['id']}", type="primary", help="Excluir esta missão"):
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
            if st.button("🗑️ Excluir Base do Robô", type="primary", help="Apagar o registro da base do robô"):
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
            missao_nome = (acessorio.get("missoes_tapete") or {}).get("nome", "Missão Desconhecida")
            with st.expander(f"**{acessorio['nome']}** (para: *{missao_nome}*)"):
                if acessorio['descricao']:
                    st.write(acessorio['descricao'])
                if acessorio['foto_url']:
                    st.image(acessorio['foto_url'], width=300)
                if not read_only:
                    if st.button("🗑️ Excluir Acessório", key=f"del_acessorio_{acessorio['id']}", type="primary", help="Remover este acessório"):
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
            missao_nome = (codigo.get("missoes_tapete") or {}).get("nome")
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
                    if st.button("🗑️ Excluir Código", key=f"del_codigo_{codigo['id']}", type="primary", help="Apagar este código da biblioteca"):
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
                if st.button("🗑️ Excluir Arquivo", key=f"del_arq_{arq['id']}", type="primary", help="Remover este arquivo do projeto"):
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
                        if st.button("🗑️", key=f"del_check_{item['id']}", help="Excluir este item do checklist"):
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
                        if st.button("🗑️ Excluir Registro", key=f"del_reuniao_{reuniao['id']}", type="primary", help="Apagar este registro de reunião"):
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
                        if st.button("🗑️ Excluir Registro", key=f"del_erro_{erro['id']}", type="primary", help="Apagar este registro de erro"):
                            excluir_erro_solucao(conn, erro['id'])
                            st.rerun()
def render_banco_da_dino_tech(conn, pode_editar=False):
    st.markdown("<h2 style='color:#6A5ACD;'>🏦 Banco da Dino-Tech</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🏷️ Itens Disponíveis", "💰 Total Gasto", "💸 Pagar Itens"])
    with tab1:
        if pode_editar:
            st.info("Gerencie os itens disponíveis no Banco da Dino-Tech. Adicione, remova e visualize os itens e seus preços.")
            st.markdown("---")
            add_itens = st.text_input("Nome do Item para Adicionar ao Banco da Dino-Tech")
            quantidade = st.number_input("Preço do item")
            if st.button("➕ Adicionar Item"):
                if add_itens.strip():
                    if adicionar_item(conn, add_itens, quantidade):
                        st.success(f"✅ Item '{add_itens}' adicionado com sucesso!")
                        st.rerun()
                        st.success(f"✅ Item '{add_itens}' adicionado com sucesso!")
                    else:
                        st.error("❌ Erro ao adicionar o item. Verifique se ele já não existe.")
                else:
                    st.warning("⚠️ O nome do item é obrigatório.")
        itens = listar_itens(conn)
        if not itens:
            st.info("Nenhum item no Banco da Dino-Tech ainda.")
        else:
            for item in itens:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{item['nome']}**")
                with col2:
                    st.markdown(f"R$ {item['preco']:.2f}")
                if pode_editar:    
                    with col3:
                        if st.button("🗑️", key=f"del_item_{item['id']}", help="Excluir este item do banco"):
                            excluir_item(conn, item['id'])
                            st.rerun()
                else:
                    st.markdown("")  # Coluna vazia para alinhamento                
    with tab2:
        st.info("Veja o total gasto com os itens do Banco da Dino-Tech.")
        total = total_preco(conn)
        din = totalizar_dinheiro_atual(conn)
        st.metric("Dinheiro Atual", f"R$ {din:.2f}")
        st.metric("Total a Gastar", f"R$ {total:.2f}")
        if pode_editar:
            total_dinheiro = st.number_input("Digite o total de dinheiro disponível", min_value=0.0, step=10.0)
            if st.button("Atualizar Total"):
                atualizar_dinheiro_atual(conn, total_dinheiro)
                st.success("✅ Total atualizado com sucesso!")
                st.rerun()
    with tab3:
        
        if pode_editar:
            st.info("Registre as transações de pagamento dos itens do Banco da Dino-Tech.")
            with st.expander("➕ Registrar Nova Transação"):
                with st.form("form_nova_transacao", clear_on_submit=True):
                    
                    tipo = st.selectbox("tipo de pagamento", options=["saida", "entrada"], format_func=lambda x: "💸 Saída" if x == "saida" else "💰 Entrada")
                    valor_pago = st.number_input("Valor Pago", min_value=0.0, step=1.0)
                    data_transacao = st.date_input("Data da Transação", value=datetime.date.today())
                    data_transacao = data_transacao.strftime("%Y-%m-%d")
                    descricao = st.text_area("Descrição da Transação")
                    
                    if st.form_submit_button("💾 Registrar Transação"):
                        if registrar_transacao(conn, tipo, valor_pago, descricao, data_transacao):
                            st.toast("✅ Transação registrada com sucesso!", icon="✅")
                        else:
                            st.toast("❌ Erro ao registrar a transação.", icon="❌")    
        listar_transacoes_list = listar_transacoes(conn)
        if not listar_transacoes_list:
            st.info("Nenhuma transação registrada.")
        else:
            for transacao in listar_transacoes_list:
                data_formatada = datetime.datetime.strptime(
                    transacao['data_criacao'],
                    "%Y-%m-%dT%H:%M:%S"
                    )
                item_info = next(
                (item for item in listar_itens(conn) if item['id'] == transacao['id']),
                None
            )

                item_nome = item_info['nome'] if item_info else "Item Desconhecido"
                with st.expander(f"**{data_formatada}** - {item_nome}"):
                    st.markdown(f"**Valor Pago:** R$ {transacao['valor']:.2f}")
                    if pode_editar:
                        if st.button("🗑️ Excluir Registro", key=f"del_transacao_{transacao['id']}", type="primary", help="Apagar este registro de transação"):
                            excluir_transacao(conn, transacao['id'])
                            st.rerun()
                    