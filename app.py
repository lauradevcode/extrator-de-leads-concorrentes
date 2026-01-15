import streamlit as st
import pandas as pd
import re
import requests
from urllib.parse import quote
import streamlit.components.v1 as components

# Configuração da Página
st.set_page_config(page_title="Lead Machine Pro", page_icon="🎯", layout="wide")

# --- ESTADOS DE SESSÃO (Memória do App) ---
if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = 0
if "chamados" not in st.session_state: st.session_state.chamados = set()

# --- CSS PARA DESIGN E ESPAÇAMENTO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .op-row {
        background-color: #1d2129; padding: 25px; border-radius: 15px;
        margin-bottom: 25px; border: 1px solid #2d323d;
    }
    .status-badge { padding: 6px 15px; border-radius: 8px; font-size: 12px; font-weight: bold; }
    .pending { background-color: #3b4252; color: #eceff4; }
    .done { background-color: #25D366; color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE EXTRAÇÃO (BACKEND) ---
def extrair_leads(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Busca padrão de celulares e nomes por proximidade
        telefones = re.findall(r'9\d{4}[-\s]?\d{4}', res.text)
        leads = []
        vistos = set()
        for tel in telefones:
            num = re.sub(r'\D', '', tel)
            num_f = "55" + num if len(num) == 11 else num
            if num_f not in vistos and "984679566" not in num_f:
                vistos.add(num_f)
                leads.append({"name": "Profissional Localizado", "normalized": num_f})
        return pd.DataFrame(leads)
    except: return pd.DataFrame()

# --- INTERFACE POR ABAS ---
tab1, tab2 = st.tabs(["🔍 1. Extrair leads do site", "🚀 2. Disparar Mensagens"])

with tab1:
    st.subheader("Minerador de Contatos")
    url_alvo = st.text_input("URL para extração", placeholder="Cole o link da busca aqui...")
    if st.button("Executar Mineração"):
        with st.spinner("Buscando leads..."):
            df_extraido = extrair_leads(url_alvo)
            if not df_extraido.empty:
                st.success(f"{len(df_extraido)} contatos encontrados!")
                st.dataframe(df_extraido, use_container_width=True)
                csv = df_extraido.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV de Leads", csv, "leads.csv", "text/csv")
            else:
                st.error("Nenhum contato encontrado. Tente outra URL ou suba um CSV manualmente.")

with tab2:
    # Sidebar Configs
    with st.sidebar:
        st.header("⚙️ Ajustes")
        link_dest = st.text_input("Link da sua Bio/Site", "https://psitelemedicina.netlify.app/")
        if st.button("Resetar Histórico"):
            st.session_state.chamados = set()
            st.rerun()

    uploaded = st.file_uploader("Suba o CSV para disparar", type="csv")
    
    if uploaded:
        df = pd.read_csv(uploaded)
        if 'normalized' in df.columns:
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            df = df.drop_duplicates(subset=['tel_limpo'])
            contatos = df.to_dict('records')
            
            # Dashboard
            total = len(contatos)
            atendidos = len(st.session_state.chamados)
            c1, c2 = st.columns(2)
            c1.metric("Leads Totais", total)
            c2.metric("Atendidos", atendidos)
            st.progress(atendidos/total if total > 0 else 0)

            # Lista Operacional
            st.markdown("### 📋 Fila de Trabalho")
            
            itens = 10
            inicio = st.session_state.pagina_atual * itens
            fim = min(inicio + itens, total)
            bloco = contatos[inicio:fim]

            for p in bloco:
                num = p['tel_limpo']
                status = "done" if num in st.session_state.chamados else "pending"
                label = "✅ CHAMADO" if num in st.session_state.chamados else "⏳ PENDENTE"
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 2])
                    col1.markdown(f"**{p.get('name', 'Profissional')}**<br><small>{num}</small>", unsafe_allow_html=True)
                    col2.markdown(f'<span class="status-badge {status}">{label}</span>', unsafe_allow_html=True)
                    
                    # Logica de disparo: Botão Real
                    msg = f"Olá! Conheça meu projeto: {link_dest}"
                    url_wa = f"https://wa.me/{num}?text={quote(msg)}"
                    
                    # Aqui está a correção: O botão dispara o JS e atualiza o estado
                    if num not in st.session_state.chamados:
                        if col3.button(f"Abrir WhatsApp", key=f"btn_{num}"):
                            # 1. Marca como chamado
                            st.session_state.chamados.add(num)
                            # 2. Comando JS para abrir aba
                            components.html(f"<script>window.open('{url_wa}', '_blank');</script>", height=0)
                            # 3. Recarrega para mudar a cor do status na hora
                            st.rerun()
                    else:
                        col3.write("Concluído")

            # Navegação no Rodapé (UX corrigida)
            st.divider()
            b1, b2, b3 = st.columns([1, 2, 1])
            if b1.button("⬅️ Anterior") and st.session_state.pagina_atual > 0:
                st.session_state.pagina_atual -= 1
                st.rerun()
            b2.markdown(f"<center>Página {st.session_state.pagina_atual + 1}</center>", unsafe_allow_html=True)
            if b3.button("Próximo ➡️") and (st.session_state.pagina_atual + 1) * itens < total:
                st.session_state.pagina_atual += 1
                st.rerun()
        else:
            st.error("O CSV deve conter a coluna 'normalized'.")
    else:
        st.info("Aguardando upload de leads...")