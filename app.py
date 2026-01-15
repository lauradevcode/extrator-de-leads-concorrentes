import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Extrator de Lead Pro", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    
    /* Cards de métricas */
    .metric-card {
        background-color: #161b22; padding: 20px; border-radius: 4px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: 700; color: #ffffff; }
    .metric-lab { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }

    /* Fila de contatos */
    .contact-row {
        background-color: #161b22; padding: 15px; border-radius: 4px;
        border: 1px solid #30363d; margin-bottom: 8px;
    }
    
    /* Botões Profissionais */
    div.stButton > button {
        background-color: #00a884; color: white; border: none;
        padding: 8px 16px; border-radius: 4px; font-size: 13px;
        width: 100%;
    }
    div.stButton > button:hover { background-color: #008f6f; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTADOS DE SESSÃO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Configuracoes</h3>", unsafe_allow_html=True)
    link_destino = st.text_input("Link de destino", "https://psitelemedicina.netlify.app/")
    leads_por_pagina = st.select_slider("Registros por pagina", options=[10, 20, 50], value=10)
    if st.button("Resetar historico"):
        st.session_state.chamados = set()
        st.session_state.pagina = 0
        st.rerun()

# --- 5. AREA PRINCIPAL ---
st.markdown("<h2 style='color: white; margin-bottom: 25px;'>Gerenciador de Leads</h2>", unsafe_allow_html=True)

tab_ext, tab_gestao = st.tabs(["Extracao via URL", "Gestao de Disparos"])

with tab_ext:
    st.text_input("URL para mineracao", placeholder="Insira o link do diretorio...")
    st.button("Iniciar extracao")

with tab_gestao:
    arquivo = st.file_uploader("Importar base de dados (CSV)", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo)
        
        if 'normalized' in df.columns:
            # Correção do processamento da coluna
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            contatos = df.drop_duplicates(subset=['tel_limpo']).to_dict('records')
            total_leads = len(contatos)
            chamados_total = len(st.session_state.chamados)

            # Dashboard
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><div class="metric-lab">Total Unicos</div><div class="metric-val">{total_leads}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><div class="metric-lab">Chamados</div><div class="metric-val">{chamados_total}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card"><div class="metric-lab">Restante</div><div class="metric-val">{total_leads - chamados_total}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Paginacao
            inicio = st.session_state.pagina * leads_por_pagina
            fim = min(inicio + leads_por_pagina, total_leads)
            bloco = contatos[inicio:fim]

            # Listagem
            for p in bloco:
                num = p['tel_limpo']
                foi_chamado = num in st.session_state.chamados
                
                with st.container():
                    st.markdown(f"""
                        <div class="contact-row">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="color: white; font-weight: 600;">{p.get('name', 'Profissional')}</span><br>
                                    <span style="color: #8b949e; font-size: 12px;">{num}</span>
                                </div>
                                <div style="color: {'#00a884' if foi_chamado else '#8b949e'}; font-size: 11px; font-weight: bold;">
                                    {'CONCLUIDO' if foi_chamado else 'PENDENTE'}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if not foi_chamado:
                        if st.button(f"Abrir WhatsApp", key=f"btn_{num}"):
                            st.session_state.chamados.add(num)
                            
                            # Preparacao da URL
                            texto = quote(f"Ola {p.get('name', 'Doutor(a)')}, conheca meu projeto: {link_destino}")
                            url_wa = f"https://wa.me/{num}?text={texto}"
                            
                            # JavaScript injetado de forma limpa para evitar erro no VS Code
                            js = f'window.open("{url_wa}", "_blank");'
                            components.html(f"<script>{js}</script>", height=0)
                            
                            time.sleep(0.5)
                            st.rerun()

            # Navegacao
            st.markdown("---")
            b_prev, b_pag, b_next = st.columns([1, 2, 1])
            if b_prev.button("Anterior") and st.session_state.pagina > 0:
                st.session_state.pagina -= 1
                st.rerun()
            b_pag.markdown(f"<center style='color: #8b949e; margin-top: 10px;'>Pagina {st.session_state.pagina + 1}</center>", unsafe_allow_html=True)
            if b_next.button("Proximo") and (st.session_state.pagina + 1) * leads_por_pagina < total_leads:
                st.session_state.pagina += 1
                st.rerun()
        else:
            st.error("O arquivo CSV deve conter a coluna 'normalized'.")