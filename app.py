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

# --- 3. FUNÇÃO DO POP-UP ---
@st.dialog("☕ Apoie o Projeto")
def modal_apoio():
    st.write("Sua ajuda é fundamental para manter o servidor online e trazer novas atualizações!")
    st.info("Chave PIX (CPF):")
    st.code("06060001190", language="text")
    st.write("Qualquer valor é bem-vindo. Obrigado pelo apoio!")
    st.caption("Clique no 'X' acima ou fora desta caixa para fechar.")

# --- 4. ESTADOS DE SESSAO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0
if "lista_leads" not in st.session_state: st.session_state.lista_leads = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    st.subheader("Script de Mensagem")
    msg_custom = st.text_area(
        "Personalize seu texto:", 
        value="Olá {nome}, vi seu perfil e gostaria de apresentar meu projeto: {link}",
        help="Use {nome} para o nome do lead e {link} para o seu link de destino."
    )
    
    link_destino = st.text_input("Link de destino:", "https://psitelemedicina.netlify.app/")
    registros_pag = st.select_slider("Leads por página:", options=[10, 20, 50], value=10)
    
    st.divider()
    
    st.markdown(f"""
    <div class="pix-sidebar">
        <b style="color:white; font-size:16px;">☕ Apoie o Projeto</b><br>
        <span style="color:#8b949e; font-size:12px;">Gostou da ferramenta? Ajude-nos!</span><br><br>
        <b style="color:#00a884;">Chave PIX (CPF):</b><br>
        <code style="color:#00a884;">06060001190</code>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Limpar Tudo"):
        st.session_state.chamados = set()
        st.session_state.lista_leads = []
        st.session_state.pagina = 0
        st.rerun()

# --- 6. AREA PRINCIPAL ---
st.title("🚀 Gerenciador de Leads")

tab_url, tab_csv = st.tabs(["🔍 Extração via URL", "📁 Importar CSV"])

with tab_url:
    url_minerar = st.text_input("Cole a URL para extração:")
    if st.button("Iniciar Mineração"):
        st.info("Simulação: Leads extraídos com sucesso!")
        # Apenas para teste visual da paginação se não tiver CSV
        st.session_state.lista_leads = [{"name": f"Lead {i}", "normalized": f"551199999{i:04d}"} for i in range(25)]
        modal_apoio()

with tab_csv:
    arquivo = st.file_uploader("Importar base de dados (CSV)", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo)
        if 'normalized' in df.columns:
            st.session_state.lista_leads = df.to_dict('records')
            modal_apoio()
        else:
            st.error("Coluna 'normalized' não encontrada no CSV.")

# --- 7. EXIBIÇÃO E DISPAROS ---
if st.session_state.lista_leads:
    leads = st.session_state.lista_leads
    total = len(leads)
    feitos = len(st.session_state.chamados)
    
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div style="color:#8b949e">TOTAL</div><div class="metric-val">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div style="color:#8b949e">CHAMADOS</div><div class="metric-val">{feitos}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div style="color:#8b949e">RESTANTE</div><div class="metric-val">{total - feitos}</div></div>', unsafe_allow_html=True)

    st.write("---")

    # LÓGICA DE PAGINAÇÃO REINSERIDA
    inicio = st.session_state.pagina * registros_pag
    fim = inicio + registros_pag
    bloco = leads[inicio : fim]

    for p in bloco:
        num = str(p['normalized']).replace('+', '').replace(' ', '').strip()
        foi_chamado = num in st.session_state.chamados
        
        col_info, col_status, col_acao = st.columns([4, 1, 1.5])
        
        with col_info:
            st.markdown(f"**{p.get('name', 'Profissional')}** \n<small style='color:#8b949e'>{num}</small>", unsafe_allow_html=True)
        
        with col_status:
            status_txt = "CONCLUÍDO" if foi_chamado else "PENDENTE"
            status_cor = "#00a884" if foi_chamado else "#8b949e"
            st.markdown(f"<p style='color:{status_cor}; font-weight:bold; font-size:12px; margin-top:10px;'>{status_txt}</p>", unsafe_allow_html=True)
        
        with col_acao:
            if not foi_chamado:
                if st.button("Abrir WhatsApp", key=f"btn_{num}"):
                    st.session_state.chamados.add(num)
                    texto = msg_custom.replace("{nome}", p.get('name', 'Doutor(a)')).replace("{link}", link_destino)
                    link_wa = f"https://wa.me/{num}?text={quote(texto)}"
                    js = f'window.open("{link_wa}", "_blank");'
                    components.html(f"<script>{js}</script>", height=0)
                    time.sleep(0.5)
                    st.rerun()
        st.markdown("<hr style='margin:5px 0; border-color:#1d2129;'>", unsafe_allow_html=True)

    # CONTROLES DE PAGINAÇÃO (Abaixo da lista)
    st.markdown("<br>", unsafe_allow_html=True)
    c_pag1, c_pag2, c_pag3 = st.columns([1, 2, 1])
    
    with c_pag1:
        if st.button("⬅️ Anterior") and st.session_state.pagina > 0:
            st.session_state.pagina -= 1
            st.rerun()
            
    with c_pag2:
        pag_atual = st.session_state.pagina + 1
        total_paginas = (total // registros_pag) + (1 if total % registros_pag > 0 else 0)
        st.markdown(f"<center style='color:#8b949e;'>Página {pag_atual} de {total_paginas}</center>", unsafe_allow_html=True)
        
    with c_pag3:
        if st.button("Próximo ➡️") and fim < total:
            st.session_state.pagina += 1
            st.rerun()
else:
    st.info("Aguardando carregamento de contatos...")