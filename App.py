import streamlit as st
import google.generativeai as genai
import json
import os
import pysrt

# 🔹 Obtener la clave de API de Gemini desde Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 🔹 Configurar Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Configuración de la interfaz
st.set_page_config(page_title="Freaky Video Assistant", page_icon="🎬", layout="wide")

# 🔹 Logo y título
logo_url = "https://github.com/EzeStudio34/transcriptor-streamlit/blob/main/Studio34_Logos_S34_White.png?raw=true"

col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo_url, width=100)
with col2:
    st.markdown("<h1 style='text-align: left;'>Freaky Video Assistant 🎬</h1>", unsafe_allow_html=True)

# 🔹 Subir archivo `.srt`
st.subheader("Upload a subtitle file (.srt)")
uploaded_file = st.file_uploader("Choose a file", type=["srt"])

# 🔹 Campo de entrada para el prompt
st.subheader("Enter your prompt")
user_prompt = st.text_area("Describe what you want the final video to focus on (theme, tone, key moments, etc.)")

# 🔹 Botón para ejecutar el análisis
if st.button("Run Analysis"):
    if uploaded_file is not None and user_prompt:
        # Leer el archivo .srt
        subtitles = pysrt.open(uploaded_file)
        transcriptions = []
        
        for sub in subtitles:
            transcriptions.append(f"[{sub.start}] {sub.text}")
        
        full_text = "\n".join(transcriptions)

        # 🔹 Enviar el texto a Gemini para análisis
        response = genai.chat(
            model="gemini-pro",
            messages=[
                {"role": "system", "content": "You are an AI expert in video editing and social media content."},
                {"role": "user", "content": f"Here is a transcript:\n\n{full_text}\n\nFind the most engaging moments based on this prompt:\n{user_prompt}"}
            ]
        )

        try:
            best_segments = response["choices"][0]["message"]["content"]
            
            # 🔹 Mostrar el resultado
            st.subheader("Selected content preview")
            st.write(best_segments)
            
            # 🔹 Descargar archivo CSV con timestamps
            csv_filename = "video_markers.csv"
            with open(csv_filename, "w", encoding="utf-8") as f:
                f.write("Timestamp,Content\n")
                for line in best_segments.split("\n"):
                    f.write(f"{line}\n")

            st.download_button("Download CSV", csv_filename)

        except Exception as e:
            st.error(f"❌ Error generating content: {str(e)}")
    else:
        st.warning("Please upload a .srt file and enter a prompt before running the analysis.")
