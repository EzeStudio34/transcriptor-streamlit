import streamlit as st
import xml.etree.ElementTree as ET
import pysrt
import tempfile
import os
import openai

# 🔹 Get OpenAI API Key from Secrets
OPENAI_API_KEY = st.secrets["OPENAI"]["API_KEY"]

def select_segments_with_gpt(transcription, prompt, max_duration):
    """
    Sends the transcription and prompt to GPT-4o to select the best segments.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Updated OpenAI Client Initialization

    response = client.chat.completions.create(
        model="gpt-4o",  # Updated to GPT-4o
        messages=[
            {"role": "system", "content": "You are a video editing expert. Select the most relevant segments based on the prompt and specified duration."},
            {"role": "user", "content": f"Here is the transcription:\n\n{transcription}\n\nBased on the following prompt: \"{prompt}\", select the most relevant segments without exceeding {max_duration} seconds."}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content  # Updated response handling

def generate_premiere_xml(segments):
    """Generates an XML file compatible with Adobe Premiere."""
    root = ET.Element("xmeml", version="4")
    sequence = ET.SubElement(root, "sequence")
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    
    for sub in segments:
        clip = ET.SubElement(video, "clip")
        ET.SubElement(clip, "start").text = str(sub.start.ordinal / 1000)
        ET.SubElement(clip, "end").text = str(sub.end.ordinal / 1000)
        ET.SubElement(clip, "name").text = sub.text.replace('\n', ' ')
    
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
            selected_segments = select_segments_with_gpt(full_transcription, prompt, max_duration)
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
