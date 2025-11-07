import streamlit as st
import pandas as pd
import os

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="CA-Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Header with logo
# -------------------------------
logo_path = "college_logo.png"
col1, col2 = st.columns([3, 1])
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
# Sidebar: Module and Student selection
# -------------------------------
st.sidebar.header("🔍 Select Module and Student")

# Automatically detect Excel files in current directory
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
module_choice = st.sidebar.selectbox("Select Module", excel_files)

# Load selected module
@st.cache_data
def load_data(file_name):
    return pd.read_excel(file_name)

df = load_data(module_choice)

# Student ID selection
student_ids = df['Student No'].astype(str).tolist()
selected_id = st.sidebar.selectbox("Select your Student No", student_ids)

student_data = df[df['Student No'].astype(str) == selected_id]

# -------------------------------
# Display student info and marks
# -------------------------------
if not student_data.empty:
    st.subheader("🧑 Student Details")
    st.markdown(f"<span style='color:#2E86C1'><b>Name:</b> {student_data['Name'].values[0]}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#2E86C1'><b>Gender:</b> {student_data['Gender'].values[0]}</span>", unsafe_allow_html=True)

    st.subheader(f"📊 {module_choice.replace('.xlsx','')} Marks")

    # CA columns (auto detect numeric columns after first 3 columns)
    ca_columns = df.columns[2:]  
    marks_df = student_data[ca_columns]

    # Max scores (customize per module if needed)
    max_scores = [float(col.split('(')[1].replace(')','')) if '(' in col else 10 for col in ca_columns]
    max_dict = dict(zip(ca_columns, max_scores))

    # Function for coloring
    def color_marks(val, col):
        max_val = max_dict[col]
        if val >= 0.8 * max_val:
            return 'background-color:#27AE60; color:white'
        elif val >= 0.5 * max_val:
            return 'background-color:#F1C40F; color:black'
        else:
            return 'background-color:#E74C3C; color:white'

    # Apply styling per column
    styled_df = marks_df.copy()
    for col in ca_columns:
        styled_df[col] = styled_df[col].astype(float)
    styled_df = styled_df.style.apply(lambda x: [color_marks(v, x.name) for v in x], axis=0)

    st.dataframe(styled_df, use_container_width=True)

    # Total
    total = marks_df.sum(axis=1).values[0]
    st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}</h3>", unsafe_allow_html=True)
else:
    st.warning("Student ID not found in this module. Please select a valid ID.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed using AI|Bimal K. Chetri (PhD)</p>", unsafe_allow_html=True)
