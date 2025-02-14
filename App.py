import streamlit as st
import requests
import tempfile
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Configurar la URL de la Web App de Google Apps Script
script_url = "https://script.google.com/macros/s/TU_NUEVA_URL_DEL_SCRIPT/exec"

st.title("🎬 Generador de Clips para Redes Sociales")

# Subir archivo de audio
uploaded_file = st.file_uploader("📤 Sube tu archivo de audio", type=["mp3", "wav", "m4a"])

# Especificar la duración y temática del video final
duracion = st.slider("⏳ Duración deseada del video (en segundos)", 15, 120, 60)
tematica = st.text_input("🎯 Especifica la temática del video", "Motivación, Educación, Entretenimiento...")

# Botón para procesar el audio
if uploaded_file is not None:
    with st.spinner("⏳ Subiendo archivo a Google Drive..."):
        # Autenticación con Google Drive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Subir el archivo a Google Drive
        file_drive = drive.CreateFile({"title": uploaded_file.name})
        file_drive.SetContentFile(temp_file_path)
        file_drive.Upload()

        # Obtener el ID del archivo subido
        file_id = file_drive["id"]

        st.success(f"✅ Archivo subido a Google Drive con ID: {file_id}")

        # Generar el enlace para que Google Colab procese el archivo
        colab_url = f"https://colab.research.google.com/drive/TU_ID_DEL_NOTEBOOK?file_id={file_id}"

        st.markdown(f"📌 **Abre este enlace en Google Colab para procesar la transcripción:** [Abrir Colab]({colab_url})")

        # Eliminar el archivo temporal
        os.remove(temp_file_path)
