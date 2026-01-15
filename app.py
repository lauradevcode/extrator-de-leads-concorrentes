import streamlit as st
import pandas as pd
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="CRM de Disparo Pro", page_icon="🎯", layout="wide")

# --- CSS PARA UX AVANÇADA ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Estilização da Tabela de Operação */
    .stTable { background-color: #1d2129; border-radius: 10px; }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .status-pending { background-color: #3b4252; color: #eceff4; }
    .status-done { background-color: #25D366; color: #000; }
    
    /* Botões fixos na linha */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO (Jornada do Usuário) ---
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 0
if "contatos_chamados" not in st.session_state:
    st.session_state.contatos_chamados = set()

# --- SIDEBAR E CONFIGS ---
with st.sidebar:
    st.header("🚀 Jornada de Trabalho")
    link_projeto = st.text_input("🔗 Link de Destino", "https://psitelemedicina.netlify.app/")
    itens_por_pagina = st.select_slider("Leads por tela", options=[5, 10, 15, 20, 50], value=10)
    
    st.divider()
    if st.button("🧹 Limpar Histórico de Cliques"):
        st.session_state.contatos_chamados = set()
        st.rerun()

st.title("🎯 Painel de Operação de Leads")

# --- FLUXO DE TRABALHO ---
uploaded_file = st.file_uploader("📥 Arraste seu CSV para começar", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    if 'normalized' in df_raw.columns:
        # Processamento e Limpeza
        df_raw['tel_limpo'] = df_raw['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
        df = df_raw.drop_duplicates(subset=['tel_limpo'])
        df = df[~df['tel_limpo'].str.contains('984679566', na=False)]
        
        contatos = df.to_dict('records')
        total_leads = len(contatos)
        total_paginas = (total_leads // itens_por_pagina) + (1 if total_leads % itens_por_pagina > 0 else 0)

        # --- INDICADORES DE PERFORMANCE ---
        chamados = len(st.session_state.contatos_chamados)
        progresso_total = chamados / total_leads if total_leads > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Leads Totais", total_leads)
        c2.metric("Já Chamados", chamados)
        c3.metric("Conversão da Lista", f"{progresso_total:.0%}")
        st.progress(progresso_total)

        # --- NAVEGAÇÃO COMPACTA ---
        st.divider()
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        if nav_col1.button("⬅️ Anterior", use_container_width=True) and st.session_state.pagina_atual > 0:
            st.session_state.pagina_atual -= 1
            st.rerun()
            
        nav_col2.markdown(f"<center>Página <b>{st.session_state.pagina_atual + 1}</b> de {total_paginas}</center>", unsafe_allow_html=True)
            
        if nav_col3.button("Próximo ➡️", use_container_width=True) and st.session_state.pagina_atual < total_paginas - 1:
            st.session_state.pagina_atual += 1
            st.rerun()

        # --- LISTA OPERACIONAL (UX MELHORADA) ---
        st.markdown("""
            <div style='display: flex; font-weight: bold; padding: 10px; border-bottom: 2px solid #2d323d;'>
                <div style='flex: 2;'>👤 NOME DO PROFISSIONAL</div>
                <div style='flex: 1;'>📞 WHATSAPP</div>
                <div style='flex: 1;'>🏷️ STATUS</div>
                <div style='flex: 1;'>⚡ AÇÃO</div>
            </div>
        """, unsafe_allow_html=True)

        inicio = st.session_state.pagina_atual * itens_por_pagina
        fim = min(inicio + itens_por_pagina, total_leads)
        bloco = contatos[inicio:fim]

        for i, pessoa in enumerate(bloco):
            nome = str(pessoa.get('name', 'Profissional'))
            p_nome = nome.split()[0].capitalize()
            numero = pessoa['tel_limpo']
            
            # Verifica se já foi clicado nesta sessão
            foi_chamado = numero in st.session_state.contatos_chamados
            status_html = '<span class="status-done">✅ CHAMADO</span>' if foi_chamado else '<span class="status-pending">⏳ PENDENTE</span>'
            
            msg = f"Olá {p_nome}! Tudo bem? Vi seu perfil e gostaria de te convidar para conhecer: {link_projeto}"
            link_wa = f"https://wa.me/{numero}?text={quote(msg)}"

            # Linha da Tabela
            row = st.container()
            with row:
                col_n, col_t, col_s, col_a = st.columns([2, 1, 1, 1])
                col_n.write(f"**{nome}**")
                col_t.code(numero, language=None)
                col_s.markdown(status_html, unsafe_allow_html=True)
                
                # O botão agora atualiza o status ao ser clicado
                if col_a.link_button(f"Falar com {p_nome}", link_wa, use_container_width=True):
                    st.session_state.contatos_chamados.add(numero)

        st.divider()
        st.caption(f"Exibindo leads de {inicio} a {fim}. Use a navegação acima para mudar de página.")

    else:
        st.error("Coluna 'normalized' não encontrada no CSV.")