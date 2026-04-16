import streamlit as st
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
st.set_page_config(
    page_title="Gestión Asistencial - FOMAG",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Procesador de PDFs - FOMAG")

st.write("App cargada correctamente ✅")

# -------------------------------------------------
# FUNCIONES
# -------------------------------------------------
def crear_overlay(cliente, convenio):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica", 9)
    c.drawString(80, 520, cliente)
    c.drawString(80, 505, convenio)

    c.save()
    buffer.seek(0)
    return buffer


def procesar_pdf(pdf_bytes, cliente, convenio):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    overlay = PdfReader(crear_overlay(cliente, convenio))

    for page in reader.pages:
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    salida = io.BytesIO()
    writer.write(salida)
    salida.seek(0)
    return salida


# -------------------------------------------------
# INTERFAZ
# -------------------------------------------------
cliente = st.text_input(
    "Nombre del Cliente",
    "PATRIMONIO AUTONOMOS FIDUCIARIA LA PREVISORA"
)

convenio = st.text_input(
    "Convenio",
    "FONDO NACIONAL DE PRESTACIONES SOCIALES DEL"
)

archivos = st.file_uploader(
    "Sube PDFs",
    type="pdf",
    accept_multiple_files=True
)

if archivos:
    st.success(f"{len(archivos)} archivo(s) cargado(s)")

    for archivo in archivos:
        resultado = procesar_pdf(
            archivo.read(),
            cliente,
            convenio
        )

        st.download_button(
            label=f"⬇️ Descargar {archivo.name}",
            data=resultado,
            file_name=f"EDITADO_{archivo.name}",
            mime="application/pdf"
        )
