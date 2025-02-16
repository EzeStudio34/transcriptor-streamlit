import streamlit as st
import xml.etree.ElementTree as ET
import pysrt
import tempfile
import os
import google.generativeai as genai

# 🔹 Get Google Gemini API Key from Secrets
GEMINI_API_KEY = st.secrets["GEMINI"]["API_KEY"]

# 🔹 Configure Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

def select_segments_with_gemini(transcription, prompt, max_duration):
    """
    Uses Google Gemini AI to analyze the transcription and extract the most relevant segments.
    """
    model = genai.GenerativeModel("gemini-pro")
    
    response = model.generate_content(
        f"Here is a transcription:\n{transcription}\n\nBased on the following user request: '{prompt}', "
        f"select the most relevant segments without exceeding {max_duration} seconds. "
        f"Provide the timestamps and key dialogue from the text."
    )
    
    return response.text  # Returns the AI's response

def generate_premiere_xml(segments):
    """Generates an XML file compatible with Adobe Premiere."""
    root = ET.Element("xmeml", version="4")
    sequence = ET.SubElement(root, "sequence")
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    
    for sub in segments:
        clipitem = ET.SubElement(video, "clipitem")
        ET.SubElement(clipitem, "name").text = sub.text.replace('\n', ' ')
        ET.SubElement(clipitem, "start").text = str(sub.start.ordinal // 1000)
        ET.SubElement(clipitem, "end").text = str(sub.end.ordinal // 1000)
        ET.SubElement(clipitem, "file").text = "video_placeholder.mov"  # Generic placeholder file
    
    return ET.tostring(root, encoding="utf-8").decode("utf-8")

st.title("🎬 Premiere XML Generator from SRT with AI")

uploaded_file = st.file_uploader("📂 Upload your .srt file", type=["srt"])
max_duration = st.slider("⏳ Maximum video duration (seconds)", 15, 90, 60)
prompt = st.text_area("✏️ Describe what you want in the final video (theme, tone, specific information)")

if uploaded_file and prompt:
    if st.button("▶️ Run Processing"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
            temp_srt.write(uploaded_file.read())
            temp_srt_path = temp_srt.name
        
        subs = pysrt.open(temp_srt_path)
        full_transcription = "\n".join([sub.text.replace('\n', ' ') for sub in subs])
        
        try:
            selected_segments = select_segments_with_gemini(full_transcription, prompt, max_duration)
            if not selected_segments:
                st.error("❌ No relevant segments found based on the prompt.")
            else:
                xml_content = generate_premiere_xml(subs)
                temp_xml_path = os.path.join(tempfile.gettempdir(), "premiere_export.xml")
                with open(temp_xml_path, "w", encoding="utf-8") as xml_file:
                    xml_file.write(xml_content)
                
                st.success("✅ XML file successfully generated.")
                st.download_button("⬇️ Download XML for Premiere", data=xml_content, file_name="premiere_export.xml", mime="application/xml")
        except Exception as e:
            st.error(f"❌ Error generating XML: {e}")
