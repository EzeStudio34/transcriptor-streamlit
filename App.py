import streamlit as st
import requests
import whisper
import tempfile
import os

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
    with st.spinner("⏳ Procesando la transcripción..."):
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Transcribir con Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(temp_file_path)
        text_transcription = result["text"]

        # Enviar la transcripción a Google Sheets para análisis con ChatGPT
        data = {"texto": text_transcription, "duracion": duracion, "tematica": tematica}
        response = requests.post(script_url, json=data)

        st.success("✅ Transcripción enviada. Generando contenido optimizado...")

        # Obtener los resultados de la Web App de Google Sheets
        response = requests.get(script_url)
        contenido = response.text

        # Mostrar la transcripción y los fragmentos optimizados
        st.subheader("📜 Transcripción:")
        st.text_area("", text_transcription, height=200)

        st.subheader("⏳ Timestamps Generados:")
        st.text_area("", contenido.split("\n\n")[0], height=150)

        st.subheader("🔥 Partes Más Impactantes para Redes Sociales:")
        st.text_area("", contenido.split("\n\n")[1], height=150)

        # Botón para descargar los resultados
        with open("contenido_redes_sociales.txt", "w") as f:
            f.write(contenido)

        st.download_button("📥 Descargar Resultados", "contenido_redes_sociales.txt")
        
        # Eliminar el archivo temporal
        os.remove(temp_file_path)
