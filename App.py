import streamlit as st
import requests
import tempfile
import os
import time

# Configurar la API de Replicate para Whisper
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
HEADERS = {"Authorization": "Token r8_H7DMSYNn6XQ6XyZ4r9T1o4h9FeACDFx2Lvpoa"}  # Reemplaza con tu API Key de Replicate

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
    with st.spinner("⏳ Procesando la transcripción con Replicate..."):
        # Guardar archivo temporalmente
        temp_file_path = f"/tmp/{uploaded_file.name}"

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())

        # Enviar el archivo a Replicate
        with open(temp_file_path, "rb") as f:
            files = {"audio": f}
            data = {
                "version": "openai/whisper",
                "input": {
                    "audio": f"data:audio/mpeg;base64,{uploaded_file.getvalue().hex()}"
                }
            }
            response = requests.post(REPLICATE_API_URL, headers=HEADERS, json=data)

        if response.status_code == 200:
            prediction_url = response.json()["urls"]["get"]

            # Esperar a que Replicate procese el audio
            for _ in range(10):  # Intentos de consulta cada 5 segundos
                transcription_response = requests.get(prediction_url, headers=HEADERS)
                if transcription_response.status_code == 200 and "output" in transcription_response.json():
                    text_transcription = transcription_response.json()["output"]
                    st.success("✅ Transcripción completada.")
                    break
                time.sleep(5)  # Espera antes de volver a consultar

            if text_transcription == "No se ha generado ninguna transcripción.":
                st.error("❌ Error: La transcripción no se completó a tiempo.")

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
        st.text_area("Timestamps", timestamps, height=150, key="timestamps_area")

        st.subheader("🔥 Partes Más Impactantes para Redes Sociales:")
        st.text_area("Partes Clave", partes_interesantes, height=150, key="partes_interesantes_area")

        # Guardar los resultados en un archivo descargable
        with open("contenido_redes_sociales.txt", "w") as f:
            f.write(contenido)

        st.download_button("📥 Descargar Resultados", "contenido_redes_sociales.txt")

        # Eliminar el archivo temporal
        os.remove(temp_file_path)
