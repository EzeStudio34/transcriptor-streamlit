import streamlit as st
import xml.etree.ElementTree as ET
import pysrt
import tempfile
import os

def seleccionar_segmentos(subs, max_duracion, prompt):
    """
    Selecciona los segmentos más relevantes basados en el prompt y la duración máxima.
    """
    seleccionados = []
    duracion_total = 0
    
    for sub in subs:
        texto = sub.text.replace('\n', ' ')
        duracion = (sub.end.ordinal - sub.start.ordinal) / 1000  # Duración en segundos
        
        if prompt.lower() in texto.lower():  # Filtra segmentos según el prompt
            if duracion_total + duracion <= max_duracion:
                seleccionados.append(sub)
                duracion_total += duracion
            else:
                break  # Detiene la selección si se excede la duración máxima
    
    return seleccionados

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

st.title("🎬 Generador de XML para Premiere desde SRT")

uploaded_file = st.file_uploader("📂 Sube tu archivo .srt", type=["srt"])
max_duracion = st.slider("⏳ Duración máxima del video (segundos)", 15, 90, 60)
prompt = st.text_area("✏️ Describe qué quieres ver en el video final (temática, tono, info específica)")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
        temp_srt.write(uploaded_file.read())
        temp_srt_path = temp_srt.name
    
    subs = pysrt.open(temp_srt_path)
    segmentos = seleccionar_segmentos(subs, max_duracion, prompt)
    
    if not segmentos:
        st.error("❌ No se encontraron segmentos relevantes según el prompt.")
    else:
        xml_content = generar_xml_premiere(segmentos)
        temp_xml_path = os.path.join(tempfile.gettempdir(), "premiere_export.xml")
        with open(temp_xml_path, "w", encoding="utf-8") as xml_file:
            xml_file.write(xml_content)
        
        st.success("✅ Archivo XML generado correctamente.")
        st.download_button("⬇️ Descargar XML para Premiere", data=xml_content, file_name="premiere_export.xml", mime="application/xml")
