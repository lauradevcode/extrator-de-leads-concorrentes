import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Extrator Pro", page_icon="📲", layout="wide")

# Inicialização de estados
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0
if "leads_extraidos" not in st.session_state:
    st.session_state.leads_extraidos = None

# --- CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #25D366; color: white; font-weight: bold; }
    .metric-card { background-color: #1d2129; padding: 15px; border-radius: 10px; border: 1px solid #2d323d; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def extrair_leads_da_url(url):
    try:
        header = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=header, timeout=10)
        html = response.text
        # Busca padrões de telefone brasileiros (simplificado)
        padrao = re.findall(r'(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9\d{4}[-\s]?\d{4}', html)
        leads = list(set([re.sub(r'\D', '', p) for p in padrao])) # Limpa e remove duplicados
        
        # Cria um formato compatível com o seu disparador
        lista_formatada = [{"name": f"Lead {i+1}", "tel_limpo": tel} for i, tel in enumerate(leads)]
        return lista_formatada
    except Exception as e:
        st.error(f"Erro ao acessar site: {e}")
        return []

st.title("📲 Extrator e Disparador Inteligente")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Reiniciar Tudo"):
        st.session_state.bloco_atual = 0
        st.session_state.leads_extraidos = None
        st.rerun()

# --- INTERFACE PRINCIPAL ---
tab1, tab2 = st.tabs(["🔍 Extração Automática", "🚀 Gerenciar Envio"])

with tab1:
    url_alvo = st.text_input("Cole a URL para buscar leads (ex: psitto.com.br)")
    if st.button("🔍 Vasculhar Site agora"):
        with st.spinner("Procurando números de contato..."):
            leads = extrair_leads_da_url(url_alvo)
            if leads:
                st.session_state.leads_extraidos = leads
                st.success(f"Sucesso! Encontramos {len(leads)} leads no site.")
            else:
                st.warning("Nenhum lead encontrado automaticamente. Por favor, suba um arquivo CSV na aba de Disparo.")

with tab2:
    copy_template = st.text_area("📝 Sua Mensagem", "Olá {nome}! Tudo bem? Veja meu projeto: {link}", height=100)
    
    # LÓGICA DE DADOS: Prioriza Extração, depois CSV
    dados_para_envio = None
    
    if st.session_state.leads_extraidos:
        st.info("💡 Usando leads extraídos automaticamente do site.")
        dados_para_envio = st.session_state.leads_extraidos
    else:
        uploaded_file = st.file_uploader("📤 Nenhum lead extraído. Suba seu CSV:", type=["csv"])
        if uploaded_file:
            df_raw = pd.read_csv(uploaded_file)
            if 'normalized' in df_raw.columns:
                df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
                df = df_raw.drop_duplicates(subset=['tel_limpo'])
                df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
                dados_para_envio = df.to_dict('records')
            else:
                st.error("Coluna 'normalized' não encontrada no CSV.")

    # Exibição e Disparo
    if dados_para_envio:
        total = len(dados_para_envio)
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        lista_bloco = dados_para_envio[inicio:fim]

        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="metric-card"><h5>Total Leads</h5><h2>{total}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><h5>Bloco</h5><h2>{inicio}-{fim}</h2></div>', unsafe_allow_html=True)

        if lista_bloco:
            st.dataframe(pd.DataFrame(lista_bloco)[['name', 'tel_limpo']], use_container_width=True)
            
            if st.button(f"🚀 ABRIR BLOCO ({inicio} a {fim})"):
                import webbrowser
                for pessoa in lista_bloco:
                    nome = str(pessoa.get('name', 'Doutor(a)')).split()[0].capitalize()
                    texto = copy_template.format(nome=nome, link=link_projeto)
                    link_wa = f"https://web.whatsapp.com/send?phone={pessoa['tel_limpo']}&text={quote(texto)}"
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                st.session_state.bloco_atual += 10
                st.rerun()
        else:
            st.success("🎉 Todos os leads foram processados!")