# -------------------------------
# app.py - CA Marks Dashboard
# -------------------------------

import streamlit as st
import pandas as pd

# -------------------------------
# 1️⃣ Page configuration
# -------------------------------
st.set_page_config(
    page_title="CA-Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# 2️⃣ Custom Header
# -------------------------------
# Optional: College logo
st.image("college_logo.png", width=120)

# Main header with HTML for color and style
st.markdown("""
    <div style="background-color:#2E86C1; padding:20px; border-radius:10px">
        <h1 style="color:white; text-align:center;">Department of Life Science</h1>
        <h2 style="color:white; text-align:center;">CA-Dashboard - Sherubtse College</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("### View your Continuous Assessment (CA) marks below 👇")

st.markdown("---")  # horizontal line

# -------------------------------
# 3️⃣ Load data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("CA_Marks_Dashboard.xlsx")
    return df

df = load_data()

# -------------------------------
# 4️⃣ Sidebar for student selection
# -------------------------------
st.sidebar.header("🔍 Search Your Marks")
student_ids = df['Student No'].astype(str).tolist()
selected_id = st.sidebar.selectbox("Select your Student No", student_ids)

# Filter the dataframe for the selected student
student_data = df[df['Student No'].astype(str) == selected_id]

# -------------------------------
# 5️⃣ Display student information
# -------------------------------
if not student_data.empty:
    # Student Info
    st.subheader("🧑 Student Details")
    st.markdown(f"<span style='color:#2E86C1'><b>Name:</b> {student_data['Name'].values[0]}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#2E86C1'><b>Gender:</b> {student_data['Gender'].values[0]}</span>", unsafe_allow_html=True)

    # Marks Table
    st.subheader("📊 Continuous Assessment Marks")
    marks_df = student_data.drop(columns=['Student No', 'Name', 'Gender'])
    st.dataframe(marks_df.style.set_properties(**{
        'background-color': '#D6EAF8', 'color': 'black', 'border-color': 'white'
    }), use_container_width=True)

    # Total marks
    total = marks_df.sum(axis=1).values[0]
    st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/60</h3>", unsafe_allow_html=True)

else:
    st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# 6️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed by Dr. Bimal K. Chetri</p>", unsafe_allow_html=True)
