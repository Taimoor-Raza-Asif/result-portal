import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 1. Setup Page & Credentials
st.set_page_config(page_title="Result Portal", page_icon="🎓")
st.title("📂 Student Result Portal")
st.write("Enter your details exactly as they appear on your registration.")

# Load secrets from Streamlit (for deployment)
if "google_auth" in st.secrets:
    info = dict(st.secrets["google_auth"])
    credentials = service_account.Credentials.from_service_account_info(info)
    DRIVE_FOLDER_ID = st.secrets["FOLDER_ID"]
else:
    st.error("Secrets not configured correctly.")
    st.stop()

service = build('drive', 'v3', credentials=credentials)

# 2. Student Input Form
with st.form("search_form"):
    name = st.text_input("Student Name")
    f_name = st.text_input("Father Name")
    cnic = st.text_input("Student CNIC (without dashes)")
    submit = st.form_submit_button("Search Result")

if submit:
    if name and f_name and cnic:
        # Match the filename format: studentName_fatherName_studentCnic.pdf
        target_name = f"{name}_{f_name}_{cnic}.pdf"
        
        # 3. Query Google Drive
        query = f"name = '{target_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            st.warning("No result found. Please check your details and try again.")
        else:
            file_id = items[0]['id']
            # 4. Securely download the file
            request = service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # 5. Provide the download button
            st.success(f"Result found for {name}!")
            st.download_button(
                label="📥 Download Result PDF",
                data=file_stream.getvalue(),
                file_name=target_name,
                mime="application/pdf"
            )
    else:
        st.error("Please fill in all fields.")