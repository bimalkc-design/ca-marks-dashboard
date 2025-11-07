# app.py
import streamlit as st
import pandas as pd
import os

# -------------------------------
# 1️⃣ Page config
# -------------------------------
st.set_page_config(
    page_title="CA Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# 2️⃣ Header with logo
# -------------------------------
header_html = """
<div style="display:flex; align-items:center; justify-content: space-between; background-color:#154360; padding:15px; border-radius:10px;">
    <div>
        <h1 style="color:white; margin:0;">Department of Life Science</h1>
        <h3 style="color:white; margin:0;">CA Dashboard - Sherubtse College</h3>
    </div>
    <div>
        <img src="college_logo.png" width="100">
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.markdown("### View your Continuous Assessment (CA) marks below 👇")

# -------------------------------
# 3️⃣ List available Excel files dynamically
# -------------------------------
excel_files = [f for f in os.listdir() if f.endswith(".xlsx")]

module_choice = st.selectbox("Select Module/Excel File", excel_files)

if module_choice:
    # -------------------------------
    # 4️⃣ Load Excel with robust header cleanup
    # -------------------------------
    df = pd.read_excel(module_choice)
    df.columns = [str(col).strip().replace('\n','').replace('\r','').replace('\xa0',' ') for col in df.columns]

    required_cols = ["Student No", "Name", "Gender"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel file must contain columns: {', '.join(required_cols)}")
    else:
        # -------------------------------
        # 5️⃣ Sidebar: select student
        # -------------------------------
        student_list = df["Student No"].tolist()
        student_choice = st.sidebar.selectbox("🔍 Select Student", student_list)

        student_df = df[df["Student No"] == student_choice]

        if not student_df.empty:
            st.markdown(f"### Student: {student_df['Name'].values[0]} ({student_choice})")
            st.markdown(f"**Gender:** {student_df['Gender'].values[0]}")

            # -------------------------------
            # 6️⃣ Display CA marks table
            # -------------------------------
            ca_columns = [col for col in df.columns if col not in required_cols]
            marks_df = student_df[ca_columns]

            # Convert marks to float if possible
            for col in marks_df.columns:
                try:
                    marks_df[col] = marks_df[col].astype(float)
                except:
                    pass

            styled_df = marks_df.style.set_properties(**{
                'background-color': '#D6EAF8',
                'color': 'black',
                'border-color': 'white',
                'text-align': 'center'
            })
            st.dataframe(styled_df, use_container_width=True)

            # Total marks
            total = marks_df.sum(axis=1).values[0]
            max_total = sum([15 if "15" in col else 10 for col in ca_columns])
            st.markdown(f"<h3 style='color:#CB4335'>Total CA Marks: {total}/{max_total}</h3>", unsafe_allow_html=True)
        else:
            st.warning("Student ID not found. Please select a valid ID from the sidebar.")

# -------------------------------
# 7️⃣ Footer
# -------------------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>© 2025 Department of Life Science | Sherubtse College | Developed by Dr. Bimal K. Chetri</p>", unsafe_allow_html=True)
