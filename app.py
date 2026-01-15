import streamlit as st

# --- 1. INICIALIZAÇÃO DO ESTADO ---
if "primeiro_acesso" not in st.session_state:
    st.session_state.primeiro_acesso = True

# --- 2. DEFINIÇÃO DO MODAL (DIALOG) ---
@st.dialog("🚀 Guia Rápido: Operação de Leads")
def mostrar_guia():
    st.markdown("""
    Para uma extração eficiente e disparos sem erros, siga esta ordem:
    
    1. **🔍 Extrair:** Na aba de URL, minere os leads e **baixe o CSV**.
    2. **📤 Subir:** Na aba de Disparo, coloque o arquivo que você baixou.
    3. **⚡ Chamar:** Clique em 'Abrir WhatsApp'. O status mudará para ✅ automaticamente.
    
    *Dica: Ajuste o delay na lateral se o seu PC for lento.*
    """)
    if st.button("Entendi, vamos decolar!"):
        st.session_state.primeiro_acesso = False
        st.rerun()

# --- 3. EXECUÇÃO DO MODAL ---
if st.session_state.primeiro_acesso:
    mostrar_guia()

# --- 4. RESTANTE DO SEU CÓDIGO (Abas, CSS, etc) ---
# ... (insira aqui o código das abas e lógica de disparo)