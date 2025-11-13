# app.py - Sherubtse College CA Marks Dashboard
# Hosted on: https://ca-marks-dashboard.streamlit.app
# Admin: Dr. Bimal | Students: View only
import streamlit as st
import pandas as pd

# ================== CONFIG ==================
st.set_page_config(
    page_title="Sherubtse CA Marks",
    page_icon="📊",
    layout="wide"
)

# ================== HEADER ==================
st.markdown("""
<div style="text-align:center; background:#1F618D; padding:25px; border-radius:15px; margin-bottom:30px">
    <h1 style="color:white; margin:0">Sherubtse College</h1>
    <h2 style="color:#D6EAF8; margin:5px">Department of Life Science</h2>
    <h3 style="color:white; margin:0">Continuous Assessment Dashboard</h3>
    <img src="https://raw.githubusercontent.com/bimalkc-design/ca-marks-dashboard/main/college_logo.png" width="100">
</div>
""", unsafe_allow_html=True)

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    files = {
        "BTS101 - Algae and Fungi (1st Year)": "BTS101.CA.xlsx",
        "BTS306 - Plant Breeding & Horticulture (3rd Year)": "BTS306.CA.xlsx"
    }
    data = {}
    for name, file in files.items():
        try:
            df = pd.read_excel(file)
            df.columns = [str(c).strip() for c in df.columns]
            df["Student No"] = df["Student No"].astype(int).astype(str).str.zfill(8)
            data[name] = df
        except Exception as e:
            st.error(f"Could not load {file}: {e}")
    return data, files

data_dict, file_map = load_data()

ca_components = [
    'Written Assignment (15)',
    'Class Test (15)',
    'Lab Record (10)',
    'Presentation (10)',
    'Project Report (10)'
]

# ================== MAIN MENU BUTTONS ==================
st.markdown("### Access Mode")
col1, col2 = st.columns(2)
with col1:
    if st.button("👨‍🎓 Student View"):
        role = "student"
with col2:
    if st.button("👨‍🏫 Admin Login"):
        role = "admin"

# Default if no button pressed
if 'role' not in locals():
    st.info("Select your access mode above to continue.")
    st.stop()

# ================== ADMIN MODE ==================
if role == "admin":
    password = st.text_input("Admin Password", type="password", help="Contact Dr. Bimal")
    if password != st.secrets.get("ADMIN_PASSWORD", "bimal@123"):
        st.error("Incorrect password")
        st.stop()
    st.success("Admin access granted")

    module_name = st.selectbox("Select Module", list(data_dict.keys()))
    df = data_dict[module_name]
    filename = file_map[module_name]

    student_list = df["Student No"].tolist()
    selected_student = st.selectbox("Select Student to Update", student_list)

    row_idx = df[df["Student No"] == selected_student].index[0]
    student = df.loc[row_idx]

    st.info(f"**{student['Name']}** | {student['Gender']} | {selected_student}")

    st.markdown("### Update CA Marks")
    with st.form("admin_update_form"):
        new_marks = {}
        cols = st.columns(3)
        max_vals = [15, 15, 10, 10, 10]

        for i, comp in enumerate(ca_components):
            with cols[i % 3]:
                current = student[comp]
                if pd.isna(current): current = 0
                new_marks[comp] = st.number_input(
                    comp, min_value=0, max_value=max_vals[i],
                    value=int(current), step=1
                )

        submitted = st.form_submit_button("💾 Save Marks")

        if submitted:
            for comp, val in new_marks.items():
                df.at[row_idx, comp] = val
            df.to_excel(filename, index=False)
            st.success(f"Marks updated for {student['Name']} in {module_name}")
            st.balloons()
            st.cache_data.clear()

# ================== STUDENT MODE ==================
else:
    module_name = st.selectbox("Select Module", list(data_dict.keys()))
    df = data_dict[module_name]

    st.markdown("### Enter Your Student No")
    student_no_input = st.text_input("", placeholder="e.g. 07250087")
    if student_no_input:
        student_no_input = student_no_input.strip().zfill(8)
        if st.button("🔍 View Marks"):
            if student_no_input not in df["Student No"].values:
                st.error("Student No not found. Please check and try again.")
            else:
                student = df[df["Student No"] == student_no_input].iloc[0]
                st.success(f"Welcome, **{student['Name']}** ({student['Gender']})")

                st.markdown("### Your CA Marks")
                total = 0
                marks_data = []
                for comp in ca_components:
                    marks = int(student[comp]) if not pd.isna(student[comp]) else 0
                    max_mark = int(comp.split("(")[1].split(")")[0])
                    total += marks
                    marks_data.append((comp, marks, max_mark, f"{marks}/{max_mark}"))
                
                # Display table with colors
                st.table(pd.DataFrame(marks_data, columns=["Component", "Marks Obtained", "Max Marks", "Score"]))

                st.markdown(f"""
                <div style="text-align:center; margin:20px; padding:20px; background:#D6EAF8; border-radius:15px">
                    <h2 style="color:#CB4335; margin:0">Total CA Marks: {total}/60</h2>
                </div>
                """, unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("---")
st.caption("Developed by Dr. Bimal K Chetri (PhD) | Sherubtse College | 2025 | Hosted on GitHub + Streamlit")
