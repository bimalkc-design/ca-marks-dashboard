import streamlit as st
import pandas as pd
import glob

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="CA Dashboard", page_icon="📊", layout="wide")

# -------------------------------
# Header
# -------------------------------
col1, col2 = st.columns([5,1])
with col1:
    st.markdown(
        """
        <div style='background-color:#1F618D; padding:10px; border-radius:5px'>
        <h2 style='color:white; margin:0'>Department of Life Science</h2>
        <h3 style='color:white; margin:0'>CA Dashboard - Sherubtse College</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.image("college_logo.png", width=80)

st.markdown("## View your Continuous Assessment (CA) marks below 👇")

# -------------------------------
# Detect all Excel files
# -------------------------------
excel_files = glob.glob("*.xlsx")
module_choice = st.sidebar.selectbox("🔍 Select Module/Excel File", excel_files)

# -------------------------------
# Load selected Excel file
# -------------------------------
if module_choice:
    df = pd.read_excel(module_choice)
    df.columns = [col.strip() for col in df.columns]  # strip spaces

    # Sidebar: select student
    student_list = df["Student No"].tolist()
    student_choice = st.sidebar.selectbox("🔍 Select Student", student_list)

    # Filter for selected student
    student_df = df[df["Student No"] == student_choice]

    if not student_df.empty:
        # Display student details
        st.markdown(f"### Student: {student_df['Name'].values[0]} ({student_choice})")
        st.markdown(f"**Gender:** {student_df['Gender'].values[0]}")

        # Keep only CA columns
        ca_columns = [col for col in df.columns if col not in ["Student No", "Name", "Gender"]]
        marks_df = student_df[ca_columns]

        # Color styling
        styled_df = marks_df.style.set_properties(**{
            'background-color': '#D6EAF8',
            'color': 'black',
            'border-color': 'white'
        })

        st.dataframe(styled_df, use_container_width=True)

        # Total marks
        total = marks_df.sum(axis=1).values[0]
        st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/{marks_df.shape[1]*15}</h3>", unsafe_allow_html=True)
    else:
        st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed using AI |Bimal K. Chetri (PhD)</p>", unsafe_allow_html=True)
