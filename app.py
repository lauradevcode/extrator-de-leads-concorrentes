import streamlit as st
import pandas as pd
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Lead Manager Pro", page_icon="🚀", layout="wide")

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #25D366; }
    .stButton>button { border-radius: 8px; height: 3em; font-weight: bold; }
    .contact-card {
        background-color: #1d2129;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #25D366;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Painel")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    itens_por_pagina = st.slider("Itens por página", 5, 20, 10)
    if st.button("🔄 Resetar App"):
        st.session_state.pagina_atual = 0
        st.rerun()

st.title("📲 Gerenciador de Leads de Alta Performance")

# --- LOGICA DE DADOS ---
uploaded_file = st.file_uploader("📂 Importe sua lista (CSV)", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    if 'normalized' in df_raw.columns:
        # Limpeza conforme original
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total_leads = len(contatos)
        total_paginas = (total_leads // itens_por_pagina) + (1 if total_leads % itens_por_pagina > 0 else 0)

        # --- DASHBOARD ---
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Leads", total_leads)
        c2.metric("Página", f"{st.session_state.pagina_atual + 1} de {total_paginas}")
        c3.metric("Status", "Pronto para Envio")

        # --- CONTROLE DE PAGINAÇÃO ---
        st.markdown("---")
        col_prev, col_center, col_next = st.columns([1, 2, 1])
        
        if col_prev.button("⬅️ Anterior") and st.session_state.pagina_atual > 0:
            st.session_state.pagina_atual -= 1
            st.rerun()
            
        if col_next.button("Próximo ➡️") and st.session_state.pagina_atual < total_paginas - 1:
            st.session_state.pagina_atual += 1
            st.rerun()

        # --- LISTAGEM DE LEADS ---
        inicio = st.session_state.pagina_atual * itens_por_pagina
        fim = min(inicio + itens_por_pagina, total_leads)
        bloco = contatos[inicio:fim]

        st.write(f"Mostrando **{inicio}** - **{fim}** de **{total_leads}**")

        for pessoa in bloco:
            nome_full = str(pessoa.get('name', 'Doutor(a)'))
            p_nome = nome_full.split()[0].capitalize()
            numero = pessoa['tel_limpo']
            
            # Texto personalizado baseado no seu original
            msg = f"Olá {p_nome}! Tudo bem? Vi seu perfil e gostaria de te convidar para conhecer: {link_projeto}"
            link_wa = f"https://wa.me/{numero}?text={quote(msg)}"

            # Card de contato com botão individual (Design Melhorado)
            with st.container():
                st.markdown(f"""
                <div class="contact-card">
                    <strong>👤 {nome_full}</strong><br>
                    <small>📞 {numero}</small>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(f"🚀 Chamar {p_nome} no WhatsApp", link_wa, use_container_width=True)
                st.write("") # Espaçador

    else:
        st.error("Erro: A coluna 'normalized' não foi encontrada.")

# --- FOOTER ---
if not uploaded_file:
    st.info("💡 Dica: Suba o arquivo CSV para visualizar os leads e iniciar os disparos.")