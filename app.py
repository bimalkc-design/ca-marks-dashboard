# -------------------------------
# app.py - Mobile Friendly Colored Table CA Dashboard
# -------------------------------

import streamlit as st
import pandas as pd
import os

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
# 2️⃣ Header with logo
# -------------------------------
logo_path = "college_logo.png"

# Use st.columns for text + logo alignment
col1, col2 = st.columns([3,1])

with col1:
    st.markdown("""
    <div style="background-color:#2E86C1; padding:15px; border-radius:10px; color:white;">
        <h1 style="margin:0; font-size:28px;">Department of Life Science</h1>
        <h2 style="margin:0; font-size:22px;">CA-Dashboard - Sherubtse College</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

st.markdown("---")
st.markdown("### View your Continuous Assessment (CA) marks below 👇")

# -------------------------------
# 3️⃣ Load data
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("CA_Marks_Dashboard.xlsx")

df = load_data()

# -------------------------------
# 4️⃣ Sidebar: select student
# -------------------------------
st.sidebar.header("🔍 Search Your Marks")
student_ids = df['Student No'].astype(str).tolist()
selected_id = st.sidebar.selectbox("Select your Student No", student_ids)

student_data = df[df['Student No'].astype(str) == selected_id]

# -------------------------------
# 5️⃣ Display student info and marks table
# -------------------------------
if not student_data.empty:
    # Student Info
    st.subheader("🧑 Student Details")
    st.markdown(f"<span style='color:#2E86C1'><b>Name:</b> {student_data['Name'].values[0]}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#2E86C1'><b>Gender:</b> {student_data['Gender'].values[0]}</span>", unsafe_allow_html=True)

    st.subheader("📊 Continuous Assessment Marks")

    # Extract CA columns
    ca_columns = ['Written Assignment (15)', 'Class Test (15)',
                  'Lab Record (10)', 'Presentation (10)', 'Project Report (10)']
    marks_df = student_data[ca_columns]

    # Style the table with background color and conditional formatting
    def color_marks(val, max_val):
        if val >= 0.8 * max_val:
            color = 'background-color:#27AE60; color:white'  # green
        elif val >= 0.5 * max_val:
            color = 'background-color:#F1C40F; color:black'  # yellow
        else:
            color = 'background-color:#E74C3C; color:white'  # red
        return color

    # Build style dataframe
    max_scores = [15, 15, 10, 10, 10]
    styles = []
    for i, col in enumerate(ca_columns):
        styles.append(marks_df[col].apply(lambda x: color_marks(x, max_scores[i])))

    styled_df = marks_df.style.apply(lambda x: styles, axis=None)

    st.dataframe(styled_df, use_container_width=True)

    # Total
    total = marks_df.sum(axis=1).values[0]
    st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/60</h3>", unsafe_allow_html=True)

else:
    st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# 6️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed by Dr. Bimal K. Chetri</p>", unsafe_allow_html=True)
