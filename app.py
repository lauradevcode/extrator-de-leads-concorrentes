import streamlit as st
import pandas as pd
import time
import requests
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCOES DE APOIO ---
def buscar_leads_notion(token, database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            leads = []
            for page in data.get("results", []):
                props = page.get("properties", {})
                nome = props.get("Nome", {}).get("title", [{}])[0].get("text", {}).get("content", "Profissional")
                tel = ""
                if "Telefone" in props:
                    p_type = props["Telefone"]["type"]
                    if p_type == "phone_number": tel = props["Telefone"]["phone_number"]
                    elif props["Telefone"]["rich_text"]: tel = props["Telefone"]["rich_text"][0]["text"]["content"]
                if tel: leads.append({"name": nome, "normalized": tel})
            return leads
        return None
    except: return None

# --- 4. ESTADOS DE SESSAO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0
if "lista_leads" not in st.session_state: st.session_state.lista_leads = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Configuracoes</h3>", unsafe_allow_html=True)
    link_destino = st.text_input("Link de destino", "https://psitelemedicina.netlify.app/")
    registros_pag = st.select_slider("Registros por pagina", options=[10, 20, 50], value=10)
    if st.button("Limpar Tudo"):
        st.session_state.chamados = set()
        st.session_state.lista_leads = []
        st.rerun()

# --- 6. AREA PRINCIPAL ---
st.markdown("<h2 style='color: white; margin-bottom: 25px;'>Gerenciador de Leads</h2>", unsafe_allow_html=True)

# Tabs para as 3 formas de entrada
tab_url, tab_csv, tab_notion = st.tabs(["🔍 Extracao via URL", "📁 Importar CSV", "🔌 Conectar Notion"])

with tab_url:
    url_minerar = st.text_input("Cole a URL do site (ex: PsyMeet)", placeholder="https://www.psymeet.social/...")
    if st.button("Iniciar Mineracao"):
        st.warning("Integracao de mineracao ativa. Aguardando processamento da URL...")
        # Aqui entraria sua logica de scraping da URL

with tab_csv:
    arquivo = st.file_uploader("Suba seu arquivo CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo)
        if 'normalized' in df.columns:
            st.session_state.lista_leads = df.to_dict('records')
            st.success(f"{len(st.session_state.lista_leads)} leads carregados!")

with tab_notion:
    n_token = st.text_input("Notion Secret", type="password")
    n_id = st.text_input("Database ID")
    if st.button("Sincronizar Notion"):
        if n_token and n_id:
            leads = buscar_leads_notion(n_token, n_id)
            if leads:
                st.session_state.lista_leads = leads
                st.success(f"{len(leads)} leads importados!")
                st.rerun()

# --- 7. EXIBICAO DA FILA DE DISPAROS ---
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
    m3.markdown(f'<div class="metric-card"><div class="metric-lab">Restante</div><div class="metric-val">{total_l - feitos}</div></div>', unsafe_allow_html=True)

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
    if n1.button("Anterior") and st.session_state.pagina > 0:
        st.session_state.pagina -= 1
        st.rerun()
    if n3.button("Proximo") and (st.session_state.pagina + 1) * registros_pag < total_l:
        st.session_state.pagina += 1
        st.rerun()
else:
    st.info("Utilize uma das abas acima para carregar sua lista de contatos.")