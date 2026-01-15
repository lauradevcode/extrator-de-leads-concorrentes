import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Extrator Pro v2", page_icon="📲", layout="wide")

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

def extrair_leads_inteligente(url):
    try:
        # Simulando um navegador real para evitar bloqueios e acessar mais dados
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text

        # Regex aprimorada para capturar números brasileiros em diversos formatos
        # Captura: +5511999999999, 11999999999, (11) 99999-9999, etc.
        pattern_tel = r'(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9\d{4}[-\s]?\d{4}'
        telefones_crus = re.findall(pattern_tel, html_content)
        
        leads = []
        vistos = set()

        for tel in telefones_crus:
            limpo = re.sub(r'\D', '', tel)
            # Garante que tem o 55 no início se o usuário esqueceu
            if len(limpo) == 11: limpo = "55" + limpo
            
            # Filtro de segurança (Evita o suporte do PsyMeet e duplicados)
            if limpo not in vistos and "984679566" not in limpo:
                vistos.add(limpo)
                
                # Tenta buscar um nome no texto ao redor do número (Lógica de proximidade)
                # No PsyMeet, nomes geralmente estão em tags <h3> ou <span> próximas
                pos = html_content.find(tel)
                trecho = html_content[max(0, pos-150):pos] # Pega 150 caracteres antes do número
                
                # Procura por padrões de nomes (Letra maiúscula seguida de minúsculas)
                nomes_encontrados = re.findall(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)', trecho)
                nome_final = nomes_encontrados[-1] if nomes_encontrados else "Profissional"
                
                leads.append({"name": nome_final, "tel_limpo": limpo})

        return leads
    except Exception as e:
        st.error(f"Erro na extração: {e}")
        return []

st.title("📲 Extrator e Disparador de Leads")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do Projeto", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Reiniciar Tudo"):
        st.session_state.bloco_atual = 0
        st.session_state.leads_extraidos = None
        st.rerun()

# --- ABAS ---
tab1, tab2 = st.tabs(["🔍 Vasculhar Site", "🚀 Disparar Mensagens"])

with tab1:
    url_input = st.text_input("Insira a URL do PsyMeet ou similar:", placeholder="https://www.psymeet.com.br/busca...")
    if st.button("Iniciar Extração Profissional"):
        with st.spinner("O robô está analisando o código do site..."):
            resultados = extrair_leads_inteligente(url_input)
            if resultados:
                st.session_state.leads_extraidos = resultados
                st.success(f"Encontramos {len(resultados)} leads com sucesso!")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.error("Não foi possível extrair leads automaticamente desta URL. O site pode estar protegido ou os dados são carregados apenas por scroll.")

with tab2:
    if st.session_state.leads_extraidos:
        dados = st.session_state.leads_extraidos
        st.info("✅ Usando leads extraídos da URL.")
    else:
        uploaded_file = st.file_uploader("📤 Sem extração ativa. Suba seu CSV:", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if 'normalized' in df.columns:
                df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).strip()
                df = df.drop_duplicates(subset=['tel_limpo'])
                df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
                dados = df.to_dict('records')
            else:
                st.error("Coluna 'normalized' não encontrada.")
                dados = None
        else:
            dados = None

    if dados:
        total = len(dados)
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        bloco = dados[inicio:fim]

        if bloco:
            st.subheader(f"Bloco Atual: {inicio} a {fim}")
            # Botão de disparo original
            if st.button(f"🚀 ABRIR BLOCO ({len(bloco)} abas)"):
                import webbrowser
                for p in bloco:
                    nome = str(p.get('name', 'Doutor(a)')).split()[0].capitalize()
                    msg = f"Olá {nome}! Tudo bem? Vi seu perfil e convido você para o projeto: {link_projeto}"
                    link_wa = f"https://web.whatsapp.com/send?phone={p['tel_limpo']}&text={quote(msg)}"
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                st.session_state.bloco_atual += 10
                st.rerun()