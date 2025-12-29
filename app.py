import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 1. Page Configuration
st.set_page_config(page_title="Mastwaar College Of Sciences - Result Portal", page_icon="College Logo.png", layout="centered")

# --- UI BRANDING SECTION ---
col_space_l, col_logo, col_text, col_space_r = st.columns([0.5, 1, 4, 0.5], vertical_alignment="center")

with col_logo:
    st.image("College Logo.png", width=120) 

with col_text:
    st.markdown("""
        <div style='line-height: 1.2; text-align: center;'>
            <h2 style='color: #cc299b; margin-bottom: 0; white-space: nowrap;'>Mastwaar College Of Sciences</h2>
            <p style='color: #6B7280; font-size: 0.9em; margin-top: 2px;'>Makhdoom Pur Sharif, Chakwal</p>
            <h3 style='color: #4B5563; margin-top: 5px;'>Student Result Portal</h3>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='border-bottom: 2px solid #cc299b; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

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

# --- 5. CONTACT & ADMINISTRATION SECTION (GRID VIEW) ---
st.markdown("<br><br>", unsafe_allow_html=True) # Adding space before the info section
col_admin, col_tech = st.columns(2)

with col_admin:
    st.markdown("""
        <div style="background-color: #f9fafb; padding: 20px; border-radius: 10px; border-left: 5px solid #cc299b; min-height: 200px;">
            <h4 style="color: #cc299b; margin-top: 0;">🏛️ Administration</h4>
            <p style="margin-bottom: 5px;"><b>Principal:</b><br>Dr. Kashif Mehmood Khakvi</p>
            <p><b>Contact:</b><br><a href='tel:03348724125' style='color: #4B5563; text-decoration: none;'>03348724125</a></p>
        </div>
    """, unsafe_allow_html=True)

with col_tech:
    st.markdown("""
        <div style="background-color: #f9fafb; padding: 20px; border-radius: 10px; border-left: 5px solid #10b981; min-height: 200px;">
            <h4 style="color: #10b981; margin-top: 0;">🛠️ Technical Support</h4>
            <p style="margin-bottom: 5px;">For portal issues or errors, contact:</p>
            <p><b>Mujtaba Asif Raja:</b><br><a href='tel:03195000255' style='color: #4B5563; text-decoration: none;'>03195000255</a></p>
        </div>
    """, unsafe_allow_html=True)

# 6. Footer
st.markdown("---")
st.caption("© 2025 Mastwaar College Of Sciences | System Developed by Taimoor Raza Asif")