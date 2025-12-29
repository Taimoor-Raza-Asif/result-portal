import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 1. Page Configuration (Title and Layout)
st.set_page_config(page_title="Jamia Tul Mastwaar - Result Portal", page_icon="Jamia Logo.png", layout="centered")

# --- UI BRANDING SECTION ---
# Add your logo and Institute Name
col_space_l, col_logo, col_text, col_space_r = st.columns([1, 1, 3, 1], vertical_alignment="center")

with col_logo:
    # Ensure "Jamia Logo.png" is uploaded to your GitHub repo
    st.image("Jamia Logo.png", width=100) 

with col_text:
    st.markdown("""
        <div style='line-height: 1;'>
            <h1 style='color: #cc299b; margin-bottom: 0;'>Jamia Tul Mastwaar</h1>
            <h3 style='color: #4B5563; margin-top: 5px;'>Student Result Portal</h3>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='border-bottom: 2px solid #cc299b; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

st.write("") # Add some spacing

# 2. Secure Credentials Loading
if "google_auth" in st.secrets:
    try:
        info = dict(st.secrets["google_auth"])
        credentials = service_account.Credentials.from_service_account_info(info)
        DRIVE_FOLDER_ID = st.secrets["FOLDER_ID"]
        service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error(f"Error connecting to Google Drive: {e}")
        st.stop()
else:
    st.error("Credentials not found in Streamlit Secrets.")
    st.stop()

# 3. Student Input Form
with st.container():
    st.info("Enter details exactly as they appear on your school registration.")
    with st.form("search_form"):
        name = st.text_input("👤 Student Name")
        f_name = st.text_input("👨‍👦 Father's Name")
        class_num = st.selectbox("📚 Select Your Class", options=["6", "7", "8", "9", "10", "11", "12"])
        
        submit = st.form_submit_button("🔍 Find My Result")

# 4. Search and Download Logic
if submit:
    if name and f_name:
        target_name = f"{name.strip()}_{f_name.strip()}_{class_num}.pdf"
        query = f"name = '{target_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed = false"
        
        try:
            results = service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                st.warning(f"No result found for '{target_name}'. Please check your spelling.")
            else:
                file_id = items[0]['id']
                request = service.files().get_media(fileId=file_id)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()

                st.success(f"Result for {name} (Class {class_num}) found!")
                st.download_button(
                    label="📥 Download Result PDF",
                    data=file_stream.getvalue(),
                    file_name=target_name,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error("An error occurred during the search. Please contact the administrator.")
    else:
        st.error("Please fill in both Name and Father's Name fields.")

# 5. Footer
st.markdown("---")
st.caption("© 2025 Jamia Tul Mastwaar | System Developed by Taimoor Raza Asif")