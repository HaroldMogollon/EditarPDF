import streamlit as st
import os
import io
import tempfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -------------------------------------------------
# CONFIGURACIÓN DE LA APP
# -------------------------------------------------
st.set_page_config(
    page_title=" FOMAG - PDF",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Goleman - FOMAG")

st.markdown("""
Esta herramienta aplica el estampado de **Nombre del Cliente** y **Convenio**
directamente sobre PDFs escaneados (sin campos editables).
""")

# -------------------------------------------------
# FUNCIONES
# -------------------------------------------------
def crear_overlay(cliente, convenio):
    """
    Crea una capa transparente con texto en posiciones fijas.
    Ajusta las coordenadas si tu formato cambia.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # === COORDENADAS (AJUSTABLES) ===
    can.setFont("Helvetica", 9)
    can.drawString(80, 520, cliente)
    can.drawString(80, 505, convenio)

    can.save()
    packet.seek(0)
    return packet


def procesar_pdf(pdf_bytes, cliente, convenio):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    overlay_pdf = PdfReader(crear_overlay(cliente, convenio))

    for page in reader.pages:
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    salida = io.BytesIO()
    writer.write(salida)
    salida.seek(0)
    return salida


# -------------------------------------------------
# INTERFAZ
# -------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.info("### Parámetros de Llenado")

    val_cliente = st.text_input(
        "Nombre del Cliente:",
        value="PATRIMONIO AUTONOMOS FIDUCIARIA LA PREVISORA"
    )

    val_convenio = st.text_input(
        "Convenio:",
        value="FONDO NACIONAL DE PRESTACIONES SOCIALES DEL"
    )

    archivos = st.file_uploader(
        "Sube uno o varios PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

with col2:
    if archivos and st.button("📄 Procesar PDFs"):
        st.success(f"Procesando {len(archivos)} archivo(s)...")

        for archivo in archivos:
            resultado = procesar_pdf(
                archivo.read(),
                val_cliente,
                val_convenio
            )

            st.download_button(
                label=f"⬇️ Descargar {archivo.name}",
                data=resultado,
                file_name=f"EDITADO_{archivo.name}",
                mime="application/pdf"
            )
