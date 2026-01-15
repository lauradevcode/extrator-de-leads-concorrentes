import streamlit as st
import pandas as pd
import webbrowser
import time
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Extrator de leads de site para o whatsapp", page_icon="🚀", layout="wide")

# Inicialização do estado do bloco (Crucial para mudar a tela)
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0

# --- CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #25D366;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1d2129;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2d323d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📲 Extrator de leads de site para o whatsapp")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações de Envio")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Reiniciar Lista"):
        st.session_state.bloco_atual = 0
        st.rerun()

# --- AREA DE MENSAGEM ---
copy_template = st.text_area("📝 Personalize sua Mensagem", "Olá {nome}! Tudo bem? Vi seu perfil no PsyMeet... {link}", height=100)

# --- PROCESSAMENTO DO ARQUIVO ---
uploaded_file = st.file_uploader("📤 Suba sua lista (CSV)", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    if 'normalized' in df_raw.columns:
        # Limpeza e preparação
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total = len(contatos)
        
        # Dashboard
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        progresso_pct = int((inicio / total) * 100) if total > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="metric-card"><h5>Total Únicos</h5><h2>{total}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><h5>Bloco Atual</h5><h2>{inicio} - {fim}</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><h5>Progresso</h5><h2>{progresso_pct}%</h2></div>', unsafe_allow_html=True)

        st.markdown("### 🔍 Visualização do Próximo Bloco")
        lista_bloco = contatos[inicio:fim]

        if lista_bloco:
            # Mostra a tabela do bloco atual
            df_preview = pd.DataFrame(lista_bloco)[['name', 'tel_limpo']]
            df_preview.columns = ['Nome do Profissional', 'Número de WhatsApp']
            st.dataframe(df_preview, use_container_width=True)
            
            # BOTÃO DE AÇÃO
            if st.button(f"🚀 ABRIR BLOCO ({inicio} até {fim})"):
                for pessoa in lista_bloco:
                    nome = str(pessoa['name']).split()[0].capitalize() if pd.notna(pessoa['name']) else "Doutor(a)"
                    texto = copy_template.format(nome=nome, link=link_projeto)
                    link_wa = f"https://web.whatsapp.com/send?phone={pessoa['tel_limpo']}&text={quote(texto)}"
                    
                    # Abre no navegador (Funciona apenas LOCALMENTE)
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                
                # Atualiza o índice para o próximo bloco e REINICIA a tela
                st.session_state.bloco_atual += 10
                st.rerun() 
        else:
            st.success("🎉 Todos os contatos foram processados!")
    else:
        st.error("Coluna 'normalized' não encontrada.")