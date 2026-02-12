import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from PIL import Image
from fpdf import FPDF

# --- CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="Zeladoria Digital Pro", layout="wide", page_icon="🏛️")

# CSS para visual profissional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS ---
# SUBSTITUA PELO SEU LINK ABAIXO:
url = "https://docs.google.com/spreadsheets/d/1sgo8CHW_Ng-ZpLs9ZWZCVsXFuP9vEW_QkgM4x5PqeDA/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Lê as colunas A até H
        data = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6,7])
        return data
    except:
        return pd.DataFrame(columns=["Protocolo", "Ouvidoria", "Tipo", "Endereço", "Data", "Status", "Descrição", "Caminho_Foto"])

df = carregar_dados()
PASTA_FOTOS = "fotos"
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

# --- FUNÇÃO PDF ---
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatorio de Zeladoria Urbana", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    fields = [("Protocolo Interno", 'Protocolo'), ("Protocolo Ouvidoria", 'Ouvidoria'), 
              ("Data", 'Data'), ("Categoria", 'Tipo'), ("Endereco", 'Endereço'), ("Status", 'Status')]
    for label, key in fields:
        pdf.cell(200, 10, f"{label}: {dados[key]}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Descricao: {dados['Descrição']}")
    if os.path.exists(str(dados['Caminho_Foto'])):
        pdf.ln(10)
        pdf.image(dados['Caminho_Foto'], x=10, w=100)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACE ---
st.title("🏛️ Zeladoria Digital Pro")
st.caption("Conectado ao Google Sheets | Relatórios PDF")

aba1, aba2 = st.tabs(["📝 REGISTRAR OCORRÊNCIA", "📊 DASHBOARD E GESTÃO"])

with aba1:
    with st.container():
        st.subheader("📋 Nova Denúncia")
        with st.form("form_denuncia", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                protocolo = st.text_input("Número do Protocolo Interno", placeholder="Ex: 001/2026")
                ouvidoria = st.text_input("Número do Protocolo da Ouvidoria", placeholder="Ex: n°2212348")
                tipo = st.selectbox("O que aconteceu?", [
                    "Buraco", "Mato Alto", "Iluminação", "Calçada", "Bueiro Entupido",
                    "Transporte Público", "Mobilidade Urbana", "Trânsito", 
                    "Desalinhamento De Fios Em Rede Pública", "Canil", "Dengue", 
                    "Água", "Esgoto", "Outros"
                ])
            with col_b:
                endereco = st.text_input("Endereço Completo", placeholder="Rua, Número, Bairro")
                foto = st.file_uploader("Subir foto do local", type=["jpg", "png", "jpeg"])
            
            descricao = st.text_area("Relato detalhado para o post")
            
            if st.form_submit_button("CONCLUIR REGISTRO"):
                if protocolo and endereco:
                    caminho_foto = "fotos/no_image.jpg"
                    if foto:
                        nome_limpo = protocolo.replace('/', '_').replace('\\', '_')
                        caminho_foto = f"{PASTA_FOTOS}/{nome_limpo}.jpg"
                        with open(caminho_foto, "wb") as f: f.write(foto.getbuffer())
                    
                    nova_linha = {
                        "Protocolo": protocolo, "Ouvidoria": ouvidoria if ouvidoria else "Não informado",
                        "Tipo": tipo, "Endereço": endereco, "Data": datetime.now().strftime("%d/%m/%Y"), 
                        "Status": "Sem Resposta", "Descrição": descricao, "Caminho_Foto": caminho_foto
                    }
                    
                    # Salva no Google Sheets
                    df_atualizado = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                    conn.update(spreadsheet=url, data=df_atualizado)
                    
                    st.success(f"✅ Protocolo {protocolo} salvo no Google Sheets!")
                    
                    with st.expander("✨ Texto para Instagram"):
                        texto = f"🚨 DESCASO: {tipo.upper()}!\n📍 Local: {endereco}\n🆔 Protocolo: {protocolo}\n📞 Ouvidoria: {ouvidoria}\n\n#Zeladoria #Cidadania"
                        st.code(texto)
                else:
                    st.error("Preencha os campos obrigatórios.")

with aba2:
    if df.empty:
        st.info("Nenhuma denúncia encontrada na planilha.")
    else:
        # Métricas
        m1, m2, m3 = st.columns(3)
        m1.metric("Total", len(df))
        m2.metric("Concluídas", len(df[df["Status"] == "Concluído"]))
        m3.metric("Pendentes", len(df[df["Status"] == "Sem Resposta"]))
        
        st.divider()
        col_esq, col_dir = st.columns([1.2, 1])
        
        with col_esq:
            st.subheader("📈 Panorama")
            fig = px.pie(df, names='Status', hole=.4, color='Status', 
                         color_discrete_map={'Sem Resposta': '#E74C3C', 'Em Análise': '#F1C40F', 
                                            'Em Andamento': '#3498DB', 'Concluído': '#2ECC71'})
            st.plotly_chart(fig, use_container_width=True)

        with col_dir:
            st.subheader("🔍 Gestão")
            prot_sel = st.selectbox("Selecione o Protocolo:", df["Protocolo"].unique())
            resumo = df[df["Protocolo"] == prot_sel].iloc[0]
            
            with st.container(border=True):
                if os.path.exists(str(resumo['Caminho_Foto'])):
                    st.image(resumo['Caminho_Foto'], use_container_width=True)
                
                pdf_bytes = gerar_pdf(resumo)
                st.download_button("📥 BAIXAR PDF", pdf_bytes, f"Relatorio_{prot_sel}.pdf", "application/pdf")
                
                novo_st = st.selectbox("Alterar Status:", ["Sem Resposta", "Em Análise", "Em Andamento", "Concluído"],
                                       index=["Sem Resposta", "Em Análise", "Em Andamento", "Concluído"].index(resumo['Status']))
                
                if st.button("SALVAR ATUALIZAÇÃO"):
                    df.loc[df["Protocolo"] == prot_sel, "Status"] = novo_st
                    conn.update(spreadsheet=url, data=df)
                    st.success("Status atualizado no Google Sheets!")
                    st.rerun()

        st.divider()

        st.dataframe(df, use_container_width=True)

