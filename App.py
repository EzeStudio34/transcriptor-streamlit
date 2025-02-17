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

# 🔹 Set App Title and Logo
st.set_page_config(page_title="Video Editor AI Assistant", page_icon="🎬")

# 🔹 Display Logo
logo_url = "https://drive.google.com/uc?export=view&id=1XlHZiaiMfskhQU23c8H8GyC-mq9FjwaN"
st.image(logo_url, use_container_width=True)

st.title("🎬 Video Editor AI Assistant")

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

def generate_premiere_fcpxml(segments):
    """Generates an FCPXML file compatible with Adobe Premiere markers."""
    root = ET.Element("fcpxml", version="1.8")
    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event")
    project = ET.SubElement(event, "project")
    sequence = ET.SubElement(project, "sequence")
    spine = ET.SubElement(sequence, "spine")

    for sub in segments:
        marker = ET.SubElement(spine, "marker", start=f"{sub.start.ordinal // 1000}s", duration="1s")
        marker.text = sub.text.replace("\n", " ")

    temp_fcpxml_path = os.path.join(tempfile.gettempdir(), "premiere_markers.fcpxml")
    
    with open(temp_fcpxml_path, "w", encoding="utf-8") as file:
        file.write(ET.tostring(root, encoding="utf-8").decode("utf-8"))
    
    return temp_fcpxml_path

uploaded_file = st.file_uploader("📂 Upload your .srt file", type=["srt"])
max_duration = st.slider("⏳ Maximum video duration (seconds)", 15, 90, 60)
prompt = st.text_area("✏️ Describe what you want in the final video (theme, tone, specific information)")

if uploaded_file and prompt:
    if st.button("▶️ Run Processing"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
            temp_srt.write(uploaded_file.read())
            temp_srt_path = temp_srt.name
        
        subs = pysrt.open(temp_srt_path)
        full_transcription = "\n".join([sub.text.replace("\n", " ") for sub in subs])
        
        try:
            selected_segments = select_segments_with_gemini(full_transcription, prompt, max_duration)
            if not selected_segments:
                st.error("❌ No relevant segments found based on the prompt.")
            else:
                # Display AI-selected text preview without timestamps
                st.subheader("📜 Selected Text Preview:")
                st.text_area("", selected_segments, height=200)
                
                fcpxml_path = generate_premiere_fcpxml(subs)
                
                with open(fcpxml_path, "r", encoding="utf-8") as fcpxml_file:
                    fcpxml_content = fcpxml_file.read()
                
                st.success("✅ FCPXML file successfully generated for Premiere markers.")
                st.download_button("⬇️ Download FCPXML for Premiere", data=fcpxml_content, file_name="premiere_markers.fcpxml", mime="application/xml")
        except Exception as e:
            st.error(f"❌ Error generating FCPXML: {e}")
