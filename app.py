import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import streamlit.components.v1 as components

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zeladoria Digital Pro", layout="wide", page_icon="🏛️")

# Identidade Visual
LOGO_URL = "https://raw.githubusercontent.com/leonardodossantos1/zeladoria-digital/main/logo.png"

# Injeção para ícone e remover rodapé padrão
components.html(
    f"""
    <script>
        var link = window.parent.document.createElement('link');
        link.rel = 'apple-touch-icon';
        link.href = '{LOGO_URL}';
        window.parent.document.getElementsByTagName('head')[0].appendChild(link);
    </script>
    """,
    height=0,
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; font-weight: bold; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS (USANDO SECRETS) ---
# Aqui o 'gsheets' procura automaticamente o que você colou lá no Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Ele lê a planilha principal definida nas configurações
        return conn.read(ttl=0) # ttl=0 garante que ele busque o dado mais novo sempre
    except:
        return pd.DataFrame(columns=["Protocolo", "Ouvidoria", "Tipo", "Endereço", "Data", "Status", "Descrição", "Caminho_Foto"])

df = carregar_dados()

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.title("🏛️ Zeladoria")
    st.divider()
    st.markdown("### 👨‍💻 Desenvolvedor")
    st.info("**Leonardo Dos Santos (PL-SP)**")

# --- HEADER ---
st.title("Zeladoria Digital Pro")
st.caption("Fiscalização e Gestão Urbana | Matão-SP")

aba1, aba2 = st.tabs(["📝 REGISTRAR OCORRÊNCIA", "📊 DASHBOARD"])

with aba1:
    with st.form("form_denuncia", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            protocolo = st.text_input("Protocolo Interno")
            tipo = st.selectbox("Tipo", ["Buraco", "Mato Alto", "Iluminação", "Calçada", "Esgoto", "Outros"])
        with col_b:
            endereco = st.text_input("Endereço")
            foto = st.file_uploader("Foto da Ocorrência", type=["jpg", "png"])
        
        descricao = st.text_area("Descrição Detalhada")
        
        if st.form_submit_button("CONCLUIR REGISTRO"):
            if protocolo and endereco:
                # Criar nova linha
                nova_linha = pd.DataFrame([{
                    "Protocolo": protocolo,
                    "Ouvidoria": "Não informado",
                    "Tipo": tipo,
                    "Endereço": endereco,
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Status": "Sem Resposta",
                    "Descrição": descricao,
                    "Caminho_Foto": "fotos/no_image.jpg"
                }])
                
                # Adicionar ao DataFrame atual
                df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
                
                # SALVAR NO GOOGLE SHEETS
                try:
                    conn.update(data=df_atualizado)
                    st.success("✅ Registro enviado com sucesso para a planilha!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Campos obrigatórios: Protocolo e Endereço.")

with aba2:
    if df.empty:
        st.info("Nenhum dado encontrado.")
    else:
        st.metric("Total de Registros", len(df))
        st.dataframe(df, use_container_width=True)

# --- RODAPÉ PERSONALIZADO ---
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; padding: 25px;'>
        <hr>
        <p><strong>Developed by Leonardo Dos Santos (PL-SP)</strong><br>
        Tecnologia para uma fiscalização urbana eficiente e transparente.</p>
    </div>
    """,
    unsafe_allow_html=True
)
