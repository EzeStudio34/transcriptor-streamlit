import streamlit as st
import requests
import tempfile
import os

# Configurar la API de Hugging Face para Whisper
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
HEADERS = {"Authorization": "Bearer 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"}  # Reemplaza con tu API Key de Hugging Face

# Configurar la URL de la Web App de Google Apps Script
script_url = "https://script.google.com/macros/s/TU_NUEVA_URL_DEL_SCRIPT/exec"

st.title("🎬 Generador de Clips para Redes Sociales")

# Subir archivo de audio
uploaded_file = st.file_uploader("📤 Sube tu archivo de audio", type=["mp3", "wav", "m4a"])

# Especificar la duración y temática del video final
duracion = st.slider("⏳ Duración deseada del video (en segundos)", 15, 120, 60)
tematica = st.text_input("🎯 Especifica la temática del video", "Motivación, Educación, Entretenimiento...")

# Variable inicial para la transcripción
text_transcription = "No se ha generado ninguna transcripción."

# Procesar el audio si se subió un archivo
if uploaded_file is not None:
    with st.spinner("⏳ Procesando la transcripción con Whisper en la nube..."):
        # Guardar archivo temporalmente
        temp_file_path = f"/tmp/{uploaded_file.name}"

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())

        # Enviar el archivo a Hugging Face para transcripción
        with open(temp_file_path, "rb") as f:
            files = {"file": (uploaded_file.name, f, "audio/mpeg")}
            response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, files=files)

        if response.status_code == 200:
            text_transcription = response.json().get("text", "No se pudo obtener la transcripción.")
            st.success("✅ Transcripción completada.")
        else:
            st.error(f"❌ Error en la transcripción. Código de error: {response.status_code}")

        # Enviar la transcripción a Google Sheets para análisis con ChatGPT
        data = {"texto": text_transcription, "duracion": duracion, "tematica": tematica}
        response = requests.post(script_url, json=data)

        st.success("✅ Transcripción enviada. Generando contenido optimizado...")

        # Obtener los resultados de la Web App de Google Sheets
        response = requests.get(script_url)
        contenido = response.text

        # Dividir el contenido recibido en Timestamps y Partes Interesantes
        contenido_dividido = contenido.split("\n\n")
        timestamps = contenido_dividido[0] if len(contenido_dividido) > 0 else "No se encontraron timestamps."
        partes_interesantes = contenido_dividido[1] if len(contenido_dividido) > 1 else "No se encontraron partes interesantes."

        # Mostrar los resultados en la interfaz con claves únicas
        st.subheader("📜 Transcripción:")
        st.text_area("Transcripción", text_transcription, height=200, key="transcripcion_area")

        st.subheader("⏳ Timestamps Generados:")
       
