# -------------------------------
# app.py - Mobile Friendly CA Dashboard
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
# 2️⃣ Custom Header with logo
# -------------------------------
logo_path = "college_logo.png"

# Using st.columns to align text and logo
col1, col2 = st.columns([3,1])  # 3:1 width ratio

with col1:
    st.markdown("""
    <div style="background-color:#2E86C1; padding:15px; border-radius:10px; color:white;">
        <h1 style="margin:0; font-size:28px;">Department of Life Science</h1>
        <h2 style="margin:0; font-size:22px;">CA-Dashboard - Sherubtse College</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image(logo_path, width=120)

st.markdown("### View your Continuous Assessment (CA) marks below 👇")
st.markdown("---")

# -------------------------------
# 3️⃣ Load data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("CA_Marks_Dashboard.xlsx")
    return df

df = load_data()

# -------------------------------
# 4️⃣ Sidebar: select student
# -------------------------------
st.sidebar.header("🔍 Search Your Marks")
student_ids = df['Student No'].astype(str).tolist()
selected_id = st.sidebar.selectbox("Select your Student No", student_ids)

student_data = df[df['Student No'].astype(str) == selected_id]

# -------------------------------
# 5️⃣ Display student info and marks
# -------------------------------
if not student_data.empty:
    # Student Info
    st.subheader("🧑 Student Details")
    st.markdown(f"<span style='color:#2E86C1'><b>Name:</b> {student_data['Name'].values[0]}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#2E86C1'><b>Gender:</b> {student_data['Gender'].values[0]}</span>", unsafe_allow_html=True)

    st.subheader("📊 Continuous Assessment Marks")
    ca_components = ['Written Assignment (15)', 'Class Test (15)',
                     'Lab Record (10)', 'Presentation (10)', 'Project Report (10)']
    ca_scores = student_data[ca_components].iloc[0]

    st.markdown("#### Your CA Components Progress")
    for comp in ca_components:
        score = ca_scores[comp]
        max_score = int(comp.split("(")[1].replace(")", ""))
        pct = (score / max_score) * 100

        # Color code
        if pct >= 80:
            color = "#27AE60"  # green
        elif pct >= 50:
            color = "#F1C40F"  # yellow
        else:
            color = "#E74C3C"  # red

        # Use st.markdown + HTML progress bar for responsive design
        st.markdown(f"""
        <div style='margin-bottom:5px;'>
            <b>{comp}: {score}/{max_score}</b>
            <div style='background-color:#D5DBDB; border-radius:5px; width:100%; height:18px;'>
                <div style='width:{pct}%; background-color:{color}; height:100%; border-radius:5px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    total = ca_scores.sum()
    st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/60</h3>", unsafe_allow_html=True)

else:
    st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# 6️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed by Dr. Bimal K. Chetri</p>", unsafe_allow_html=True)
