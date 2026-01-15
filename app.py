import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuração da Página (Sempre o primeiro comando)
st.set_page_config(page_title="Extrator de Leads em Massa", page_icon="🚀", layout="wide")

# --- 2. LÓGICA DE BOAS-VINDAS (ESTÁVEL) ---
if "primeiro_acesso" not in st.session_state:
    st.session_state.primeiro_acesso = True

if st.session_state.primeiro_acesso:
    # Criamos uma caixa de destaque que funciona como o modal da sua imagem
    with st.container():
        st.markdown("""
            <div style="background-color: #1d2129; padding: 30px; border-radius: 15px; border: 2px solid #25D366; margin-bottom: 25px;">
                <h2 style="color: #25D366; margin-top: 0;">🚀 Bem-vindo ao Extrator de Leads!</h2>
                <p>Siga estes passos para começar sua operação:</p>
                <ol>
                    <li><b>Extração:</b> Cole a URL do concorrente na aba de busca e minere os contatos.</li>
                    <li><b>Download:</b> Baixe o arquivo CSV gerado pelo sistema.</li>
                    <li><b>Disparo:</b> Suba o CSV na aba de disparos e inicie suas mensagens.</li>
                </ol>
                <p style="font-size: 0.9em; color: #888;"><i>Dica: Use a tag <b>{nome}</b> para personalizar seus convites.</i></p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔥 ENTENDI, VAMOS DECOLAR!"):
            st.session_state.primeiro_acesso = False
            st.rerun()
    st.stop() # Interrompe o restante da página até o usuário clicar no botão

# --- 3. RESTANTE DO CÓDIGO (Só carrega após o botão ser clicado) ---

# Título e Header
st.title("📲 Extrator de Leads em Massa dos Concorrentes")
st.markdown("---")

# Barra Lateral (Sidebar)
with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/", help="Link enviado na mensagem.")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5], value=1.2)
    if st.button("Limpar Cache/Reiniciar"):
        st.session_state.primeiro_acesso = True
        st.rerun()

# Abas de Trabalho
tab1, tab2 = st.tabs(["🔍 1. Extração Direta", "🚀 2. Disparo de Mensagens"])

with tab1:
    st.subheader("Módulo de Mineração")
    url_target = st.text_input("URL da busca (PsyMeet/Psitto):", placeholder="https://www.psymeetsocial.com/busca...")
    if st.button("Iniciar Busca de Leads", help="Vasculha o site em busca de números de WhatsApp."):
        st.warning("Implemente aqui sua lógica de scraping ou use um CSV.")

with tab2:
    uploaded_file = st.file_uploader("📥 Suba sua lista CSV", type=["csv"])
    if uploaded_file:
        # Coloque aqui sua lógica de processamento de CSV e o botão 'Abrir WhatsApp'
        st.success("Lista carregada com sucesso!")