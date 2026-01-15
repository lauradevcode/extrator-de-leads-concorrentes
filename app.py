import streamlit as st
import pandas as pd
import time
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Disparador Pro", page_icon="🚀", layout="wide")

# Inicialização do estado de controle
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0

st.title("📲 Disparador de Leads (Modo Online)")

with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do seu Site", "https://psitelemedicina.netlify.app/")
    if st.button("🔄 Reiniciar Lista"):
        st.session_state.bloco_atual = 0
        st.rerun()

# --- UPLOAD ---
uploaded_file = st.file_uploader("📤 Suba sua lista CSV", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    if 'normalized' in df_raw.columns:
        # Limpeza de dados baseada no seu script original
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)] # Filtro de suporte
        
        contatos = df.to_dict('records')
        total = len(contatos)
        
        # Controle de Bloco
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        lista_bloco = contatos[inicio:fim]

        st.markdown(f"### 📋 Bloco Atual: {inicio} até {fim} (Total: {total})")
        
        # CRIANDO OS BOTÕES DE DISPARO
        for pessoa in lista_bloco:
            nome_completo = str(pessoa.get('name', 'Doutor(a)'))
            primeiro_nome = nome_completo.split()[0].capitalize()
            numero = pessoa['tel_limpo']
            
            # Montagem da mensagem
            texto_msg = f"Olá {primeiro_nome}! Tudo bem? Vi seu perfil e gostaria de te convidar para conhecer: {link_projeto}"
            link_wa = f"https://wa.me/{numero}?text={quote(texto_msg)}"
            
            # Layout de linha com botão individual
            col_nome, col_btn = st.columns([3, 1])
            col_nome.write(f"**{nome_completo}** ({numero})")
            col_btn.get_window_extent # Espaçador
            col_btn.link_button(f"✉️ Enviar para {primeiro_nome}", link_wa)

        st.divider()
        
        # Botão para avançar para o próximo bloco
        if fim < total:
            if st.button("➡️ CARREGAR PRÓXIMOS 10"):
                st.session_state.bloco_atual += 10
                st.rerun()
        else:
            st.success("🎉 Todos os leads foram listados!")
    else:
        st.error("A coluna 'normalized' não foi encontrada.")