import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote
import webbrowser

# Configuração da Página
st.set_page_config(page_title="Extrator Pro v4", page_icon="📲", layout="wide")

# Inicialização de estados
if "bloco_atual" not in st.session_state:
    st.session_state.bloco_atual = 0
if "leads_extraidos" not in st.session_state:
    st.session_state.leads_extraidos = None

# --- CSS PARA DESIGN ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #25D366; color: white; font-weight: bold; }
    .metric-card { background-color: #1d2129; padding: 20px; border-radius: 15px; border: 1px solid #2d323d; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def extrair_dados_avancado(url):
    try:
        # Cabeçalhos muito mais completos para parecer um Chrome real no Windows
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive"
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20)
        html = response.text

        # 1. Busca todos os números de telefone possíveis
        # Padrão: 11999999999 ou 5511999999999
        telefones = re.findall(r'9\d{4}[-\s]?\d{4}', html)
        
        leads_finais = []
        vistos = set()

        # 2. Lógica de captura de nomes baseada na estrutura do PsyMeet
        # Procuramos por blocos que contenham o nome antes do telefone
        for tel in telefones:
            limpo = re.sub(r'\D', '', tel)
            # Adiciona o prefixo do Brasil se necessário
            tel_pronto = "55" + limpo if len(limpo) == 11 else limpo
            
            # Filtro anti-suporte e duplicados
            if tel_pronto not in vistos and "984679566" not in tel_pronto:
                vistos.add(tel_pronto)
                
                # Procura o nome: No código do PsyMeet, nomes ficam em tags de título
                pos = html.find(tel)
                contexto = html[max(0, pos-400):pos] # Analisa um trecho maior antes do número
                
                # Busca padrões de nomes próprios (Palavras com inicial maiúscula)
                # Tenta extrair o que parece ser o nome do profissional
                nomes_encontrados = re.findall(r'([A-Z][a-zà-ú]+(?:\s[A-Z][a-zà-ú]+)+)', contexto)
                
                # Pega o último nome encontrado antes do telefone (geralmente o do perfil)
                nome_doc = nomes_encontrados[-1] if nomes_encontrados else "Profissional"
                
                leads_finais.append({"name": nome_doc, "tel_limpo": tel_pronto})

        return leads_finais
    except Exception as e:
        st.error(f"Erro ao acessar site: {e}")
        return []

# --- INTERFACE PRINCIPAL ---
st.title("📲 Extrator e Disparador de Leads")

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    link_projeto = st.text_input("🔗 Link do seu Site", "https://psitelemedicina.netlify.app/")
    delay = st.select_slider("⏲️ Delay entre abas", options=[0.5, 1.0, 1.2, 1.5, 2.0], value=1.2)
    if st.button("🔄 Limpar Cache/Reiniciar"):
        st.session_state.bloco_atual = 0
        st.session_state.leads_extraidos = None
        st.rerun()

tab1, tab2 = st.tabs(["🔍 Extração Direta", "🚀 Disparo de Mensagens"])

with tab1:
    url_target = st.text_input("URL da busca (PsyMeet/Psitto):", placeholder="https://www.psymeetsocial.com/busca")
    if st.button("🚀 Iniciar Busca de Leads"):
        with st.spinner("O robô está tentando contornar a proteção do site..."):
            res = extrair_dados_avancado(url_target)
            if res:
                st.session_state.leads_extraidos = res
                st.success(f"Encontramos {len(res)} leads com sucesso!")
                st.dataframe(pd.DataFrame(res), use_container_width=True)
            else:
                st.error("O site bloqueou o acesso automático. Tente rolar a página até o fim no seu navegador, copie a URL novamente ou use um arquivo CSV.")

with tab2:
    if st.session_state.leads_extraidos:
        dados = st.session_state.leads_extraidos
    else:
        st.warning("Nenhum lead extraído. Use a aba anterior ou suba um CSV abaixo.")
        uploaded = st.file_uploader("Subir CSV", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            # Lógica de processamento de CSV original
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            df = df.drop_duplicates(subset=['tel_limpo'])
            df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
            dados = df.to_dict('records')
        else:
            dados = None

    if dados:
        inicio = st.session_state.bloco_atual
        fim = min(inicio + 10, len(dados))
        bloco = dados[inicio:fim]

        if bloco:
            st.dataframe(pd.DataFrame(bloco), use_container_width=True)
            if st.button(f"🔥 DISPARAR BLOCO ({inicio} a {fim})"):
                for p in bloco:
                    nome = str(p['name']).split()[0].capitalize()
                    msg = f"Olá {nome}! Vi seu perfil e achei fantástico. Conheça meu projeto: {link_projeto}"
                    link_wa = f"https://web.whatsapp.com/send?phone={p['tel_limpo']}&text={quote(msg)}"
                    webbrowser.open(link_wa)
                    time.sleep(delay)
                st.session_state.bloco_atual += 10
                st.rerun()