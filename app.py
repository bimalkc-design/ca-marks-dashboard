# ==============================
# CA Dashboard - Sherubtse College
# Multi-module, mobile-friendly
# ==============================

import streamlit as st
import pandas as pd

# -------------------------------
# 1️⃣ Page configuration
# -------------------------------
st.set_page_config(
    page_title="CA Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# 2️⃣ Header with logo
# -------------------------------
col1, col2 = st.columns([4, 1])  # text:logo ratio
with col1:
    st.markdown(
        """
        <div style="background-color:#D6EAF8; padding:15px; border-radius:10px">
            <h2 style='color:#1F618D; margin:0px'>Department of Life Science</h2>
            <h3 style='color:#1F618D; margin:0px'>CA-Dashboard - Sherubtse College</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.image("college_logo.png", width=100)

st.markdown("---")

# -------------------------------
# 3️⃣ Module / Excel selection
# -------------------------------
st.subheader("🔍 Select Module / Excel File")

# List all CA Excel files in the folder
excel_files = ["BTS101.CA.xlsx", "BTS306.CA.xlsx"]
selected_file = st.selectbox("Select Module/Excel File", excel_files)

# -------------------------------
# 4️⃣ Load Excel
# -------------------------------
try:
    df = pd.read_excel(selected_file)
except Exception as e:
    st.error(f"Failed to load {selected_file}: {e}")
    st.stop()

# Normalize column headers (remove spaces, newlines, non-breaking spaces)
df.columns = [str(col).strip().replace('\xa0',' ').replace('\n',' ') for col in df.columns]

# Required columns
required_cols = ["Student No", "Name", "Gender"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Excel file must contain columns: {', '.join(required_cols)}")
    st.stop()

# -------------------------------
# 5️⃣ Student selection
# -------------------------------
st.subheader("👤 Select Student")
student_list = df["Student No"].tolist()
selected_student = st.selectbox("Student No", student_list)

# Filter student record
student_data = df[df["Student No"] == selected_student]
if student_data.empty:
    st.warning("Student ID not found.")
    st.stop()

# -------------------------------
# 6️⃣ Display CA marks in colored table
# -------------------------------
st.subheader("📊 Continuous Assessment Marks")

# Extract CA columns (all except Student No, Name, Gender)
ca_cols = [col for col in df.columns if col not in ["Student No", "Name", "Gender"]]
marks_df = student_data[ca_cols]

# Convert CA columns to numeric
marks_df = marks_df.apply(pd.to_numeric, errors='coerce').fillna(0)

# Style table
styled_df = marks_df.style.set_properties(
    **{
        'background-color': '#D6EAF8',
        'color': 'black',
        'border-color': 'white',
        'font-size': '16px'
    }
).set_table_styles([
    {'selector': 'th', 'props': [('background-color', '#85C1E9'), ('color', 'white')]}
])

st.dataframe(styled_df, use_container_width=True)

# Total marks calculation (out of 60)
total = marks_df.sum(axis=1).values[0]
st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/60</h3>", unsafe_allow_html=True)

# -------------------------------
# 7️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray'>Developed using AI 2025 | Bimal K Chetri (PhD)</p>",
    unsafe_allow_html=True
)
