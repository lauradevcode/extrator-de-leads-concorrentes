import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote
import webbrowser

# Configuração da Página
st.set_page_config(page_title="Extrator Pro v3", page_icon="📲", layout="wide")

# Inicialização de estados para navegação e dados
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0
if "leads_extraidos" not in st.session_state:
    st.session_state.leads_extraidos = None

# --- CSS PARA DESIGN PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #25D366; color: white; font-weight: bold; height: 3em; }
    .metric-card { background-color: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #2d323d; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def extrair_leads_inteligente(url):
    try:
        # Headers para simular um navegador real e evitar bloqueios
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text

        # Regex para capturar telefones em diversos formatos (brasileiros)
        pattern_tel = r'(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9\d{4}[-\s]?\d{4}'
        matches = re.finditer(pattern_tel, html_content)
        
        leads = []
        vistos = set()

        for match in matches:
            tel_cru = match.group()
            limpo = re.sub(r'\D', '', tel_cru)
            
            # Formatação e Filtros (Ignora suporte PsyMeet e duplicados)
            if len(limpo) == 11: limpo = "55" + limpo
            if limpo not in vistos and "984679566" not in limpo and len(limpo) >= 10:
                vistos.add(limpo)
                
                # Busca o nome próximo ao número (olhando 200 caracteres para trás)
                pos = match.start()
                contexto = html_content[max(0, pos-200):pos]
                # Procura por padrões de nomes (ex: Nome Sobrenome)
                nomes = re.findall(r'>([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)<', contexto)
                nome_final = nomes[-1] if nomes else "Profissional"
                
                leads.append({"name": nome_final, "tel_limpo": limpo})

        return leads
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return []

# --- INTERFACE ---
st.title("📲 Extrator e Disparador de Leads")

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    link_projeto = st.text_input("🔗 Link do seu Site", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay (segundos)", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Limpar Tudo"):
        st.session_state.bloco_atual = 0
        st.session_state.leads_extraidos = None
        st.rerun()

tab1, tab2 = st.tabs(["🔍 Extração via URL", "🚀 Disparar Mensagens"])

with tab1:
    url_input = st.text_input("Cole a URL da busca do PsyMeet:", placeholder="https://www.psymeetsocial.com/busca")
    if st.button("🚀 Iniciar Extração de Leads"):
        with st.spinner("Analisando o site e coletando dados..."):
            resultados = extrair_leads_inteligente(url_input)
            if resultados:
                st.session_state.leads_extraidos = resultados
                st.success(f"✅ {len(resultados)} leads encontrados com sucesso!")
                st.dataframe(pd.DataFrame(resultados), use_container_width=True)
            else:
                st.error("❌ Não encontramos leads. Tente rolar a página no navegador antes de copiar a URL ou suba um CSV.")

with tab2:
    copy_template = st.text_area("📝 Mensagem (use {nome} e {link})", 
        "Olá {nome}! Tudo bem? Vi seu perfil e achei seu trabalho fantástico. Conheça meu projeto: {link}", height=120)
    
    # Decide a fonte dos dados
    dados = st.session_state.leads_extraidos
    if not dados:
        uploaded_file = st.file_uploader("📂 Ou suba seu arquivo CSV:", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if 'normalized' in df.columns:
                df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
                df = df.drop_duplicates(subset=['tel_limpo'])
                df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
                dados = df.to_dict('records')

    if dados:
        total = len(dados)
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, total)
        bloco = dados[inicio:fim]

        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><h5>Total Leads</h5><h2>{total}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h5>Posição Atual</h5><h2>{inicio} - {fim}</h2></div>', unsafe_allow_html=True)

        if bloco:
            st.dataframe(pd.DataFrame(bloco)[['name', 'tel_limpo']], use_container_width=True)
            if st.button(f"🔥 ABRIR BLOCO ({inicio} a {fim})"):
                for p in bloco:
                    nome = str(p.get('name', 'Doutor(a)')).split()[0].capitalize()
                    msg = copy_template.format(nome=nome, link=link_projeto)
                    link_wa = f"https://web.whatsapp.com/send?phone={p['tel_limpo']}&text={quote(msg)}"
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                st.session_state.bloco_atual += 10
                st.rerun()