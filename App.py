import streamlit as st
import pysrt
import tempfile
import os
import csv
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

def generate_premiere_csv(segments):
    """Generates a CSV file compatible with Adobe Premiere markers."""
    temp_csv_path = os.path.join(tempfile.gettempdir(), "premiere_markers.csv")
    
    with open(temp_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Timecode", "Name", "Description"])
        
        for sub in segments:
            start_time = f"{sub.start.hours:02}:{sub.start.minutes:02}:{sub.start.seconds:02}.{sub.start.milliseconds:03}"
            writer.writerow([start_time, "Key Moment", sub.text.replace('\n', ' ')])
    
    return temp_csv_path

st.title("🎬 Premiere CSV Marker Generator from SRT with AI")

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
                csv_path = generate_premiere_csv(subs)
                
                with open(csv_path, "r", encoding="utf-8") as csv_file:
                    csv_content = csv_file.read()
                
                st.success("✅ CSV file successfully generated for Premiere markers.")
                st.download_button("⬇️ Download CSV for Premiere", data=csv_content, file_name="premiere_markers.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Error generating CSV: {e}")
