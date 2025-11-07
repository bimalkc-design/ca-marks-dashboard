import streamlit as st
import pandas as pd
from PIL import Image

# -------------------------------
# 1️⃣ Page configuration
# -------------------------------
st.set_page_config(
    page_title="CA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 2️⃣ Header with logo
# -------------------------------
# Load logo
logo_path = "college_logo.png"
logo = Image.open(logo_path)

# Header box with color, logo on right
st.markdown(
    f"""
    <div style='display:flex; justify-content: space-between; align-items:center;
                background-color:#1F618D; padding: 15px; border-radius: 8px'>
        <div>
            <h2 style='color:white; margin:0'>Department of Life Science</h2>
            <h3 style='color:white; margin:0'>CA Dashboard - Sherubtse College</h3>
        </div>
        <div>
            <img src='data:image/png;base64,{st.image(logo)._repr_png_()}' width='100'>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("## View your Continuous Assessment (CA) marks below 👇")

# -------------------------------
# 3️⃣ Module selection
# -------------------------------
excel_files = [f for f in ["BTS101.CA.xlsx", "BTS306.CA.xlsx"]]
module_selected = st.selectbox("Select Module/Excel File", excel_files)

# Load selected Excel file
try:
    df = pd.read_excel(module_selected)
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Normalize column headers (remove leading/trailing spaces)
df.columns = df.columns.str.strip()

# Check required columns
required_cols = ["Student No", "Name", "Gender"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Excel file must contain columns: {', '.join(required_cols)}")
    st.stop()

# -------------------------------
# 4️⃣ Student selection
# -------------------------------
student_list = df["Student No"].tolist()
student_selected = st.selectbox("Select Student No", student_list)

# Filter student data
student_data = df[df["Student No"] == student_selected]
if student_data.empty:
    st.warning("Student ID not found. Please select a valid ID.")
    st.stop()

# -------------------------------
# 5️⃣ Display CA marks table
# -------------------------------
marks_cols = df.columns.difference(["Student No", "Name", "Gender"])
marks_df = student_data[marks_cols]

# Convert to numeric
for col in marks_df.columns:
    marks_df[col] = pd.to_numeric(marks_df[col], errors="coerce")

# Apply styling
styled_df = marks_df.style.set_properties(
    **{'background-color': '#D6EAF8', 'color': 'black', 'border-color': 'white'}
)

st.dataframe(styled_df, use_container_width=True)

# Total marks
total = marks_df.sum(axis=1).values[0]
st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/{marks_df.sum(axis=1).max()}</h3>", unsafe_allow_html=True)

# -------------------------------
# 6️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed using AI | Bimal K. Chetri (PhD)</p>",
    unsafe_allow_html=True
)
