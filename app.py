import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from fpdf import FPDF

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zeladoria Digital Pro", layout="wide", page_icon="🏛️")

# Truque para o iPhone reconhecer a logo como ícone do App na tela de início
st.markdown(
    f"""
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/leonardodossantos1/zeladoria-digital/main/logo.png">
    """,
    unsafe_allow_html=True
)

# Estilização CSS Profissional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS ---
url = "https://docs.google.com/spreadsheets/d/1sgo8CHW_Ng-ZpLs9ZWZCVsXFuP9vEW_QkgM4x5PqeDA/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Lê as colunas de A até H
        data = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6,7])
        return data
    except:
        return pd.DataFrame(columns=["Protocolo", "Ouvidoria", "Tipo", "Endereço", "Data", "Status", "Descrição", "Caminho_Foto"])

df = carregar_dados()
PASTA_FOTOS = "fotos"
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

# --- FUNÇÃO GERAR PDF ---
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatorio Oficial de Zeladoria", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Protocolo Interno: {dados['Protocolo']}", ln=True)
    pdf.cell(200, 10, f"Protocolo Ouvidoria: {dados['Ouvidoria']}", ln=True)
    pdf.cell(200, 10, f"Data do Registro: {dados['Data']}", ln=True)
    pdf.cell(200, 10, f"Categoria: {dados['Tipo']}", ln=True)
    pdf.cell(200, 10, f"Local: {dados['Endereço']}", ln=True)
    pdf.cell(200, 10, f"Status: {dados['Status']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Descricao dos Fatos:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"{dados['Descrição']}")
    
    if os.path.exists(str(dados['Caminho_Foto'])):
        pdf.ln(10)
        pdf.image(dados['Caminho_Foto'], x=10, w=100)
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- HEADER COM LOGO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        logo_img = Image.open("logo.png")
        st.image(logo_img, width=110)
    except:
        st.write("🏛️") # Emoji reserva caso a logo não carregue

with col_titulo:
    st.title("Zeladoria Digital Pro")
    st.caption("Gestão Inteligente de Manutenção Urbana | Conectado ao Google Sheets")

aba1, aba2 = st.tabs(["📝 REGISTRAR OCORRÊNCIA", "📊 DASHBOARD E GESTÃO"])

# --- ABA 1: REGISTRO ---
with aba1:
    with st.container():
        st.subheader("📋 Nova Denúncia")
        with st.form("form_denuncia", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                protocolo = st.text_input("Número do Protocolo Interno", placeholder="Ex: 001/2026")
                ouvidoria = st.text_input("Protocolo da Ouvidoria (opcional)", placeholder="Ex: n°2212348")
                tipo = st.selectbox("O que aconteceu?", [
                    "Buraco", "Mato Alto", "Iluminação", "Calçada", "Bueiro Entupido",
