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
    
    # 🔹 Create the sequence (Main Timeline)
    sequence = ET.SubElement(root, "sequence")
    ET.SubElement(sequence, "name").text = "AI Generated Sequence"
    
    # 🔹 Define duration of the sequence
    duration = sum([(sub.end.ordinal - sub.start.ordinal) // 1000 for sub in segments])
    ET.SubElement(sequence, "duration").text = str(duration)
    
    # 🔹 Media container
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    
    # 🔹 Track to hold clips
    track = ET.SubElement(video, "track")
    
    for index, sub in enumerate(segments):
        clipitem = ET.SubElement(track, "clipitem", id=f"clip{index + 1}")

        # 🔹 Clip name (Using subtitle text)
        ET.SubElement(clipitem, "name").text = sub.text.replace("\n", " ")

        # 🔹 Start and End times in seconds
        start_time = sub.start.ordinal // 1000
        end_time = sub.end.ordinal // 1000
        ET.SubElement(clipitem, "start").text = str(start_time)
        ET.SubElement(clipitem, "end").text = str(end_time)

        # 🔹 Link to a video file (User will replace it in Premiere)
        file_element = ET.SubElement(clipitem, "file")
        ET.SubElement(file_element, "name").text = "Replace_in_Premiere.mov"
    
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
        full_transcription = "\n".join([sub.text.replace("\n", " ") for sub in subs])
        
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
