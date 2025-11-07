import streamlit as st
import pandas as pd

# ---------------------------------------------------
# Load Excel data
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("CA_Marks_Dashboard.xlsx")
    # Normalize column names for easier use
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    return df

df = load_data()

# ---------------------------------------------------
# App Title and Intro
# ---------------------------------------------------
st.title("📘 Continuous Assessment Marks Dashboard")
st.markdown("View individual student marks and performance summary")

# ---------------------------------------------------
# Student Selection
# ---------------------------------------------------
student_name = st.selectbox("Select a student:", df['Name'].sort_values())

student = df[df['Name'] == student_name].iloc[0]

# ---------------------------------------------------
# Student Info
# ---------------------------------------------------
st.subheader("Student Details")
col1, col2 = st.columns(2)
col1.metric("Student No", student['Student_No'])
col2.metric("Gender", student['Gender'])

# ---------------------------------------------------
# Marks Breakdown
# ---------------------------------------------------
st.subheader("Marks Breakdown (CA Components)")
marks_cols = [
    'Written_Assignment_(15)',
    'Class_Test_(15)',
    'Lab_Record_(10)',
    'Presentation_(10)',
    'Project_Report_(10)'
]

# Display marks in table
st.dataframe(student[marks_cols].to_frame("Marks").rename_axis("Component"))

# ---------------------------------------------------
# Calculate and Display Totals
# ---------------------------------------------------
total = student[marks_cols].sum()
percentage = (total / 60) * 100

st.subheader("📊 Summary")
col1, col2 = st.columns(2)
col1.metric("Total Marks", f"{total:.1f} / 60")
col2.metric("Percentage", f"{percentage:.2f}%")

# ---------------------------------------------------
# Footer
# ---------------------------------------------------
st.markdown("---")
st.caption("Developed by Dr. Bimal Kumar Chetri | Sherubtse College")
