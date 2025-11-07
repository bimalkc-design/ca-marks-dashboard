# -------------------------------
# app.py - CA Marks Dashboard
# -------------------------------

import streamlit as st
import pandas as pd

# -------------------------------
# 1️⃣ Page configuration
# -------------------------------
st.set_page_config(
    page_title="CA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# 2️⃣ Header
# -------------------------------
st.title("Sherubtse College - CA Dashboard")
st.markdown("View your Continuous Assessment (CA) marks here. Select your student ID from the sidebar to see your details.")

# Optional: College logo (if you have a PNG file)
# st.image("college_logo.png", width=120)

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
st.sidebar.header("Search Your Marks")
student_ids = df['Student No'].astype(str).tolist()
selected_id = st.sidebar.selectbox("Select your Student No", student_ids)

# Filter the dataframe for the selected student
student_data = df[df['Student No'].astype(str) == selected_id]

# -------------------------------
# 5️⃣ Display student information
# -------------------------------
if not student_data.empty:
    st.subheader("Student Details")
    st.write(f"**Name:** {student_data['Name'].values[0]}")
    st.write(f"**Gender:** {student_data['Gender'].values[0]}")

    st.subheader("Continuous Assessment Marks")
    st.dataframe(
        student_data.drop(columns=['Student No', 'Name', 'Gender']),
        use_container_width=True
    )

    # Optional: Calculate total CA marks
    total = student_data[['Written Assignment (15)', 'Class Test (15)', 
                          'Lab Record (10)', 'Presentation (10)', 
                          'Project Report (10)']].sum(axis=1).values[0]
    st.markdown(f"**Total CA Marks:** {total}/60")
else:
    st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# 6️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown("© 2025 Sherubtse College | Developed by Dr. Bimal K. Chetri")
