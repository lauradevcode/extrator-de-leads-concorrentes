import streamlit as st
import pandas as pd
import time
import webbrowser
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Disparador de Leads Pro", page_icon="📲", layout="wide")

# Inicialização do estado do bloco
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0

# --- INTERFACE ---
st.title("📲 Gerenciador de Disparos")

with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do seu Site", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5], value=1.2)
    if st.button("🔄 Reiniciar Lista"):
        st.session_state.bloco_atual = 0
        st.rerun()

# --- DISPARO POR CSV (SOLUÇÃO GARANTIDA) ---
st.markdown("### 📂 Upload da Lista de Leads")
uploaded_file = st.file_uploader("Suba o arquivo CSV extraído do navegador:", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    # Lógica de limpeza do disparo_final.py
    if 'normalized' in df_raw.columns:
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        # Remove o suporte do PsyMeet
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total = len(contatos)
        
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        lista_bloco = contatos[inicio:fim]

        # Dashboard de Progresso
        st.write(f"📊 **Progresso:** {inicio} de {total} contatos processados.")
        
        if lista_bloco:
            # Tabela do próximo bloco
            df_view = pd.DataFrame(lista_bloco)[['name', 'tel_limpo']]
            st.dataframe(df_view, use_container_width=True)
            
            if st.button(f"🚀 ABRIR PRÓXIMAS 10 JANELAS ({inicio} - {fim})"):
                for pessoa in lista_bloco:
                    nome = str(pessoa['name']).split()[0].capitalize() if pd.notna(pessoa['name']) else "Doutor(a)"
                    msg = f"Olá {nome}! Tudo bem? Veja meu projeto: {link_projeto}"
                    link_wa = f"https://web.whatsapp.com/send?phone={pessoa['tel_limpo']}&text={quote(msg)}"
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                
                st.session_state.bloco_atual += 10
                st.rerun()
        else:
            st.success("🎉 Fim da lista! Todos os contatos foram abertos.")