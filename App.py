import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import uuid  # Para generar IDs únicos

# 🔹 Cargar credenciales desde Streamlit Secrets
firebase_creds = st.secrets["FIREBASE"]
firebase_creds_dict = json.loads(json.dumps(firebase_creds))

# 🔹 Inicializar Firebase usando las credenciales de Secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred, {"databaseURL": firebase_creds["databaseURL"]})

st.title("🎬 Transcriptor con Firebase en Streamlit Cloud")

# 🔹 Prueba rápida para verificar conexión a Firebase
try:
    ref = db.reference("/")
    ref.set({"test": "Conexión exitosa con Firebase en Streamlit Cloud"})
    st.success("✅ Firebase está funcionando correctamente.")
except Exception as e:
    st.error(f"❌ Error al conectar con Firebase: {e}")

# 🔹 Subir archivo de audio
uploaded_file = st.file_uploader("📤 Sube tu archivo de audio", type=["mp3", "wav", "m4a"])

# 🔹 Especificar la duración y temática del video final
duracion = st.slider("⏳ Duración deseada del video (en segundos)", 15, 120, 60)
tematica = st.text_input("🎯 Especifica la temática del video", "Motivación, Educación, Entretenimiento...")

# 🔹 Procesar el audio si se subió un archivo
if uploaded_file is not None:
    st.write("⏳ Procesando la transcripción...")

    # 🔹 Simulación de la transcripción (Aquí debes integrar Whisper o AssemblyAI)
    transcripcion = "Ejemplo de transcripción generada a partir del audio."
    
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
