import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuracao da Pagina
st.set_page_config(page_title="Extrator Lead Pro", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    .metric-card {
        background-color: #161b22; padding: 20px; border-radius: 4px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: 700; color: #ffffff; }
    .metric-lab { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    div.stButton > button {
        background-color: #00a884; color: white; border: none;
        padding: 8px 20px; border-radius: 4px; font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover { background-color: #008f6f; color: white; }
    .pix-box {
        background-color: #1d2129;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #25D366;
        color: white;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTADOS DE SESSAO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0
if "lista_leads" not in st.session_state: st.session_state.lista_leads = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Configurações</h3>", unsafe_allow_html=True)
    link_destino = st.text_input("Link de destino", "https://psitelemedicina.netlify.app/")
    registros_pag = st.select_slider("Registros por página", options=[10, 20, 50], value=10)
    
    st.divider()
    
    # --- CAMPO DE APOIO (PIX) ---
    st.markdown("### ☕ Apoie o Projeto")
    st.markdown("""
    <div class="pix-box">
        Gostou da ferramenta? Ajude a manter o servidor online!<br><br>
        <b>PIX (CPF):</b><br>
        <code>06060001190</code>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("Limpar Tudo"):
        st.session_state.chamados = set()
        st.session_state.lista_leads = []
        st.session_state.pagina = 0
        st.rerun()

# --- 5. AREA PRINCIPAL ---
st.markdown("<h2 style='color: white; margin-bottom: 25px;'>Gerenciador de Leads</h2>", unsafe_allow_html=True)

# Tabs para as formas de entrada
tab_url, tab_csv = st.tabs(["🔍 Extração via URL", "📁 Importar CSV"])

with tab_url:
    url_minerar = st.text_input("Cole a URL do site (ex: PsyMeet)", placeholder="https://www.psymeet.social/...")
    if st.button("Iniciar Mineração"):
        st.warning("Integração de mineração ativa. Aguardando processamento da URL...")

with tab_csv:
    arquivo = st.file_uploader("Suba seu arquivo CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo)
        if 'normalized' in df.columns:
            st.session_state.lista_leads = df.to_dict('records')
            st.success(f"{len(st.session_state.lista_leads)} leads carregados via CSV!")
        else:
            st.error("Coluna 'normalized' não encontrada no arquivo.")

# --- 6. EXIBICAO DA FILA DE DISPAROS ---
if st.session_state.lista_leads:
    contatos = st.session_state.lista_leads
    for c in contatos:
        c['tel_limpo'] = str(c.get('normalized', '')).replace('+', '').replace(' ', '').strip()
    
    total_l = len(contatos)
    feitos = len(st.session_state.chamados)

    # Metricas
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="metric-lab">Total</div><div class="metric-val">{total_l}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-lab">Chamados</div><div class="metric-val">{feitos}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-lab">Restante</div><div class="metric-val">{max(0, total_l - feitos)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Lista
    inicio = st.session_state.pagina * registros_pag
    bloco = contatos[inicio : inicio + registros_pag]

    for p in bloco:
        num = p['tel_limpo']
        foi_chamado = num in st.session_state.chamados
        col_info, col_status, col_acao = st.columns([4, 1, 1.5])
        
        with col_info:
            st.markdown(f"<div style='color:white; font-weight:600;'>{p.get('name', 'Profissional')}</div><div style='color:#8b949e; font-size:12px;'>{num}</div>", unsafe_allow_html=True)
        
        with col_status:
            txt = "CONCLUIDO" if foi_chamado else "PENDENTE"
            cor = "#00a884" if foi_chamado else "#8b949e"
            st.markdown(f"<div style='margin-top:10px; color:{cor}; font-size:11px; font-weight:bold;'>{txt}</div>", unsafe_allow_html=True)
        
        with col_acao:
            if not foi_chamado:
                if st.button("Abrir WhatsApp", key=f"btn_{num}"):
                    st.session_state.chamados.add(num)
                    msg = quote(f"Ola {p.get('name', 'Doutor(a)')}, conheca meu projeto: {link_destino}")
                    js = f'window.open("https://wa.me/{num}?text={msg}", "_blank");'
                    components.html(f"<script>{js}</script>", height=0)
                    time.sleep(0.5)
                    st.rerun()
        st.markdown("<hr style='margin:5px 0; border-color:#30363d;'>", unsafe_allow_html=True)

    # Paginacao
    n1, n2, n3 = st.columns([1, 2, 1])
    if n1.button("⬅️ Anterior") and st.session_state.pagina > 0:
        st.session_state.pagina -= 1
        st.rerun()
    n2.markdown(f"<center style='color:#8b949e; padding-top:10px;'>Página {st.session_state.pagina + 1}</center>", unsafe_allow_html=True)
    if n3.button("Próximo ➡️") and (st.session_state.pagina + 1) * registros_pag < total_l:
        st.session_state.pagina += 1
        st.rerun()
else:
    st.info("Utilize uma das abas acima para carregar sua lista de contatos.")