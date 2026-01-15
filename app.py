import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote
import streamlit.components.v1 as components

# Configuração da Página com Tooltip de título
st.set_page_config(page_title="Extrator de Leads em Massa", page_icon="🚀", layout="wide")

# --- CSS PARA DESIGN PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .op-row {
        background-color: #1d2129; padding: 20px; border-radius: 12px;
        margin-bottom: 15px; border: 1px solid #2d323d;
    }
    .status-badge { padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; }
    .pending { background-color: #3b4252; color: #eceff4; }
    .done { background-color: #25D366; color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADOS DE SESSÃO ---
if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = 0
if "chamados" not in st.session_state: st.session_state.chamados = set()

# --- HEADER COM AJUDA ---
st.title("📲 Extrator de Leads em Massa dos Concorrentes")
st.info("💡 **Jornada:** 1º Extraia os leads na aba de pesquisa -> 2º Baixe o CSV -> 3º Suba na aba de disparo.")

# --- ABAS DE TRABALHO ---
tab1, tab2 = st.tabs(["🔍 1. Extração via URL", "🚀 2. Operação de Disparo"])

with tab1:
    st.subheader("Módulo de Mineração")
    url_target = st.text_input("URL do site concorrente", 
                               help="Cole aqui o link da página de busca do site que deseja minerar.")
    if st.button("Iniciar Extração Profissional"):
        st.success("Extração simulada: Use o backend de requests para minerar o HTML aqui.")

with tab2:
    with st.sidebar:
        st.header("⚙️ Painel de Controle")
        link_bio = st.text_input("Link de Destino", "https://psitelemedicina.netlify.app/",
                                help="Link que será enviado automaticamente na mensagem de WhatsApp.")
        leads_por_pag = st.select_slider("Leads por tela", options=[10, 20, 50], value=10)
        if st.button("Limpar Histórico de Cliques", help="Reseta o status de 'Chamado' para todos os contatos."):
            st.session_state.chamados = set()
            st.rerun()

    uploaded = st.file_uploader("Suba o arquivo CSV", type="csv", 
                                help="O arquivo deve conter uma coluna chamada 'normalized'.")

    if uploaded:
        df = pd.read_csv(uploaded)
        # Lógica de processamento
        if 'normalized' in df.columns:
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            contatos = df.drop_duplicates(subset=['tel_limpo']).to_dict('records')
            
            # Dashboard
            total = len(contatos)
            inicio = st.session_state.pagina_atual * leads_por_pag
            fim = min(inicio + leads_por_pag, total)
            
            st.metric("Total de Leads Únicos", total)
            
            for p in contatos[inicio:fim]:
                num = p['tel_limpo']
                status = "done" if num in st.session_state.chamados else "pending"
                
                with st.container():
                    c1, c2, c3 = st.columns([4, 2, 2])
                    c1.write(f"**{p.get('name', 'Profissional')}**")
                    c2.markdown(f'<span class="status-badge {status}">{"✅ CHAMADO" if status == "done" else "⏳ PENDENTE"}</span>', unsafe_allow_html=True)
                    
                    if c3.button("Abrir WhatsApp", key=f"btn_{num}"):
                        st.session_state.chamados.add(num)
                        url_wa = f"https://wa.me/{num}?text={quote(f'Olá! Veja meu projeto: {link_bio}')}"
                        components.html(f"<script>window.open('{url_wa}', '_blank');</script>", height=0)
                        st.rerun()

            # Navegação no Rodapé
            st.divider()
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            if col_prev.button("⬅️ Anterior") and st.session_state.pagina_atual > 0:
                st.session_state.pagina_atual -= 1
                st.rerun()
            col_page.markdown(f"<center>Página {st.session_state.pagina_atual + 1}</center>", unsafe_allow_html=True)
            if col_next.button("Próximo ➡️") and (st.session_state.pagina_atual + 1) * leads_por_pag < total:
                st.session_state.pagina_atual += 1
                st.rerun()