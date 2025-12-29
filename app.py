import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 1. Page Configuration & Setup
st.set_page_config(page_title="Student Result Portal", page_icon="🎓", layout="centered")

st.title("📂 Student Result Portal")
st.info("Enter your name and father's name exactly as per school records.")

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
with st.form("search_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Student Name")
    with col2:
        f_name = st.text_input("Father's Name")
        
    # Dropdown for Class Number (6 to 12)
    class_num = st.selectbox("Select Your Class", options=["6", "7", "8", "9", "10", "11", "12"])
    
    submit = st.form_submit_button("🔍 Find My Result")

# 4. Search and Download Logic
if submit:
    if name and f_name:
        # Construct the target filename (stripping extra spaces)
        # Format: studentName_fatherName_classNumber.pdf
        target_name = f"{name.strip()}_{f_name.strip()}_{class_num}.pdf"
        
        # Search query for Google Drive
        query = f"name = '{target_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed = false"
        
        try:
            results = service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                st.warning(f"No result found for '{target_name}'. Please ensure spelling is correct.")
            else:
                file_id = items[0]['id']
                
                # Fetching the file
                request = service.files().get_media(fileId=file_id)
                file_stream = io.BytesIO()
                downloader = MediaIoBaseDownload(file_stream, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()

                st.success(f"Result for {name} (Class {class_num}) is ready!")
                
                # Download Button
                st.download_button(
                    label="📥 Download Result PDF",
                    data=file_stream.getvalue(),
                    file_name=target_name,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error("An error occurred during the search. Please contact the administrator.")
    else:
        st.error("Please fill in both the Name and Father's Name fields.")

# 5. Footer (Nice for Portfolio)
st.markdown("---")
st.caption("Developed by Taimoor Raza Asif")