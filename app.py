# app.py - Sherubtse College CA Marks Dashboard (Responsive Version)
# Hosted on: https://ca-marks-dashboard.streamlit.app
# Admin access: password-protected

import streamlit as st
import pandas as pd

# ================== CONFIG ==================
st.set_page_config(
    page_title="Sherubtse CA Marks",
    page_icon="📊",
    layout="wide",               # Wide layout for PC and mobile
    initial_sidebar_state="collapsed"
)

# ================== HEADER ==================
st.markdown("""
<div style="text-align:center; background:#1F618D; padding:20px; border-radius:15px; margin-bottom:30px; max-width:90%; margin-left:auto; margin-right:auto;">
    <h1 style="color:white; margin:0; font-size:2em">Sherubtse College</h1>
    <h2 style="color:#D6EAF8; margin:5px; font-size:1.2em">Department of Life Science</h2>
    <h3 style="color:white; font-size:1em">Continuous Assessment Dashboard</h3>
    <img src="https://raw.githubusercontent.com/bimalkc-design/ca-marks-dashboard/main/college_logo.png" width="80%">
</div>
""", unsafe_allow_html=True)

# ================== ADMIN LOGIN ==================
# Admin login input (hidden to students)
admin_password = st.sidebar.text_input("Admin Password", type="password", placeholder="Enter password", help="Contact Dr. Bimal")
is_admin = False
if admin_password:
    if admin_password == st.secrets.get("ADMIN_PASSWORD", "bimal@123"):
        is_admin = True
        st.sidebar.success("Admin access granted")
    else:
        st.sidebar.error("Incorrect password")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    files = {
        "BTS101 - Life Science": "BTS101.CA.xlsx",
        "BTS306 - Advanced Biology": "BTS306.CA.xlsx"
    }
    data = {}
    for name, file in files.items():
        try:
            df = pd.read_excel(file)
            df.columns = [str(c).strip() for c in df.columns]
            df["Student No"] = df["Student No"].astype(str)
            data[name] = df
        except:
            st.error(f"Could not load {file}")
    return data, files

data_dict, file_map = load_data()
module_name = st.selectbox("Select Module", list(data_dict.keys()))
df = data_dict[module_name]
filename = file_map[module_name]

ca_components = [
    'Written Assignment (15)',
    'Class Test (15)',
    'Lab Record (10)',
    'Presentation (10)',
    'Project Report (10)'
]

# ================== ADMIN MODE ==================
if is_admin:
    st.success("Admin Mode Active")
    student_list = df["Student No"].tolist()
    selected_student = st.selectbox("Select Student to Update", student_list, index=0)

    row_idx = df[df["Student No"] == selected_student].index[0]
    student = df.loc[row_idx]

    st.info(f"**{student['Name']}** | {student['Gender']} | {selected_student}")

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

        submitted = st.form_submit_button("SAVE MARKS TO EXCEL FILE")
        if submitted:
            for comp, val in new_marks.items():
                df.at[row_idx, comp] = val
            df.to_excel(filename, index=False)
            st.success(f"Marks updated for {student['Name']} in {module_name}")
            st.balloons()
            st.cache_data.clear()

# ================== STUDENT VIEW ==================
else:
    student_no = st.text_input("Enter Your Student No", placeholder="e.g. 2021001")
    if not student_no:
        st.info("Please enter your Student No to continue.")
        st.stop()
    if student_no not in df["Student No"].values:
        st.error("Student No not found. Please check and try again.")
        st.stop()

    student = df[df["Student No"] == student_no].iloc[0]
    st.success(f"Welcome, **{student['Name']}** ({student['Gender']})")

    st.markdown("### Your CA Marks")
    total = 0
    cols = st.columns(3)
    for i, comp in enumerate(ca_components):
        marks = student[comp]
        if pd.isna(marks): marks = 0
        marks = int(marks)
        total += marks
        max_mark = int(comp.split("(")[1].split(")")[0])
        with cols[i % 3]:
            delta = f"{marks}/{max_mark}"
            st.metric(comp, marks, delta)

    st.markdown(f"""
    <div style="text-align:center; margin:20px; padding:15px; background:#D6EAF8; border-radius:15px">
        <h2 style="color:#CB4335; margin:0">Total CA Marks: {total}/60</h2>
    </div>
    """, unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("---")
st.caption("Developed using AI tool by Bimal K Chetri (PhD) | Sherubtse College | 2025 | Hosted on GitHub + Streamlit")
