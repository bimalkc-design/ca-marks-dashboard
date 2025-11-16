# app.py – Sherubtse CA Dashboard | Student Results Viewer
# Updated for Streamlit Cloud
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# ----------------------
# Page Configuration
# ----------------------
st.set_page_config(
    page_title="Sherubtse CA Results",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# CSS Styling
# ----------------------
st.markdown("""
<style>
.title {color: #003366; font-weight: bold; text-align: center; font-size: 3rem;}
.subtitle {color: #0066cc; text-align: center; font-size: 1.5rem;}
.header-box {background: #fff; padding: 1rem; border-radius: 10px; text-align: center;}
.success-box {background: #d4edda; color: #155724; padding: 0.8rem; border-radius: 8px; font-weight: bold; text-align: center;}
.stDataFrame {font-size: 1.4rem !important; text-align: center;}
.footer {color: #555; font-size: 1rem; text-align: center; margin-top: 2rem; font-style: italic;}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Header
# ----------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=120)
    st.markdown('<div class="header-box"><div class="title">Sherubtse College</div><div class="subtitle">Continuous Assessment Results</div></div>', unsafe_allow_html=True)

# ----------------------
# Excel Files
# ----------------------
excel_files = {
    "BTS101": "BTS101.CA.xlsx",
    "BTS306": "BTS306.CA.xlsx"
}

# ----------------------
# Load Data
# ----------------------
@st.cache_data(ttl=3600)
def load_data():
    dfs = []
    for subj, file in excel_files.items():
        if not os.path.exists(file):
            st.warning(f"File not found: {file}")
            continue
        df = pd.read_excel(file, dtype={"Student No": str})
        keep = ["Student No","Name","Gender"]
        marks_cols = [c for c in df.columns if re.search(r"\(\d+\)", c)]
        if not marks_cols:
            st.warning(f"No assessment columns in {file}")
            continue
        melted = df.melt(id_vars=keep, value_vars=marks_cols,
                         var_name="Assessment_Type", value_name="Marks_Obtained")
        melted["Max_Marks"] = melted["Assessment_Type"].str.extract(r"\((\d+)\)").astype(float)
        melted["Marks_Obtained"] = pd.to_numeric(melted["Marks_Obtained"], errors="coerce")
        melted = melted.dropna(subset=["Marks_Obtained"])
        melted["Subject"] = subj
        melted["Student_Number"] = melted["Student No"].astype(str).str.strip()
        dfs.append(melted)
    if not dfs:
        st.error("No data available. Please check Excel files.")
        st.stop()
    data = pd.concat(dfs, ignore_index=True)
    data["Percentage"] = (data["Marks_Obtained"]/data["Max_Marks"]*100).round(2)
    return data

df = load_data()

# ----------------------
# Sidebar – Login
# ----------------------
with st.sidebar:
    st.markdown("### 🎓 Student Login")
    subjects = sorted(df["Subject"].unique()) if not df.empty else []
    subject = st.selectbox("Select Module", options=subjects) if subjects else None
    student_input = st.text_input("Enter Student No", placeholder="e.g., 07250087", type="password")
    st.caption("🔒 Secure & Private • View Only")

# ----------------------
# Display Student Data
# ----------------------
if student_input and subject:
    clean_input = ''.join(filter(str.isdigit, student_input.strip()))
    if not (7 <= len(clean_input) <= 8):
        st.error("⚠️ Enter 7–8 digits")
    else:
        candidates = [clean_input]
        if clean_input.startswith('7') and len(clean_input)==7: candidates.append('0'+clean_input)
        if clean_input.startswith('0') and len(clean_input)==8: candidates.append(clean_input[1:])
        filt = df[(df["Subject"]==subject) & (df["Student_Number"].isin(candidates))]
        if filt.empty:
            st.warning("❌ No results found")
        else:
            row = filt.iloc[0]
            st.markdown(f'<div class="success-box">Hello <strong>{row["Name"]}</strong>! Module: <strong>{subject}</strong> (ID: {row["Student_Number"]})</div>', unsafe_allow_html=True)
            
            # Metrics
            avg_pct = filt["Percentage"].mean()
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Average %", f"{avg_pct:.1f}%")
            with col2: st.metric("Assessments", len(filt))
            with col3: st.markdown(f"<div style='color:{'green' if avg_pct>=50 else 'red'}; font-weight:bold'>{'PASS' if avg_pct>=50 else 'AT RISK'}</div>", unsafe_allow_html=True)
            
            # Table
            disp = filt[["Assessment_Type","Marks_Obtained","Max_Marks","Percentage"]]
            st.dataframe(disp.style.format({"Percentage":"{:.1f}%","Marks_Obtained":"{:.1f}","Max_Marks":"{:.0f}"}).applymap(lambda x: f"background-color: {'#d4edda' if x>=50 else '#f8d7da'}", subset=["Percentage"]), use_container_width=True)
            
            # Charts
            fig_bar = px.bar(disp, x="Assessment_Type", y="Percentage", title="Performance Overview", color="Percentage", color_continuous_scale="Blues", text="Percentage")
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Pass Line")
            st.plotly_chart(fig_bar, use_container_width=True)

            fig_pie = px.pie(disp, values="Percentage", names="Assessment_Type", title="Assessment Breakdown", hole=0.4, color_discrete_sequence=px.colors.qualitative.Plotly)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------
# Footer
# ----------------------
st.markdown('<div class="footer">Developed using AI tool by Bimal K. Chetri (PhD), Dept. of Life Science, Sherubtse © 2025</div>', unsafe_allow_html=True)
