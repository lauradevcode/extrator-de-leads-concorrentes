import streamlit as st
import pandas as pd
import webbrowser
import time
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Extrator de leads concorrentes", page_icon="🚀", layout="wide")

# --- CSS CUSTOMIZADO PARA DESIGN PREMIUM ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #25D366; /* Verde WhatsApp */
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        border: none;
        color: white;
    }
    .metric-card {
        background-color: #1d2129;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2d323d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("📲 Extrator de leads de site para o whatsapp")
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações de Envio")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay entre abas (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0, 3.0], value=1.2)
    st.divider()
    st.caption("Desenvolvido para automação de convites PsyMeet.")

# --- AREA DE TEXTO ---
copy_template = st.text_area(
    "📝 Personalize sua Mensagem", 
    "Olá {nome}! Tudo bem? Vi seu perfil no PsyMeet e achei seu trabalho fantástico. Estou expandindo um projeto para viabilizar atendimentos online com mais tecnologia e gostaria de te convidar para conhecer: {link}",
    height=120
)

# --- UPLOAD E PROCESSAMENTO ---
uploaded_file = st.file_uploader("📤 Suba sua lista (CSV)", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    # Processamento dos dados (Lógica original)
    if 'normalized' in df_raw.columns:
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total = len(contatos)

        # Dashboard de Status
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f'<div class="metric-card"><h5>Total Únicos</h5><h2>{total}</h2></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="metric-card"><h5>Status Arquivo</h5><h2 style="color: #25D366;">Pronto</h2></div>', unsafe_allow_html=True)
        with col_m3:
            if "bloco_atual" not in st.session_state:
                st.session_state.bloco_atual = 0
            progresso_pct = min(st.session_state.bloco_atual / total, 1.0)
            st.markdown(f'<div class="metric-card"><h5>Progresso</h5><h2>{progresso_pct:.0%}</h2></div>', unsafe_allow_html=True)

        st.markdown("### 🔍 Visualização do Próximo Bloco")
        
        # Definição do Bloco
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        lista_bloco = contatos[inicio:fim]

        # --- EXIBIÇÃO DOS NÚMEROS (TABELA) ---
        if lista_bloco:
            df_preview = pd.DataFrame(lista_bloco)[['name', 'tel_limpo']]
            df_preview.columns = ['Nome do Profissional', 'Número de WhatsApp']
            st.dataframe(df_preview, use_container_width=True)
            
            st.info(f"O botão abaixo abrirá o contato de **{inicio}** até **{fim}**.")
            
            # --- BOTÃO DE AÇÃO ---
            if st.button(f"🚀 ABRIR BLOCO ({inicio} - {fim})"):
                progresso_bar = st.progress(0)
                for idx, pessoa in enumerate(lista_bloco):
                    numero = pessoa['tel_limpo']
                    nome_completo = str(pessoa['name']) if pd.notna(pessoa['name']) else "Doutor(a)"
                    primeiro_nome = nome_completo.split()[0].capitalize()
                    
                    texto_msg = copy_template.format(nome=primeiro_nome, link=link_projeto)
                    link_whatsapp = f"https://web.whatsapp.com/send?phone={numero}&text={quote(texto_msg)}"
                    
                    webbrowser.open(link_whatsapp)
                    time.sleep(delay)
                    progresso_bar.progress((idx + 1) / len(lista_bloco))
                
                st.session_state.bloco_atual += 10
                st.rerun() # Atualiza a tela para mostrar o próximo bloco
        else:
            st.success("🎉 Todos os contatos foram processados!")
            if st.button("Recomeçar Lista"):
                st.session_state.bloco_atual = 0
                st.rerun()

    else:
        st.error("A coluna 'normalized' não foi encontrada no arquivo.")