import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# Configuração estrita da página
st.set_page_config(page_title="Lead Machine Pro", layout="wide")

# --- DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    /* Estilização Geral */
    .stApp { background-color: #0b0e11; font-family: 'Inter', sans-serif; }
    
    /* Tutorial de Boas-vindas Estilizado */
    .welcome-card {
        background-color: #161b22;
        padding: 40px;
        border-radius: 8px;
        border-left: 5px solid #00a884;
        margin-bottom: 30px;
    }
    .welcome-title { color: #ffffff; font-size: 24px; font-weight: 700; margin-bottom: 10px; }
    .welcome-text { color: #8b949e; font-size: 16px; line-height: 1.6; }

    /* Botões Profissionais */
    div.stButton > button {
        background-color: #00a884;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover { background-color: #008f6f; border: none; color: white; }

    /* Cards de Métricas */
    .metric-container {
        background-color: #161b22;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #ffffff; }
    .metric-label { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }

    /* Inputs e Áreas de Texto */
    .stTextArea textarea, .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 4px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        font-weight: 500;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #00a884; border-bottom: 2px solid #00a884 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTERFACE ---
if "primeiro_acesso" not in st.session_state:
    st.session_state.primeiro_acesso = True

# Tutorial de Entrada
if st.session_state.primeiro_acesso:
    st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">Bem-vindo à Operação</div>
            <div class="welcome-text">
                Otimize sua prospecção seguindo o fluxo de trabalho integrado:<br><br>
                1. Módulo de busca: Extraia os dados brutos da URL desejada.<br>
                2. Processamento: Gere o arquivo de exportação consolidado.<br>
                3. Operação de disparo: Realize os contatos via interface otimizada.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Iniciar Sistema"):
        st.session_state.primeiro_acesso = False
        st.rerun()
    st.stop()

# --- CONTEÚDO PRINCIPAL ---
st.markdown("<h1 style='color: white; font-size: 28px; margin-bottom: 30px;'>Gerenciador de Leads</h1>", unsafe_allow_html=True)

# Layout de Colunas Superiores (Métricas)
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div class="metric-container"><div class="metric-label">Total de Registros</div><div class="metric-value">0</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-container"><div class="metric-label">Contatos Realizados</div><div class="metric-value">0</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-container"><div class="metric-label">Taxa de Operação</div><div class="metric-value">0%</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navegação
tab_extract, tab_op = st.tabs(["Extração via URL", "Gestão de Disparos"])

with tab_extract:
    st.markdown("<h3 style='font-size: 18px; color: #8b949e;'>Configuração de Busca</h3>", unsafe_allow_html=True)
    url_input = st.text_input("Endereço de destino", placeholder="Insira a URL para mineração de dados...")
    
    c1, c2 = st.columns([1, 4])
    with c1:
        st.button("Executar Busca")

with tab_op:
    st.markdown("<h3 style='font-size: 18px; color: #8b949e;'>Importação de Base</h3>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload de arquivo CSV", label_visibility="collapsed")
    
    if uploaded:
        st.success("Base de dados importada com sucesso.")
        # Lógica de exibição de lista com status PENDENTE / CHAMADO usando CSS sóbrio