import streamlit as st
import xml.etree.ElementTree as ET
import pysrt
import tempfile
import os
import google.generativeai as genai
from keybert import KeyBERT

# 🔹 Get Google Gemini API Key from Secrets
GEMINI_API_KEY = st.secrets["GEMINI"]["API_KEY"]

# 🔹 Configure Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Set App Title and Logo
st.set_page_config(page_title="Freaky Video Assistant", page_icon="🎬")

# 🔹 Display Logo and Title in One Row
col1, col2 = st.columns([1, 4])
with col1:
    logo_url = "https://github.com/EzeStudio34/transcriptor-streamlit/blob/main/Studio34_Logos_S34_White.png?raw=true"  # Replace with actual GitHub URL
    st.image(logo_url, width=120)  # Adjust width to make it smaller

with col2:
    st.markdown("<h1 style='text-align: left;'>Freaky Video Assistant 🎬</h1>", unsafe_allow_html=True)

# 🔹 Function to filter relevant parts using KeyBERT
def filter_relevant_parts(transcription, prompt):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(transcription, keyphrase_ngram_range=(1, 2), top_n=10)
    
    relevant_sentences = [sentence for sentence in transcription.split(". ") if any(kw in sentence for kw, _ in keywords)]
    return " ".join(relevant_sentences)  # Return only relevant sentences

# 🔹 Function to select segments with Gemini
def select_segments_with_gemini(transcription, prompt, max_duration):
    """
    Uses Google Gemini AI to analyze the transcription and extract the most relevant segments.
    """
    model = genai.GenerativeModel("gemini-pro")
    
    response = model.generate_content(
        f"""You are an expert video editor analyzing a transcription of a long video. 
        Your task is to extract the most engaging and relevant parts that align with the user's request.

        **User's request:** {prompt}

        **Filtered Transcription:**
        {transcription}

        **Rules for selecting content:**
        - Select only the most engaging or informative moments.
        - Ensure a smooth flow between the selected parts.
        - Keep the total duration under {max_duration} seconds.
        - Avoid repetitive or redundant segments.
        - Provide output in plain text without timestamps.

        **Expected output format:**
        - Provide the extracted text, making sure it forms a coherent short video.
        - Keep it concise and impactful.
        """,
        temperature=0.5  # Lower temperature makes responses more structured
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
            # 🔹 Filter transcription using KeyBERT
            filtered_transcription = filter_relevant_parts(full_transcription, prompt)
            
            # 🔹 Select segments using Gemini
            selected_segments = select_segments_with_gemini(filtered_transcription, prompt, max_duration)
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
