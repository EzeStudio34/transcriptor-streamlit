import streamlit as st
import requests
import tempfile
import os
import time

# Configurar la API de AssemblyAI
ASSEMBLYAI_API_URL = "https://api.assemblyai.com/v2/transcript"
HEADERS = {"Authorization": "8f5c18f7060042baacac252cb9f9c6ad"}  # Reemplaza con tu API Key de AssemblyAI

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

# Función para transcribir audio con AssemblyAI
def transcribir_audio_assemblyai(audio_path):
    """Envía un archivo de audio a AssemblyAI y obtiene la transcripción"""
    with open(audio_path, "rb") as f:
        response = requests.post(
            ASSEMBLYAI_API_URL, headers=HEADERS, files={"audio": f}
        )

    if response.status_code == 200:
        transcript_id = response.json()["id"]
        return transcript_id
    else:
        return None

# Función para obtener la transcripción procesada
def obtener_transcripcion_assemblyai(transcript_id):
    """Consulta el estado de la transcripción en AssemblyAI"""
    url = f"{ASSEMBLYAI_API_URL}/{transcript_id}"
    
    for _ in range(10):  # Intentos de consulta cada 5 segundos
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200 and response.json()["status"] == "completed":
            return response.json()["text"]
        time.sleep(5)

    return None

# Procesar el audio si se subió un archivo
if uploaded_file is not None:
    with st.spinner("⏳ Procesando la transcripción con AssemblyAI..."):
        # Guardar archivo temporalmente
        temp_file_path = f"/tmp/{uploaded_file.name}"

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())

        # Obtener el ID de la transcripción
        transcript_id = transcribir_audio_assemblyai(temp_file_path)

        if transcript_id:
            # Obtener la transcripción completa
            text_transcription = obtener_transcripcion_assemblyai(transcript_id)

            if text_transcription:
                st.success("✅ Transcripción completada.")
            else:
                st.error("❌ Error: La transcripción no se completó a tiempo.")
        else:
            st.error("❌ Error al enviar el archivo a AssemblyAI.")

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
        st.text_area("Timestamps", timestamps, height=150, key="timestamps_area")

        st.subheader("🔥 Partes Más Impactantes para Redes Sociales:")
        st.text_area("Partes Clave", partes_interesantes, height=150, key="partes_interesantes_area")

        # Guardar los resultados en un archivo descargable
        with open("contenido_redes_sociales.txt", "w") as f:
            f.write(contenido)

        st.download_button("📥 Descargar Resultados", "contenido_redes_sociales.txt")

        # Eliminar el archivo temporal
        os.remove(temp_file_path)
