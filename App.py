import streamlit as st
import json
import requests
import os
import pandas as pd
import pysrt
from google.generativeai import GenerativeModel
from keybert import KeyBERT

# Configuración de la API de Gemini
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configuración de la app
st.set_page_config(page_title="Freaky Video Assistant", layout="wide")

# Cargar el logo
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://raw.githubusercontent.com/TU_REPOSITORIO/logo.png" width="50">
        <h1 style="margin: 0;">Freaky Video Assistant 🎬</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Título de la aplicación
st.subheader("Upload your SRT file and generate a Premiere-compatible MXL file")

# Subir el archivo SRT
uploaded_file = st.file_uploader("Choose an SRT file", type=["srt"])

# Campo para ingresar el prompt del usuario
user_prompt = st.text_area(
    "Describe the theme, tone, and focus for the video selection:",
    "Extract the most engaging and relevant moments for a short video (up to 90 seconds).",
)

# Botón para procesar
if st.button("Generate MXL File"):
    if uploaded_file is not None and user_prompt.strip():
        try:
            # Leer el archivo SRT
            srt_content = uploaded_file.read().decode("utf-8")
            subs = pysrt.from_string(srt_content)

            # Convertir SRT en texto plano para el análisis
            transcript_text = "\n".join([sub.text for sub in subs])

            # Modelo de IA para la selección de contenido
            model = GenerativeModel("gemini-pro", api_key=GEMINI_API_KEY)
            response = model.generate_content(f"Analyze this transcription and select the best moments based on this prompt: {user_prompt}\n\n{transcript_text}")

            # Extraer la respuesta de la IA
            selected_text = response.text

            # Mostrar la previsualización del texto seleccionado
            st.subheader("Selected Content Preview")
            st.write(selected_text)

            # Generar un archivo MXL compatible con Adobe Premiere
            mxl_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <mxl>
                <transcription>{selected_text}</transcription>
            </mxl>"""

            # Guardar archivo y ofrecer descarga
            mxl_file = "output.mxl"
            with open(mxl_file, "w", encoding="utf-8") as f:
                f.write(mxl_content)

            st.download_button("Download MXL File", data=mxl_content, file_name="output.mxl", mime="application/xml")

        except Exception as e:
            st.error(f"❌ Error generating MXL: {str(e)}")
    else:
        st.warning("Please upload an SRT file and enter a prompt before generating the MXL file.")

