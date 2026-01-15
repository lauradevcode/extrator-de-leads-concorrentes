import streamlit as st
import pandas as pd
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="CRM Operational Pro", page_icon="🎯", layout="wide")

# --- CSS REFINADO PARA UX/UI ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* Tabelas e Linhas */
    .op-row {
        background-color: #1d2129;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px; /* Espaçamento entre linhas */
        border: 1px solid #2d323d;
        display: flex;
        align-items: center;
    }
    
    /* Status Badges */
    .badge {
        padding: 5px 15px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
    }
    .pending { background-color: #3b4252; color: #eceff4; }
    .done { background-color: #25D366; color: #0e1117; }
    
    /* Tooltip discreto */
    .helper-text {
        color: #8892b0;
        font-size: 0.85rem;
        margin-top: 5px;
    }
    
    /* Ajuste de botões */
    div.stButton > button {
        border-radius: 6px;
        height: 2.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO USUÁRIO ---
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 0
if "contatos_chamados" not in st.session_state:
    st.session_state.contatos_chamados = set()

# --- HEADER E INTRODUÇÃO DISCRETA ---
st.title("🎯 Painel de Operação")
if not st.session_state.contatos_chamados:
    st.info("💡 **Dica de Início:** Suba seu CSV, clique nos botões de ação para abrir o WhatsApp e use a navegação no final da página para ver mais leads.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    link_projeto = st.text_input("🔗 Link do Destino", "https://psitelemedicina.netlify.app/", help="Link que será enviado na mensagem.")
    itens_por_pagina = st.select_slider("Leads por visualização", options=[10, 20, 50], value=10)
    st.divider()
    if st.button("🧹 Limpar Histórico"):
        st.session_state.contatos_chamados = set()
        st.rerun()

# --- WORKFLOW ---
uploaded_file = st.file_uploader("📥 Arraste seu CSV (Ex: phones_full.csv)", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    if 'normalized' in df_raw.columns:
        # Limpeza e Deduplicação
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total_leads = len(contatos)
        total_paginas = (total_leads // itens_por_pagina) + (1 if total_leads % itens_por_pagina > 0 else 0)

        # --- DASHBOARD DE PROGRESSO ---
        chamados = len(st.session_state.contatos_chamados)
        progresso = chamados / total_leads if total_leads > 0 else 0
        
        cols = st.columns(4)
        cols[0].metric("Total", total_leads)
        cols[1].metric("Atendidos", chamados)
        cols[2].metric("Restante", total_leads - chamados)
        cols[3].metric("Meta", f"{progresso:.0%}")
        st.progress(progresso)
        
        st.markdown("### 📋 Fila de Trabalho")
        st.caption("Clique no botão à direita para iniciar a conversa. O status mudará automaticamente.")

        # --- LISTA COM ESPAÇAMENTO UX ---
        inicio = st.session_state.pagina_atual * itens_por_pagina
        fim = min(inicio + itens_por_pagina, total_leads)
        bloco = contatos[inicio:fim]

        for pessoa in bloco:
            nome = str(pessoa.get('name', 'Profissional'))
            primeiro_nome = nome.split()[0].capitalize()
            numero = pessoa['tel_limpo']
            foi_chamado = numero in st.session_state.contatos_chamados
            
            # Mensagem e Link
            msg = f"Olá {primeiro_nome}! Tudo bem? Vi seu perfil e gostaria de te convidar: {link_projeto}"
            link_wa = f"https://wa.me/{numero}?text={quote(msg)}"

            # Container de Linha com UX aprimorada
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                
                c1.markdown(f"**{nome}**")
                c2.code(numero, language=None)
                
                if foi_chamado:
                    c3.markdown('<span class="badge done">✅ CHAMADO</span>', unsafe_allow_html=True)
                else:
                    c3.markdown('<span class="badge pending">⏳ PENDENTE</span>', unsafe_allow_html=True)
                
                # Botão de Ação
                if c4.link_button(f"Falar com {primeiro_nome}", link_wa, use_container_width=True):
                    st.session_state.contatos_chamados.add(numero)
            
            st.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True) # Espaçador manual

        # --- NAVEGAÇÃO NO RODAPÉ (CONFORME SOLICITADO) ---
        st.divider()
        b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
        
        if b_col1.button("⬅️ Bloco Anterior", use_container_width=True) and st.session_state.pagina_atual > 0:
            st.session_state.pagina_atual -= 1
            st.rerun()
            
        b_col2.markdown(f"<center>Página <b>{st.session_state.pagina_atual + 1}</b> de {total_paginas}</center>", unsafe_allow_html=True)
            
        if b_col3.button("Próximo Bloco ➡️", use_container_width=True) and st.session_state.pagina_atual < total_paginas - 1:
            st.session_state.pagina_atual += 1
            st.rerun()
            
    else:
        st.error("A coluna 'normalized' não foi encontrada no arquivo CSV.")
else:
    # Modal/Aviso discreto para novo usuário
    st.markdown("""
        <div style="background-color: #1d2129; padding: 30px; border-radius: 15px; border: 1px dashed #25D366; text-align: center;">
            <h3 style="color: #25D366;">Bem-vindo ao seu CRM de Disparos</h3>
            <p>Siga a jornada abaixo para começar sua prospecção:</p>
            <ol style="display: inline-block; text-align: left; color: #8892b0;">
                <li>Importe sua lista de contatos no formato <b>CSV</b>.</li>
                <li>Verifique o link do seu projeto na <b>barra lateral</b>.</li>
                <li>Clique no botão de cada lead para abrir o WhatsApp.</li>
                <li>Avance as páginas no <b>final da lista</b> conforme concluir os blocos.</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)