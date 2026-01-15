import streamlit as st

# --- LÓGICA DO MODAL DE BOAS-VINDAS ---
@st.dialog("🚀 Bem-vindo ao Extrator de Leads!")
def boas_vindas():
    st.markdown("""
    ### Como extrair e disparar em 3 passos:
    
    1. **🔍 Extração:** Vá na aba **Extração**, cole a URL do concorrente e clique em iniciar. Ao terminar, **baixe o arquivo CSV**.
    2. **📤 Upload:** Mude para a aba **Disparo** e suba o arquivo CSV que você acabou de baixar.
    3. **⚡ Ação:** Personalize sua mensagem na barra lateral e clique em **Abrir WhatsApp** para iniciar os contatos.
    
    ---
    *Dica: Use a tag `{nome}` na sua mensagem para chamar o lead pelo nome!*
    """)
    if st.button("Entendi, vamos começar!"):
        st.session_state.primeiro_acesso = False
        st.rerun()

# Verifica se é o primeiro acesso na sessão
if "primeiro_acesso" not in st.session_state:
    st.session_state.primeiro_acesso = True

if st.session_state.primeiro_acesso:
    boas_vindas()