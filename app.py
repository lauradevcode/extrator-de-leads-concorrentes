import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuracao da Pagina
st.set_page_config(page_title="Lead Machine Pro", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    .metric-card {
        background-color: #161b22; padding: 20px; border-radius: 4px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: 700; color: #00a884; }
    div.stButton > button {
        background-color: #00a884; color: white; border: none;
        padding: 8px 20px; border-radius: 4px; font-weight: 600;
        width: 100%;
    }
    .pix-sidebar {
        background-color: #1d2129; padding: 15px; border-radius: 8px;
        border: 1px dashed #00a884; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÃO DO POP-UP (CORRIGIDA) ---
@st.dialog("☕ Apoie o Projeto")
def modal_apoio():
    st.write("Sua ajuda mantém o servidor online!")
    st.code("06060001190", language="text")
    st.caption("Chave PIX (CPF)")
    # No Dialog, o botão apenas precisa existir. O clique no X ou fora também fecha.
    if st.button("Entendido"):
        st.rerun()

# --- 4. ESTADOS DE SESSAO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0
if "lista_leads" not in st.session_state: st.session_state.lista_leads = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # NOVA FUNÇÃO: Mensagem Customizada
    st.subheader("Script de Abordagem")
    msg_padrao = "Olá {nome}, vi seu perfil e gostaria de apresentar meu projeto: {link}"
    user_msg = st.text_area("Edite sua mensagem:", value=msg_padrao, help="Use {nome} para o nome do lead e {link} para o seu link.")
    
    link_destino = st.text_input("Link de destino:", "https://psitelemedicina.netlify.app/")
    registros_pag = st.select_slider("Leads por página:", options=[10, 20, 50], value=10)
    
    st.divider()
    st.markdown(f'<div class="pix-sidebar"><b style="color:white;">☕ Apoie o Projeto</b><br><small>Chave PIX (CPF):</small><br><code style="color:#00a884;">06060001190</code></div>', unsafe_allow_html=True)
    
    if st.button("Limpar Tudo"):
        st.session_state.chamados = set()
        st.session_state.lista_leads = []
        st.rerun()

# --- 6. AREA PRINCIPAL ---
st.title("🚀 Gerenciador de Leads")

tab_url, tab_csv = st.tabs(["🔍 Extração via URL", "📁 Importar CSV"])

with tab_url:
    url_minerar = st.text_input("Cole a URL do site:")
    if st.button("Iniciar Mineração"):
        st.info("Funcionalidade em desenvolvimento para a URL inserida.")

with tab_csv:
    arquivo = st.file_uploader("Suba sua lista (CSV)", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo)
        if 'normalized' in df.columns:
            st.session_state.lista_leads = df.to_dict('records')
            modal_apoio()
        else:
            st.error("Erro: Coluna 'normalized' não encontrada.")

# --- 7. FILA DE DISPAROS ---
if st.session_state.lista_leads:
    leads = st.session_state.lista_leads
    total = len(leads)
    feitos = len(st.session_state.chamados)
    
    # Dashboard
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div style="color:#8b949e">TOTAL</div><div class="metric-val">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div style="color:#8b949e">CHAMADOS</div><div class="metric-val">{feitos}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div style="color:#8b949e">RESTANTE</div><div class="metric-val">{total - feitos}</div></div>', unsafe_allow_html=True)

    # Paginação
    inicio = st.session_state.pagina * registros_pag
    bloco = leads[inicio : inicio + registros_pag]

    for p in bloco:
        num = str(p['normalized']).replace('+', '').replace(' ', '').strip()
        foi_chamado = num in st.session_state.chamados
        
        col_info, col_status, col_acao = st.columns([4, 1, 1.5])
        
        with col_info:
            st.markdown(f"<div style='color:white; font-weight:600;'>{p.get('name', 'Profissional')}</div><div style='color:#8b949e; font-size:12px;'>{num}</div>", unsafe_allow_html=True)
        
        with col_status:
            cor = "#00a884" if foi_chamado else "#8b949e"
            st.markdown(f"<div style='margin-top:10px; color:{cor}; font-size:11px; font-weight:bold;'>{'CONCLUÍDO' if foi_chamado else 'PENDENTE'}</div>", unsafe_allow_html=True)
        
        with col_acao:
            if not foi_chamado:
                if st.button("Enviar WhatsApp", key=f"btn_{num}"):
                    st.session_state.chamados.add(num)
                    # Lógica de Mensagem Customizada
                    nome_lead = p.get('name', 'Doutor(a)')
                    texto_final = user_msg.replace("{nome}", nome_lead).replace("{link}", link_destino)
                    
                    link_wa = f"https://wa.me/{num}?text={quote(texto_final)}"
                    js = f'window.open("{link_wa}", "_blank");'
                    components.html(f"<script>{js}</script>", height=0)
                    time.sleep(0.5)
                    st.rerun()
        st.markdown("<hr style='margin:5px 0; border-color:#1d2129;'>", unsafe_allow_html=True)