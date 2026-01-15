import streamlit as st
import pandas as pd
from urllib.parse import quote
import streamlit.components.v1 as components

# Configuração de alta performance
st.set_page_config(page_title="Lead Machine Pro", layout="wide")

# --- DESIGN MINIMALISTA (CSS) ---
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
        background-color: #161b22; padding: 12px 20px; border-radius: 4px;
        border: 1px solid #30363d; margin-bottom: 8px;
    }
    
    /* Botões */
    div.stButton > button {
        background-color: #00a884; color: white; border: none;
        padding: 8px 16px; border-radius: 4px; font-size: 13px;
    }
    div.stButton > button:hover { background-color: #008f6f; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADOS DE SESSÃO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0

# --- BARRA LATERAL (AJUSTES) ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Configurações</h3>", unsafe_allow_html=True)
    link_destino = st.text_input("Link de destino", "https://psitelemedicina.netlify.app/")
    leads_por_pagina = st.select_slider("Registros por página", options=[10, 20, 50], value=10)
    if st.button("Resetar histórico"):
        st.session_state.chamados = set()
        st.session_state.pagina = 0
        st.rerun()

# --- ÁREA PRINCIPAL ---
st.markdown("<h2 style='color: white; margin-bottom: 25px;'>Gerenciador de Leads</h2>", unsafe_allow_html=True)

tab_ext, tab_gestao = st.tabs(["Extração via URL", "Gestão de Disparos"])

with tab_ext:
    st.text_input("URL para mineração", placeholder="Insira o link do diretório...")
    st.button("Iniciar extração")

with tab_gestao:
    arquivo = st.file_uploader("Importar base de dados (CSV)", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo)
        
        if 'normalized' in df.columns:
            # CORREÇÃO DO BUG: Uso correto do .str.strip() para colunas do Pandas
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            
            contatos = df.drop_duplicates(subset=['tel_limpo']).to_dict('records')
            total_leads = len(contatos)
            chamados_total = len(st.session_state.chamados)

            # Dashboard de métricas
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><div class="metric-lab">Total Únicos</div><div class="metric-val">{total_leads}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><div class="metric-lab">Chamados</div><div class="metric-val">{chamados_total}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card"><div class="metric-lab">Restante</div><div class="metric-val">{total_leads - chamados_total}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Lógica de Paginação
            inicio = st.session_state.pagina * leads_por_pagina
            fim = min(inicio + leads_por_pagina, total_leads)
            bloco = contatos[inicio:fim]

            # Exibição da Fila
            for p in bloco:
                num = p['tel_limpo']
                foi_chamado = num in st.session_state.chamados
                
                with st.container():
                    col_info, col_status, col_btn = st.columns([3, 1, 1.2])
                    
                    # Nome e Telefone
                    col_info.markdown(f"<span style='color: white; font-weight: 600;'>{p.get('name', 'Profissional')}</span><br><span style='color: #8b949e; font-size: 12px;'>{num}</span>", unsafe_allow_html=True)
                    
                    # Status visual discreto
                    if foi_chamado:
                        col_status.markdown('<div style="margin-top: 10px; color: #00a884; font-size: 11px; font-weight: bold;">CONCLUÍDO</div>', unsafe_allow_html=True)
                        col_btn.write("") # Oculta o botão se já foi chamado
                    else:
                        col_status.markdown('<div style="margin-top: 10px; color: #8b949e; font-size: 11px; font-weight: bold;">PENDENTE</div>', unsafe_allow_html=True)
                        if col_btn.button("Abrir WhatsApp", key=f"btn_{num}"):
                            st.session_state.chamados.add(num)
                            texto = quote(f"Olá {p.get('name', 'Doutor(a)')}, conheça meu projeto: {link_destino}")
                            url_wa = f"https://wa.me/{num}?text={texto}"
                            components.html(f"<script>window.open('{url_wa}', '_blank');</script>", height=0)
                            st.rerun()

            # Navegação no rodapé
            st.markdown("---")
            b_prev, b_pag, b_next = st.columns([1, 2, 1])
            if b_prev.button("Anterior") and st.session_state.pagina > 0:
                st.session_state.pagina -= 1
                st.rerun()
            b_pag.markdown(f"<center style='color: #8b949e; margin-top: 10px;'>Página {st.session_state.pagina + 1}</center>", unsafe_allow_html=True)
            if b_next.button("Próximo") and (st.session_state.pagina + 1) * leads_por_pagina < total_leads:
                st.session_state.pagina += 1
                st.rerun()
        else:
            st.error("O arquivo CSV deve conter a coluna 'normalized'.")