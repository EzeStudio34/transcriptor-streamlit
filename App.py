import streamlit as st
import xml.etree.ElementTree as ET
import pysrt
import tempfile
import os
import openai

# 🔹 Obtener API Key de OpenAI desde Secrets
OPENAI_API_KEY = st.secrets["OPENAI"]["API_KEY"]

def seleccionar_segmentos_con_gpt(transcripcion, prompt, max_duracion):
    """
    Envía la transcripción y el prompt a GPT-4 para seleccionar los mejores segmentos.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en edición de video. Selecciona los fragmentos más relevantes basados en el prompt y la duración especificada."},
            {"role": "user", "content": f"Aquí está la transcripción:
\n{transcripcion}\n\nBasado en el siguiente prompt: \"{prompt}\", selecciona los fragmentos más relevantes sin superar {max_duracion} segundos."}
        ],
        max_tokens=500
    )
    return response["choices"][0]["message"]["content"]

def generar_xml_premiere(segmentos):
    """Genera un archivo XML compatible con Adobe Premiere."""
    root = ET.Element("xmeml", version="4")
    sequence = ET.SubElement(root, "sequence")
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    
    for sub in segmentos:
        clip = ET.SubElement(video, "clip")
        ET.SubElement(clip, "start").text = str(sub.start.ordinal / 1000)
        ET.SubElement(clip, "end").text = str(sub.end.ordinal / 1000)
        ET.SubElement(clip, "name").text = sub.text.replace('\n', ' ')
    
    return ET.tostring(root, encoding="utf-8").decode("utf-8")

st.title("🎬 Generador de XML para Premiere desde SRT con IA")

uploaded_file = st.file_uploader("📂 Sube tu archivo .srt", type=["srt"])
max_duracion = st.slider("⏳ Duración máxima del video (segundos)", 15, 90, 60)
prompt = st.text_area("✏️ Describe qué quieres ver en el video final (temática, tono, info específica)")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
        temp_srt.write(uploaded_file.read())
        temp_srt_path = temp_srt.name
    
    subs = pysrt.open(temp_srt_path)
    transcripcion_completa = "\n".join([sub.text.replace('\n', ' ') for sub in subs])
    segmentos_gpt = seleccionar_segmentos_con_gpt(transcripcion_completa, prompt, max_duracion)
    
    if not segmentos_gpt:
        st.error("❌ No se encontraron segmentos relevantes según el prompt.")
    else:
        xml_content = generar_xml_premiere(subs)
        temp_xml_path = os.path.join(tempfile.gettempdir(), "premiere_export.xml")
        with open(temp_xml_path, "w", encoding="utf-8") as xml_file:
            xml_file.write(xml_content)
        
        st.success("✅ Archivo XML generado correctamente.")
        st.download_button("⬇️ Descargar XML para Premiere", data=xml_content, file_name="premiere_export.xml", mime="application/xml")
