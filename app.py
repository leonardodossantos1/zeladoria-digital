import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from fpdf import FPDF
import streamlit.components.v1 as components

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zeladoria Digital Pro", layout="wide", page_icon="🏛️")

# URL RAW DIRETA DO GITHUB (Para Ícone e Logo)
LOGO_URL = "https://raw.githubusercontent.com/leonardodossantos1/zeladoria-digital/main/logo.png"

# INJEÇÃO PARA ÍCONE DO IPHONE E ESCONDER RODAPÉ PADRÃO
components.html(
    f"""
    <script>
        var link = window.parent.document.createElement('link');
        link.rel = 'apple-touch-icon';
        link.href = '{LOGO_URL}?v={datetime.now().second}';
        window.parent.document.getElementsByTagName('head')[0].appendChild(link);
    </script>
    """,
    height=0,
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS ---
url = "https://docs.google.com/spreadsheets/d/1sgo8CHW_Ng-ZpLs9ZWZCVsXFuP9vEW_QkgM4x5PqeDA/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        return conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6,7])
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
    pdf.cell(200, 10, f"Protocolo: {dados['Protocolo']}", ln=True)
    pdf.cell(200, 10, f"Data: {dados['Data']}", ln=True)
    pdf.multi_cell(0, 10, f"Local: {dados['Endereço']}")
    pdf.multi_cell(0, 10, f"Descricao: {dados['Descrição']}")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- SIDEBAR COM ASSINATURA ---
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
st.caption("Gestão de Manutenção Urbana | Matão-SP")

aba1, aba2 = st.tabs(["📝 REGISTRAR OCORRÊNCIA", "📊 DASHBOARD E GESTÃO"])

with aba1:
    st.subheader("📋 Nova Denúncia")
    with st.form("form_denuncia", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            protocolo = st.text_input("Protocolo Interno")
            ouvidoria = st.text_input("Protocolo Ouvidoria")
            tipo = st.selectbox("Tipo", ["Buraco", "Mato Alto", "Iluminação", "Calçada", "Esgoto", "Outros"])
        with col_b:
            endereco = st.text_input("Endereço")
            foto = st.file_uploader("Foto", type=["jpg", "png"])
        
        descricao = st.text_area("Descrição do Problema")
        
        if st.form_submit_button("CONCLUIR REGISTRO"):
            if protocolo and endereco:
                caminho_foto = "fotos/no_image.jpg"
                nova_linha = {
                    "Protocolo": protocolo, "Ouvidoria": ouvidoria if ouvidoria else "Não informado",
                    "Tipo": tipo, "Endereço": endereco, "Data": datetime.now().strftime("%d/%m/%Y"), 
                    "Status": "Sem Resposta", "Descrição": descricao, "Caminho_Foto": caminho_foto
                }
                
                df_atualizado = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                
                try:
                    conn.update(spreadsheet=url, data=df_atualizado)
                    st.success("✅ Protocolo salvo com sucesso no Google Sheets!")
                    st.rerun()
                except Exception:
                    st.error("⚠️ Erro de Permissão (Google Sheets bloqueou a gravação).")
                    st.info("Para salvar automaticamente, você precisa configurar a 'Service Account' no Streamlit Cloud.")
                    st.code(f"Backup para cópia: {protocolo} - {endereco}")
            else:
                st.error("Protocolo e Endereço são campos obrigatórios.")

with aba2:
    if df.empty:
        st.info("Nenhuma denúncia registrada na base de dados.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Total", len(df))
        m2.metric("Pendentes", len(df[df["Status"] == "Sem Resposta"]))
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        
        prot_sel = st.selectbox("Gerar PDF de:", df["Protocolo"].unique())
        resumo = df[df["Protocolo"] == prot_sel].iloc[0]
        pdf_bytes = gerar_pdf(resumo)
        st.download_button("📥 BAIXAR RELATÓRIO PDF", pdf_bytes, f"Relatorio_{prot_sel}.pdf")

# --- RODAPÉ PERSONALIZADO ---
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; padding: 25px;'>
        <hr style='border: 0.5px solid #e9ecef;'>
        <p style='font-size: 0.9em; line-height: 1.6;'>
            <strong>Developed by Leonardo Dos Santos (PL-SP)</strong><br>
            Tecnologia para uma fiscalização urbana eficiente e transparente.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
