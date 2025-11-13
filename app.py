import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ========================
# Streamlit Page Config
# ========================
st.set_page_config(
    page_title="College CA Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ========================
# App Header
# ========================
st.markdown(
    """
    <div style="text-align: center; background-color: #4CAF50; padding: 15px; border-radius: 10px;">
        <h1 style="color: white;">Department of Life Sciences</h1>
        <h2 style="color: white;">College CA Dashboard</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ========================
# Google Sheets Authentication
# ========================
creds_info = st.secrets["google_service_account"]
creds = Credentials.from_service_account_info(
    creds_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

# ========================
# Google Sheets IDs
# ========================
SHEET_IDS = {
    "BTS101": "1bxIkhxyP3jmvb8AsYDqx-rK5HDzhJO7q4wky1QkSPHk",
    "BTS306": "1El3R6gKLfs3tb_o8lJYzqna5JQ9Q3JJitc0uVDDKkv0"
}

# ========================
# Sidebar for Student Input
# ========================
st.sidebar.header("Student Login")
student_number = st.sidebar.text_input("Enter your Student Number:")

selected_course = st.sidebar.selectbox("Select Course:", list(SHEET_IDS.keys()))

# ========================
# Load Sheet Data
# ========================
def load_sheet(sheet_id):
    try:
        sheet = client.open_by_key(sheet_id).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {e}")
        return pd.DataFrame()

if student_number:
    df_course = load_sheet(SHEET_IDS[selected_course])
    if not df_course.empty:
        df_student = df_course[df_course["Student Number"] == student_number]
        if not df_student.empty:
            st.markdown(
                f"<h3 style='color:#4CAF50;'>CA Marks for Student Number: {student_number}</h3>",
                unsafe_allow_html=True
            )
            st.dataframe(df_student, use_container_width=True)
        else:
            st.warning("No records found for this Student Number.")
else:
    st.info("Enter your Student Number in the sidebar to view your CA marks.")

# ========================
# Footer
# ========================
st.markdown(
    """
    <div style="text-align:center; margin-top:30px; color: gray; font-size:12px;">
        Developed using AI tools by Bimal K Chetri (PhD) | Department of Life Sciences
    </div>
    """,
    unsafe_allow_html=True
)
