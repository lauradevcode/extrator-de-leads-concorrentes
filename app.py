import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
import streamlit.components.v1 as components

# 1. Configuracao da Pagina
st.set_page_config(page_title="Lead Machine Pro", layout="wide")

# --- 2. DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    
    /* Dashboard de Metricas */
    .metric-card {
        background-color: #161b22; padding: 20px; border-radius: 4px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: 700; color: #ffffff; }
    .metric-lab { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }

    /* Card de Lead Individual - Layout Horizontal */
    .lead-container {
        background-color: #161b22;
        padding: 16px 24px;
        border-radius: 6px;
        border: 1px solid #30363d;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Estilizacao do Botao para nao quebrar o layout */
    div.stButton > button {
        background-color: #00a884;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 4px;
        font-weight: 600;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #008f6f;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTADOS DE SESSAO ---
if "chamados" not in st.session_state: st.session_state.chamados = set()
if "pagina" not in st.session_state: st.session_state.pagina = 0

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: white;'>Ajustes de Operacao</h3>", unsafe_allow_html=True)
    link_destino = st.text_input("Link da sua Bio/Site", "https://psitelemedicina.netlify.app/")
    registros_pag = st.select_slider("Registros por pagina", options=[10, 20, 50], value=10)
    if st.button("Resetar Historico"):
        st.session_state.chamados = set()
        st.session_state.pagina = 0
        st.rerun()

# --- 5. AREA PRINCIPAL ---
st.markdown("<h2 style='color: white; margin-bottom: 25px;'>Gerenciador de Leads</h2>", unsafe_allow_html=True)

t_extrair, t_gestao = st.tabs(["Extracao via URL", "Gestao de Disparos"])

with t_extrair:
    st.text_input("Link para mineracao", placeholder="Insira a URL do diretorio...")
    st.button("Iniciar Extracao")

with t_gestao:
    arquivo = st.file_uploader("Importar base de dados (CSV)", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo)
        
        if 'normalized' in df.columns:
            # Limpeza tecnica dos dados
            df['tel_limpo'] = df['normalized'].astype(str).str.replace('+', '', regex=False).str.strip()
            contatos = df.drop_duplicates(subset=['tel_limpo']).to_dict('records')
            total_leads = len(contatos)
            total_chamados = len(st.session_state.chamados)

            # Dashboard Superior
            m1, m2, m3 = st.columns(3)
            m1.markdown(f'<div class="metric-card"><div class="metric-lab">Total Unicos</div><div class="metric-val">{total_leads}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-card"><div class="metric-lab">Chamados</div><div class="metric-val">{total_chamados}</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-card"><div class="metric-lab">Restante</div><div class="metric-val">{total_leads - total_chamados}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Logica de Paginacao
            inicio = st.session_state.pagina * registros_pag
            fim = min(inicio + registros_pag, total_leads)
            bloco = contatos[inicio:fim]

            # Listagem com UI Otimizada
            for p in bloco:
                num = p['tel_limpo']
                status_concluido = num in st.session_state.chamados
                
                # Criamos uma linha com colunas para alinhar Nome/Telefone e Botao
                col_info, col_status, col_acao = st.columns([4, 1, 1.5])
                
                with col_info:
                    st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            <div style="color: white; font-weight: 600; font-size: 16px;">{p.get('name', 'Profissional')}</div>
                            <div style="color: #8b949e; font-size: 13px;">{num}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_status:
                    if status_concluido:
                        st.markdown('<div style="margin-top: 10px; color: #00a884; font-size: 12px; font-weight: bold;">CONCLUIDO</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="margin-top: 10px; color: #8b949e; font-size: 12px; font-weight: bold;">PENDENTE</div>', unsafe_allow_html=True)

                with col_acao:
                    if not status_concluido:
                        if st.button("Abrir WhatsApp", key=f"btn_{num}"):
                            st.session_state.chamados.add(num)
                            
                            # Preparar Mensagem
                            texto = quote(f"Ola {p.get('name', 'Doutor(a)')}, conheca meu projeto: {link_destino}")
                            url_wa = f"https://wa.me/{num}?text={texto}"
                            
                            # Injetar Script de abertura sem quebrar o VS Code
                            js_script = f'window.open("{url_wa}", "_blank");'
                            components.html(f"<script>{js_script}</script>", height=0)
                            
                            time.sleep(0.5)
                            st.rerun()
                
                st.markdown("<hr style='margin: 5px 0; border-color: #1d2129;'>", unsafe_allow_html=True)

            # Navegacao de Paginas
            st.markdown("<br>", unsafe_allow_html=True)
            n_prev, n_center, n_next = st.columns([1, 2, 1])
            if n_prev.button("Anterior") and st.session_state.pagina > 0:
                st.session_state.pagina -= 1
                st.rerun()
            n_center.markdown(f"<center style='color: #8b949e;'>Pagina {st.session_state.pagina + 1}</center>", unsafe_allow_html=True)
            if n_next.button("Proximo") and (st.session_state.pagina + 1) * registros_pag < total_leads:
                st.session_state.pagina += 1
                st.rerun()
        else:
            st.error("Coluna 'normalized' nao encontrada no CSV.")