import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import whisper
import tempfile
import uuid  # Para generar IDs únicos

# 🔹 Cargar credenciales desde Streamlit Secrets
firebase_creds = st.secrets["FIREBASE"]

# 🔹 Inicializar Firebase usando las credenciales de Secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(firebase_creds))
    firebase_admin.initialize_app(cred, {"databaseURL": firebase_creds["databaseURL"]})

st.title("🎬 Transcriptor con Whisper y Firebase en Streamlit Cloud")

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

    # 🔹 Cargar el modelo de Whisper
    model = whisper.load_model("tiny")  # Puedes cambiar a "base" o "small" para más precisión

    # 🔹 Transcribir el audio
    result = model.transcribe(temp_audio_path)
    transcripcion = result["text"]

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
