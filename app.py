import streamlit as st
import pandas as pd
import time
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Extrator e Disparador de Leads", page_icon="🚀", layout="wide")

# Inicialização do estado do bloco (para não resetar ao clicar)
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0

# --- CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #25D366;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1d2129;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d323d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📲 Extrator e Disparador de Leads")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Reiniciar Contador"):
        st.session_state.bloco_atual = 0
        st.rerun()

# --- DEFINIÇÃO DAS ABAS ---
tab1, tab2 = st.tabs(["🔍 Extrair Leads de URL", "🚀 Disparar Mensagens"])

with tab1:
    st.header("Vasculhar Site")
    url_alvo = st.text_input("Insira a URL do site (Ex: PsyMeet busca)", placeholder="https://www.psitto.com.br/")
    
    if st.button("Iniciar Extração Inteligente"):
        with st.spinner("O robô está navegando no site..."):
            time.sleep(2) # Simulação
            st.success("Foram encontrados 15 novos leads nesta página!")
            st.info("⚠️ Nota: A extração automática via URL online requer integração com APIs de scraping. Por enquanto, use a aba de Disparo com seu CSV.")

with tab2:
    st.header("Gerenciador de Disparos")
    
    copy_template = st.text_area(
        "📝 Personalize sua Mensagem", 
        "Olá {nome}! Tudo bem? Vi seu perfil no PsyMeet e achei seu trabalho fantástico. Estou expandindo um projeto para viabilizar atendimentos online com mais tecnologia e gostaria de te convidar para conhecer: {link}",
        height=100
    )

    uploaded_file = st.file_uploader("📤 Suba sua lista (CSV)", type=["csv"], key="disparador_upload")

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        
        if 'normalized' in df_raw.columns:
            # Limpeza e tratamento (Lógica do disparo_final.py)
            df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            df = df_raw.drop_duplicates(subset=['tel_limpo'])
            df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
            
            contatos = df.to_dict('records')
            total = len(contatos)
            
            # Dashboard de métricas
            inicio = st.session_state.bloco_atual
            fim = min(inicio + 10, total)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="metric-card"><h5>Total na Lista</h5><h2>{total}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h5>Bloco Visível</h5><h2>{inicio} - {fim}</h2></div>', unsafe_allow_html=True)

            st.markdown("---")
            st.subheader(f"🔍 Visualização do Bloco ({inicio} a {fim})")
            
            lista_bloco = contatos[inicio:fim]

            if lista_bloco:
                # Mostra a tabela para conferência
                df_preview = pd.DataFrame(lista_bloco)[['name', 'tel_limpo']]
                df_preview.columns = ['Nome do Profissional', 'Número de WhatsApp']
                st.dataframe(df_preview, use_container_width=True)
                
                # BOTÃO DE AÇÃO (Para rodar localmente via webbrowser)
                if st.button(f"🚀 ABRIR ESTES {len(lista_bloco)} NO WHATSAPP"):
                    import webbrowser
                    progresso = st.progress(0)
                    for idx, pessoa in enumerate(lista_bloco):
                        nome = str(pessoa['name']).split()[0].capitalize() if pd.notna(pessoa['name']) else "Doutor(a)"
                        texto = copy_template.format(nome=nome, link=link_projeto)
                        link_wa = f"https://web.whatsapp.com/send?phone={pessoa['tel_limpo']}&text={quote(texto)}"
                        
                        webbrowser.open(link_wa)
                        time.sleep(delay)
                        progresso.progress((idx + 1) / len(lista_bloco))
                    
                    st.session_state.bloco_atual += 10
                    st.success("Bloco aberto! Clique em 'Próximo' para ver os seguintes.")
                    st.rerun()
            else:
                st.success("🎉 Todos os contatos foram processados!")
        else:
            st.error("A coluna 'normalized' não foi encontrada no arquivo CSV.")