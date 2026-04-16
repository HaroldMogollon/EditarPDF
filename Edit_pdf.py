import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import zipfile

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Gestión Asistencial - FOMAG",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Procesador Masivo de Formatos - Goleman's")
st.markdown("""
Esta herramienta aplica el estampado de **Nombre del Cliente** y **Convenio**
directamente sobre PDFs escaneados (sin campos editables).
""")

# --- FORMULARIO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.info("### Parámetros de Llenado")
    val_cliente = st.text_input(
        "Nombre del Cliente:",
        value="PATRIMONIO AUTÓNOMO FIDUCIARIA LA PREVISORA"
    )
    val_convenio = st.text_input(
        "Convenio:",
        value="FONDO NACIONAL DE PRESTACIONES SOCIALES DEL"
    )

with col2:
    uploaded_files = st.file_uploader(
        "📂 Carga uno o varios PDFs",
        type="pdf",
        accept_multiple_files=True
    )

# --- FUNCIÓN OVERLAY ---
def crear_overlay(cliente, convenio):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # ⬇️ Ajusta coordenadas según tu formato real
    can.setFont("Helvetica", 9)
    can.drawString(120, 520, cliente)
    can.drawString(120, 500, convenio)

    can.save()
    packet.seek(0)
    return packet

# --- PROCESAMIENTO ---
if uploaded_files and st.button("🚀 Procesar PDFs"):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in uploaded_files:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()

            overlay_pdf = PdfReader(crear_overlay(val_cliente, val_convenio))
            overlay_page = overlay_pdf.pages[0]

            for page in reader.pages:
                page.merge_page(overlay_page)
                writer.add_page(page)

            output_pdf = io.BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)

            zip_file.writestr(pdf_file.name, output_pdf.read())

    zip_buffer.seek(0)

    st.success("✅ Procesamiento finalizado")
    st.download_button(
        label="📥 Descargar PDFs procesados",
        data=zip_buffer,
        file_name="pdfs_procesados.zip",
        mime="application/zip"
    )
