cat > app.py <<'PY'
# app.py – Student Self-Service CA Dashboard (WSL / Local Excel)
import streamlit as st
import pandas as pd
import plotly.express as px
import os, re

# ----------------------
# Page config (wide = mobile-friendly)
# ----------------------
st.set_page_config(
    page_title="CNR CA Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# Responsive CSS
# ----------------------
st.markdown("""
<style>
    .main {background:#f0f8ff;padding:1rem;}
    .title {color:#004080;font-weight:bold;text-align:center;}
    .subtitle {color:#0066cc;margin-bottom:1rem;text-align:center;}
    .footer {color:#555;font-size:14px;text-align:center;margin-top:2rem;}
    .stButton>button {background:#004080;color:white;width:100%;}
    @media (max-width:768px){
        .title{font-size:1.8rem;}
        .subtitle{font-size:1rem;}
        [data-testid="metric-container"]{font-size:1rem;}
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Header
# ----------------------
if os.path.exists("college_logo.png"):
    st.image("college_logo.png", width=120, use_column_width="auto")
st.markdown('<div class="title">Department of Life Sciences</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Continuous Assessment Dashboard</div>', unsafe_allow_html=True)

# ----------------------
# Local Excel files
# ----------------------
excel_files = {
    "BTS101": "BTS101.CA.xlsx",
    "BTS306": "BTS306.CA.xlsx"
}

# ----------------------
# Load + melt (cached)
# ----------------------
@st.cache_data
def load_data():
    dfs = []
    for subj, path in excel_files.items():
        if not os.path.exists(path):
            st.warning(f"Missing {path}")
            continue
        df = pd.read_excel(path)
        keep = ["Student No", "Name", "Gender"]
        mark_cols = [c for c in df.columns if re.search(r"\(\d+\)", c)]
        melted = df.melt(id_vars=keep, value_vars=mark_cols,
                         var_name="Assessment_Type", value_name="Marks_Obtained")
        melted["Max_Marks"] = melted["Assessment_Type"].str.extract(r"\((\d+)\)").astype(float)
        melted["Subject"] = subj
        melted.rename(columns={"Student No":"Student_Number"}, inplace=True)
        dfs.append(melted)
    if not dfs: st.stop()
    data = pd.concat(dfs, ignore_index=True)
    data["Percentage"] = (data["Marks_Obtained"]/data["Max_Marks"]*100).round(2)
    return data

df = load_data()
st.success(f"Loaded {len(df)} rows from {df['Subject'].nunique()} subject(s)")

# ----------------------
# Sidebar – Student login
# ----------------------
st.sidebar.header("Student Access")
subject = st.sidebar.selectbox("Select Subject", options=sorted(df["Subject"].unique()))
student_no = st.sidebar.text_input("Student Number", type="password")

if student_no and subject:
    filt = df[(df["Subject"]==subject) & (df["Student_Number"].astype(str)==student_no)]
    if filt.empty:
        st.warning(f"No record for **{subject}** – Student No **{student_no}**")
    else:
        name = filt["Name"].iloc[0]
        st.success(f"**{name}** – {subject}")

        # ---- Metrics ----
        col1,col2,col3 = st.columns(3)
        avg = filt["Percentage"].mean()
        col1.metric("Average", f"{avg:.1f}%")
        col2.metric("Assessments", len(filt))
        col3.metric("Status", "Pass" if avg>=50 else "At Risk", delta=None)

        # ---- Table ----
        disp = filt[["Assessment_Type","Marks_Obtained","Max_Marks","Percentage"]]
        st.markdown("### Your Marks")
        st.dataframe(disp.style.format({"Percentage":"{:.1f}%"}), use_container_width=True)

        # ---- Bar ----
        fig_bar = px.bar(disp, x="Assessment_Type", y="Percentage",
                         title="Performance %", color_discrete_sequence=["#0066cc"])
        fig_bar.add_hline(y=50, line_dash="dash", line_color="red")
        fig_bar.update_layout(height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---- Pie ----
        fig_pie = px.pie(disp, values="Percentage", names="Assessment_Type",
                         title="Breakdown", hole=.3)
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------
# Footer
# ----------------------
st.markdown("""
<div class="footer">
    Developed by Dr. Bimal K. Chetri (PhD) | © 2025 | CNR Bhutan
</div>
""", unsafe_allow_html=True)
PY
