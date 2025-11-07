import streamlit as st
import pandas as pd
import os

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="CA-Dashboard",
    page_icon="📊",
    layout="wide"
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
# Sidebar: Excel selection and Student ID
# -------------------------------
st.sidebar.header("🔍 Select Module/Excel and Student")

# Auto detect Excel files
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
if not excel_files:
    st.warning("No Excel files found in the folder.")
    st.stop()

module_choice = st.sidebar.selectbox("Select Module/Excel File", excel_files)

# Load selected Excel file safely
@st.cache_data
def load_data(file_name):
    try:
        df = pd.read_excel(file_name)
        return df
    except Exception as e:
        st.error(f"Error loading file {file_name}: {e}")
        return pd.DataFrame()

df = load_data(module_choice)

# -------------------------------
# Student selection
# -------------------------------
if "Student No" not in df.columns:
    st.error("Excel file must have 'Student No' column")
    st.stop()

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

    # Automatically detect CA columns (everything after first 3 columns)
    ca_columns = df.columns[2:]
    marks_df = student_data[ca_columns]

    # Safe numeric conversion
    marks_df = marks_df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Max scores detection (from column header like "Written Assignment (15)")
    max_scores = []
    for col in ca_columns:
        if '(' in col and ')' in col:
            try:
                max_scores.append(float(col.split('(')[1].split(')')[0]))
            except:
                max_scores.append(10)
        else:
            max_scores.append(10)
    max_dict = dict(zip(ca_columns, max_scores))

    # Coloring function
    def color_marks(val, col):
        max_val = max_dict[col]
        if val >= 0.8 * max_val:
            return 'background-color:#27AE60; color:white'
        elif val >= 0.5 * max_val:
            return 'background-color:#F1C40F; color:black'
        else:
            return 'background-color:#E74C3C; color:white'

    styled_df = marks_df.style.apply(lambda x: [color_marks(v, x.name) for v in x], axis=0)

    st.dataframe(styled_df, use_container_width=True)

    total = marks_df.sum(axis=1).values[0]
    st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}</h3>", unsafe_allow_html=True)
else:
    st.warning("Student ID not found in this module. Please select a valid ID.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed using AI|Bimal K. Chetri (PhD)</p>", unsafe_allow_html=True)
