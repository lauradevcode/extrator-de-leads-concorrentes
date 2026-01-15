import streamlit as st
import pandas as pd
import re
import requests
from urllib.parse import quote
import streamlit.components.v1 as components

# Configuração da Página
st.set_page_config(page_title="Extrator de Lead Pro", page_icon="🎯", layout="wide")

# --- ESTADOS DE SESSÃO ---
if "pagina_atual" not in st.session_state: 
    st.session_state.pagina_atual = 0  # Começa no índice 0
if "chamados" not in st.session_state: 
    st.session_state.chamados = set()

# --- CSS PARA UX ---
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
    /* Espaçamento entre colunas da lista */
    div[data-testid="column"] { padding: 10px 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def extrair_leads_backend(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        telefones = re.findall(r'9\d{4}[-\s]?\d{4}', res.text)
        leads = []
        vistos = set()
        for tel in telefones:
            num = re.sub(r'\D', '', tel)
            num_f = "55" + num if len(num) == 11 else num
            if num_f not in vistos and "984679566" not in num_f:
                vistos.add(num_f)
                leads.append({"name": "Lead Extraído", "normalized": num_f})
        return pd.DataFrame(leads)
    except: return pd.DataFrame()

def marcar_como_chamado(numero, url_wa):
    st.session_state.chamados.add(numero)
    # Abre o WhatsApp em nova aba
    components.html(f"<script>window.open('{url_wa}', '_blank');</script>", height=0)

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2 = st.tabs(["🔍 1. Extração Inteligente", "🚀 2. Operação de Disparo"])

with tab1:
    st.subheader("Extrair Leads da URL")
    url_target = st.text_input("URL para vasculhar")
    if st.button("Iniciar Extração"):
        with st.spinner("Minerando dados..."):
            df_ext = extrair_leads_backend(url_target)
            if not df_ext.empty:
                st.success(f"{len(df_ext)} leads encontrados!")
                st.dataframe(df_ext, use_container_width=True)
                csv = df_ext.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV Gerado", csv, "leads_extraidos.csv", "text/csv")
            else:
                st.warning("Nenhum lead encontrado. Tente outra URL ou use um CSV pronto.")

with tab2:
    with st.sidebar:
        st.header("⚙️ Configurações")
        link_bio = st.text_input("Seu Link", "https://psitelemedicina.netlify.app/")
        leads_por_pag = st.select_slider("Leads por página", options=[10, 20, 50], value=10)
        if st.button("Resetar Tudo"):
            st.session_state.pagina_atual = 0
            st.session_state.chamados = set()
            st.rerun()

    uploaded = st.file_uploader("📥 Suba o arquivo CSV", type="csv")
    
    if uploaded:
        df = pd.read_csv(uploaded)
        if 'normalized' in df.columns:
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            df = df.drop_duplicates(subset=['tel_limpo'])
            contatos = df.to_dict('records')
            
            total_leads = len(contatos)
            total_paginas = (total_leads // leads_por_pag) + (1 if total_leads % leads_por_pag > 0 else 0)
            
            # Dashboard de Progresso
            chamados_count = len(st.session_state.chamados)
            c1, c2 = st.columns(2)
            c1.metric("Total na Lista", total_leads)
            c2.metric("Atendidos", chamados_count)
            st.progress(chamados_count/total_leads if total_leads > 0 else 0)

            st.markdown("### 📋 Fila de Trabalho")
            
            # Cálculo de Paginação Correto
            inicio = st.session_state.pagina_atual * leads_por_pag
            fim = min(inicio + leads_por_pag, total_leads)
            bloco = contatos[inicio:fim]

            for p in bloco:
                num = p['tel_limpo']
                foi_chamado = num in st.session_state.chamados
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 2])
                    col1.markdown(f"**{p.get('name', 'Profissional')}**<br><small>{num}</small>", unsafe_allow_html=True)
                    
                    if foi_chamado:
                        col2.markdown('<span class="status-badge done">✅ CHAMADO</span>', unsafe_allow_html=True)
                        col3.write("Aguardando retorno")
                    else:
                        col2.markdown('<span class="status-badge pending">⏳ PENDENTE</span>', unsafe_allow_html=True)
                        
                        msg = f"Olá! Tudo bem? Conheça meu projeto: {link_bio}"
                        url_wa = f"https://wa.me/{num}?text={quote(msg)}"
                        
                        # O clique agora chama a função que marca como feito E abre a aba
                        if col3.button(f"Abrir WhatsApp", key=f"btn_{num}"):
                            marcar_como_chamado(num, url_wa)
                            st.rerun()

            # --- PAGINAÇÃO NO RODAPÉ (AJUSTADA) ---
            st.divider()
            b1, b2, b3 = st.columns([1, 2, 1])
            
            if b1.button("⬅️ Anterior") and st.session_state.pagina_atual > 0:
                st.session_state.pagina_atual -= 1
                st.rerun()
            
            # Exibe Página 1 se st.session_state.pagina_atual for 0
            b2.markdown(f"<center>Página <b>{st.session_state.pagina_atual + 1}</b> de {total_paginas}</center>", unsafe_allow_html=True)
            
            if b3.button("Próximo ➡️") and (st.session_state.pagina_atual + 1) < total_paginas:
                st.session_state.pagina_atual += 1
                st.rerun()
        else:
            st.error("O CSV precisa da coluna 'normalized'.")
    else:
        st.info("Suba um arquivo para começar a jornada.")