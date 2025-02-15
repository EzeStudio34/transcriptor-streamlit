import streamlit as st
import yt_dlp
import whisperx
import tempfile
import os

st.title("🎬 Transcriptor de YouTube con WhisperX")

# 🔹 Ingresar URL de YouTube
url = st.text_input("📹 Ingresa el enlace del video de YouTube")

def descargar_audio_youtube(url):
    """Descarga el audio de un video de YouTube"""
    temp_dir = tempfile.gettempdir()
    audio_path = os.path.join(temp_dir, "youtube_audio.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": audio_path,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        "quiet": True,  # ✅ Evita que muestre demasiada información en consola
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return audio_path

def transcribir_audio_whisperx(audio_path):
    """Transcribe el audio descargado usando WhisperX"""
    model = whisperx.load_model("large-v2", device="cpu")  # ✅ Usa CPU, si tienes GPU usa "cuda"
    result = model.transcribe(audio_path)
    return result["text"]

if url:
    st.write("⏳ Descargando audio...")

    # 🔹 Descargar audio de YouTube
    try:
        audio_path = descargar_audio_youtube(url)
        st.success("✅ Audio descargado correctamente")

        # 🔹 Transcribir el audio con WhisperX
        st.write("⏳ Transcribiendo...")
        transcripcion = transcribir_audio_whisperx(audio_path)

        # 🔹 Mostrar transcripción
        st.subheader("📜 Transcripción:")
        st.text_area("Texto", transcripcion, height=200)

    except Exception as e:
        st.error(f"❌ Error: {e}")
