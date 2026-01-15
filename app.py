import streamlit as st
import pandas as pd
import time
import re
import requests
from urllib.parse import quote
from io import BytesIO

# Configuração da Página
st.set_page_config(page_title="Lead Machine Pro", page_icon="🎯", layout="wide")

# --- CSS PARA UX E ESPAÇAMENTO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #1d2129;
        border-radius: 10px 10px 0 0; color: white; padding: 10px 20px;
    }
    .op-row {
        background-color: #1d2129; padding: 20px; border-radius: 12px;
        margin-bottom: 20px; border: 1px solid #2d323d;
    }
    .status-badge { padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; }
    .pending { background-color: #3b4252; color: #eceff4; }
    .done { background-color: #25D366; color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND DE EXTRAÇÃO (Lógica Separada) ---
def backend_extractor(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        # Busca telefones e nomes (padrão regex)
        telefones = re.findall(r'9\d{4}[-\s]?\d{4}', html)
        leads = []
        vistos = set()
        for tel in telefones:
            num = re.sub(r'\D', '', tel)
            num_final = "55" + num if len(num) == 11 else num
            if num_final not in vistos and "984679566" not in num_final:
                vistos.add(num_final)
                # Tenta pegar nome por proximidade no HTML
                pos = html.find(tel)
                contexto = html[max(0, pos-300):pos]
                nomes = re.findall(r'([A-Z][a-zà-ú]+(?:\s[A-Z][a-zà-ú]+)+)', contexto)
                nome = nomes[-1] if nomes else "Profissional"
                leads.append({"name": nome, "normalized": num_final})
        return pd.DataFrame(leads)
    except:
        return pd.DataFrame()

# --- ESTADOS DE SESSÃO ---
if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = 0
if "contatos_chamados" not in st.session_state: st.session_state.contatos_chamados = set()

# --- INTERFACE ---
st.title("🎯 Lead Machine: Extração e Conversão")

tab1, tab2 = st.tabs(["🔍 1. Extração via URL (Backend)", "🚀 2. Operação de Disparo"])

with tab1:
    st.markdown("### Backend de Mineração")
    st.caption("Insira a URL do site. O sistema irá vasculhar, organizar e gerar um CSV pronto para uso.")
    
    url_input = st.text_input("URL do Site Alvo", placeholder="https://www.psymeetsocial.com/busca...")
    
    if st.button("Executar Extração Eficiente"):
        with st.spinner("O Backend está processando os dados..."):
            df_result = backend_extractor(url_input)
            if not df_result.empty:
                st.success(f"Encontrados {len(df_result)} leads!")
                st.dataframe(df_result, use_container_width=True)
                
                # Conversão para CSV para download
                csv = df_result.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Lista de Leads (CSV)",
                    data=csv,
                    file_name="leads_extraidos.csv",
                    mime="text/csv"
                )
                st.info("💡 Após baixar, suba o arquivo na aba 'Operação de Disparo'.")
            else:
                st.error("Não foi possível extrair dados desta URL automaticamente.")

with tab2:
    # Modal de boas-vindas discreto
    if "df_trabalho" not in st.session_state:
        st.markdown("""
            <div style="background-color: #1d2129; padding: 25px; border-radius: 12px; border: 1px dashed #25D366;">
                <h4 style="color: #25D366; margin:0;">👋 Boas-vindas à Operação</h4>
                <p style="color: #8892b0; font-size: 14px;">Suba o CSV gerado na aba anterior ou um arquivo próprio para iniciar os disparos.</p>
            </div>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Configurações")
        link_projeto = st.text_input("Link no WhatsApp", "https://psitelemedicina.netlify.app/")
        itens_pag = st.select_slider("Leads por página", options=[10, 20, 50], value=10)
        if st.button("Limpar Histórico de Cliques"):
            st.session_state.contatos_chamados = set()
            st.rerun()

    uploaded_file = st.file_uploader("📥 Suba seu CSV aqui", type=["csv"])

    if uploaded_file:
        df_op = pd.read_csv(uploaded_file)
        if 'normalized' in df_op.columns:
            # Limpeza
            df_op['tel_limpo'] = df_op['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            df_op = df_op.drop_duplicates(subset=['tel_limpo'])
            df_op = df_op[~df_op['tel_limpo'].str.contains('984679566', na=False)]
            
            contatos = df_op.to_dict('records')
            total = len(contatos)
            
            # Dashboard
            chamados = len(st.session_state.contatos_chamados)
            c1, c2, c3 = st.columns(3)
            c1.metric("Leads na Lista", total)
            c2.metric("Atendidos", chamados)
            c3.metric("Faltam", total - chamados)
            st.progress(chamados/total if total > 0 else 0)

            # Lista Operacional
            st.markdown("### 📋 Fila de Contatos")
            
            inicio = st.session_state.pagina_atual * itens_pag
            fim = min(inicio + itens_pag, total)
            bloco = contatos[inicio:fim]

            for pessoa in bloco:
                num = pessoa['tel_limpo']
                nome = str(pessoa.get('name', 'Profissional'))
                
                # Correção do Status: Só entra no set se o botão for realmente clicado
                foi_clicado = num in st.session_state.contatos_chamados
                status_class = "done" if foi_clicado else "pending"
                status_text = "✅ CHAMADO" if foi_clicado else "⏳ PENDENTE"

                with st.container():
                    col_n, col_t, col_s, col_a = st.columns([3, 2, 2, 2])
                    col_n.markdown(f"**{nome}**")
                    col_t.code(num, language=None)
                    col_s.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', unsafe_allow_html=True)
                    
                    msg = f"Olá {nome.split()[0]}! Tudo bem? Conheça meu projeto: {link_projeto}"
                    link_wa = f"https://wa.me/{num}?text={quote(msg)}"
                    
                    # Link button não aciona callback, então usamos um truque de UX: 
                    # Um checkbox ou botão de confirmação ao lado, ou apenas o link.
                    # Para marcar como feito, o ideal no Streamlit é um botão normal que abre o link via js ou link_button e o usuário marca um check.
                    # Vou usar o link_button e um botão de "Marcar como Feito" para garantir a jornada.
                    if not foi_clicado:
                        if col_a.button(f"⚡ Iniciar", key=f"btn_{num}"):
                            st.session_state.contatos_chamados.add(num)
                            # Abre o link em nova aba usando JS (Hack para Streamlit manter estado)
                            js = f"window.open('{link_wa}')"
                            st.components.v1.html(f"<script>{js}</script>", height=0)
                            st.rerun()
                    else:
                        col_a.write("---")

            # Navegação no Rodapé
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2, b3 = st.columns([1, 2, 1])
            if b1.button("⬅️ Bloco Anterior") and st.session_state.pagina_atual > 0:
                st.session_state.pagina_atual -= 1
                st.rerun()
            b2.markdown(f"<center>Página {st.session_state.pagina_atual + 1}</center>", unsafe_allow_html=True)
            if b3.button("Próximo Bloco ➡️") and (st.session_state.pagina_atual + 1) * itens_pag < total:
                st.session_state.pagina_atual += 1
                st.rerun()