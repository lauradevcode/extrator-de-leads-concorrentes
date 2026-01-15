import streamlit as st
import pandas as pd
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuração Estrita
st.set_page_config(page_title="Lead Machine Pro", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; font-family: 'Inter', sans-serif; }
    .welcome-card {
        background-color: #161b22; padding: 40px; border-radius: 8px;
        border-left: 5px solid #00a884; margin-bottom: 30px;
    }
    .metric-container {
        background-color: #161b22; padding: 20px; border-radius: 8px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 700; color: #ffffff; }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Estilização da Fila de Leads */
    .lead-row {
        background-color: #161b22; padding: 15px; border-radius: 4px;
        margin-bottom: 10px; border: 1px solid #30363d;
        display: flex; justify-content: space-between; align-items: center;
    }
    .status-done { color: #00a884; font-weight: bold; font-size: 12px; }
    .status-pending { color: #8b949e; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE ESTADO E BOAS-VINDAS ---
if "primeiro_acesso" not in st.session_state: st.session_state.primeiro_acesso = True
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0

if st.session_state.primeiro_acesso:
    st.markdown("""
        <div class="welcome-card">
            <div style="color: white; font-size: 24px; font-weight: 700;">Bem-vindo à Operação</div>
            <div style="color: #8b949e; margin-top: 10px;">
                1. Extraia os dados na aba de busca.<br>
                2. Realize o upload do arquivo consolidado.<br>
                3. Inicie os disparos individuais na gestão de leads.
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Iniciar Sistema"):
        st.session_state.primeiro_acesso = False
        st.rerun()
    st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Ajustes</h3>", unsafe_allow_html=True)
    link_bio = st.text_input("Link de destino", "https://psitelemedicina.netlify.app/")
    leads_por_tela = st.select_slider("Registros por página", options=[10, 20, 50], value=10)
    if st.button("Resetar Histórico"):
        st.session_state.chamados = set()
        st.session_state.pagina = 0
        st.rerun()

# --- 5. CONTEÚDO PRINCIPAL ---
st.markdown("<h1 style='color: white; font-size: 24px;'>Gerenciador de Leads</h1>", unsafe_allow_html=True)

tab_ext, tab_disp = st.tabs(["Extração via URL", "Gestão de Disparos"])

with tab_ext:
    url = st.text_input("URL de destino para mineração")
    st.button("Executar Busca Técnica")

with tab_disp:
    uploaded = st.file_uploader("Importar base CSV", type="csv", label_visibility="collapsed")
    
    if uploaded:
        df = pd.read_csv(uploaded)
        if 'normalized' in df.columns:
            # Limpeza e Normalização
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).strip()
            contatos = df.drop_duplicates(subset=['tel_limpo']).to_dict('records')
            total_leads = len(contatos)
            
            # Métricas
            atendidos = len(st.session_state.chamados)
            m1, m2, m3 = st.columns(3)
            m1.markdown(f'<div class="metric-container"><div class="metric-label">Registros Únicos</div><div class="metric-value">{total_leads}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-container"><div class="metric-label">Contatos Realizados</div><div class="metric-value">{atendidos}</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-container"><div class="metric-label">Taxa</div><div class="metric-value">{atendidos/total_leads:.0% if total_leads > 0 else 0}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Paginação
            inicio = st.session_state.pagina * leads_por_tela
            fim = min(inicio + leads_por_tela, total_leads)
            bloco = contatos[inicio:fim]

            # Listagem de Leads
            for p in bloco:
                num = p['tel_limpo']
                foi_chamado = num in st.session_state.chamados
                
                with st.container():
                    col_info, col_status, col_btn = st.columns([3, 1, 1])
                    
                    col_info.markdown(f"<span style='color: white; font-weight: 600;'>{p.get('name', 'Profissional')}</span><br><span style='color: #8b949e; font-size: 12px;'>{num}</span>", unsafe_allow_html=True)
                    
                    if foi_chamado:
                        col_status.markdown('<div style="margin-top: 10px;" class="status-done">CONCLUÍDO</div>', unsafe_allow_html=True)
                        col_btn.write("") 
                    else:
                        col_status.markdown('<div style="margin-top: 10px;" class="status-pending">PENDENTE</div>', unsafe_allow_html=True)
                        if col_btn.button("Falar no WhatsApp", key=f"btn_{num}"):
                            st.session_state.chamados.add(num)
                            msg = quote(f"Olá {p.get('name', 'Doutor(a)')}, conheça meu projeto: {link_bio}")
                            url_wa = f"https://wa.me/{num}?text={msg}"
                            components.html(f"<script>window.open('{url_wa}', '_blank');</script>", height=0)
                            st.rerun()

            # Navegação
            st.markdown("---")
            nav_prev, nav_page, nav_next = st.columns([1, 2, 1])
            if nav_prev.button("Anterior") and st.session_state.pagina > 0:
                st.session_state.pagina -= 1
                st.rerun()
            nav_page.markdown(f"<center style='color: #8b949e;'>Página {st.session_state.pagina + 1}</center>", unsafe_allow_html=True)
            if nav_next.button("Próximo") and (st.session_state.pagina + 1) * leads_por_tela < total_leads:
                st.session_state.pagina += 1
                st.rerun()
        else:
            st.error("Erro: A coluna 'normalized' não foi detectada no CSV.")