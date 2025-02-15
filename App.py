import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import requests
import tempfile
import uuid  # Para generar IDs únicos
import time  # Para manejar los reintentos

# 🔹 Cargar credenciales desde Streamlit Secrets
firebase_creds = st.secrets["FIREBASE"]

# 🔹 Inicializar Firebase usando las credenciales de Secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(firebase_creds))
    firebase_admin.initialize_app(cred, {"databaseURL": firebase_creds["databaseURL"]})

st.title("🎬 Transcriptor con Whisper API y Firebase en Streamlit Cloud")

# 🔹 Obtener API Key de Hugging Face desde Secrets
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
HF_API_KEY = st.secrets["HUGGINGFACE"]["API_KEY"]

# 🔹 Subir archivo de audio
uploaded_file = st.file_uploader("📤 Sube tu archivo de audio", type=["mp3", "wav", "m4a"])

# 🔹 Especificar la duración y temática del video final
duracion = st.slider("⏳ Duración deseada del video (en segundos)", 15, 120, 60)
tematica = st.text_input("🎯 Especifica la temática del video", "Motivación, Educación, Entretenimiento...")

# 🔹 Procesar el audio si se subió un archivo
if uploaded_file is not None:
    st.write("⏳ Procesando la transcripción...")

    # 🔹 Guardar el archivo en un directorio temporal
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_audio_path = temp_file.name

    # 🔹 Enviar el archivo a Hugging Face API para transcribirlo con reintentos
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    data = {"return_timestamps": True}  # ✅ Asegura que la API interprete bien el formato

    transcripcion = "❌ No se pudo obtener la transcripción"
    max_retries = 5
    wait_time = 20  # Segundos de espera entre intentos

    for i in range(max_retries):
        with open(temp_audio_path, "rb") as f:
            response = requests.post(HF_API_URL, headers=headers, files={"file": f}, json=data)  # ✅ Usa `json=data`

        if response.status_code == 200:
            transcripcion = response.json()["text"]
            break
        elif "is currently loading" in response.text:
            st.warning(f"⚠️ El modelo está cargando. Reintentando en {wait_time} segundos... ({i+1}/{max_retries})")
            time.sleep(wait_time)
        else:
            transcripcion = f"❌ Error en la transcripción: {response.text}"
            break

    # 🔹 Simulación de generación de timestamps
    timestamps = "[00:00:05] Introducción\n[00:01:20] Punto clave"
    partes_interesantes = "El momento más importante del video es..."

    # 🔹 Guardar los datos en Firebase con un ID único
    transcripcion_id = str(uuid.uuid4())
    ref = db.reference(f"/transcripciones/{transcripcion_id}")
    ref.set({
        "texto": transcripcion,
        "duracion": duracion,
        "tematica": tematica,
        "timestamps": timestamps,
        "partes_interesantes": partes_interesantes
    })

    st.success(f"✅ Transcripción guardada en Firebase con ID: {transcripcion_id}")

    # 🔹 Mostrar la transcripción
    st.subheader("📜 Transcripción:")
    st.text_area("Texto", transcripcion, height=200)

    st.subheader("⏳ Timestamps Generados:")
    st.text_area("Timestamps", timestamps, height=150)

    st.subheader("🔥 Partes Más Impactantes para Redes Sociales:")
    st.text_area("Partes Clave", partes_interesantes, height=150)
