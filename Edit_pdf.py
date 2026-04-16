import streamlit as st
import os
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Gestión Asistencial - FOMAG", page_icon="🏥", layout="wide")

def seleccionar_carpeta():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    ruta = filedialog.askdirectory(master=root)
    root.destroy()
    return ruta

def crear_overlay(cliente, convenio):
    """
    Crea una capa transparente con los datos en las coordenadas 
    específicas según el formato de tu PDF.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Configuración de fuente (Helvetica es estándar y limpia)
    can.setFont("Helvetica", 7)
    
    # --- COORDENADAS CALCULADAS ---
    # En PDF, (0,0) es la esquina inferior izquierda.
    # Los valores se miden en puntos (1 pulgada = 72 puntos).
    
    # Posición para 'PATRIMONIOS AUTONOMOS'
    # Se ubica a la derecha de la etiqueta "Nombre del Cliente:"
    can.drawString(110, 598, cliente) 
    
    # Posición para 'FOMAG'
    # Se ubica a la derecha de la etiqueta "Convenio:"
    can.drawString(410, 598, convenio) 
    
    can.save()
    packet.seek(0)
    return packet

# --- CUERPO DE LA APLICACIÓN ---
st.title("🏥 Procesador Masivo de Formatos - Goleman's")
st.markdown("""
Esta herramienta aplica el estampado de **Nombre del Cliente** y **Convenio** directamente sobre los PDFs escaneados (sin campos editables).
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.info("### Parámetros de Llenado")
    val_cliente = st.text_input("Nombre del Cliente:", value="PATRIMONIO AUTONOMOS FIDUCIARIA LA PREVISORA")
    val_convenio = st.text_input("Convenio:", value="FONDO NACIONAL DE PRESTACIONES SOCIALES DEL")
    
    st.divider()
    if st.button("📁 Seleccionar Carpeta y Ejecutar"):
        ruta_origen = seleccionar_carpeta()
        if ruta_origen:
            st.session_state['ruta'] = ruta_origen
        else:
            st.error("No se seleccionó ninguna carpeta.")

with col2:
    if 'ruta' in st.session_state:
        ruta = st.session_state['ruta']
        archivos = [f for f in os.listdir(ruta) if f.lower().endswith('.pdf')]
        
        st.success(f"**Carpeta origen:** {ruta}")
        st.write(f"Archivos encontrados: **{len(archivos)}**")

        if st.button("🚀 Iniciar Procesamiento"):
            ruta_dest = os.path.join(ruta, "Editados")
            if not os.path.exists(ruta_dest):
                os.makedirs(ruta_dest)

            exitos = 0
            barra = st.progress(0)
            status = st.empty()

            for i, nombre_archivo in enumerate(archivos):
                try:
                    path_full = os.path.join(ruta, nombre_archivo)
                    
                    # Leer original
                    original_pdf = PdfReader(path_full)
                    output = PdfWriter()

                    # Crear el texto a estampar
                    overlay_data = crear_overlay(val_cliente, val_convenio)
                    overlay_pdf = PdfReader(overlay_data)

                    # Fusionar con la primera página
                    primera_pagina = original_pdf.pages[0]
                    primera_pagina.merge_page(overlay_pdf.pages[0])
                    output.add_page(primera_pagina)

                    # Copiar el resto de páginas si existen
                    for n_pag in range(1, len(original_pdf.pages)):
                        output.add_page(original_pdf.pages[n_pag])

                    # Guardar resultado
                    with open(os.path.join(ruta_dest, nombre_archivo), "wb") as f:
                        output.write(f)
                    
                    exitos += 1
                    status.text(f"Procesando: {nombre_archivo}")
                except Exception as e:
                    st.error(f"Error en {nombre_archivo}: {e}")
                
                barra.progress((i + 1) / len(archivos))

            st.success(f"✅ Proceso terminado. {exitos} documentos guardados en la carpeta /Editados.")
            #st.balloons()
